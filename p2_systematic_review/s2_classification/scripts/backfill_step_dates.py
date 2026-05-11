"""Backfill audit script: rewrites synthetic per-step timestamps to a sentinel.

Earlier runs of `run_classification.py` (the production pipeline that produced
the 777 outputs) computed `now = datetime.now().isoformat()` once per paper
and fed the same string to all six `_write_stepN_results` calls, so every
classified frontmatter shows six identical `step{N}_date` fields.

This script walks `output/processed/*.md`, and **only when all six step dates
exist and are identical and are not already the sentinel**, rewrites them to
the sentinel string `"unknown_pre_2026-05-02"`. Idempotent (re-running is a
no-op once papers have been backfilled).

Outputs an audit report at `output/audit/step_date_backfill_report.json`.

The forward fix (per-step `datetime.now()`) is in
`run_classification.py::run_paper`; this script only reconciles the existing
corpus.

Usage (from the repo root):

    python -m p2_systematic_review.s2_classification.scripts.backfill_step_dates
    python -m p2_systematic_review.s2_classification.scripts.backfill_step_dates --dry-run
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_S2_ROOT = _SCRIPT_DIR.parent
_P2_ROOT = _S2_ROOT.parent
_REPO_ROOT = _P2_ROOT.parent

for p in (str(_P2_ROOT), str(_REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from s2_classification.utils.frontmatter import (  # noqa: E402
    read_frontmatter,
    update_frontmatter,
)

PROCESSED_DIR = _P2_ROOT / "output" / "processed"
AUDIT_DIR = _P2_ROOT / "output" / "audit"
REPORT_PATH = AUDIT_DIR / "step_date_backfill_report.json"

SENTINEL = "unknown_pre_2026-05-02"
STEP_FIELDS = [f"step{n}_date" for n in range(1, 7)]


def _classify(meta: dict) -> str:
    """Return one of: 'sentinel', 'identical', 'distinct', 'incomplete', 'absent'."""
    values = [meta.get(f) for f in STEP_FIELDS]
    if all(v is None or v == "" for v in values):
        return "absent"
    if any(v is None or v == "" for v in values):
        return "incomplete"
    if all(v == SENTINEL for v in values):
        return "sentinel"
    if len(set(values)) == 1:
        return "identical"
    return "distinct"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Report only; do not modify files.")
    args = parser.parse_args()

    if not PROCESSED_DIR.is_dir():
        print(f"No processed directory at {PROCESSED_DIR}", file=sys.stderr)
        sys.exit(1)

    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    report: dict = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "sentinel": SENTINEL,
        "dry_run": args.dry_run,
        "by_status": {"identical": [], "sentinel": [], "distinct": [], "incomplete": [], "absent": []},
    }

    md_files = sorted(PROCESSED_DIR.glob("*.md"))
    for md in md_files:
        meta, _ = read_frontmatter(str(md))
        status = _classify(meta)
        report["by_status"][status].append(md.stem)

        if status == "identical" and not args.dry_run:
            updates = {field: SENTINEL for field in STEP_FIELDS}
            update_frontmatter(str(md), updates)

    report["counts"] = {k: len(v) for k, v in report["by_status"].items()}
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Backfill report \u2192 {REPORT_PATH.relative_to(_REPO_ROOT)}")
    for status, ids in report["by_status"].items():
        print(f"  {status:11s} : {len(ids):4d}")
    if args.dry_run:
        print("(dry-run \u2014 no files modified)")


if __name__ == "__main__":
    main()
