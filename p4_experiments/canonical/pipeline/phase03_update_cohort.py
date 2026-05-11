"""Phase 3 - Apply S2-backed manual adjudication to cohort.json.

For each label classified in phase3_compare.json:
  * Append an entry to labels[<id>].fidelity_history capturing
        the Phase 3 classification (tier, rationale, criteria, S2 paper-file
        SHA-256, date, phase).
    * Overwrite labels[<id>].fidelity with the checked S2-backed manual
        adjudication classification.

Top-level _summary, _silo_summary, and _phase_status are refreshed.

Idempotent: if a Phase 3 entry for the same date already exists for a
label, it is replaced rather than duplicated.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from p4_experiments.canonical.data.s2_extraction_index import s2_experiment, s2_extraction_sha256

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
COMPARE = REPORTS / "phase3_compare.json"

DATE = datetime.now(timezone.utc).date().isoformat()
PHASE_TAG = "Phase 3 S2 quantitative extraction + manual audit adjudication"


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    compare = json.loads(COMPARE.read_text(encoding="utf-8"))
    classifications = compare["classifications"]

    labels = cohort["labels"]
    n_updated = 0
    n_changed_tier = 0

    for label_id, result in classifications.items():
        if label_id not in labels:
            continue
        ext_sha = (
            s2_extraction_sha256(labels[label_id])
            if s2_experiment(labels[label_id]) is not None else None
        )

        new_tier = result["classification"]
        prev_tier = labels[label_id].get("fidelity")
        if new_tier != prev_tier:
            n_changed_tier += 1

        history_entry = {
            "date": DATE,
            "tier": new_tier,
            "rationale": result.get("rationale", ""),
            "phase": PHASE_TAG,
            "extraction_path": result.get("extraction_path"),
            "extraction_sha256": ext_sha,
            "criteria": result.get("criteria"),
            "method": result.get("method"),
            "paper_fidelity": result.get("paper_fidelity"),
        }

        history = labels[label_id].setdefault("fidelity_history", [])
        # Replace any existing Phase 3 entry from today (idempotent).
        history = [h for h in history if not (h.get("date") == DATE and "Phase 3" in (h.get("phase") or ""))]
        history.append(history_entry)
        labels[label_id]["fidelity_history"] = history
        labels[label_id]["fidelity"] = new_tier
        if result.get("paper_fidelity"):
            labels[label_id]["paper_fidelity"] = result["paper_fidelity"]
        n_updated += 1

    # Refresh top-level summaries.
    tier_counts = Counter(l["fidelity"] for l in labels.values())
    summary = cohort.setdefault("_summary", {})
    summary["fidelity_breakdown"] = dict(tier_counts)
    summary["F_count"] = tier_counts.get("F", 0)
    summary["P_count"] = tier_counts.get("P", 0)
    summary["last_phase3_update_utc"] = datetime.now(timezone.utc).isoformat()

    silo_summary = cohort.get("_silo_summary", {})
    per_silo: dict = {}
    for l in labels.values():
        s = l["silo"]
        per_silo.setdefault(s, {"F": 0, "P": 0, "total": 0})
        per_silo[s][l["fidelity"]] = per_silo[s].get(l["fidelity"], 0) + 1
        per_silo[s]["total"] += 1
    for s, counts in per_silo.items():
        if s in silo_summary and isinstance(silo_summary[s], dict):
            silo_summary[s]["fidelity_breakdown_phase3"] = counts
        else:
            silo_summary[s] = {"fidelity_breakdown_phase3": counts}
    cohort["_silo_summary"] = silo_summary

    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {"_legacy_value": ps} if ps is not None else {}
    ps["phase3"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "F_count": tier_counts.get("F", 0),
        "P_count": tier_counts.get("P", 0),
        "total": sum(tier_counts.values()),
        "compare_file": "p4_experiments/canonical/reports/phase3_compare.json",
        "extractions_dir": "p3_thematic_synthesis/s2_quantitative/output/extractions/",
        "source_resolution": "paper_id + experiment_id",
        "classification_basis": "S2 quantitative extraction + reviewed faithful set + Vincent/manual joint triage adjudication",
        "audit_inputs": {
            "vincent_review_dir": "p4_experiments/experiments/review/phase8_faithfulness_review/vincent/",
            "joint_triage_index": "p4_experiments/experiments/review/phase8_faithfulness_review/triage/TRIAGE_INDEX.md",
            "quantitative_triage": "p2_systematic_review/output/audit/triage_classification.json",
            "manual_extraction_targets": "p2_systematic_review/output/audit/manual_extraction_targets.txt",
        },
    }
    cohort["_phase_status"] = ps

    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    print(f"[Phase 3d] cohort.json updated: {n_updated} labels, {n_changed_tier} tier changes")
    print(f"[Phase 3d] new tier counts: {dict(tier_counts)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
