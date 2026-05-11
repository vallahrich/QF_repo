"""Render the Stage C3 theme-to-literature crosswalk prompt for ONE silo.

Per-silo variant of render_c3_prompt.py:
- Theme set: ALL analytical themes (ATs) from
  s4_thematic_coding/{silo}/themes/b2_silo_themes.json (output.analytical_themes).
- Review pool: identical to the cross-silo C3 run (16 reviews extracted from
  P2 processed markdown), so per-silo crosswalks are comparable.

Outputs (under s4_thematic_coding/{silo}/themes/):
  c3_crosswalk.prompt.txt
  c3_crosswalk.meta.json

The prompt template is unchanged: prompts/c3_theme_literature_crosswalk_v1.txt.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parent
P2_DIR = REPO_ROOT / "p2_systematic_review" / "output" / "processed"
PROMPT_FILE = ROOT / "prompts" / "c3_theme_literature_crosswalk_v1.txt"

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
SECTION_MAX_CHARS = 1400

SILO_CODE = {
    "credit_lending": "CL",
    "derivative_pricing": "DP",
    "fraud_detection": "FD",
    "portfolio_optimization": "PO",
    "quantum_ml_finance": "QML",
    "risk_management": "RM",
    "simulation_monte_carlo": "SMC",
    "trading_execution": "TE",
}


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
        reviews.append({"paper_id": md_path.stem, "title": title, "sections": sections})
    return reviews


def load_silo_themes(silo: str) -> tuple[list[dict], str]:
    path = ROOT / "s4_thematic_coding" / silo / "themes" / "b2_silo_themes.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    silo_code = data["output"].get("silo") or SILO_CODE[silo]
    ats = data["output"]["analytical_themes"]
    themes = []
    for at in ats:
        themes.append({
            "theme_id": at["theme_id"],
            "silo_code": silo_code,
            "theme_label": at["theme_label"],
            "interpretation": at.get("interpretation", ""),
            "verdict": "analytical_theme",
            "supporting_paper_count": len(at.get("supporting_papers", [])),
        })
    return themes, silo_code


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--silo", required=True, choices=sorted(SILO_CODE))
    args = ap.parse_args()
    silo = args.silo

    themes, silo_code = load_silo_themes(silo)
    reviews = load_reviews()

    tpl = PROMPT_FILE.read_text(encoding="utf-8")
    prompt_sha = hashlib.sha256(tpl.encode("utf-8")).hexdigest()

    rendered = tpl.format(
        themes_json=json.dumps(themes, indent=2, ensure_ascii=False),
        reviews_json=json.dumps(reviews, indent=2, ensure_ascii=False),
    )
    rendered_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    out_dir = ROOT / "s4_thematic_coding" / silo / "themes"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "c3_crosswalk.prompt.txt").write_text(rendered, encoding="utf-8")

    meta = {
        "stage": "C3",
        "scope": "per_silo",
        "silo": silo,
        "silo_code": silo_code,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_file": "c3_theme_literature_crosswalk_v1.txt",
        "prompt_sha256": prompt_sha,
        "rendered_sha256": rendered_sha,
        "prompt_chars": len(rendered),
        "approx_tokens_k": round(len(rendered) / 4000, 1),
        "theme_count": len(themes),
        "theme_ids": [t["theme_id"] for t in themes],
        "review_pool_size": len(reviews),
        "review_ids": [r["paper_id"] for r in reviews],
        "model_intended": "claude-opus-4.6",
    }
    (out_dir / "c3_crosswalk.meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"silo={silo} ({silo_code}) themes={len(themes)} reviews={len(reviews)} "
          f"chars={len(rendered):,} ~{meta['approx_tokens_k']}K tok")
    print(f"written: {out_dir.relative_to(REPO_ROOT)}/c3_crosswalk.prompt.txt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
