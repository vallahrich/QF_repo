"""Phase 8b update — backfill measured wall_clock_seconds into cohort.json.

For each label in p4_experiments/common/output/classical_results/<label>_paper_named.json,
update cohort.json[labels][label].classical_baseline:

  wall_clock_seconds         <- measured median (paper_named variant)
  metric_value               <- kernel name + brief output summary
  _phase8b_provenance        <- {kernel, n_repeats, iqr, started/completed_utc,
                                 record_path, single_thread_note}

Silo-default variants are NOT pushed into cohort.json (they live in the
record files for sensitivity reporting).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT_PATH = CANON / "cohort.json"
RES_DIR = ROOT / "p4_experiments" / "common" / "output" / "classical_results"


def main() -> int:
    cohort = json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    updated = 0
    skipped = 0
    for record_path in sorted(RES_DIR.glob("*_paper_named.json")):
        rec = json.loads(record_path.read_text(encoding="utf-8"))
        label = rec["label"]
        if label not in cohort["labels"]:
            print(f"  [{label}] WARNING: not in cohort.labels; skipping")
            skipped += 1
            continue
        entry = cohort["labels"][label]
        cb = entry.setdefault("classical_baseline", {})
        m = rec["measurement"]
        median = m["wall_clock_seconds_median"]
        cb["wall_clock_seconds"] = median
        cb["metric_value"] = {
            "kernel": rec["kernel"],
            "summary": "Phase 8b measured (numpy/scipy single-thread)",
            "baseline_relationship": rec.get("baseline_relationship", "paper_named_exact"),
            "baseline_scale_type": rec.get("baseline_scale_type"),
            "paper_published_scale_estimate_status": rec.get("paper_published_scale_estimate_status"),
            "headline_h4_eligible": rec.get("headline_h4_eligible"),
        }
        cb["_phase8b_provenance"] = {
            "phase": "phase8b_classical_baseline",
            "kernel": rec["kernel"],
            "baseline_relationship": rec.get("baseline_relationship", "paper_named_exact"),
            "baseline_scale_type": rec.get("baseline_scale_type"),
            "paper_published_scale_estimate_seconds": rec.get("paper_published_scale_estimate_seconds"),
            "paper_published_scale_estimate_status": rec.get("paper_published_scale_estimate_status"),
            "headline_h4_eligible": rec.get("headline_h4_eligible"),
            "baseline_claim_scope": rec.get("baseline_claim_scope"),
            "n_repeats_completed": m["n_repeats_completed"],
            "wall_clock_seconds_median": median,
            "wall_clock_seconds_iqr": m["wall_clock_seconds_iqr"],
            "started_utc": m["started_utc"],
            "completed_utc": m["completed_utc"],
            "record_path": str(record_path.relative_to(ROOT)),
            "single_thread_note": m["single_thread_note"],
            "thread_env_at_run": m["thread_env"],
            "substitution_note": rec.get("note", ""),
            "operator_decisions_ref": rec.get("operator_decisions_ref"),
            "applied_utc": datetime.now(timezone.utc).isoformat(),
        }
        # Mark legacy placeholder fields explicitly resolved
        cb["_status"] = "PHASE_8B_MEASURED"
        updated += 1
        print(f"  [{label}] wall_clock_seconds <- {median:.4g}s ({rec['kernel']})")

    COHORT_PATH.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    print(f"[Phase 8b update] cohort.json updated: {updated} labels, {skipped} skipped")
    # Self-record phase status so run_pipeline's --resume can skip and
    # downstream audits (and any future audit_phase8b) can detect
    # completion via cohort._phase_status.phase8b_cohort.status.
    cohort = json.loads(COHORT_PATH.read_text(encoding="utf-8"))
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {}
    ps["phase8b_cohort"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "labels_updated": updated,
        "labels_skipped": skipped,
        "results_dir": str(RES_DIR.relative_to(ROOT)).replace("\\", "/"),
    }
    cohort["_phase_status"] = ps
    COHORT_PATH.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
