"""Finalize local Phase 8 status after syncing remote VM results.

The six-VM run updates each VM's private copy of ``cohort.json``. The
local workspace receives result JSON files via ``Sync-Results.ps1``, so
this script scans the local result directory and stamps
``cohort._phase_status.phase8`` once the canonical 71 x 36 grid is present.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = [1e-3, 1e-4, 1e-6]
MODES = ["bare", "full"]
EXPECTED_PER_LABEL = len(PROFILES) * len(EPSILONS) * len(MODES)


def _read_json(path: Path, attempts: int = 5) -> dict:
    for attempt in range(attempts):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (PermissionError, OSError, json.JSONDecodeError):
            if attempt == attempts - 1:
                raise
            time.sleep(0.2)
    raise RuntimeError(f"unreachable read retry state for {path}")


def _expected_filename(label: str, profile: str, eps: float, mode: str) -> str:
    return f"{label}_{profile}_eps{eps:.0e}_{mode}.json"


def _scan(cohort: dict) -> dict:
    labels = sorted(cohort["labels"].keys())
    expected = {
        _expected_filename(label, profile, eps, mode)
        for label in labels
        for profile in PROFILES
        for eps in EPSILONS
        for mode in MODES
    }
    found = {path.name: path for path in RESULTS.glob("*.json")} if RESULTS.exists() else {}
    missing = sorted(expected - set(found))
    extra = sorted(set(found) - expected)
    breakdown = {"total_records": len(found), "ok": 0, "engine_failure": 0}
    for path in found.values():
        try:
            rec = _read_json(path)
        except Exception:
            continue
        if (rec.get("measured") or {}).get("status") == "engine_failure":
            breakdown["engine_failure"] += 1
        else:
            breakdown["ok"] += 1
    return {
        "labels": labels,
        "expected_total": len(expected),
        "found_total": len(found),
        "missing": missing,
        "extra": extra,
        "breakdown": breakdown,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalize local Phase 8 status from synced result records.")
    parser.add_argument("--fail-if-incomplete", action="store_true")
    args = parser.parse_args()

    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    scan = _scan(cohort)
    complete = not scan["missing"] and not scan["extra"]

    phase_status = cohort.get("_phase_status")
    if not isinstance(phase_status, dict):
        phase_status = {"_legacy": phase_status} if phase_status is not None else {}
    payload = {
        "status": "complete" if complete else "incomplete_after_sync",
        "finalized_utc": datetime.now(timezone.utc).isoformat(),
        "label_count_in_plan": len(scan["labels"]),
        "expected_total_cells": scan["expected_total"],
        "expected_cells_per_label": EXPECTED_PER_LABEL,
        "results_breakdown": scan["breakdown"],
        "missing_count": len(scan["missing"]),
        "extra_count": len(scan["extra"]),
        "source": "local finalize_phase8_results.py after VM result sync",
    }
    if complete:
        payload["completed_utc"] = payload["finalized_utc"]
    else:
        payload["first_missing"] = scan["missing"][:10]
        payload["first_extra"] = scan["extra"][:10]
    phase_status["phase8"] = payload
    cohort["_phase_status"] = phase_status
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")

    print(
        f"[finalize_phase8] status={payload['status']} "
        f"records={scan['found_total']}/{scan['expected_total']} "
        f"missing={len(scan['missing'])} extra={len(scan['extra'])}"
    )
    if args.fail_if_incomplete and not complete:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())