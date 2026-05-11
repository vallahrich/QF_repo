"""Canonical Phase 8d: QAE/HHL high-N fixed-precision scout.

Appendix-only resource-estimation scout for the finance-relevant QAE/HHL
families. This deliberately decouples problem size ``N`` from precision
qubits ``m``:

  - N: work/problem-size qubits, swept over [20, 50, 100, 250, 500, 1000]
  - m: QAE eval qubits or HHL clock qubits, swept over [4, 6, 8]

The canary plan runs (N, m) = (100, 6), (500, 6), (1000, 6) first on
``maj_e6_floquet``. Full floquet/surface plans can be launched afterwards if
the canaries behave.

Outputs are deterministic JSON records under::

    p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/results/

This is the only canonical Phase 8d track. The legacy Hoefler N-sweep remains
in the repository only as deprecated historical code.

This script does not write canonical Phase 8 results or cohort labels; run
``phase8d_finalize_qae_hhl.py`` after syncing VM results to stamp Phase 8d.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
OUTPUTS = CANON / "outputs"
SCOUT_DIR = OUTPUTS / "phase08d_qae_hhl_scout"
RESULTS_DIR = SCOUT_DIR / "results"
SELECTION_PATH = SCOUT_DIR / "selection_manifest.json"
SEED = 0x50414D50

N_VALUES = [20, 50, 100, 250, 500, 1000]
M_VALUES = [4, 6, 8]
CANARY_N_VALUES = [100, 500, 1000]
CANARY_M_VALUES = [6]
PROFILES = ["maj_e6_floquet", "maj_e6_surface"]
DEFAULT_PROFILE = ["maj_e6_floquet"]
EPSILONS = [1e-4]
DEFAULT_TIMEOUT_S = int(os.environ.get("P4_SCOUT_CELL_TIMEOUT_S", "36000"))

ENTITIES: Dict[str, Dict[str, Any]] = {
    "qae_simmc_fixed_m": {
        "family": "qae",
        "description": "QAE over simulation-MC state-prep proxy with fixed eval precision m.",
    },
    "hhl_s1_fixed_m": {
        "family": "hhl",
        "hsim_steps": 1,
        "description": "HHL proxy with fixed clock precision m and one Hamiltonian-simulation step.",
    },
    "hhl_s2_fixed_m": {
        "family": "hhl",
        "hsim_steps": 2,
        "description": "HHL proxy with fixed clock precision m and two Hamiltonian-simulation steps.",
    },
}

Cell = Tuple[str, int, int, str, float]


def _enforce_single_thread() -> None:
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"


def _parse_csv(value: str | None, default: Iterable[str]) -> List[str]:
    if value is None:
        return list(default)
    return [part.strip() for part in value.split(",") if part.strip()]


def _parse_int_csv(value: str | None, default: Iterable[int]) -> List[int]:
    if value is None:
        return list(default)
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def _default_entities_from_selection() -> List[str]:
    if not SELECTION_PATH.exists():
        return list(ENTITIES.keys())
    try:
        manifest = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    except Exception:
        return list(ENTITIES.keys())
    selected = manifest.get("selected_entities") or []
    if selected:
        return [str(entity_id) for entity_id in selected]
    return list(ENTITIES.keys())


def _ensure_selection_ready() -> None:
    if not SELECTION_PATH.exists():
        raise SystemExit(
            "Phase 8d selection_manifest.json missing; run "
            "python -m p4_experiments.canonical.pipeline.phase08d_select_experiments "
            "after Phase 8/8a, 8b, and 8c are complete."
        )
    try:
        manifest = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        raise SystemExit(f"Phase 8d selection manifest is not valid JSON: {exc}") from exc
    if manifest.get("status") != "complete" or manifest.get("blockers"):
        raise SystemExit(
            "Phase 8d selection manifest is not complete; blockers="
            f"{manifest.get('blockers')}"
        )


def _grid_id(plan: Iterable[Cell]) -> str:
    payload = json.dumps(list(plan), sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()[:16]


def _record_filename(entity_id: str, n: int, m: int, profile: str, eps: float) -> str:
    return f"{entity_id}__N{n:04d}__m{m:02d}__{profile}__eps{eps:.0e}.json"


def _record_path(entity_id: str, n: int, m: int, profile: str, eps: float) -> Path:
    return RESULTS_DIR / _record_filename(entity_id, n, m, profile, eps)


def _is_final_record(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        status = json.loads(path.read_text(encoding="utf-8")).get("status")
    except Exception:
        return False
    return status in {"ok", "engine_failure", "timeout"}


def _build_circuit(entity_id: str, n: int, m: int):
    if entity_id not in ENTITIES:
        raise ValueError(f"unknown entity_id {entity_id!r}")
    spec = ENTITIES[entity_id]
    family = spec["family"]
    seed = SEED & 0xFFFFFFFF

    if family == "qae":
        from p4_experiments.core.templates import qae, sim_mc_state_prep

        state_prep = sim_mc_state_prep.continuous_func_state_prep(
            n_state=n,
            layers=2,
            seed=seed,
        )
        circuit = qae.canonical_qae(
            state_prep,
            num_eval_qubits=m,
            name=f"qae_simmc_N{n}_m{m}",
        )
        instance = {
            "template": entity_id,
            "family": family,
            "n_state": n,
            "m_eval_qubits": m,
            "state_prep_layers": 2,
            "controlled_power_max": 2 ** (m - 1),
            "fixed_precision": True,
        }
        return circuit, instance

    if family == "hhl":
        from p4_experiments.core.templates import hhl

        hsim_steps = int(spec["hsim_steps"])
        circuit = hhl.full_hhl(
            n_b=n,
            n_clock=m,
            hamiltonian_simulation_steps=hsim_steps,
            seed=seed,
            name=f"{entity_id}_N{n}_m{m}",
        )
        instance = {
            "template": entity_id,
            "family": family,
            "n_b": n,
            "m_clock_qubits": m,
            "hamiltonian_simulation_steps": hsim_steps,
            "controlled_power_max": 2 ** (m - 1),
            "fixed_precision": True,
        }
        return circuit, instance

    raise ValueError(f"unknown family {family!r} for entity_id {entity_id!r}")


def _instance_metadata(entity_id: str, n: int, m: int) -> Dict[str, Any]:
    if entity_id not in ENTITIES:
        raise ValueError(f"unknown entity_id {entity_id!r}")
    spec = ENTITIES[entity_id]
    family = spec["family"]
    if family == "qae":
        return {
            "template": entity_id,
            "family": family,
            "n_state": n,
            "m_eval_qubits": m,
            "state_prep_layers": 2,
            "controlled_power_max": 2 ** (m - 1),
            "fixed_precision": True,
        }
    if family == "hhl":
        return {
            "template": entity_id,
            "family": family,
            "n_b": n,
            "m_clock_qubits": m,
            "hamiltonian_simulation_steps": int(spec["hsim_steps"]),
            "controlled_power_max": 2 ** (m - 1),
            "fixed_precision": True,
        }
    raise ValueError(f"unknown family {family!r} for entity_id {entity_id!r}")


def _make_record(
    *,
    entity_id: str,
    n: int,
    m: int,
    profile: str,
    eps: float,
    instance: Dict[str, Any] | None,
    measured: Dict[str, Any] | None,
    status: str,
    reason: str | None,
    grid_id: str,
    circuit_qubits: int | None,
    circuit_depth_pre_re: int | None,
    circuit_depth_post_decompose: int | None,
    ops_pre_re: int | None,
    ops_post_decompose: int | None,
    build_seconds: float | None,
    decompose_seconds: float | None,
    estimator_seconds: float | None,
    total_seconds: float | None,
) -> Dict[str, Any]:
    from p4_experiments.core.run_unit import _git_commit, _versions

    spec = ENTITIES.get(entity_id, {})
    return {
        "schema": "phase8d_qae_hhl_scout.1.0",
        "phase": "8d_qae_hhl_high_n_scout",
        "entity_id": entity_id,
        "entity_kind": "fixed-precision-template",
        "family": spec.get("family"),
        "description": spec.get("description"),
        "n_value": n,
        "m_precision_qubits": m,
        "precision_role": "qae_eval_qubits_or_hhl_clock_qubits",
        "fit_grid_id": grid_id,
        "hardware_profile": profile,
        "epsilon": eps,
        "accounting_mode": "full_fixed_precision",
        "instance_synthetic": instance or _instance_metadata(entity_id, n, m),
        "circuit_qubits": circuit_qubits,
        "circuit_depth_pre_re": circuit_depth_pre_re,
        "circuit_depth_post_decompose": circuit_depth_post_decompose,
        "ops_pre_re": ops_pre_re,
        "ops_post_decompose": ops_post_decompose,
        "measured": measured or {},
        "status": status,
        "reason": reason,
        "wall_clock_build_seconds": build_seconds,
        "wall_clock_decompose_seconds": decompose_seconds,
        "wall_clock_estimator_seconds": estimator_seconds,
        "wall_clock_total_seconds": total_seconds,
        "sweep_provenance": {
            "seed": hex(SEED),
            "git_commit": _git_commit(),
            "ts_utc": datetime.now(timezone.utc).isoformat(),
            "qdk_versions": _versions(),
            "selection_manifest_path": (
                str(SELECTION_PATH.relative_to(ROOT)).replace("\\", "/")
                if SELECTION_PATH.exists() else None
            ),
            "appendix_only": True,
            "pre_registered": False,
            "headline_excludes_phase8d_qae_hhl_scout": True,
            "canonical_phase8d_track": True,
            "problem_size_decoupled_from_precision": True,
            "canary_cell": n in CANARY_N_VALUES and m in CANARY_M_VALUES,
        },
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_one_cell(entity_id: str, n: int, m: int, profile: str, eps: float, *, force: bool = False) -> Path:
    from p4_experiments.core.qdk_bridge import _decompose_for_qdk, estimate
    from p4_experiments.core.run_unit import _engine_failure_measured

    out = _record_path(entity_id, n, m, profile, eps)
    if _is_final_record(out) and not force:
        print(f"[qae/hhl scout] RESUME-SKIP {out.name}", flush=True)
        return out

    total_start = time.perf_counter()
    grid_id = _grid_id([(entity_id, n, m, profile, eps)])
    build_start = time.perf_counter()
    circuit, instance = _build_circuit(entity_id, n, m)
    build_seconds = time.perf_counter() - build_start
    circuit_qubits = int(circuit.num_qubits)
    circuit_depth_pre_re = int(circuit.depth() or 0)
    ops_pre_re = int(sum(circuit.count_ops().values()))
    print(
        f"[qae/hhl scout] {entity_id} N={n} m={m} {profile} eps={eps:.0e} | "
        f"qubits={circuit_qubits} depth={circuit_depth_pre_re} ops={ops_pre_re}",
        flush=True,
    )
    _write_json(
        out,
        _make_record(
            entity_id=entity_id,
            n=n,
            m=m,
            profile=profile,
            eps=eps,
            instance=instance,
            measured={},
            status="running",
            reason=None,
            grid_id=grid_id,
            circuit_qubits=circuit_qubits,
            circuit_depth_pre_re=circuit_depth_pre_re,
            circuit_depth_post_decompose=None,
            ops_pre_re=ops_pre_re,
            ops_post_decompose=None,
            build_seconds=build_seconds,
            decompose_seconds=None,
            estimator_seconds=None,
            total_seconds=None,
        ),
    )

    decompose_start = time.perf_counter()
    decomposed = _decompose_for_qdk(circuit)
    decompose_seconds = time.perf_counter() - decompose_start
    circuit_depth_post_decompose = int(decomposed.depth() or 0)
    ops_post_decompose = int(sum(decomposed.count_ops().values()))

    estimator_start = time.perf_counter()
    try:
        measured = estimate(decomposed, profile, eps)
        estimator_seconds = time.perf_counter() - estimator_start
        status = "ok"
        reason = None
    except BaseException as exc:  # noqa: BLE001
        estimator_seconds = time.perf_counter() - estimator_start
        status = "engine_failure"
        reason = f"{type(exc).__name__}: {exc}"
        measured = _engine_failure_measured(reason, estimator_seconds)

    total_seconds = time.perf_counter() - total_start
    _write_json(
        out,
        _make_record(
            entity_id=entity_id,
            n=n,
            m=m,
            profile=profile,
            eps=eps,
            instance=instance,
            measured=measured,
            status=status,
            reason=reason,
            grid_id=grid_id,
            circuit_qubits=circuit_qubits,
            circuit_depth_pre_re=circuit_depth_pre_re,
            circuit_depth_post_decompose=circuit_depth_post_decompose,
            ops_pre_re=ops_pre_re,
            ops_post_decompose=ops_post_decompose,
            build_seconds=build_seconds,
            decompose_seconds=decompose_seconds,
            estimator_seconds=estimator_seconds,
            total_seconds=total_seconds,
        ),
    )
    print(f"  -> {out.name} status={status} total={total_seconds:.1f}s", flush=True)
    return out


def _timeout_record(entity_id: str, n: int, m: int, profile: str, eps: float, timeout_s: int) -> None:
    from p4_experiments.core.run_unit import _engine_failure_measured

    out = _record_path(entity_id, n, m, profile, eps)
    reason = f"timeout_after_{timeout_s}s"
    measured = _engine_failure_measured(reason, float(timeout_s))
    if out.exists():
        try:
            rec = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            rec = {}
        rec.update({
            "measured": measured,
            "status": "timeout",
            "reason": reason,
            "wall_clock_total_seconds": float(timeout_s),
            "wall_clock_estimator_seconds": rec.get("wall_clock_estimator_seconds"),
        })
    else:
        rec = _make_record(
            entity_id=entity_id,
            n=n,
            m=m,
            profile=profile,
            eps=eps,
            instance=None,
            measured=measured,
            status="timeout",
            reason=reason,
            grid_id=_grid_id([(entity_id, n, m, profile, eps)]),
            circuit_qubits=None,
            circuit_depth_pre_re=None,
            circuit_depth_post_decompose=None,
            ops_pre_re=None,
            ops_post_decompose=None,
            build_seconds=None,
            decompose_seconds=None,
            estimator_seconds=None,
            total_seconds=float(timeout_s),
        )
    _write_json(out, rec)
    print(f"  -> {out.name} status=timeout after {timeout_s}s", flush=True)


def _child_failure_record(entity_id: str, n: int, m: int, profile: str, eps: float, returncode: int, elapsed_s: float) -> None:
    from p4_experiments.core.run_unit import _engine_failure_measured

    out = _record_path(entity_id, n, m, profile, eps)
    reason = f"child_process_exit_{returncode}"
    measured = _engine_failure_measured(reason, elapsed_s)
    if out.exists():
        try:
            rec = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            rec = {}
        rec.update({
            "measured": measured,
            "status": "engine_failure",
            "reason": reason,
            "wall_clock_total_seconds": elapsed_s,
            "wall_clock_estimator_seconds": rec.get("wall_clock_estimator_seconds"),
        })
    else:
        rec = _make_record(
            entity_id=entity_id,
            n=n,
            m=m,
            profile=profile,
            eps=eps,
            instance=None,
            measured=measured,
            status="engine_failure",
            reason=reason,
            grid_id=_grid_id([(entity_id, n, m, profile, eps)]),
            circuit_qubits=None,
            circuit_depth_pre_re=None,
            circuit_depth_post_decompose=None,
            ops_pre_re=None,
            ops_post_decompose=None,
            build_seconds=None,
            decompose_seconds=None,
            estimator_seconds=None,
            total_seconds=elapsed_s,
        )
    _write_json(out, rec)
    print(f"  -> {out.name} status=engine_failure rc={returncode} elapsed={elapsed_s:.1f}s", flush=True)


def _plan_defaults(plan: str) -> tuple[List[int], List[int], List[str]]:
    if plan == "canary":
        return list(CANARY_N_VALUES), list(CANARY_M_VALUES), list(DEFAULT_PROFILE)
    if plan == "floquet":
        return list(N_VALUES), list(M_VALUES), ["maj_e6_floquet"]
    if plan == "surface":
        return list(N_VALUES), list(M_VALUES), ["maj_e6_surface"]
    if plan == "all":
        return list(N_VALUES), list(M_VALUES), list(PROFILES)
    raise ValueError(f"unknown plan {plan!r}")


def _cell_weight(cell: Cell) -> int:
    entity_id, n, m, _profile, _eps = cell
    family = ENTITIES.get(entity_id, {}).get("family")
    multiplier = 1.0
    if entity_id == "hhl_s2_fixed_m":
        multiplier = 2.0
    elif family == "qae":
        multiplier = 1.5
    return max(1, int(n * (2 ** m) * multiplier))


def _apply_weighted_shard(plan: List[Cell], shard_index: int, shard_count: int) -> List[Cell]:
    if shard_count <= 1:
        return plan
    if shard_index < 0 or shard_index >= shard_count:
        raise SystemExit("--shard-index must satisfy 0 <= index < --shard-count")
    shards: List[List[Cell]] = [[] for _ in range(shard_count)]
    weights = [0 for _ in range(shard_count)]
    for cell in sorted(plan, key=_cell_weight, reverse=True):
        target = min(range(shard_count), key=lambda idx: weights[idx])
        shards[target].append(cell)
        weights[target] += _cell_weight(cell)
    return sorted(shards[shard_index])


def build_plan(args: argparse.Namespace) -> List[Cell]:
    default_ns, default_ms, default_profiles = _plan_defaults(args.plan)
    entities = _parse_csv(args.entities, _default_entities_from_selection())
    n_values = _parse_int_csv(args.n_values, default_ns)
    m_values = _parse_int_csv(args.m_values, default_ms)
    profiles = _parse_csv(args.profiles, default_profiles)
    epsilons = [float(v) for v in _parse_csv(args.epsilons, ["1e-4"])]

    unknown_entities = sorted(set(entities) - set(ENTITIES))
    if unknown_entities:
        raise SystemExit(f"unknown entities: {unknown_entities}; known={sorted(ENTITIES)}")
    unknown_profiles = sorted(set(profiles) - set(PROFILES))
    if unknown_profiles:
        raise SystemExit(f"unknown profiles: {unknown_profiles}; known={PROFILES}")

    plan: List[Cell] = []
    for entity_id in entities:
        for n in n_values:
            for m in m_values:
                for profile in profiles:
                    for eps in epsilons:
                        plan.append((entity_id, n, m, profile, eps))
    plan = sorted(plan)
    return _apply_weighted_shard(plan, args.shard_index, args.shard_count)


def _run_cell_subprocess(cell: Cell, *, timeout_s: int, force: bool) -> int:
    entity_id, n, m, profile, eps = cell
    out = _record_path(entity_id, n, m, profile, eps)
    if _is_final_record(out) and not force:
        print(f"[qae/hhl scout] RESUME-SKIP {out.name}", flush=True)
        return 0
    cmd = [
        sys.executable,
        "-m",
        "p4_experiments.canonical.pipeline.phase08d_qae_hhl_scout",
        "--run-cell",
        "--entity",
        entity_id,
        "--n",
        str(n),
        "--m",
        str(m),
        "--profile",
        profile,
        "--epsilon",
        f"{eps:.17g}",
    ]
    if force:
        cmd.append("--force")
    start = time.perf_counter()
    try:
        completed = subprocess.run(cmd, cwd=str(ROOT), timeout=timeout_s)
        returncode = int(completed.returncode)
        if returncode not in (0, 2, 124) and not _is_final_record(out):
            _child_failure_record(entity_id, n, m, profile, eps, returncode, time.perf_counter() - start)
        return returncode
    except subprocess.TimeoutExpired:
        _timeout_record(entity_id, n, m, profile, eps, timeout_s)
        return 124


def summarize_results() -> Dict[str, Any]:
    rows = []
    for path in sorted(RESULTS_DIR.glob("*.json")):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        measured = rec.get("measured") or {}
        rows.append({
            "file": path.name,
            "entity_id": rec.get("entity_id"),
            "family": rec.get("family"),
            "n_value": rec.get("n_value"),
            "m_precision_qubits": rec.get("m_precision_qubits"),
            "hardware_profile": rec.get("hardware_profile"),
            "epsilon": rec.get("epsilon"),
            "status": rec.get("status"),
            "logical_qubits": measured.get("logical_qubits"),
            "physical_qubits": measured.get("physical_qubits"),
            "t_count": measured.get("t_count"),
            "t_depth": measured.get("t_depth"),
            "runtime_seconds": measured.get("runtime_seconds"),
            "wall_clock_total_seconds": rec.get("wall_clock_total_seconds"),
            "reason": rec.get("reason"),
        })
    by_status: Dict[str, int] = {}
    for row in rows:
        by_status[str(row["status"])] = by_status.get(str(row["status"]), 0) + 1
    summary = {
        "schema": "phase8d_qae_hhl_scout_summary.1.0",
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "results_dir": str(RESULTS_DIR.relative_to(ROOT)).replace("\\", "/"),
        "n_records": len(rows),
        "by_status": by_status,
        "rows": rows,
    }
    SCOUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_json(SCOUT_DIR / "summary.json", summary)
    return summary


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", choices=["canary", "floquet", "surface", "all"], default="canary")
    parser.add_argument("--entities", default=None, help="Comma list; default all QAE/HHL scout entities.")
    parser.add_argument("--n-values", default=None, help="Comma list of N values overriding the selected plan.")
    parser.add_argument("--m-values", default=None, help="Comma list of m precision values overriding the selected plan.")
    parser.add_argument("--profiles", default=None, help="Comma list of profiles overriding the selected plan.")
    parser.add_argument("--epsilons", default=None, help="Comma list of epsilons; default 1e-4.")
    parser.add_argument("--timeout-s", type=int, default=DEFAULT_TIMEOUT_S)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-unselected", action="store_true",
                        help="Development only: run without a complete 8d selection manifest.")
    parser.add_argument("--summarize", action="store_true")
    parser.add_argument("--run-cell", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--entity", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--n", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--m", type=int, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--profile", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--epsilon", type=float, default=1e-4, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    _enforce_single_thread()

    if not args.dry_run and not args.summarize and not args.allow_unselected:
        _ensure_selection_ready()

    if args.summarize:
        summary = summarize_results()
        print(json.dumps({"n_records": summary["n_records"], "by_status": summary["by_status"]}, indent=2))
        return 0

    if args.run_cell:
        missing = [name for name in ("entity", "n", "m", "profile") if getattr(args, name) is None]
        if missing:
            raise SystemExit(f"--run-cell missing required args: {missing}")
        path = run_one_cell(args.entity, args.n, args.m, args.profile, args.epsilon, force=args.force)
        rec = json.loads(path.read_text(encoding="utf-8"))
        return 0 if rec.get("status") == "ok" else 2

    plan = build_plan(args)
    print(
        f"[qae/hhl scout] plan={args.plan} cells={len(plan)} "
        f"shard={args.shard_index}/{args.shard_count} timeout_s={args.timeout_s}",
        flush=True,
    )
    if args.dry_run:
        for cell in plan:
            print("  ", cell)
        return 0

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    counts = {"ok": 0, "engine_failure": 0, "timeout": 0, "running": 0, "missing": 0, "other": 0}
    for cell in plan:
        rc = _run_cell_subprocess(cell, timeout_s=args.timeout_s, force=args.force)
        entity_id, n, m, profile, eps = cell
        out = _record_path(entity_id, n, m, profile, eps)
        if out.exists():
            try:
                status = str(json.loads(out.read_text(encoding="utf-8")).get("status"))
            except Exception:
                status = "other"
        else:
            status = "missing"
        if status not in counts:
            status = "other"
        counts[status] += 1
        if rc not in (0, 2, 124):
            print(f"[qae/hhl scout] child returned rc={rc} for {cell}", flush=True)

    summary = summarize_results()
    elapsed = time.perf_counter() - start
    print(f"[qae/hhl scout] done elapsed={elapsed:.1f}s shard_counts={counts}", flush=True)
    print(f"[qae/hhl scout] cumulative_records={summary['n_records']} by_status={summary['by_status']}", flush=True)
    return 0 if all(counts[key] == 0 for key in ("engine_failure", "timeout", "running", "missing", "other")) else 1


if __name__ == "__main__":
    raise SystemExit(main())