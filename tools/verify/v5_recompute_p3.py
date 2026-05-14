"""V5: recompute P3 consensus distribution from the active triangulation
matrix and emit a report alongside per-silo breakdowns.

This script does NOT validate against a documented expected distribution
(those are documented in narrative form across multiple READMEs and the
distribution shifted in Phase 3). Its purpose is to produce a single
machine-readable snapshot of the *active* numbers so any prose claim can
be checked against `tools/verify/reports/v5_recompute_p3_<date>.json`.

Exit code is always 0 (informational), unless the matrix or schema
cannot be loaded.

Run: python -m tools.verify.v5_recompute_p3
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"
# Active S3 surface is the filtered matrix (110 inactive-silo rows dropped).
# See p3_thematic_synthesis/FREEZE.md and s3_quantum_advantage/combined/output/README.md.
MATRIX = REPO_ROOT / "p3_thematic_synthesis" / "s3_quantum_advantage" / "combined" / "output" / "triangulation_matrix.filtered.json"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows = json.loads(MATRIX.read_text(encoding="utf-8"))

    consensus = Counter(r["consensus_verdict"] for r in rows)
    pre_veto = Counter(r["pre_veto_consensus"] for r in rows)
    veto_count = sum(1 for r in rows if r.get("L5_veto_applied"))
    l2_disagreement = sum(1 for r in rows if r.get("L2_merge_disagreement"))

    by_silo: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_silo[r["silo"]][r["consensus_verdict"]] += 1
    by_algo: dict[str, Counter] = defaultdict(Counter)
    for r in rows:
        by_algo[r["algorithm_family"]][r["consensus_verdict"]] += 1

    layers_scored_dist = Counter(r["layers_scored"] for r in rows)

    summary = {
        "script": "v5_recompute_p3",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "matrix_path": str(MATRIX.relative_to(REPO_ROOT)).replace("\\", "/"),
        "row_count": len(rows),
        "consensus_distribution": dict(consensus),
        "pre_veto_distribution": dict(pre_veto),
        "nisq_veto_applied_count": veto_count,
        "l2_merge_disagreement_count": l2_disagreement,
        "layers_scored_histogram": {str(k): v for k, v in sorted(layers_scored_dist.items())},
        "consensus_by_silo": {s: dict(c) for s, c in sorted(by_silo.items())},
        "consensus_by_algorithm_family": {a: dict(c) for a, c in sorted(by_algo.items())},
    }
    out = REPORT_DIR / f"v5_recompute_p3_{_dt.date.today().isoformat()}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"V5 recompute_p3: {len(rows)} rows; {len(consensus)} distinct consensus labels")
    for label, n in consensus.most_common():
        print(f"  {label:25s} {n:5d}")
    print(f"  NISQ veto applied:        {veto_count}")
    print(f"  L2 merge disagreement:    {l2_disagreement}")
    print(f"  report: {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
