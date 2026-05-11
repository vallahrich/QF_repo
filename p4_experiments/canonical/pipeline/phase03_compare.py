"""Phase 3 - Build an S2-backed, manually adjudicated cohort report.

The genuine Phase 3 source for P4 is the S2 quantitative extraction tree:

    p3_thematic_synthesis/s2_quantitative/output/extractions/<paper_id>.json

Those files are per paper, so labels must be resolved by both ``paper_id`` and
``experiment_id``. Manual review and joint triage adjudicate the P4 fidelity and
circuit-remediation decisions after S2 resolution. This report records the live
S2 source path, selected S2 fields, and the reviewed faithful-label decision
set. It intentionally does not run the retired per-label five-criterion
extraction rule, because fields such as ``oracle_structure`` are not part of the
S2 schema.
"""

from __future__ import annotations

import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p4_experiments.canonical.data.s2_extraction_index import (
    s2_experiment,
    s2_extraction_path,
    s2_extraction_relpath,
)

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
COMPARE_OUT = REPORTS / "phase3_compare.json"

AUDIT_INPUTS = {
    "vincent_review_dir": "p4_experiments/experiments/review/phase8_faithfulness_review/vincent/",
    "joint_triage_index": "p4_experiments/experiments/review/phase8_faithfulness_review/triage/TRIAGE_INDEX.md",
    "quantitative_triage": "p2_systematic_review/output/audit/triage_classification.json",
    "manual_extraction_targets": "p2_systematic_review/output/audit/manual_extraction_targets.txt",
}

REVIEWED_F_HONEST = frozenset({"B3", "B4", "B5", "SQ17"})
REVIEWED_F_TEMPLATE = frozenset({
    "SD3",
    "SD7",
    "SD8",
    "SD10",
    "SD12",
    "SD13",
    "SM5",
    "SM9",
    "SM10",
    "SP4",
    "SQ5",
    "SQ18",
    "SR1",
    "SX2",
    "SX3",
    "SX5",
})
REVIEWED_F_LABELS = REVIEWED_F_HONEST | REVIEWED_F_TEMPLATE


def _has_value(value: Any) -> bool:
    return value not in (None, "", "NOT_STATED", "not_specified")


def _source_criteria(experiment: dict[str, Any] | None) -> dict[str, bool]:
    if experiment is None:
        return {
            "s2_source_present": False,
            "s2_experiment_id_match": False,
            "s2_algorithm_family_present": False,
            "s2_quantum_resources_present": False,
        }

    algorithm = experiment.get("algorithm") or {}
    resources = experiment.get("quantum_resources") or {}
    return {
        "s2_source_present": True,
        "s2_experiment_id_match": True,
        "s2_algorithm_family_present": _has_value(algorithm.get("family")),
        "s2_quantum_resources_present": any(
            _has_value(resources.get(key))
            for key in (
                "num_qubits",
                "circuit_depth",
                "gate_count_total",
                "num_shots",
                "num_variational_params",
            )
        ),
    }


def _selected_s2_fields(experiment: dict[str, Any] | None) -> dict[str, Any]:
    if experiment is None:
        return {}

    algorithm = experiment.get("algorithm") or {}
    problem = experiment.get("problem_formulation") or {}
    resources = experiment.get("quantum_resources") or {}
    return {
        "algorithm_family": algorithm.get("family"),
        "algorithm_variant": algorithm.get("variant"),
        "ansatz": algorithm.get("ansatz"),
        "encoding_method": problem.get("encoding_method"),
        "num_qubits": resources.get("num_qubits"),
        "circuit_depth": resources.get("circuit_depth"),
        "gate_count_total": resources.get("gate_count_total"),
        "num_shots": resources.get("num_shots"),
    }


def _reviewed_subclass(label_id: str) -> str | None:
    if label_id in REVIEWED_F_HONEST:
        return "paper-faithful-honest"
    if label_id in REVIEWED_F_TEMPLATE:
        return "paper-faithful-template"
    return None


