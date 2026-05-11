"""V7: enumerate algorithm.family values across the P3 S2 extractions.

Reports the histogram of family strings actually present in the frozen
extraction corpus, plus the canonical sets hard-coded in the s3
assessor switch-statements (Dalzell QIPM gate, Rønnow applicable
families). Surfaces values that no assessor covers (potential silent
mis-classifications).

Read-only; informational.

Run: python -m tools.verify.v7_algorithm_families
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"
S2_EXTRACTIONS = REPO_ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "extractions"

# Mirror the gate sets defined in the assessors. KEEP IN SYNC if you
# touch assess_dalzell.py or assess_ronnow.py.
DALZELL_QIPM_FAMILIES = {
    "qipm", "quantum-interior-point", "quantum_interior_point",
    "quantum-ipm", "interior-point",
}
RONNOW_APPLICABLE_FAMILIES = {
    "qaoa", "grover", "amplitude-estimation", "amplitude_estimation",
    "amplitude-amplification", "amplitude_amplification",
    "quantum-annealing", "quantum_annealing", "qaoa-annealing",
}


def _iter_experiments():
    for p in S2_EXTRACTIONS.rglob("*.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        # Extractions are envelopes with experiments[]
        for exp in data.get("experiments") or []:
            yield p.relative_to(REPO_ROOT), exp


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    histogram: Counter = Counter()
    null_count = 0
    total = 0
    for _path, exp in _iter_experiments():
        total += 1
        algo = exp.get("algorithm") or {}
        family = algo.get("family")
        if family is None or family == "":
            null_count += 1
            continue
        histogram[str(family).lower().strip()] += 1

    families = set(histogram)
    summary = {
        "script": "v7_algorithm_families",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "extraction_root": str(S2_EXTRACTIONS.relative_to(REPO_ROOT)).replace("\\", "/"),
        "experiment_count": total,
        "experiments_without_algorithm_family": null_count,
        "distinct_family_count": len(families),
        "family_histogram": dict(histogram.most_common()),
        "dalzell_qipm_families": sorted(DALZELL_QIPM_FAMILIES),
        "ronnow_applicable_families": sorted(RONNOW_APPLICABLE_FAMILIES),
        "in_corpus_not_in_dalzell_qipm": sorted(families - DALZELL_QIPM_FAMILIES),
        "in_corpus_not_in_ronnow_applicable": sorted(families - RONNOW_APPLICABLE_FAMILIES),
        "in_dalzell_qipm_not_in_corpus": sorted(DALZELL_QIPM_FAMILIES - families),
        "in_ronnow_applicable_not_in_corpus": sorted(RONNOW_APPLICABLE_FAMILIES - families),
    }
    out = REPORT_DIR / f"v7_algorithm_families_{_dt.date.today().isoformat()}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"V7 algorithm.family enum:")
    print(f"  total experiments scanned: {total}")
    print(f"  without family: {null_count}")
    print(f"  distinct families: {len(families)}")
    print(f"  top 10:")
    for fam, n in histogram.most_common(10):
        print(f"    {fam:35s} {n:5d}")
    print(f"  report: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
