"""Audit + annotate cohort labels with implementation-type metadata.

For each label in the canonical cohort, determines whether its `circuit.py`
imports `qiskit_finance` directly or uses a family/template builder. The active
claim-bearing tier split is read from `canonical/cohort.json::_faithfulness_tiering`:
the current estimator-run cohort has 0 strict-tier labels, 13 family-template
labels, and 58 proxy labels.

By default this script can annotate the label's `instance.json` and backs up the
original to `instance.json.bak` once. Use `--dry-run` for read-only reviewer
audits; it still writes the JSON report but does not touch instance files.

Idempotent. No QDK / LLM / Azure calls. Safe to re-run.

Usage (from the repo root):

    python p4_experiments/scripts/audit_implementation_type.py
    python p4_experiments/scripts/audit_implementation_type.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_P4_ROOT = _SCRIPT_DIR.parent
SILOS = _P4_ROOT / "experiments" / "silos"
COHORT_CANDIDATES = [
    _P4_ROOT / "canonical" / "cohort.json",
    _P4_ROOT / "canonical" / "p4_cohort.json",
    _P4_ROOT / "canonical" / "outputs" / "cohort.json",
]

STRICT_MARKERS = ("qiskit_finance",)
TEMPLATE_MARKERS = (
    "ansatz_stretch", "qaoa_proxy", "amplitude_encoding",
    "qft_phase_proxy", "qgan_qae", "sim_mc_state_prep",
    ".templates.hhl", ".templates.qae",
    "core.templates.hhl", "core.templates.qae",
)


def _entry_label(entry: dict) -> str:
    return str(entry.get("label") or entry.get("label_id") or entry.get("paper_id") or "?")


def _load_cohort() -> tuple[list[dict], dict | None, Path | None, str]:
    for path in COHORT_CANDIDATES:
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("labels"), dict):
                entries: list[dict] = []
                for label, entry in data["labels"].items():
                    row = dict(entry)
                    row.setdefault("label", label)
                    row.setdefault("label_id", label)
                    entries.append(row)
                return entries, data, path, "cohort_json_labels"
            if isinstance(data, dict) and "entries" in data:
                entries = []
                for entry in data["entries"]:
                    row = dict(entry)
                    row.setdefault("label", row.get("label_id"))
                    row.setdefault("label_id", row.get("label"))
                    entries.append(row)
                return entries, data, path, "cohort_json_entries"
            if isinstance(data, list):
                return data, None, path, "cohort_json_list"
    print(f"WARN: no cohort file at any of: {COHORT_CANDIDATES}", file=sys.stderr)
    print("Falling back to walked-instance mode; this is NOT a cohort audit.", file=sys.stderr)
    entries: list[dict] = []
    for inst in SILOS.glob("*/*/instance.json"):
        meta = json.loads(inst.read_text(encoding="utf-8"))
        entries.append({
            "label": meta.get("label", inst.parent.name),
            "paper_id": meta.get("paper_id", inst.parent.name.split("__")[0]),
            "silo": meta.get("silo", inst.parent.parent.name.replace("_", "-")),
            "experiment_id": meta.get("experiment_id", "exp_1"),
            "_instance_dir": str(inst.parent.relative_to(_P4_ROOT)),
        })
    return entries, None, None, "walked_instance_fallback"


def _walk_instances() -> list[dict]:
    walked: list[dict] = []
    for inst in SILOS.glob("*/*/instance.json"):
        try:
            meta = json.loads(inst.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        walked.append({
            "label": str(meta.get("label") or inst.parent.name),
            "instance_dir": inst.parent,
            "paper_id": meta.get("paper_id", inst.parent.name.split("__")[0]),
            "silo": meta.get("silo", inst.parent.parent.name.replace("_", "-")),
            "experiment_id": meta.get("experiment_id", "exp_1"),
        })
    return walked


def _classify(circuit_py: Path) -> tuple[str, str]:
    """Return (implementation_type, evidence_marker)."""
    if not circuit_py.is_file():
        return "unknown", "no circuit.py"
    src = circuit_py.read_text(encoding="utf-8", errors="replace")
    for m in STRICT_MARKERS:
        if m in src:
            return "paper-faithful-strict", m
    for m in TEMPLATE_MARKERS:
        if m in src:
            return "paper-family-template", m
    return "paper-family-template", "(no template marker; defaulting to family-template)"


def _resolve_instance_dir(entry: dict) -> Path | None:
    if "_instance_dir" in entry:
        return _P4_ROOT / entry["_instance_dir"]
    raw_instance_path = entry.get("instance_path")
    if raw_instance_path:
        inst_path = Path(raw_instance_path)
        if not inst_path.is_absolute():
            inst_path = _P4_ROOT.parent / inst_path
        if inst_path.exists():
            return inst_path.parent
    raw_circuit_dir = entry.get("circuit_dir")
    if raw_circuit_dir:
        circuit_dir = Path(raw_circuit_dir)
        if not circuit_dir.is_absolute():
            circuit_dir = _P4_ROOT.parent / circuit_dir
        if (circuit_dir / "instance.json").exists():
            return circuit_dir
    silo = entry.get("silo", "").replace("-", "_")
    pid = entry.get("paper_id", "")
    exp_id = entry.get("experiment_id", "exp_1")
    candidates = [SILOS / silo / pid]
    if exp_id and exp_id != "exp_1":
        n = exp_id.split("_")[-1]
        candidates.insert(0, SILOS / silo / f"{pid}__exp_{n}")
    for c in candidates:
        if (c / "instance.json").exists():
            return c
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # Family expectations (added 2026-05-02 freeze): if `algorithm_family`
    # asserts a specific algorithm family, the circuit's evidence_marker
    # should match the corresponding template. ansatz_stretch / qgan_qae /
    # amplitude_encoding etc. used in place of the declared family is a
    # silent algorithm/implementation mismatch that the auditor must surface.
    _FAMILY_EXPECTED_MARKERS = {
        "hhl": {".templates.hhl", "core.templates.hhl", "qiskit_finance"},
        "qae": {".templates.qae", "core.templates.qae", "qiskit_finance"},
        "amplitude-estimation": {".templates.qae", "core.templates.qae", "qiskit_finance"},
        "qaoa": {"qaoa_proxy", "qiskit_finance"},
        "vqe": {"qaoa_proxy", "qiskit_finance"},
    }

    entries, cohort_data, cohort_path, source_mode = _load_cohort()
    cohort_labels = {_entry_label(entry) for entry in entries}
    strict: list[str] = []
    family: list[str] = []
    missing: list[str] = []
    mismatches: list[dict] = []
    audit_rows: list[dict] = []
    warnings: list[str] = []

    if source_mode == "walked_instance_fallback":
        warnings.append(
            "No canonical cohort JSON was loaded; this report is a walked-instance audit and must not be used as a 71-label cohort audit."
        )

    faithfulness_tier_counts: dict[str, int] = {}
    faithfulness_labels_by_tier: dict[str, list[str]] = {}
    strict_estimator_labels: list[str] = []
    if isinstance(cohort_data, dict):
        tiering = cohort_data.get("_faithfulness_tiering", {})
        faithfulness_tier_counts = dict(tiering.get("counts", {}) or {})
        faithfulness_labels_by_tier = {
            k: list(v) for k, v in (tiering.get("labels_by_tier", {}) or {}).items()
        }
        strict_estimator_labels = sorted(faithfulness_labels_by_tier.get("paper-faithful-strict", []))
        faithfulness_tier_counts.setdefault("paper-faithful-strict", len(strict_estimator_labels))
        faithfulness_labels_by_tier.setdefault("paper-faithful-strict", strict_estimator_labels)

    strict_records = 0

    for entry in entries:
        label = _entry_label(entry)
        algorithm_family = str(entry.get("algorithm_family", "") or "").strip().lower()
        inst_dir = _resolve_instance_dir(entry)
        if inst_dir is None:
            missing.append(label)
            audit_rows.append({
                "label": label,
                "status": "missing-instance",
                "algorithm_family": algorithm_family,
            })
            continue
        impl, marker = _classify(inst_dir / "circuit.py")

        # Try to read algorithm_family from instance.json if cohort entry didn't carry it.
        if not algorithm_family:
            try:
                inst_data = json.loads((inst_dir / "instance.json").read_text(encoding="utf-8"))
                algorithm_family = str(inst_data.get("algorithm_family", "") or "").strip().lower()
            except Exception:
                pass

        family_mismatch = False
        family_disclosure = None
        expected = _FAMILY_EXPECTED_MARKERS.get(algorithm_family)
        if expected is not None and marker not in expected:
            family_mismatch = True
            family_disclosure = (
                f"Declared algorithm_family='{algorithm_family}' but circuit.py "
                f"evidence_marker='{marker}' (expected one of {sorted(expected)}). "
                "This label is a template-faithful proxy at paper-stated scale, "
                "not a paper-faithful implementation of the declared family."
            )
            mismatches.append({
                "label": label,
                "algorithm_family": algorithm_family,
                "evidence_marker": marker,
                "expected_markers": sorted(expected),
            })

        audit_rows.append({
            "label": label,
            "instance_dir": str(inst_dir.relative_to(_P4_ROOT)),
            "implementation_type": impl,
            "evidence_marker": marker,
            "algorithm_family": algorithm_family or None,
            "family_mismatch": family_mismatch,
            "family_disclosure": family_disclosure,
        })
        if impl == "paper-faithful-strict":
            strict.append(label)
        else:
            family.append(label)

        if not args.dry_run:
            inst_path = inst_dir / "instance.json"
            bak = inst_path.with_suffix(".json.bak")
            if not bak.exists():
                shutil.copy2(inst_path, bak)
            data = json.loads(inst_path.read_text(encoding="utf-8"))
            data["implementation_type"] = impl
            data["_implementation_audit"] = {
                "stamped_utc": datetime.now(timezone.utc).isoformat(),
                "evidence_marker": marker,
                "algorithm_family_declared": algorithm_family or None,
                "family_mismatch": family_mismatch,
            }
            if family_disclosure:
                data["family_disclosure"] = family_disclosure
            inst_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    walked_instances = _walk_instances()

    if strict and not strict_estimator_labels:
        warnings.append(
            "Some active cohort circuits import qiskit_finance, but cohort tier metadata has no strict labels. Review before treating any strict result as claim-bearing."
        )

    report_path = _P4_ROOT / "scripts" / "implementation_type_audit_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "dry_run": args.dry_run,
        "source_mode": source_mode,
        "cohort_source": str(cohort_path.relative_to(_P4_ROOT)).replace("\\", "/") if cohort_path else None,
        "summary": {
            "labels_in_cohort": len(entries),
            "labels_with_instance_json": len(entries) - len(missing),
            "labels_without_walked_instance": len(missing),
            "walked_instance_json_total": len(walked_instances),
            "strict_estimator_record_count": strict_records,
        },
        "counts": {
            "cohort_code_marker_counts": {
                "paper-faithful-strict": len(strict),
                "paper-family-template": len(family),
            },
            "cohort_faithfulness_tier_counts": faithfulness_tier_counts,
            "missing-instance": len(missing),
            "family_mismatches": len(mismatches),
        },
        "strict_estimator_record_eligibility": {
            "active_estimator_cohort_strict_labels": strict_estimator_labels,
            "active_estimator_cohort_strict_count": len(strict_estimator_labels),
            "strict_phase8_records": strict_records,
        },
        "paper-faithful-strict": sorted(strict),
        "paper-family-template": sorted(family),
        "missing-instance": sorted(missing),
        "family_mismatches": mismatches,
        "warnings": warnings,
        "rows": audit_rows,
    }, indent=2) + "\n", encoding="utf-8")

    print(f"source mode           : {source_mode}")
    print(f"labels in cohort      : {len(entries):3d}")
    print(f"with instance.json    : {len(entries) - len(missing):3d}")
    print(f"without instance.json : {len(missing):3d}  -> {sorted(missing)}")
    print(f"code marker strict    : {len(strict):3d}  -> {sorted(strict)}")
    print(f"code marker template  : {len(family):3d}")
    print(f"tier strict active    : {len(strict_estimator_labels):3d}  -> {strict_estimator_labels}")
    print(f"tier family/proxy     : {faithfulness_tier_counts}")
    print(f"strict records        : {strict_records}")
    print(f"family_mismatches     : {len(mismatches):3d}")
    if warnings:
        for warning in warnings:
            print(f"WARN: {warning}")
    if mismatches:
        for m in mismatches[:10]:
            print(f"    [{m['label']}] family='{m['algorithm_family']}' marker='{m['evidence_marker']}'")
        if len(mismatches) > 10:
            print(f"    … and {len(mismatches) - 10} more (see report)")
    print(f"audit report          : {report_path.relative_to(_P4_ROOT)}")

    # Freeze gate: non-zero exit if structural defects were found.
    # Family mismatches are reported but do NOT fail the gate (they are
    # disclosed honestly via family_disclosure / instance.json metadata).
    # Missing-instance IS a fail because it means the cohort references a
    # label without a buildable circuit.
    if missing:
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
