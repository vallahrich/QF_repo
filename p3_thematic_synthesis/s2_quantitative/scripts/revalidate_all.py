"""Re-normalize and re-validate all existing extractions in place.

Loads each extraction JSON from output/extractions/, re-runs the updated
normalizer (which now coerces hardware.type, feasibility_horizon,
maturity_level, paper_metadata.year, and various string-typed numeric fields
to their schema enums / types), fills in missing paper_metadata from P2
output for 0-experiment papers, re-runs the validator, and writes the result
back.

No LLM calls are made.

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.revalidate_all
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from p3_thematic_synthesis.s2_quantitative.scripts.validate_benchmarks import (
    compute_quality_score,
    normalize_extraction_metrics,
    validate_extraction,
)

OUTPUT_DIR = _QUANT_ROOT / "output" / "extractions"
P2_DIR = _PROJECT_ROOT / "p2_systematic_review" / "output" / "processed"


def _p2_metadata(paper_id: str) -> dict:
    p2 = P2_DIR / f"{paper_id}_extraction.json"
    if not p2.is_file():
        p2 = P2_DIR / f"{paper_id}.json"
    if not p2.is_file():
        return {}
    try:
        d = json.loads(p2.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {
        "title": d.get("title", ""),
        "authors": d.get("authors", []),
        "year": d.get("year"),
        "doi": d.get("doi", ""),
    }


def revalidate_one(path: Path) -> tuple[int, int, bool]:
    data = json.loads(path.read_text(encoding="utf-8"))
    paper_id = data.get("paper_id", path.stem)

    # Backfill missing paper_metadata from P2 (fixes the 0-experiment fallbacks)
    pm = data.get("paper_metadata")
    if pm is None or not pm.get("title"):
        meta = _p2_metadata(paper_id)
        data["paper_metadata"] = {
            "title": meta.get("title", "") or f"(no title; paper_id={paper_id})",
            "authors": meta.get("authors", []),
            "year": meta.get("year"),
            "doi": meta.get("doi", ""),
            "scope": "gate_based",
        }

    # Ensure extraction_metadata carries the freeze stamps
    em = data.setdefault("extraction_metadata", {})
    em.setdefault("schema_version", "benchmark_extraction_v1.0")
    em.setdefault("scope", "gate_based")
    em.setdefault("revalidated_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))

    # Re-normalize
    normalize_extraction_metrics(data)

    # Re-validate
    errors, warnings = validate_extraction(data)
    em["validation_errors"] = len(errors)
    em["validation_warnings"] = len(warnings)
    em["validation_passed"] = len(errors) == 0
    em["validation_error_details"] = errors if errors else []
    em["validation_warning_details"] = warnings if warnings else []

    # Re-score
    q = compute_quality_score(data)
    em["quality_score"] = q["score"]
    em["quality_details"] = q

    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return len(errors), len(warnings), bool(em["validation_passed"])


def main() -> int:
    files = sorted(OUTPUT_DIR.glob("*.json"))
    print(f"revalidating {len(files)} extractions ...")
    n_pass = 0
    err_hist = Counter()
    warn_hist = Counter()
    for i, p in enumerate(files, 1):
        try:
            e, w, ok = revalidate_one(p)
        except Exception as exc:
            print(f"  [{i}/{len(files)}] {p.name}: FAILED {exc}")
            continue
        err_hist[e] += 1
        warn_hist[w] += 1
        if ok:
            n_pass += 1
        if i % 50 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] pass={n_pass} err_hist_top={sorted(err_hist.items())[:5]}")

    print(f"\ntotal: {len(files)}  validation_passed: {n_pass}  "
          f"error-free rate: {n_pass/len(files)*100:.1f}%")
    print(f"papers with 0 errors: {err_hist[0]}")
    print(f"papers with 1-3 errors: {sum(err_hist[k] for k in (1,2,3))}")
    print(f"papers with >=4 errors: {sum(err_hist[k] for k in err_hist if k >= 4)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
