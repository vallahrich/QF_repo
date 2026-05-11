"""Phase 8d finalizer for the fixed-precision QAE/HHL high-N scout.

The actual Phase 8d cells are launched on idle Azure VMs by
``p4_experiments/infra/azure/phase8_6vm_20260425/Start-QAEHHLScout.ps1``
and synced back with ``Sync-QAEHHLScout.ps1``. This local finalizer summarizes the synced JSON
records, checks the staged grid is complete, writes ``phase8d_status.json``,
and stamps ``cohort.json['_phase_status']['phase8d']``.

Stages:
  - canary:  N={100,500,1000}, m={6}, profile=maj_e6_floquet
  - floquet: N={20,50,100,250,500,1000}, m={4,6,8}, profile=maj_e6_floquet
  - surface: floquet grid plus maj_e6_surface grid
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from p4_experiments.canonical.pipeline import phase08d_qae_hhl_scout as scout
from p4_experiments.canonical.pipeline.phase08d_select_experiments import SELECTION_PATH

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
STATUS_PATH = scout.SCOUT_DIR / "phase8d_status.json"

FINAL_STATUSES = {"ok", "engine_failure", "timeout"}
STAGES = ("canary", "floquet", "surface")


def _cell_key(row: dict[str, Any]) -> tuple[str, int, int, str, float] | None:
    try:
        return (
            str(row["entity_id"]),
            int(row["n_value"]),
            int(row["m_precision_qubits"]),
            str(row["hardware_profile"]),
            float(row["epsilon"]),
        )
    except Exception:
        return None


def expected_cells(stage: str) -> set[tuple[str, int, int, str, float]]:
    if stage == "canary":
        n_values = scout.CANARY_N_VALUES
        m_values = scout.CANARY_M_VALUES
        profiles = ["maj_e6_floquet"]
    elif stage == "floquet":
        n_values = scout.N_VALUES
        m_values = scout.M_VALUES
        profiles = ["maj_e6_floquet"]
    elif stage == "surface":
        n_values = scout.N_VALUES
        m_values = scout.M_VALUES
        profiles = list(scout.PROFILES)
    else:
        raise ValueError(f"unknown Phase 8d stage {stage!r}")

    return {
        (entity_id, int(n_value), int(m_value), profile, 1e-4)
        for entity_id in scout.ENTITIES
        for n_value in n_values
        for m_value in m_values
        for profile in profiles
    }


def _selection_manifest() -> dict[str, Any]:
    if not SELECTION_PATH.exists():
        raise SystemExit(
            "Phase 8d selection_manifest.json missing; run "
            "python -m p4_experiments.canonical.pipeline.phase08d_select_experiments "
            "after Phase 8/8a, 8b, and 8c are complete."
        )
    manifest = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    if manifest.get("status") != "complete":
        raise SystemExit(
            "Phase 8d selection manifest is not complete; blockers="
            f"{manifest.get('blockers')}"
        )
    selected = manifest.get("selected_entities") or []
    if not selected:
        raise SystemExit("Phase 8d selection manifest contains no selected_entities")
    return manifest


def selected_expected_cells(stage: str, selected_entities: list[str]) -> set[tuple[str, int, int, str, float]]:
    return {
        cell for cell in expected_cells(stage)
        if cell[0] in set(selected_entities)
    }


def detect_stage(rows: list[dict[str, Any]]) -> str:
    keys = {key for row in rows if (key := _cell_key(row)) is not None}
    if any(key[3] == "maj_e6_surface" for key in keys):
        return "surface"

    canary = expected_cells("canary")
    for key in keys:
        profile = key[3]
        if profile == "maj_e6_floquet" and key not in canary:
            return "floquet"
    return "canary"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stamp_cohort(status: dict[str, Any]) -> None:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    phase_status = cohort.get("_phase_status")
    if not isinstance(phase_status, dict):
        phase_status = {"_legacy": phase_status} if phase_status is not None else {}
    phase_status["phase8d"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "track": "qae_hhl_fixed_precision_high_n",
        "stage": status["stage"],
        "records": status["n_records"],
        "expected_records": status["expected_records"],
        "by_status": status["by_status"],
        "appendix_only": True,
        "headline_excludes_phase8d": True,
        "problem_size_decoupled_from_precision": True,
        "canonical_phase8_results_unchanged": True,
        "selection_manifest_path": str(SELECTION_PATH.relative_to(ROOT)).replace("\\", "/"),
        "selected_entities": status.get("selected_entities"),
        "selected_labels": status.get("selected_labels"),
        "status_path": str(STATUS_PATH.relative_to(ROOT)).replace("\\", "/"),
    }
    cohort["_phase_status"] = phase_status
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")


def finalize(stage: str = "auto") -> dict[str, Any]:
    selection = _selection_manifest()
    selected_entities = [str(entity_id) for entity_id in selection["selected_entities"]]
    summary = scout.summarize_results()
    rows = list(summary.get("rows") or [])
    if not rows:
        raise SystemExit(
            "no Phase 8d QAE/HHL scout records found; run/sync canary results first"
        )

    resolved_stage = detect_stage(rows) if stage == "auto" else stage
    expected = selected_expected_cells(resolved_stage, selected_entities)
    observed = {key for row in rows if (key := _cell_key(row)) is not None}
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    nonfinal = sorted(
        row.get("file") or str(_cell_key(row))
        for row in rows
        if str(row.get("status")) not in FINAL_STATUSES
    )

    status = {
        "schema": "phase8d_qae_hhl_status.1.0",
        "phase": "8d",
        "track": "qae_hhl_fixed_precision_high_n",
        "stage": resolved_stage,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "summary_path": str((scout.SCOUT_DIR / "summary.json").relative_to(ROOT)).replace("\\", "/"),
        "selection_manifest_path": str(SELECTION_PATH.relative_to(ROOT)).replace("\\", "/"),
        "selected_entities": selected_entities,
        "selected_labels": [row.get("label") for row in selection.get("selected_labels", [])],
        "results_dir": str(scout.RESULTS_DIR.relative_to(ROOT)).replace("\\", "/"),
        "n_records": len(rows),
        "expected_records": len(expected),
        "by_status": summary.get("by_status") or {},
        "missing_cells": [list(cell) for cell in missing],
        "extra_cells": [list(cell) for cell in extra],
        "nonfinal_records": nonfinal,
        "appendix_only": True,
        "headline_excludes_phase8d": True,
        "problem_size_decoupled_from_precision": True,
        "canonical_phase8_results_unchanged": True,
        "stage_policy": {
            "canary": "pilot gate before full floquet grid",
            "floquet": "primary high-N Majorana floquet scaling grid",
            "surface": "optional surface-code extension after floquet behaves",
        },
    }
    _write_json(STATUS_PATH, status)

    if missing or nonfinal:
        print(
            f"[phase8d-finalize] incomplete stage={resolved_stage}: "
            f"missing={len(missing)} nonfinal={len(nonfinal)}"
        )
        return status

    _stamp_cohort(status)
    print(
        f"[phase8d-finalize] complete stage={resolved_stage} "
        f"records={len(rows)} expected={len(expected)} by_status={status['by_status']}"
    )
    return status


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("auto",) + STAGES, default="auto")
    args = parser.parse_args(argv)
    status = finalize(args.stage)
    return 0 if not status["missing_cells"] and not status["nonfinal_records"] else 1


if __name__ == "__main__":
    raise SystemExit(main())