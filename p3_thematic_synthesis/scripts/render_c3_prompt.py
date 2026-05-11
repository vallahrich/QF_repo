"""Render the Stage C3 theme-to-literature crosswalk prompt.

Loads:
- shortlist of analytical themes from s5_cross_silo/crosswalk_shortlist.json
- review-article pool: P2 processed markdown files whose titles match
  review | survey | overview | state of the art | taxonomy | landscape | systematic
  (extracts structured sections: Abstract summary, Findings, Quantum advantage
  claim, Limitations, Key ideas, Contradictions)

Renders the pre-committed prompt template with theme + review payload,
writes to s5_cross_silo/c3_crosswalk.prompt.txt plus meta.
"""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
P2_DIR = REPO_ROOT / "p2_systematic_review" / "output" / "processed"
TITLE_PATTERN = re.compile(
    r"\b(review|survey|overview|state of the art|taxonomy|landscape|systematic)\b",
    re.IGNORECASE,
)
SECTIONS_WANTED = [
    "Abstract summary",
    "Findings",
    "Quantum advantage claim",
    "Limitations",
    "Key ideas",
    "Contradictions",
]
SECTION_MAX_CHARS = 1400  # Per-section cap to bound prompt size.


def extract_title(md_head: str) -> str | None:
    m = re.search(r"aliases:\s*(?:\n-\s*.+)+", md_head)
    if not m:
        return None
    first = re.search(r"-\s*['\"]?(.+?)['\"]?\n", m.group(0) + "\n")
    return first.group(1).strip() if first else None


def extract_sections(md: str) -> dict[str, str]:
    sections = {}
    for sec in SECTIONS_WANTED:
        pat = re.compile(rf"(?ms)^##\s+{re.escape(sec)}\s*$\n(.+?)(?=^##\s|\Z)")
        m = pat.search(md)
        if not m:
            continue
        text = m.group(1).strip()
        if len(text) > SECTION_MAX_CHARS:
            text = text[:SECTION_MAX_CHARS] + " …[truncated]"
        sections[sec] = text
    return sections


def load_reviews() -> list[dict]:
    reviews = []
    for md_path in sorted(P2_DIR.glob("*.md")):
        head = md_path.read_text(encoding="utf-8", errors="ignore")[:2000]
        title = extract_title(head)
        if not title or not TITLE_PATTERN.search(title):
            continue
        full = md_path.read_text(encoding="utf-8", errors="ignore")
        sections = extract_sections(full)
        if not sections:
            continue
        reviews.append({
            "paper_id": md_path.stem,
            "title": title,
            "sections": sections,
        })
    return reviews


def load_shortlist() -> list[dict]:
    data = json.loads(
        (ROOT / "s5_cross_silo" / "crosswalk_shortlist.json").read_text(encoding="utf-8")
    )
    themes = []
    for r in data["shortlist"]:
        themes.append({
            "theme_id": r["theme_id"],
            "silo_code": r["silo_code"],
            "theme_label": r["theme_label"],
            "interpretation": r["interpretation"],
            "verdict": r["verdict"],
            "supporting_paper_count": r["supporting_paper_count"],
        })
    return themes


def main():
    themes = load_shortlist()
    reviews = load_reviews()

    tpl = (ROOT / "prompts" / "c3_theme_literature_crosswalk_v1.txt").read_text(encoding="utf-8")
    prompt_sha = hashlib.sha256(tpl.encode("utf-8")).hexdigest()

    rendered = tpl.format(
        themes_json=json.dumps(themes, indent=2, ensure_ascii=False),
        reviews_json=json.dumps(reviews, indent=2, ensure_ascii=False),
    )
    rendered_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    out_dir = ROOT / "s5_cross_silo"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "c3_crosswalk.prompt.txt").write_text(rendered, encoding="utf-8")

    meta = {
        "stage": "C3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_file": "c3_theme_literature_crosswalk_v1.txt",
        "prompt_sha256": prompt_sha,
        "rendered_sha256": rendered_sha,
        "prompt_chars": len(rendered),
        "approx_tokens_k": round(len(rendered) / 4000, 1),
        "theme_count": len(themes),
        "review_pool_size": len(reviews),
        "review_ids": [r["paper_id"] for r in reviews],
        "model_intended": "claude-opus-4.6",
    }
    (out_dir / "c3_crosswalk.meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Themes: {len(themes)}")
    print(f"Reviews in pool: {len(reviews)}")
    print(f"Prompt size: {len(rendered):,} chars (~{meta['approx_tokens_k']}K tokens)")
    print(f"Written: s5_cross_silo/c3_crosswalk.prompt.txt")


if __name__ == "__main__":
    main()
