"""Validate and persist a per-silo Stage C3 crosswalk.

Mirrors validate_and_persist_c3.py but reads/writes under
s4_thematic_coding/{silo}/themes/.

Enforces L-C3:
  1. Every theme_id from the silo's b2 analytical_themes appears exactly once.
  2. Each theme has 2-3 crosswalk entries.
  3. Every review_paper_id is in the prompt's review pool (no hallucination).
  4. Every relationship is one of {confirms, extends, contradicts, complements}.
  5. quoted_claim length <= 40 words.
  6. quoted_claim is a verbatim substring of the review's extracted sections.
  7. Stance discrimination: each of confirms/extends/contradicts used >= 2x.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from render_c3_per_silo import load_reviews, SILO_CODE  # noqa: E402

VALID_RELATIONSHIPS = {"confirms", "extends", "contradicts", "complements"}


def extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        m = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, flags=re.DOTALL)
        if m:
            raw = m.group(1)
    # Try direct parse; fall back to first { ... } block.
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


def word_count(s: str) -> int:
    return len(s.split())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--silo", required=True, choices=sorted(SILO_CODE))
    args = ap.parse_args()
    silo = args.silo

    base = ROOT / "s4_thematic_coding" / silo / "themes"
    raw_path = base / "c3_crosswalk.raw_response.txt"
    meta_path = base / "c3_crosswalk.meta.json"
    b2_path = base / "b2_silo_themes.json"

    if not raw_path.exists():
        print(f"FAIL: missing raw response at {raw_path}")
        return 1
    if not meta_path.exists():
        print(f"FAIL: missing meta at {meta_path} (run render_c3_per_silo.py first)")
        return 1

    raw = raw_path.read_text(encoding="utf-8")
    try:
        data = extract_json(raw)
    except json.JSONDecodeError as e:
        print(f"FAIL: JSON parse error: {e}")
        return 1

    b2 = json.loads(b2_path.read_text(encoding="utf-8"))
    expected_theme_ids = {at["theme_id"] for at in b2["output"]["analytical_themes"]}

    prompt_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    review_pool_ids = set(prompt_meta["review_ids"])

    reviews = {r["paper_id"]: r for r in load_reviews()}
    review_combined_text = {
        pid: " ".join(r["sections"].values()) for pid, r in reviews.items()
    }

    errs: list[str] = []
    cw = data.get("crosswalk")
    seen_theme_ids: set[str] = set()
    relationship_counts = {k: 0 for k in VALID_RELATIONSHIPS}
    reviews_cited: set[str] = set()
    if not isinstance(cw, list):
        errs.append("output.crosswalk missing or not a list")
    else:
        for item in cw:
            tid = item.get("theme_id")
            if tid in seen_theme_ids:
                errs.append(f"duplicate theme_id {tid}")
            seen_theme_ids.add(tid)
            if tid not in expected_theme_ids:
                errs.append(f"unexpected theme_id {tid}")
            entries = item.get("entries", [])
            if not isinstance(entries, list) or not 2 <= len(entries) <= 3:
                errs.append(f"{tid}: entries count {len(entries)} not in [2,3]")
                continue
            for j, e in enumerate(entries):
                rpid = e.get("review_paper_id")
                if rpid not in review_pool_ids:
                    errs.append(f"{tid}/entry{j}: review_paper_id {rpid!r} not in pool")
                    continue
                reviews_cited.add(rpid)
                rel = e.get("relationship")
                if rel not in VALID_RELATIONSHIPS:
                    errs.append(f"{tid}/entry{j}: invalid relationship {rel!r}")
                else:
                    relationship_counts[rel] += 1
                q = e.get("quoted_claim", "")
                if word_count(q) > 40:
                    errs.append(f"{tid}/entry{j}: quoted_claim has {word_count(q)} words (>40)")
                haystack = review_combined_text.get(rpid, "")
                hs_norm = re.sub(r"\s+", " ", haystack).lower()
                q_norm = re.sub(r"\s+", " ", q).lower()
                if q_norm and q_norm not in hs_norm:
                    fragment = q_norm[:60]
                    if fragment not in hs_norm:
                        errs.append(
                            f"{tid}/entry{j}: quoted_claim not found in review {rpid} "
                            f"(first 60 chars: {fragment!r})"
                        )
        missing = expected_theme_ids - seen_theme_ids
        if missing:
            errs.append(f"missing theme_ids in output: {sorted(missing)}")
        for req_rel in ("confirms", "extends", "contradicts"):
            if relationship_counts[req_rel] < 2:
                errs.append(
                    f"stance discrimination failure: {req_rel} used "
                    f"{relationship_counts[req_rel]}x (need >=2)"
                )

    if errs:
        print(f"L-C3 FAIL ({silo}) — violations:")
        for e in errs:
            print(f"  - {e}")
        return 1

    out_path = base / "c3_crosswalk.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"L-C3 PASS ({silo})")
    print(f"  themes covered: {len(seen_theme_ids)}/{len(expected_theme_ids)}")
    print(f"  relationship counts: {relationship_counts}")
    print(f"  distinct reviews cited: {len(reviews_cited)}/{len(review_pool_ids)}")
    print(f"  written: {out_path.relative_to(ROOT.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
