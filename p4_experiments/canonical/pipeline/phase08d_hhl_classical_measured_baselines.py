"""Measured classical linear-system baselines for Phase 8d HHL context.

The output is appendix-only. It times classical scipy solvers on synthetic SPD
tridiagonal systems whose numeric size is aligned to the Phase 8d HHL proxy `N`
grid. This is not a semantic proof that the proxy HHL circuit solved the same
matrix; it is a time-bound classical reference with residuals, kappa settings,
and hardware metadata recorded explicitly.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

THREAD_ENV_VARS = [
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "OPENBLAS_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
]
for thread_env_var in THREAD_ENV_VARS:
    os.environ.setdefault(thread_env_var, "1")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import linalg, sparse
from scipy.sparse import linalg as sparse_linalg

from p4_experiments.canonical.pipeline.phase08d_hhl_classical_context import (
    OUTPUT_DIR,
    ROOT,
    _hhl_rows,
    _read_source_rows,
)


OUT_CSV = OUTPUT_DIR / "hhl_classical_measured_baselines.csv"
OUT_JSON = OUTPUT_DIR / "hhl_classical_measured_baselines.json"
OUT_PNG = OUTPUT_DIR / "p4_hhl_classical_measured_time.png"

DEFAULT_DENSE_N_VALUES = [20, 50, 100, 250, 500, 1000, 2000, 3000, 5000]
DEFAULT_SPARSE_N_VALUES = [20, 50, 100, 250, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 250000, 500000, 1000000]
DEFAULT_KAPPAS = [100, 1000]
DEFAULT_TOLERANCE = 1e-4
DEFAULT_REPEATS = 3


def _laplacian_extreme_eigenvalues(matrix_size: int) -> tuple[float, float]:
    smallest = 2.0 - 2.0 * np.cos(np.pi / (matrix_size + 1))
    largest = 2.0 - 2.0 * np.cos(matrix_size * np.pi / (matrix_size + 1))
    return float(smallest), float(largest)


def _shift_for_target_kappa(matrix_size: int, target_kappa: float) -> tuple[float, float]:
    smallest, largest = _laplacian_extreme_eigenvalues(matrix_size)
    natural_kappa = largest / smallest
    if target_kappa >= natural_kappa:
        return 0.0, natural_kappa
    shift = (largest - target_kappa * smallest) / (target_kappa - 1.0)
    achieved = (largest + shift) / (smallest + shift)
    return float(shift), float(achieved)


def _rhs_vector(matrix_size: int) -> np.ndarray:
    rng = np.random.default_rng(0x50414D50 + matrix_size)
    vector = rng.standard_normal(matrix_size).astype(np.float64, copy=False)
    return vector / np.linalg.norm(vector)


def _dense_spd_matrix(matrix_size: int, target_kappa: float) -> tuple[np.ndarray, np.ndarray, float]:
    shift, achieved_kappa = _shift_for_target_kappa(matrix_size, target_kappa)
    matrix = np.zeros((matrix_size, matrix_size), dtype=np.float64)
    np.fill_diagonal(matrix, 2.0 + shift)
    diagonal_indices = np.arange(matrix_size - 1)
    matrix[diagonal_indices, diagonal_indices + 1] = -1.0
    matrix[diagonal_indices + 1, diagonal_indices] = -1.0
    return matrix, _rhs_vector(matrix_size), achieved_kappa


def _sparse_spd_matrix(matrix_size: int, target_kappa: float) -> tuple[sparse.csr_matrix, np.ndarray, float]:
    shift, achieved_kappa = _shift_for_target_kappa(matrix_size, target_kappa)
    matrix = sparse.diags(
        diagonals=[
            np.full(matrix_size - 1, -1.0, dtype=np.float64),
            np.full(matrix_size, 2.0 + shift, dtype=np.float64),
            np.full(matrix_size - 1, -1.0, dtype=np.float64),
        ],
        offsets=[-1, 0, 1],
        format="csr",
    )
    return matrix, _rhs_vector(matrix_size), achieved_kappa


def _relative_residual(matrix: Any, solution: np.ndarray, rhs: np.ndarray) -> float:
    numerator = np.linalg.norm(matrix @ solution - rhs)
    denominator = np.linalg.norm(rhs)
    return float(numerator / denominator)


def _quantiles(values: list[float]) -> tuple[float, float, float]:
    array = np.asarray(values, dtype=np.float64)
    return tuple(float(value) for value in np.quantile(array, [0.25, 0.5, 0.75]))


def _summarize_runs(
    *,
    benchmark_id: str,
    algorithm_family: str,
    solver: str,
    matrix_model: str,
    matrix_size: int,
    target_kappa: int,
    achieved_kappa: float,
    tolerance: float,
    run_records: list[dict[str, Any]],
    memory_proxy_bytes: int,
    notes: str,
) -> dict[str, Any]:
    total_seconds = [float(record["total_seconds"]) for record in run_records]
    build_seconds = [float(record["build_seconds"]) for record in run_records]
    solve_seconds = [float(record["solve_seconds"]) for record in run_records]
    residuals = [float(record["relative_residual"]) for record in run_records]
    iterations = [record.get("iterations") for record in run_records if record.get("iterations") is not None]
    p25_total, median_total, p75_total = _quantiles(total_seconds)

    return {
        "benchmark_id": benchmark_id,
        "algorithm_family": algorithm_family,
        "solver": solver,
        "matrix_model": matrix_model,
        "n_value": matrix_size,
        "target_kappa": target_kappa,
        "achieved_kappa": achieved_kappa,
        "tolerance": tolerance,
        "repeats": len(run_records),
        "status": "ok" if all(record["status"] == "ok" for record in run_records) else "warning",
        "median_total_seconds": median_total,
        "p25_total_seconds": p25_total,
        "p75_total_seconds": p75_total,
        "median_build_seconds": _quantiles(build_seconds)[1],
        "median_solve_seconds": _quantiles(solve_seconds)[1],
        "median_relative_residual": _quantiles(residuals)[1],
        "min_relative_residual": min(residuals),
        "max_relative_residual": max(residuals),
        "median_iterations": _quantiles([float(value) for value in iterations])[1] if iterations else None,
        "memory_proxy_bytes": memory_proxy_bytes,
        "output_contract": "full_solution_vector",
        "comparison_scope": "measured local scipy baseline for time-bound context, not a quantum advantage claim",
        "notes": notes,
        "runs": run_records,
    }


def _run_dense_baseline(matrix_size: int, target_kappa: int, repeats: int, tolerance: float) -> dict[str, Any]:
    run_records: list[dict[str, Any]] = []
    achieved_kappa = float("nan")
    for repeat_index in range(repeats):
        total_start = time.perf_counter()
        matrix, rhs, achieved_kappa = _dense_spd_matrix(matrix_size, target_kappa)
        build_done = time.perf_counter()
        solution = linalg.solve(matrix, rhs, assume_a="pos", check_finite=False)
        solve_done = time.perf_counter()
        residual = _relative_residual(matrix, solution, rhs)
        run_records.append({
            "repeat_index": repeat_index,
            "status": "ok",
            "build_seconds": build_done - total_start,
            "solve_seconds": solve_done - build_done,
            "total_seconds": solve_done - total_start,
            "relative_residual": residual,
            "iterations": None,
        })
    memory_proxy_bytes = int((matrix_size * matrix_size + 2 * matrix_size) * np.dtype(np.float64).itemsize)
    return _summarize_runs(
        benchmark_id=f"dense_cholesky_n{matrix_size}_k{target_kappa}",
        algorithm_family="dense_direct",
        solver="scipy.linalg.solve_assume_pos",
        matrix_model="shifted_1d_laplacian_stored_dense_spd",
        matrix_size=matrix_size,
        target_kappa=target_kappa,
        achieved_kappa=achieved_kappa,
        tolerance=tolerance,
        run_records=run_records,
        memory_proxy_bytes=memory_proxy_bytes,
        notes="Dense direct timing uses dense storage and a Cholesky-family scipy solve on the same SPD tridiagonal matrix family.",
    )


def _run_sparse_baseline(matrix_size: int, target_kappa: int, repeats: int, tolerance: float) -> dict[str, Any]:
    run_records: list[dict[str, Any]] = []
    achieved_kappa = float("nan")
    matrix_memory_bytes = 0
    for repeat_index in range(repeats):
        total_start = time.perf_counter()
        matrix, rhs, achieved_kappa = _sparse_spd_matrix(matrix_size, target_kappa)
        matrix_memory_bytes = int(matrix.data.nbytes + matrix.indices.nbytes + matrix.indptr.nbytes)
        build_done = time.perf_counter()
        iteration_counter = {"count": 0}

        def count_iteration(_solution: np.ndarray) -> None:
            iteration_counter["count"] += 1

        solution, info = sparse_linalg.cg(
            matrix,
            rhs,
            rtol=tolerance,
            atol=0.0,
            callback=count_iteration,
            maxiter=max(10 * matrix_size, 1000),
        )
        solve_done = time.perf_counter()
        residual = _relative_residual(matrix, solution, rhs)
        run_records.append({
            "repeat_index": repeat_index,
            "status": "ok" if info == 0 else f"cg_info_{info}",
            "build_seconds": build_done - total_start,
            "solve_seconds": solve_done - build_done,
            "total_seconds": solve_done - total_start,
            "relative_residual": residual,
            "iterations": iteration_counter["count"],
        })
    memory_proxy_bytes = matrix_memory_bytes + int(2 * matrix_size * np.dtype(np.float64).itemsize)
    return _summarize_runs(
        benchmark_id=f"sparse_cg_n{matrix_size}_k{target_kappa}_tol{tolerance:.0e}",
        algorithm_family="sparse_iterative",
        solver="scipy.sparse.linalg.cg",
        matrix_model="shifted_1d_laplacian_sparse_spd",
        matrix_size=matrix_size,
        target_kappa=target_kappa,
        achieved_kappa=achieved_kappa,
        tolerance=tolerance,
        run_records=run_records,
        memory_proxy_bytes=memory_proxy_bytes,
        notes="Sparse CG exploits tridiagonal sparsity; convergence is reported via actual residual and iteration count.",
    )


def _write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "benchmark_id",
        "algorithm_family",
        "solver",
        "matrix_model",
        "n_value",
        "target_kappa",
        "achieved_kappa",
        "tolerance",
        "repeats",
        "status",
        "median_total_seconds",
        "p25_total_seconds",
        "p75_total_seconds",
        "median_build_seconds",
        "median_solve_seconds",
        "median_relative_residual",
        "min_relative_residual",
        "max_relative_residual",
        "median_iterations",
        "memory_proxy_bytes",
        "output_contract",
        "comparison_scope",
        "notes",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({fieldname: row.get(fieldname) for fieldname in fieldnames})


def _load_hhl_ok_rows() -> list[dict[str, Any]]:
    return [row for row in _hhl_rows(_read_source_rows()) if row["status"] == "ok" and row["runtime_seconds"]]


def _write_figure(rows: list[dict[str, Any]]) -> None:
    hhl_rows = _load_hhl_ok_rows()
    fig, ax = plt.subplots(figsize=(8.4, 5.8))

    hhl_specs = [
        ("hhl_s1_fixed_m", 4, "#2266aa", "o"),
        ("hhl_s1_fixed_m", 6, "#4f9bd6", "s"),
        ("hhl_s2_fixed_m", 4, "#aa5522", "^"),
    ]
    for entity_id, precision, color, marker in hhl_specs:
        selected = [
            row for row in hhl_rows
            if row["entity_id"] == entity_id and row["m_precision_qubits"] == precision
        ]
        if not selected:
            continue
        ax.loglog(
            [row["n_value"] for row in selected],
            [row["runtime_seconds"] for row in selected],
            marker=marker,
            linestyle="-",
            color=color,
            ms=5.2,
            lw=1.5,
            label=f"QDK HHL estimate {entity_id}, m={precision}",
        )

    plot_specs = [
        ("dense_direct", 100, "#333333", "D", "dense scipy solve, kappa=100"),
        ("sparse_iterative", 100, "#9467bd", "x", "sparse CG measured, kappa=100"),
        ("sparse_iterative", 1000, "#d62728", "+", "sparse CG measured, kappa=1000"),
    ]
    for algorithm_family, target_kappa, color, marker, label in plot_specs:
        selected = [
            row for row in rows
            if row["algorithm_family"] == algorithm_family and row["target_kappa"] == target_kappa
        ]
        if not selected:
            continue
        selected = sorted(selected, key=lambda row: int(row["n_value"]))
        ax.loglog(
            [row["n_value"] for row in selected],
            [row["median_total_seconds"] for row in selected],
            marker=marker,
            linestyle="--" if algorithm_family == "sparse_iterative" else ":",
            color=color,
            ms=5.8,
            lw=1.7,
            label=label,
        )

    ax.set_title(
        "Phase 8d time-bound context: QDK estimated HHL proxy runtime vs measured local scipy baselines\n"
        "Shared proxy/scaffold N grid, but different hardware, matrix semantics, and output contracts."
    )
    ax.set_xlabel("HHL proxy size / classical scaffold dimension N")
    ax.set_ylabel("Seconds (QDK estimate or measured local wall-clock)")
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.55)
    ax.legend(fontsize=6.9, framealpha=0.92)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=220)
    plt.close(fig)


def run_benchmarks(
    *,
    repeats: int = DEFAULT_REPEATS,
    tolerance: float = DEFAULT_TOLERANCE,
    dense_n_values: list[int] | None = None,
    sparse_n_values: list[int] | None = None,
    kappas: list[int] | None = None,
) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    dense_sizes = dense_n_values or DEFAULT_DENSE_N_VALUES
    sparse_sizes = sparse_n_values or DEFAULT_SPARSE_N_VALUES
    target_kappas = kappas or DEFAULT_KAPPAS

    rows: list[dict[str, Any]] = []
    for target_kappa in target_kappas:
        for matrix_size in dense_sizes:
            rows.append(_run_dense_baseline(matrix_size, target_kappa, repeats, tolerance))
        for matrix_size in sparse_sizes:
            rows.append(_run_sparse_baseline(matrix_size, target_kappa, repeats, tolerance))

    _write_csv(rows)
    _write_figure(rows)

    payload = {
        "schema": "phase8d_hhl_classical_measured_baselines.1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Appendix-only measured local scipy baselines for Phase 8d HHL time-bound context.",
        "outputs": {
            "csv": OUT_CSV.relative_to(ROOT).as_posix(),
            "figure_png": OUT_PNG.relative_to(ROOT).as_posix(),
        },
        "benchmark_contract": {
            "matrix_family": "shifted 1D Laplacian SPD system",
            "rhs_family": "fixed-seed normalized Gaussian vector per N",
            "numeric_size_alignment": "Uses a shared proxy/scaffold N grid: HHL N is a work-register proxy size and classical N is a scaffold matrix dimension; no semantic equivalence is asserted.",
            "output_contract": "full classical solution vector with residual reported",
            "tolerance": tolerance,
            "repeats": repeats,
            "dense_n_values": dense_sizes,
            "sparse_n_values": sparse_sizes,
            "target_kappas": target_kappas,
        },
        "hardware_metadata": {
            "platform": platform.platform(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": os.cpu_count(),
            "numpy_version": np.__version__,
            "scipy_version": scipy.__version__,
            "thread_env": {thread_env_var: os.environ.get(thread_env_var) for thread_env_var in THREAD_ENV_VARS},
        },
        "non_claims": [
            "Measured classical laptop/runtime rows are not a direct quantum advantage denominator.",
            "QDK HHL seconds are fault-tolerant hardware-model estimates, not measured quantum hardware wall-clock.",
            "The synthetic SPD matrix family is a comparison scaffold, not the proxy HHL unitary semantics.",
        ],
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _parse_int_list(value: str) -> list[int]:
    return [int(part.strip()) for part in value.split(",") if part.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEATS)
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    parser.add_argument("--dense-n", type=_parse_int_list, default=DEFAULT_DENSE_N_VALUES)
    parser.add_argument("--sparse-n", type=_parse_int_list, default=DEFAULT_SPARSE_N_VALUES)
    parser.add_argument("--kappas", type=_parse_int_list, default=DEFAULT_KAPPAS)
    args = parser.parse_args()

    payload = run_benchmarks(
        repeats=args.repeats,
        tolerance=args.tolerance,
        dense_n_values=args.dense_n,
        sparse_n_values=args.sparse_n,
        kappas=args.kappas,
    )
    print(json.dumps({
        "csv": payload["outputs"]["csv"],
        "figure_png": payload["outputs"]["figure_png"],
        "n_rows": len(payload["rows"]),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())