def _classification(label_id: str, experiment: dict[str, Any] | None) -> tuple[str, str, str]:
    subclass = _reviewed_subclass(label_id)
    if subclass and experiment is not None:
        return (
            "F",
            subclass,
            "Label belongs to the reviewed Phase 3 faithful set and resolves "
            "to the genuine S2 quantitative extraction by paper_id and experiment_id.",
        )
    if subclass:
        return (
            "P",
            "proxy",
            "Label belongs to the reviewed Phase 3 faithful set, but the S2 "
            "paper file or experiment_id resolution failed; retained as P until repaired.",
        )
    return (
        "P",
        "proxy",
        "Label is outside the reviewed Phase 3 faithful set; it remains "
        "Proxy-declared and is justified from the matching S2 quantitative extraction.",
    )


def _v5_instance_path(entry: dict[str, Any]) -> str | None:
    circuit_rel = entry.get("circuit_path")
    if not circuit_rel:
        return None
    instance_path = (ROOT / circuit_rel).parent / "instance.json"
    if not instance_path.exists():
        return None
    return str(instance_path.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = cohort.get("labels", {})

    classifications: "OrderedDict[str, dict[str, Any]]" = OrderedDict()
    missing_s2_sources: list[str] = []

    for label_id, entry in labels.items():
        experiment = s2_experiment(entry)
        if experiment is None:
            missing_s2_sources.append(label_id)

        classification, paper_fidelity, rationale = _classification(label_id, experiment)

        source_path = s2_extraction_path(entry)
        result = {
            "classification": classification,
            "method": "phase3_s2_manual_adjudication",
            "paper_fidelity": paper_fidelity,
            "reviewed_fidelity_subclass": _reviewed_subclass(label_id),
            "rationale": rationale,
            "criteria": _source_criteria(experiment),
            "label_id": label_id,
            "paper_id": entry.get("paper_id"),
            "experiment_id": entry.get("experiment_id"),
            "silo": entry.get("silo"),
            "extraction_path": s2_extraction_relpath(entry) if source_path.exists() else None,
            "v5_instance_path": _v5_instance_path(entry),
            "s2_fields": _selected_s2_fields(experiment),
        }
        classifications[label_id] = result

    summary = {
        "total_classified": len(classifications),
        "F_classified": sum(1 for item in classifications.values() if item["classification"] == "F"),
        "P_classified": sum(1 for item in classifications.values() if item["classification"] == "P"),
        "missing_s2_sources": missing_s2_sources,
        "reviewed_faithful_labels_present": sorted(set(labels) & REVIEWED_F_LABELS),
        "reviewed_faithful_labels_absent": sorted(REVIEWED_F_LABELS - set(labels)),
    }

    per_silo: dict[str, dict[str, int]] = {}
    for item in classifications.values():
        silo = item["silo"]
        if silo not in per_silo:
            per_silo[silo] = {"F": 0, "P": 0, "total": 0}
        per_silo[silo][item["classification"]] += 1
        per_silo[silo]["total"] += 1

    out = {
        "_phase": 3,
        "_subphase": "S2-backed manual adjudication",
        "_generated_utc": datetime.now(timezone.utc).isoformat(),
        "_classification_rule_summary": (
            "F iff the label is in the reviewed Phase 3 faithful set and resolves "
            "to the genuine P3 S2 per-paper extraction by paper_id and experiment_id; "
            "manual review and joint triage adjudicate the checked P4 cohort; all "
            "other labels are P."
        ),
        "_audit_inputs": AUDIT_INPUTS,
        "_summary": summary,
        "_per_silo": per_silo,
        "classifications": classifications,
    }
    COMPARE_OUT.parent.mkdir(parents=True, exist_ok=True)
    COMPARE_OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[Phase 3] phase3_compare.json -> {COMPARE_OUT.relative_to(ROOT)}")
    print(f"[Phase 3] {summary}")
    print(f"[Phase 3] Per-silo: {per_silo}")
    if missing_s2_sources:
        print(f"[Phase 3] WARNING: {len(missing_s2_sources)} S2 sources missing: {missing_s2_sources}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
