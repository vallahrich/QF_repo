"""Legacy Hoefler empirical N-sweep, superseded for canonical Phase 8d.

Canonical Phase 8d is now the fixed-precision QAE/HHL high-N scout in
``phase8d_qae_hhl_scout.py``. This file is retained only for audit trail
continuity and requires ``--legacy-ok`` before it will run.

Sweeps each of {3 retained per-paper builders, 5 per-template kernels} across
a grid of problem sizes N at 2 hardware profiles {maj_e6_floquet,
maj_e6_surface} and epsilon=1e-04. Emits one phase8d.1.0 record per cell
into canonical/s8d_n_sweep/results/<entity>__N<N>__<profile>__eps1e-04.json.

DOES NOT touch:
  - common/output/results/             (canonical pre-reg cells)
  - canonical/cohort.json[labels]       (only writes _phase_status.phase8d)
  - any locked schema / artifact

Reuses run_unit.py infra:
  - apply_accounting()  for per-paper full-mode wrap
  - qdk_bridge.estimate() + _decompose_for_qdk() for the RE call
  - run_unit._estimate_with_timeout(), _engine_failure_measured(),
    _git_commit(), _versions()  (imported as private utilities)

Run:
    python -m p4_experiments.canonical.pipeline.phase08d_n_sweep --smoke
    python -m p4_experiments.canonical.pipeline.phase08d_n_sweep
    python -m p4_experiments.canonical.pipeline.phase08d_n_sweep --entities B3,tmpl_qae_simmc
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
SWEEP_DIR = CANON / "s8d_n_sweep"
RESULTS_DIR = SWEEP_DIR / "results"
SEED = 0x50414D50

PROFILES = ["maj_e6_floquet", "maj_e6_surface"]
EPSILONS = [1e-4]
PER_CELL_TIMEOUT_S = 1800

# ---------------------------------------------------------------- Entity registry

PER_PAPER_ENTITIES: Dict[str, Dict[str, Any]] = {
    # NOTE: N_grids trimmed empirically based on observed wall-clock times
    # (RE estimator runtime grows ~exponentially in N for full-mode wrapped
    # circuits). 5 N-values per (entity, profile) is sufficient for the
    # log-log power-law fit (need >=4 points). See DECISIONS_LOG Phase 8d.
    "B3": {
        "label": "B3",
        "params_for_N": lambda n: {"n_features": n, "feature_map_reps": 2},
        "N_grid": [3, 4, 6, 8, 12],
        "profiles": PROFILES,
    },
    "B4": {
        "label": "B4",
        "params_for_N": lambda n: {"n_qubits": n, "n_features": n, "ansatz_reps": 1},
        "N_grid": [3, 4, 6, 8, 10],
        "profiles": PROFILES,
    },
    "B5": {
        "label": "B5",
        "params_for_N": lambda n: {"n_qubits": n, "num_eval_qubits": n, "generator_reps": 2},
        "N_grid": [3, 4, 5, 6, 7],
        "profiles": PROFILES,
    },
}

PER_TEMPLATE_ENTITIES: Dict[str, Dict[str, Any]] = {
    # Trimmed to keep each per-cell wall-clock <=~5min; >=4 points for fit.
    "tmpl_ansatz_stretch": {"kind": "ansatz_stretch", "N_grid": [3, 4, 6, 8, 12]},
    "tmpl_amp_encoding":   {"kind": "amp_encoding",   "N_grid": [3, 4, 6, 8, 12]},
    "tmpl_qae_simmc":      {"kind": "qae_simmc",      "N_grid": [3, 4, 5, 6, 7]},
    "tmpl_hhl_sp3":        {"kind": "hhl",            "N_grid": [2, 3, 4, 5, 6], "hsim_steps": 1},
    "tmpl_hhl_sp8":        {"kind": "hhl",            "N_grid": [2, 3, 4, 5, 6], "hsim_steps": 2},
}


def _enforce_single_thread() -> None:
    for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS",
              "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[k] = "1"


def _grid_id(entity_id: str, N_grid: List[int]) -> str:
    payload = json.dumps({"e": entity_id, "N": list(N_grid)}, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _make_per_paper_circuits(entity_id: str, n: int):
    """Return (full_circuit, instance_used) for a per-paper entity at size N."""
    from p4_experiments.core.run_unit import _LABEL_TO_INSTANCE, _import_builder_module
    from p4_experiments.core.circuit_registry import get_builder
    from p4_experiments.core.oracle_accounting import apply_accounting

    spec = PER_PAPER_ENTITIES[entity_id]
    label = spec["label"]
    _import_builder_module(label)
    inst_path = _LABEL_TO_INSTANCE[label]
    inst = json.loads(inst_path.read_text(encoding="utf-8"))
    inst = copy.deepcopy(inst)
    inst.setdefault("parameters", {})
    inst["parameters"].update(spec["params_for_N"](n))
    inst["parameters"]["random_seed"] = SEED & 0xFFFFFFFF
    bare = get_builder(label).builder(inst)
    full = apply_accounting(label, "full", inst, bare)
    return full, inst


def _make_per_template_circuits(entity_id: str, n: int):
    """Return (full_circuit, synthetic_instance) for a per-template entity at N."""
    from p4_experiments.core.templates import (
        ansatz_stretch as _as,
        amplitude_encoding as _ae,
        qae as _qae,
        sim_mc_state_prep as _smc,
        hhl as _hhl,
    )

    spec = PER_TEMPLATE_ENTITIES[entity_id]
    kind = spec["kind"]
    seed = SEED & 0xFFFFFFFF
    if kind == "ansatz_stretch":
        c = _as.ansatz_stretch(n_qubits=n, layers=3, seed=seed)
        return c, {"template": kind, "n_qubits": n, "layers": 3}
    if kind == "amp_encoding":
        c = _ae.encoding_paired_inverse(n_qubits=n, layers=4, seed=seed)
        return c, {"template": kind, "n_qubits": n, "layers": 4}
    if kind == "qae_simmc":
        sp = _smc.continuous_func_state_prep(n_state=n, layers=2, seed=seed)
        c = _qae.canonical_qae(sp, num_eval_qubits=max(2, n - 2))
        return c, {"template": kind, "n_state": n, "num_eval_qubits": max(2, n - 2)}
    if kind == "hhl":
        c = _hhl.full_hhl(
            n_b=n, n_clock=n,
            hamiltonian_simulation_steps=spec["hsim_steps"],
            seed=seed, name=f"{entity_id}_n{n}",
        )
        return c, {"template": "hhl", "n_b": n, "n_clock": n,
                   "hsim_steps": spec["hsim_steps"]}
    raise ValueError(f"unknown template kind {kind!r}")


def _record_filename(entity_id: str, n: int, profile: str, eps: float) -> str:
    return f"{entity_id}__N{n:02d}__{profile}__eps{eps:.0e}.json"


def _make_phase8d_record(entity_id, entity_kind, n, profile, eps,
                         instance, measured, status, reason, dt,
                         fit_grid_id, qubit_count, depth) -> Dict[str, Any]:
    from p4_experiments.core.run_unit import _git_commit, _versions
    return {
        "schema": "phase8d.1.0",
        "phase": "8d",
        "entity_id": entity_id,
        "entity_kind": entity_kind,
        "label_or_template": entity_id,
        "n_value": n,
        "fit_grid_id": fit_grid_id,
        "hardware_profile": profile,
        "epsilon": eps,
        "accounting_mode": "full",
        "instance_synthetic": instance,
        "circuit_qubits": qubit_count,
        "circuit_depth_pre_re": depth,
        "measured": measured,
        "status": status,
        "reason": reason,
        "wall_clock_estimator_seconds": dt,
        "sweep_provenance": {
            "seed": hex(SEED),
            "git_commit": _git_commit(),
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "qdk_versions": _versions(),
            "appendix_only": True,
            "pre_registered": False,
            "headline_excludes_phase8d": True,
        },
    }


def run_one_cell(entity_id: str, n: int, profile: str, eps: float,
                 *, force: bool = False) -> Path:
    from p4_experiments.core.run_unit import _engine_failure_measured
    from p4_experiments.core.qdk_bridge import _decompose_for_qdk, estimate

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / _record_filename(entity_id, n, profile, eps)
    if out.exists() and not force:
        rec = json.loads(out.read_text(encoding="utf-8"))
        if rec.get("status") == "ok":
            print(f"[8d] RESUME-SKIP {out.name}", flush=True)
            return out

    if entity_id in PER_PAPER_ENTITIES:
        full, inst = _make_per_paper_circuits(entity_id, n)
        kind = "per-paper"
        grid = PER_PAPER_ENTITIES[entity_id]["N_grid"]
    elif entity_id in PER_TEMPLATE_ENTITIES:
        full, inst = _make_per_template_circuits(entity_id, n)
        kind = "per-template"
        grid = PER_TEMPLATE_ENTITIES[entity_id]["N_grid"]
    else:
        raise SystemExit(f"unknown entity_id {entity_id!r}")

    qubits, depth = full.num_qubits, full.depth()
    print(f"[8d] {entity_id} N={n} {profile} eps={eps:.0e} | "
          f"qubits={qubits} depth={depth}", flush=True)

    # NOTE: Direct in-process estimate() call. The multiprocessing-based
    # _estimate_with_timeout wrapper from run_unit.py spawns a child that
    # must pickle the post-decompose circuit, which can exceed wall-clock budgets on
    # Windows. Phase 8d is a serial appendix-only sweep; soft per-cell
    # protection is sufficient.
    decomposed = _decompose_for_qdk(full)
    t0 = time.perf_counter()
    try:
        measured = estimate(decomposed, profile, eps)
        dt = time.perf_counter() - t0
        status = "ok"
        reason = None
    except BaseException as exc:  # noqa: BLE001
        dt = time.perf_counter() - t0
        status = "engine_failure"
        reason = f"{type(exc).__name__}: {exc}"
        measured = _engine_failure_measured(reason, dt)

    record = _make_phase8d_record(
        entity_id, kind, n, profile, eps, inst, measured, status, reason, dt,
        fit_grid_id=_grid_id(entity_id, grid),
        qubit_count=qubits, depth=depth,
    )
    out.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
    print(f"  -> {out.name}  status={status}  dt={dt:.1f}s", flush=True)
    return out


def _record_phase_status(payload: Dict[str, Any]) -> None:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    ps = cohort.setdefault("_phase_status", {})
    cur = ps.get("phase8d") or {}
    cur.update(payload)
    ps["phase8d"] = cur
    COHORT.write_text(json.dumps(cohort, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8", newline="\n")


def _build_full_plan() -> List[Tuple[str, int, str, float]]:
    plan: List[Tuple[str, int, str, float]] = []
    for ent_id, spec in PER_PAPER_ENTITIES.items():
        for n in spec["N_grid"]:
            for prof in spec.get("profiles", PROFILES):
                for eps in EPSILONS:
                    plan.append((ent_id, n, prof, eps))
    for ent_id, spec in PER_TEMPLATE_ENTITIES.items():
        for n in spec["N_grid"]:
            for prof in PROFILES:
                for eps in EPSILONS:
                    plan.append((ent_id, n, prof, eps))
    return plan


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--legacy-ok", action="store_true",
                        help="Run the deprecated Hoefler N-sweep instead of canonical Phase 8d.")
    parser.add_argument("--entities", default=None,
                        help="Comma list (default: all per-paper + per-template).")
    parser.add_argument("--smoke", action="store_true",
                        help="Tiny plan for end-to-end sanity check.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    _enforce_single_thread()

    if not args.legacy_ok:
        print("[8d-legacy] Deprecated path. Canonical Phase 8d is "
              "phase8d_qae_hhl_scout.py + phase8d_finalize_qae_hhl.py. "
              "Pass --legacy-ok only to reproduce historical B12 artifacts.")
        return 2

    if args.smoke:
        plan = [
            ("B3", 3, "maj_e6_floquet", 1e-4),
            ("B3", 6, "maj_e6_floquet", 1e-4),
            ("tmpl_hhl_sp3", 2, "maj_e6_floquet", 1e-4),
        ]
    elif args.entities:
        wanted = args.entities.split(",")
        plan = [(e, n, p, eps) for (e, n, p, eps) in _build_full_plan()
                if e in wanted]
    else:
        plan = _build_full_plan()

    print(f"[8d] plan: {len(plan)} cells")
    if args.dry_run:
        for cell in plan:
            print("  ", cell)
        return 0

    _record_phase_status({"status": "running",
                          "started_utc": datetime.now(timezone.utc).isoformat(),
                          "plan_size": len(plan)})
    t0 = time.perf_counter()
    n_ok = n_fail = 0
    for entity_id, n, profile, eps in plan:
        try:
            p = run_one_cell(entity_id, n, profile, eps, force=args.force)
            rec = json.loads(p.read_text(encoding="utf-8"))
            if rec.get("status") == "ok":
                n_ok += 1
            else:
                n_fail += 1
        except Exception as exc:
            n_fail += 1
            print(f"  !! {entity_id} N={n} {profile} eps={eps}: {type(exc).__name__}: {exc}")

    _record_phase_status({"status": "complete",
                          "completed_utc": datetime.now(timezone.utc).isoformat(),
                          "wall_clock_seconds": round(time.perf_counter() - t0, 1),
                          "n_ok": n_ok,
                          "n_fail": n_fail,
                          "appendix_only": True,
                          "headline_excludes_phase8d": True})
    print(f"[8d] done: {n_ok} ok / {n_fail} fail / {len(plan)} total")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
