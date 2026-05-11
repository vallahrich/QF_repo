"""Phase 8d experiment-selection manifest.

Phase 8d is not a second arbitrary sweep. It is a post-Phase-8 appendix scout
for the current paper-faithful QAE/HHL evidence in the rebound cohort. This
script records the decision rule before any high-N scout cells are launched.

Selection rule:
  1. Use only current F labels from ``cohort.json``.
  2. Keep only families with a direct fixed-precision high-N scout template:
     ``amplitude-estimation`` and ``hhl``.
  3. Require Phase 8/8a finalized resource records, Phase 8b measured
     paper-named baselines, and Phase 8c top-3 alternatives.
  4. Emit selected scout entities plus the source labels that justify them.

The default mode is strict and exits non-zero until Phase 8 is finalized.
Use ``--allow-incomplete-phase8`` only for a preview manifest while the VM tail
is still running.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"
OUTPUTS = CANON / "outputs"
SCOUT_DIR = OUTPUTS / "phase08d_qae_hhl_scout"
SELECTION_PATH = SCOUT_DIR / "selection_manifest.json"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = [1e-3, 1e-4, 1e-6]
MODES = ["bare", "full"]
ANCHOR_PROFILE = "maj_e6_floquet"
ANCHOR_EPSILON = 1e-4

FAMILY_TO_SCOUT_ENTITIES = {
    "amplitude-estimation": ["qae_simmc_fixed_m"],
    "hhl": ["hhl_s1_fixed_m", "hhl_s2_fixed_m"],
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _phase_status(cohort: dict[str, Any], phase_id: str) -> dict[str, Any]:
    status = (cohort.get("_phase_status") or {}).get(phase_id) or {}
    return status if isinstance(status, dict) else {}


def _expected_phase8_filenames(labels: list[str]) -> set[str]:
    return {
        f"{label}_{profile}_eps{eps:.0e}_{mode}.json"
        for label in labels
        for profile in PROFILES
        for eps in EPSILONS
        for mode in MODES
    }


def _phase8_prereq(cohort: dict[str, Any], *, require_complete: bool) -> dict[str, Any]:
    labels = sorted(cohort["labels"].keys())
    expected = _expected_phase8_filenames(labels)
    found = {path.name for path in RESULTS.glob("*.json")} if RESULTS.exists() else set()
    missing = sorted(expected - found)
    extra = sorted(found - expected)
    p8 = _phase_status(cohort, "phase8")
    ok = p8.get("status") == "complete" and not missing and not extra
    return {
        "ok": ok,
        "blocking": not ok,
        "preview_permitted": not require_complete and not ok,
        "phase_status": p8.get("status"),
        "records_found": len(found),
        "records_expected": len(expected),
        "missing_count": len(missing),
        "extra_count": len(extra),
        "missing_sample": missing[:10],
        "extra_sample": extra[:10],
    }


def _phase8b_prereq(cohort: dict[str, Any]) -> dict[str, Any]:
    run = _phase_status(cohort, "phase8b_run")
    backfill = _phase_status(cohort, "phase8b_cohort")
    f_labels = [lid for lid, entry in cohort["labels"].items() if entry.get("fidelity") == "F"]
    missing = []
    nonnumeric = []
    for label in f_labels:
        baseline = (cohort["labels"][label].get("classical_baseline") or {})
        if not baseline:
            missing.append(label)
        elif not isinstance(baseline.get("wall_clock_seconds"), (int, float)):
            nonnumeric.append(label)
    ok = run.get("status") == "complete" and backfill.get("status") == "complete" and not missing and not nonnumeric
    return {
        "ok": ok,
        "blocking": not ok,
        "phase8b_run_status": run.get("status"),
        "phase8b_cohort_status": backfill.get("status"),
        "faithful_labels": len(f_labels),
        "missing_baseline_labels": missing,
        "nonnumeric_baseline_labels": nonnumeric,
    }


def _phase8c_prereq(cohort: dict[str, Any]) -> dict[str, Any]:
    status = _phase_status(cohort, "phase8c_alternatives")
    alternatives = cohort.get("classical_alternatives_top3") or {}
    labels = set(cohort["labels"].keys())
    missing = sorted(labels - set(alternatives))
    ok = status.get("status") == "complete" and not missing
    return {
        "ok": ok,
        "blocking": not ok,
        "phase_status": status.get("status"),
        "labels_with_alternatives": len(alternatives),
        "labels_expected": len(labels),
        "missing_labels": missing,
    }


def _baseline_relationship(entry: dict[str, Any]) -> str | None:
    baseline = entry.get("classical_baseline") or {}
    provenance = baseline.get("_phase8b_provenance") or {}
    return provenance.get("baseline_relationship") or baseline.get("baseline_relationship")


def _top3_summary(cohort: dict[str, Any], label: str) -> dict[str, Any]:
    block = (cohort.get("classical_alternatives_top3") or {}).get(label) or {}
    values = []
    skipped = False
    for value in block.values():
        if not isinstance(value, dict):
            continue
        if value.get("status") == "skipped":
            skipped = True
        seconds = value.get("wall_clock_seconds_median")
        if isinstance(seconds, (int, float)):
            values.append(float(seconds))
    return {
        "present": bool(block),
        "n_numeric_alternatives": len(values),
        "best_wall_clock_seconds_median": min(values) if values else None,
        "has_skip_record": skipped,
    }


def _anchor_record(label: str, mode: str) -> dict[str, Any] | None:
    path = RESULTS / f"{label}_{ANCHOR_PROFILE}_eps{ANCHOR_EPSILON:.0e}_{mode}.json"
    if not path.exists():
        return None
    rec = _read_json(path)
    measured = rec.get("measured") or {}
    return {
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
        "status": rec.get("status") or measured.get("status"),
        "runtime_seconds": measured.get("runtime_seconds"),
        "logical_qubits": measured.get("logical_qubits"),
        "t_count": measured.get("t_count"),
        "t_depth": measured.get("t_depth"),
    }


def build_manifest(*, require_phase8_complete: bool = True) -> dict[str, Any]:
    cohort = _read_json(COHORT)
    labels = cohort["labels"]

    prereqs = {
        "phase8a_resource_matrix": _phase8_prereq(cohort, require_complete=require_phase8_complete),
        "phase8b_classical_baselines": _phase8b_prereq(cohort),
        "phase8c_classical_alternatives": _phase8c_prereq(cohort),
    }
    blockers = [name for name, data in prereqs.items() if data.get("blocking")]

    selected_labels = []
    excluded_f_labels = []
    selected_entities: set[str] = set()
    family_counts = Counter(entry.get("algorithm_family") for entry in labels.values())
    faithful_family_counts = Counter(
        entry.get("algorithm_family")
        for entry in labels.values()
        if entry.get("fidelity") == "F"
    )

    for label, entry in sorted(labels.items()):
        if entry.get("fidelity") != "F":
            continue
        family = entry.get("algorithm_family")
        entities = FAMILY_TO_SCOUT_ENTITIES.get(family)
        if not entities:
            excluded_f_labels.append({
                "label": label,
                "family": family,
                "reason": "no fixed-precision QAE/HHL scout template for this family",
            })
            continue
        selected_entities.update(entities)
        baseline = entry.get("classical_baseline") or {}
        selected_labels.append({
            "label": label,
            "silo": entry.get("silo"),
            "algorithm_family": family,
            "paper_fidelity": entry.get("paper_fidelity"),
            "scout_entities": entities,
            "phase8a_anchor_full": _anchor_record(label, "full"),
            "phase8a_anchor_bare": _anchor_record(label, "bare"),
            "phase8b_baseline": {
                "algorithm_label": baseline.get("algorithm_label"),
                "wall_clock_seconds": baseline.get("wall_clock_seconds"),
                "baseline_relationship": _baseline_relationship(entry),
            },
            "phase8c_top3": _top3_summary(cohort, label),
        })

    status = "complete" if not blockers else "blocked"
    manifest = {
        "schema": "phase8d_selection_manifest.1.0",
        "phase": "8d",
        "track": "qae_hhl_fixed_precision_high_n",
        "status": status,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "decision_rule": [
            "select current F labels only",
            "include amplitude-estimation and HHL families only",
            "map amplitude-estimation to qae_simmc_fixed_m",
            "map HHL to hhl_s1_fixed_m and hhl_s2_fixed_m",
            "require Phase 8/8a, 8b, and 8c prerequisites before launch/finalization",
        ],
        "prerequisites": prereqs,
        "blockers": blockers,
        "selected_entities": sorted(selected_entities),
        "selected_labels": selected_labels,
        "excluded_f_labels": excluded_f_labels,
        "cohort_summary": {
            "n_labels": len(labels),
            "n_faithful": sum(1 for entry in labels.values() if entry.get("fidelity") == "F"),
            "family_counts": dict(sorted(family_counts.items(), key=lambda item: str(item[0]))),
            "faithful_family_counts": dict(sorted(faithful_family_counts.items(), key=lambda item: str(item[0]))),
        },
        "appendix_only": True,
        "headline_excludes_phase8d": True,
        "problem_size_decoupled_from_precision": True,
    }
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--allow-incomplete-phase8", action="store_true",
                        help="Write a preview manifest while Phase 8/8a is not finalized.")
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args(argv)

    manifest = build_manifest(require_phase8_complete=not args.allow_incomplete_phase8)
    if not args.no_write:
        _write_json(SELECTION_PATH, manifest)
        print(f"[phase8d-select] wrote {SELECTION_PATH.relative_to(ROOT)}")
    print(
        f"[phase8d-select] status={manifest['status']} "
        f"selected_entities={manifest['selected_entities']} "
        f"selected_labels={[row['label'] for row in manifest['selected_labels']]} "
        f"blockers={manifest['blockers']}"
    )
    return 0 if manifest["status"] == "complete" or args.allow_incomplete_phase8 else 1


if __name__ == "__main__":
    raise SystemExit(main())