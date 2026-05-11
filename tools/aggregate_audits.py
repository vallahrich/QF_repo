"""Aggregate every ``audit_phase*.json`` into a single ``audit_report.json``.

This is the Phase F1 deliverable from the P4 Master Plan v2.

Reads every ``p4_experiments/canonical/audit_phase*.json`` (phase1..phase11
plus 8b/8c/8d/8e when present), normalises the two schema flavours
(findings-style vs results+totals), and writes
``p4_experiments/canonical/audit_report.json`` with one row per phase plus
overall totals.

The script is deterministic, read-only with respect to canonical artefacts
(it only writes ``audit_report.json``), idempotent, and exits with
non-zero status if any phase reports ``blockers_failed > 0``.

Usage
-----
    python tools/aggregate_audits.py
    python tools/aggregate_audits.py --strict   # also non-zero on n_fail>0

Run from the repository root.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

# Phase ordering for the rollup row order.  Phases not in this list are
# appended at the end in alphabetical order so the script never silently
# drops an unknown audit file.
_PHASE_ORDER = [
    "phase1", "phase2", "phase3", "phase3c", "phase4", "phase5", "phase6", "phase7",
    "phase8", "phase8b", "phase8c", "phase8d", "phase8e",
    "phase9", "phase10", "phase11",
]


def _phase_id_from_filename(name: str) -> str | None:
    m = re.match(r"^audit_(phase[0-9a-z]+)\.json$", name)
    return m.group(1) if m else None


def _normalise(phase_id: str, doc: dict) -> dict:
    """Return a uniform per-phase summary."""
    # findings-style (phase1, phase3, phase4): _n_pass / _n_fail / _blockers_failed
    if "_n_pass" in doc or "_blockers_failed" in doc:
        n_pass = int(doc.get("_n_pass", 0))
        n_fail = int(doc.get("_n_fail", 0))
        blockers_failed = int(doc.get("_blockers_failed", 0))
        n_info = int(doc.get("_n_info", 0))
    else:
        totals = doc.get("totals") or {}
        n_pass = int(totals.get("pass", totals.get("n_pass", 0)))
        n_fail = int(totals.get("fail", totals.get("n_fail", 0)))
        blockers_failed = int(totals.get("blockers_failed", 0))
        n_info = int(totals.get("info", totals.get("n_info", 0)))

    status = "pass" if (blockers_failed == 0 and n_fail == 0) else "fail"
    return {
        "phase_id": phase_id,
        "status": status,
        "n_pass": n_pass,
        "n_fail": n_fail,
        "n_info": n_info,
        "blockers_failed": blockers_failed,
        "generated_utc": doc.get("generated_utc")
            or doc.get("_audit_generated_utc"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--canonical-dir",
        type=Path,
        default=Path("p4_experiments/canonical"),
        help="Directory containing the audit_phase*.json files.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: <canonical-dir>/audit_report.json).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any phase has n_fail>0 (in addition to blockers).",
    )
    args = parser.parse_args()

    cdir = args.canonical_dir.resolve()
    if not cdir.is_dir():
        print(f"ERROR: canonical dir not found: {cdir}", file=sys.stderr)
        return 2

    out_path = (args.out or (cdir / "audit_report.json")).resolve()

    discovered: dict[str, Path] = {}
    for p in sorted(cdir.glob("audit_phase*.json")):
        pid = _phase_id_from_filename(p.name)
        if pid is None:
            continue
        discovered[pid] = p

    if not discovered:
        print(f"ERROR: no audit_phase*.json files in {cdir}", file=sys.stderr)
        return 2

    ordered_ids = [pid for pid in _PHASE_ORDER if pid in discovered]
    extras = sorted(set(discovered) - set(ordered_ids))
    ordered_ids.extend(extras)

    summaries: list[dict] = []
    fail_phase: str | None = None
    total_pass = total_fail = total_blockers = total_info = 0

    for pid in ordered_ids:
        path = discovered[pid]
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            summaries.append({
                "phase_id": pid,
                "status": "fail",
                "n_pass": 0, "n_fail": 1, "n_info": 0,
                "blockers_failed": 1,
                "error": f"{type(exc).__name__}: {exc}",
                "report_path": str(path.relative_to(cdir.parent.parent))
                    if cdir.parent.parent in path.parents
                    else str(path),
            })
            total_fail += 1
            total_blockers += 1
            if fail_phase is None:
                fail_phase = pid
            continue

        summary = _normalise(pid, doc)
        try:
            summary["report_path"] = str(path.relative_to(Path.cwd()))
        except ValueError:
            summary["report_path"] = str(path)
        summaries.append(summary)
        total_pass += summary["n_pass"]
        total_fail += summary["n_fail"]
        total_blockers += summary["blockers_failed"]
        total_info += summary["n_info"]
        if fail_phase is None and summary["status"] != "pass":
            fail_phase = pid

    report = {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "schema": "audit_report.v2",
        "seed": "0x50414D50",
        "canonical_dir": str(cdir),
        "phases_discovered": list(discovered),
        "phases_aggregated": ordered_ids,
        "phases_missing_from_known_order": [
            pid for pid in _PHASE_ORDER if pid not in discovered
        ],
        "fail_phase": fail_phase,
        "totals": {
            "n_pass": total_pass,
            "n_fail": total_fail,
            "n_info": total_info,
            "blockers_failed": total_blockers,
            "n_phases": len(summaries),
            "n_phases_pass": sum(1 for s in summaries if s["status"] == "pass"),
            "n_phases_fail": sum(1 for s in summaries if s["status"] != "pass"),
        },
        "summaries": summaries,
    }

    out_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {out_path}")
    print(f"  phases aggregated : {len(summaries)}")
    print(f"  pass / fail       : "
          f"{report['totals']['n_phases_pass']} / "
          f"{report['totals']['n_phases_fail']}")
    print(f"  blockers_failed   : {total_blockers}")
    print(f"  totals pass/fail  : {total_pass} / {total_fail}")
    if report["phases_missing_from_known_order"]:
        print("  missing phases    : "
              + ", ".join(report["phases_missing_from_known_order"]))

    if total_blockers > 0:
        return 1
    if args.strict and total_fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
