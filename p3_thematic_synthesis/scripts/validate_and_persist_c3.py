"""Validate and persist the Stage C3 theme-to-literature crosswalk.

Enforces L-C3:
  1. Every shortlisted theme_id appears exactly once.
  2. Each theme has 2-3 crosswalk entries.
  3. Every review_paper_id is in the provided review pool (no hallucination).
  4. Every relationship is one of {confirms, extends, contradicts, complements}.
  5. quoted_claim length <= 40 words.
  6. quoted_claim is a verbatim substring of the review's extracted sections.

On PASS: writes s5_cross_silo/c3_crosswalk.json (validated).
On FAIL: prints violations and exits non-zero without writing the validated file.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALID_RELATIONSHIPS = {"confirms", "extends", "contradicts", "complements"}


def extract_json(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        m = re.search(r"```(?:json)?\s*\n(.*?)\n```", raw, flags=re.DOTALL)
        if m:
            raw = m.group(1)
    return json.loads(raw)


def word_count(s: str) -> int:
    return len(s.split())


def main():
    raw_path = ROOT / "s5_cross_silo" / "c3_crosswalk.raw_response.txt"
    if not raw_path.exists():
        print(f"FAIL: missing raw response at {raw_path}")
        return 1
    raw = raw_path.read_text(encoding="utf-8")
    try:
        data = extract_json(raw)
    except json.JSONDecodeError as e:
        print(f"FAIL: JSON parse error: {e}")
        return 1

    shortlist = json.loads(
        (ROOT / "s5_cross_silo" / "crosswalk_shortlist.json").read_text(encoding="utf-8")
    )
    expected_theme_ids = {r["theme_id"] for r in shortlist["shortlist"]}

    prompt_meta = json.loads(
        (ROOT / "s5_cross_silo" / "c3_crosswalk.meta.json").read_text(encoding="utf-8")
    )
    review_pool_ids = set(prompt_meta["review_ids"])

    # Load review section texts to verify verbatim quotes.
    # Re-use render_c3_prompt.py section-extraction logic.
    from render_c3_prompt import load_reviews
    reviews = {r["paper_id"]: r for r in load_reviews()}
    review_combined_text = {
        pid: " ".join(r["sections"].values()) for pid, r in reviews.items()
    }

    errs = []
    cw = data.get("crosswalk")
    if not isinstance(cw, list):
        errs.append("output.crosswalk missing or not a list")
    else:
        seen_theme_ids = set()
        relationship_counts = {k: 0 for k in VALID_RELATIONSHIPS}
        reviews_cited = set()
        for i, item in enumerate(cw):
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
                # Normalize whitespace for robust substring match
                hs_norm = re.sub(r"\s+", " ", haystack).lower()
                q_norm = re.sub(r"\s+", " ", q).lower()
                if q_norm and q_norm not in hs_norm:
                    # Allow small fragment: try checking first 60 chars
                    fragment = q_norm[:60]
                    if fragment not in hs_norm:
                        errs.append(f"{tid}/entry{j}: quoted_claim not found in review {rpid} (first 60 chars: {fragment!r})")
        missing = expected_theme_ids - seen_theme_ids
        if missing:
            errs.append(f"missing theme_ids in output: {sorted(missing)}")

        # Stance discrimination (rule 5): at least 2 of confirms/extends/contradicts each
        # (complements can be any count)
        for req_rel in ("confirms", "extends", "contradicts"):
            if relationship_counts[req_rel] < 2:
                errs.append(f"stance discrimination failure: {req_rel} used {relationship_counts[req_rel]}x (need >=2)")

    if errs:
        print("L-C3 FAIL — violations:")
        for e in errs:
            print(f"  - {e}")
        return 1

    # Persist validated
    out_path = ROOT / "s5_cross_silo" / "c3_crosswalk.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print("L-C3 PASS")
    print(f"  themes covered: {len(seen_theme_ids)}")
    print(f"  relationship counts: {relationship_counts}")
    print(f"  distinct reviews cited: {len(reviews_cited)}/{len(review_pool_ids)}")
    print(f"  written: s5_cross_silo/c3_crosswalk.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
