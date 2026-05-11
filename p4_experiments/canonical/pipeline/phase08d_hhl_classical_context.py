"""Appendix-only HHL classical-comparison context artifacts.

This module deliberately does not claim an end-to-end HHL speedup. It builds
reviewer-facing context around the Phase 8d fixed-precision HHL scout:

* QDK resource-estimated HHL rows are plotted only as quantum resource data.
* Classical linear-system curves are operation-count proxies, not measured
  wall-clock competitors.
* HHL N is the template work-register proxy size. Classical N is a matched
    scaffold dimension used for context, not a demonstrated identical matrix.
* The generated contract states the output, precision, matrix-model, and
  data-access assumptions needed before any HHL/classical comparison can be
  interpreted as fair.

Outputs stay in the exploratory Phase 8d tail directory so the canonical
Hoefler and H1-H4 artifacts remain untouched.
"""
from __future__ import annotations

import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
OUTPUT_DIR = CANON / "outputs" / "phase08d_hhl_tail_exploratory"
SOURCE_CSV = OUTPUT_DIR / "figure_phase8d_scaling_with_tail_exploratory.csv"

OUT_CSV = OUTPUT_DIR / "hhl_classical_context.csv"
OUT_JSON = OUTPUT_DIR / "hhl_classical_context.json"
OUT_MD = OUTPUT_DIR / "hhl_classical_comparison_contract.md"
OUT_PNG = OUTPUT_DIR / "p4_hhl_classical_context.png"
OUT_SCALING_INDEX_PNG = OUTPUT_DIR / "p4_hhl_classical_scaling_index.png"
MEASURED_BASELINES_JSON = OUTPUT_DIR / "hhl_classical_measured_baselines.json"

QDK_EPSILON = 1e-4
CG_TOLERANCES = [1e-2, 1e-4, 1e-6]
CONDITION_NUMBERS = [10, 100, 1000]


def _read_source_rows() -> list[dict[str, str]]:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"missing source CSV: {SOURCE_CSV}")
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    number = _float_or_none(value)
    if number is None:
        return None
    return int(number)


def _hhl_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        if row.get("family") != "hhl":
            continue
        if row.get("hardware_profile") != "maj_e6_floquet":
            continue
        n_value = _int_or_none(row.get("n_value"))
        if n_value is None:
            continue
        selected.append({
            "entity_id": row.get("entity_id"),
            "n_value": n_value,
            "m_precision_qubits": _int_or_none(row.get("m_precision_qubits")),
            "hardware_profile": row.get("hardware_profile"),
            "epsilon": _float_or_none(row.get("epsilon")),
            "status": row.get("status"),
            "runtime_seconds": _float_or_none(row.get("runtime_seconds")),
            "physical_qubits": _float_or_none(row.get("physical_qubits")),
            "t_depth": _float_or_none(row.get("t_depth")),
            "t_count": _float_or_none(row.get("t_count")),
            "reason": row.get("reason") or "",
            "wall_clock_total_seconds": _float_or_none(row.get("wall_clock_total_seconds")),
            "source_file": row.get("source_file"),
            "exploratory_tail": str(row.get("exploratory_tail", "")).lower() == "true",
        })
    return selected


def _dense_direct_row(n_value: int) -> dict[str, Any]:
    return {
        "n_value": n_value,
        "model_id": "dense_direct_lu_full_vector",
        "matrix_model": "dense_general_or_spd",
        "classical_algorithm": "dense direct solve (LU/Cholesky family)",
        "output_contract": "full_solution_vector",
        "tolerance": None,
        "condition_number": None,
        "work_proxy_ops": (2.0 / 3.0) * (n_value ** 3),
        "memory_proxy_bytes": 8.0 * (n_value ** 2),
        "comparison_role": "upper-context for dense full-vector solve; not an HHL speedup claim",
        "notes": "HHL returns a quantum state, so dense full-vector solve is only fair if readout/tomography costs are included on the quantum side.",
    }


def _sparse_cg_row(n_value: int, condition_number: int, tolerance: float) -> dict[str, Any]:
    nnz = 3 * n_value
    # Standard CG-style iteration envelope for SPD systems: sqrt(kappa) times
    # a logarithmic tolerance factor. This is a model context, not a measured
    # benchmark and not a claim about the proxy HHL matrix semantics.
    iterations = math.ceil(math.sqrt(condition_number) * math.log(2.0 / tolerance))
    return {
        "n_value": n_value,
        "model_id": f"sparse_cg_k{condition_number}_tol{tolerance:.0e}",
        "matrix_model": "sparse_spd_tridiagonal_proxy",
        "classical_algorithm": "CG/MINRES-family sparse iterative solve",
        "output_contract": "full_solution_vector_or_observable_after_classical_solution",
        "tolerance": tolerance,
        "condition_number": condition_number,
        "work_proxy_ops": float(nnz * iterations),
        "memory_proxy_bytes": float((nnz + 3 * n_value) * 8),
        "comparison_role": "favorable sparse classical context; depends on kappa, sparsity, and residual tolerance",
        "notes": "A direct HHL comparison needs matched kappa, sparsity, data access, and requested output.",
    }


def _classical_context_rows(n_values: list[int]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n_value in n_values:
        rows.append(_dense_direct_row(n_value))
        for condition_number in CONDITION_NUMBERS:
            for tolerance in CG_TOLERANCES:
                rows.append(_sparse_cg_row(n_value, condition_number, tolerance))
    return rows


def _write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "n_value",
        "model_id",
        "matrix_model",
        "classical_algorithm",
        "output_contract",
        "tolerance",
        "condition_number",
        "work_proxy_ops",
        "memory_proxy_bytes",
        "comparison_role",
        "notes",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _configuration_boundaries(hhl_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    boundaries: list[dict[str, Any]] = []
    keys = sorted({(row["entity_id"], row["m_precision_qubits"]) for row in hhl_rows})
    for entity_id, precision in keys:
        rows = [
            row for row in hhl_rows
            if row["entity_id"] == entity_id and row["m_precision_qubits"] == precision
        ]
        successes = [row["n_value"] for row in rows if row["status"] == "ok"]
        failures = [row["n_value"] for row in rows if row["status"] != "ok"]
        tail_successes = [row["n_value"] for row in rows if row["status"] == "ok" and row["exploratory_tail"]]
        tail_failures = [row["n_value"] for row in rows if row["status"] != "ok" and row["exploratory_tail"]]
        boundaries.append({
            "entity_id": entity_id,
            "m_precision_qubits": precision,
            "max_success_n": max(successes) if successes else None,
            "max_tail_success_n": max(tail_successes) if tail_successes else None,
            "min_failed_n": min(failures) if failures else None,
            "min_tail_failed_n": min(tail_failures) if tail_failures else None,
            "n_successes": len(successes),
            "n_failures": len(failures),
        })
    return boundaries


def _write_contract(
    *,
    hhl_rows: list[dict[str, Any]],
    classical_rows: list[dict[str, Any]],
    generated_utc: str,
) -> None:
    ok_rows = [row for row in hhl_rows if row["status"] == "ok"]
    failed_rows = [row for row in hhl_rows if row["status"] != "ok"]
    tail_ok = [row for row in ok_rows if row["exploratory_tail"]]
    max_success_n = max((row["n_value"] for row in ok_rows), default=None)
    boundary_rows = _configuration_boundaries(hhl_rows)
    boundary_lines = []
    for row in boundary_rows:
        if row["n_failures"] == 0:
            continue
        tail_success_text = (
            f"max successful exploratory-tail proxy N=`{row['max_tail_success_n']}`"
            if row["max_tail_success_n"] is not None
            else "no successful exploratory-tail row for this configuration"
        )
        tail_failure_text = (
            f"minimum failed exploratory-tail proxy N=`{row['min_tail_failed_n']}`"
            if row["min_tail_failed_n"] is not None
            else "no failed exploratory-tail row for this configuration"
        )
        boundary_lines.append(
            f"- `{row['entity_id']}` m=`{row['m_precision_qubits']}`: "
            f"max successful proxy N=`{row['max_success_n']}`, "
            f"{tail_success_text}, "
            f"minimum failed proxy N=`{row['min_failed_n']}`, "
            f"{tail_failure_text}."
        )
    boundary_text = "\n".join(boundary_lines) if boundary_lines else "- No failed HHL rows in the selected data."

    text = f"""# HHL Classical-Comparison Contract

Generated UTC: `{generated_utc}`

## Status

This is an appendix-only Phase 8d comparison contract. It supports discussion of
fixed-precision HHL resource scaling, but it must not be pooled into H1-H4 and
must not be used as a standalone quantum-advantage claim.

## Quantum Object Being Compared

- Source data: `{SOURCE_CSV.relative_to(ROOT).as_posix()}`
- Quantum family: HHL fixed-precision proxy circuits only
- Hardware profile: `maj_e6_floquet`
- QDK resource-estimator error budget: `{QDK_EPSILON:g}`
- Successful HHL rows used for quantum-resource context: `{len(ok_rows)}`
- Successful exploratory tail rows: `{len(tail_ok)}`
- Failed/OOM or engine-failure HHL rows retained as boundary evidence: `{len(failed_rows)}`
- Largest successful proxy `N` in these rows: `{max_success_n}`

In this contract, HHL `N` is the current template work-register proxy size
(`n_b`). It must not be read as the dimension of a finance linear system. The
classical rows use a matched numeric scaffold dimension only to provide scaling
context.

Failure boundaries are configuration-specific, not a single monotone threshold:

{boundary_text}

The HHL template emits a quantum state proportional to the solution vector. It
does not by itself emit the full classical vector. A full-vector comparison is
therefore only fair if the quantum-side readout or tomography cost is included.

## Precision Rules

Do not equate these quantities without an explicit derivation:

1. QDK `epsilon`: a fault-tolerant resource-estimator error budget split across
   logical, T-state, and rotation-synthesis failures.
2. HHL `m_precision_qubits`: a phase-estimation clock precision parameter.
3. Classical solver tolerance: usually reported as a residual such as
   `||Ax - b|| / ||b||`.

For any reviewer-facing speedup claim, the classical residual tolerance and the
HHL phase-estimation/output error must be matched at the level of the requested
observable or solution vector. This artifact does not make that match; it only
records the required contract.

## Classical Context Included Here

The CSV `{OUT_CSV.relative_to(ROOT).as_posix()}` contains `{len(classical_rows)}`
classical model rows:

- Dense direct solve: work proxy `(2/3) N^3`, memory proxy `8 N^2` bytes.
- Sparse iterative solve: tridiagonal SPD proxy with CG/MINRES-style work
  `nnz * ceil(sqrt(kappa) * log(2/tol))`, using `kappa in {CONDITION_NUMBERS}`
  and `tol in {CG_TOLERANCES}`.

These are context curves, not measured competitors. They are intentionally kept
separate from the QDK runtime axis in the figure.

## Measured Classical Timing Addendum

If present, `{MEASURED_BASELINES_JSON.relative_to(ROOT).as_posix()}` records a
time-bound local scipy baseline scaffold: shifted 1D-Laplacian SPD systems,
fixed-seed normalized Gaussian right-hand sides, dense Cholesky-family solves
through the configured dense grid, and sparse CG solves through the configured sparse grid. Those rows are
useful because they provide seconds, residuals, iteration counts, memory proxies,
thread settings, and hardware metadata. They remain appendix context because the
synthetic SPD matrix is a matched-size classical scaffold, not a demonstrated
semantic match to the current proxy HHL unitary.

## Apples-to-Apples Output Addendum

If present, `{(OUTPUT_DIR / "hhl_apples_to_apples_contract.md").relative_to(ROOT).as_posix()}` records
the output-contract adjustment layer. It separates raw HHL state preparation,
single scalar-observable sampling, full-vector readout lower bounds, and a
tomography-style full-vector proxy. This is the artifact to cite when explaining
why HHL state preparation alone should not be compared against a classical solver
that returns the full vector.

## Allowed Statements

- The Phase 8d HHL scout provides QDK resource estimates for fixed-precision
  proxy circuits under a pinned hardware profile and error budget.
- The exploratory VM tail shows successful estimates through selected rows up
    to proxy `N=10000`, while exact decomposition becomes memory-bound for larger
    or more precise cells on the tested 84 GB VM class.
- Classical dense and sparse curves provide scaling context under explicitly
  stated matrix, tolerance, and output assumptions.
- The measured scipy addendum gives a time-bound local classical reference on a shared proxy/scaffold size grid with residual reporting, but does not by itself establish a quantum/classical advantage conclusion.

## Statements To Avoid

- Do not say the QDK `runtime_seconds` is a direct measured speedup over CPU or
  GPU wall-clock.
- Do not compare HHL state preparation to a classical full-vector solve unless
  quantum readout cost is included.
- Do not claim finance-specific HHL advantage from the current proxy `U`; the
  current template records resource scaling, not a calibrated finance matrix.
- Do not collapse QDK `epsilon`, HHL clock precision, and classical residual
  tolerance into one interchangeable precision parameter.

## Missing Before A Full PhD-Level HHL Comparison

1. A finance-relevant matrix family with documented sparsity, condition number,
   Hermitian embedding or block encoding, data-loading assumptions, and an
   explicit matrix-dimension-to-work-register mapping.
2. A matched observable-output task, or a full-vector task with quantum readout
   cost included.
3. A tolerance bridge from HHL phase-estimation error and QDK error budget to a
   classical residual tolerance.
4. Measured classical dense/sparse baselines on the matched task, with residuals,
   iteration counts, memory footprint where feasible, and fixed threading.
5. A small QDK sensitivity slice over `epsilon` and `m` that is explicitly
   reported as resource sensitivity rather than solution-accuracy equivalence.
"""
    OUT_MD.write_text(text, encoding="utf-8")


def _write_figure(hhl_rows: list[dict[str, Any]], classical_rows: list[dict[str, Any]]) -> None:
    ok_rows = [row for row in hhl_rows if row["status"] == "ok" and row["runtime_seconds"]]
    fail_rows = [row for row in hhl_rows if row["status"] != "ok"]

    fig, axes = plt.subplots(1, 2, figsize=(13.6, 5.3))

    ax = axes[0]
    markers = {
        ("hhl_s1_fixed_m", 4): "o",
        ("hhl_s1_fixed_m", 6): "s",
        ("hhl_s2_fixed_m", 4): "^",
        ("hhl_s2_fixed_m", 6): "D",
    }
    colors = {
        "hhl_s1_fixed_m": "#2266aa",
        "hhl_s2_fixed_m": "#aa5522",
    }
    plotted: set[tuple[str, int | None]] = set()
    for row in ok_rows:
        key = (row["entity_id"], row["m_precision_qubits"])
        ax.loglog(
            row["n_value"],
            row["runtime_seconds"],
            marker=markers.get(key, "o"),
            ms=6.5,
            linestyle="None",
            color=colors.get(row["entity_id"], "#555555"),
            markeredgecolor="black",
            markeredgewidth=0.5,
            label=f"{key[0]} m={key[1]}" if key not in plotted else None,
        )
        plotted.add(key)
    if fail_rows:
        xs = [row["n_value"] for row in fail_rows if row.get("wall_clock_total_seconds")]
        ys = [row["wall_clock_total_seconds"] for row in fail_rows if row.get("wall_clock_total_seconds")]
        ax.loglog(xs, ys, "x", color="#bb2222", ms=8, mew=1.8, label="failed/OOM cells (wall-clock boundary)")
    ax.set_title("A. HHL QDK resource estimates and failure boundary")
    ax.set_xlabel("HHL work-register proxy size N")
    ax.set_ylabel("QDK estimated runtime or failed-cell wall-clock (s)")
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.55)
    ax.legend(fontsize=7.4, framealpha=0.92)

    ax = axes[1]
    dense = [row for row in classical_rows if row["model_id"] == "dense_direct_lu_full_vector"]
    ax.loglog(
        [row["n_value"] for row in dense],
        [row["work_proxy_ops"] for row in dense],
        color="#333333",
        lw=2.0,
        label="dense direct solve, work approx (2/3)N^3",
    )
    for condition_number, color in [(10, "#2ca02c"), (100, "#9467bd"), (1000, "#d62728")]:
        sparse = [
            row for row in classical_rows
            if row["model_id"] == f"sparse_cg_k{condition_number}_tol1e-04"
        ]
        ax.loglog(
            [row["n_value"] for row in sparse],
            [row["work_proxy_ops"] for row in sparse],
            color=color,
            lw=1.8,
            label=f"sparse iterative, kappa={condition_number}, tol=1e-4",
        )
    ax.set_title("B. Classical linear-system work proxies (not wall-clock)")
    ax.set_xlabel("Classical scaffold dimension N")
    ax.set_ylabel("Classical operation-count proxy")
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.55)
    ax.legend(fontsize=7.4, framealpha=0.92)

    fig.suptitle(
        "Phase 8d HHL appendix context: resource estimates vs classical model curves\n"
        "Axes are intentionally separated; this is not an end-to-end speedup claim.",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(OUT_PNG, dpi=220)
    plt.close(fig)


def _normalized_series(points: list[tuple[int, float]]) -> tuple[list[int], list[float]]:
    clean = sorted((n_value, value) for n_value, value in points if value > 0)
    if not clean:
        return [], []
    baseline = clean[0][1]
    return [n_value for n_value, _ in clean], [value / baseline for _, value in clean]


def _write_scaling_index_figure(
    hhl_rows: list[dict[str, Any]],
    classical_rows: list[dict[str, Any]],
) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 5.6))

    quantum_specs = [
        ("hhl_s1_fixed_m", 4, "#2266aa", "o"),
        ("hhl_s1_fixed_m", 6, "#4f9bd6", "s"),
        ("hhl_s2_fixed_m", 4, "#aa5522", "^"),
    ]
    for entity_id, precision, color, marker in quantum_specs:
        points = [
            (row["n_value"], float(row["runtime_seconds"]))
            for row in hhl_rows
            if row["status"] == "ok"
            and row["entity_id"] == entity_id
            and row["m_precision_qubits"] == precision
            and row["runtime_seconds"]
        ]
        xs, ys = _normalized_series(points)
        if not xs:
            continue
        ax.loglog(
            xs,
            ys,
            color=color,
            marker=marker,
            ms=5.5,
            lw=1.8,
            label=f"QDK HHL {entity_id}, m={precision}",
        )

    classical_specs = [
        ("dense_direct_lu_full_vector", "#333333", "-", "dense direct, (2/3)N^3"),
        ("sparse_cg_k100_tol1e-04", "#9467bd", "--", "sparse iterative, kappa=100, tol=1e-4"),
        ("sparse_cg_k1000_tol1e-04", "#d62728", ":", "sparse iterative, kappa=1000, tol=1e-4"),
    ]
    for model_id, color, linestyle, label in classical_specs:
        points = [
            (int(row["n_value"]), float(row["work_proxy_ops"]))
            for row in classical_rows
            if row["model_id"] == model_id
        ]
        xs, ys = _normalized_series(points)
        if not xs:
            continue
        ax.loglog(xs, ys, color=color, ls=linestyle, lw=2.0, label=label)

    ax.set_title(
        "Single-panel scaling context: quantum resources and classical work models\n"
        "Each curve is normalized to its own smallest-N value; not an absolute speed comparison."
    )
    ax.set_xlabel("HHL proxy size / classical scaffold dimension N")
    ax.set_ylabel("Normalized scaling index (curve value / own first value)")
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.55)
    ax.legend(fontsize=7.2, framealpha=0.92)
    fig.tight_layout()
    fig.savefig(OUT_SCALING_INDEX_PNG, dpi=220)
    plt.close(fig)


def make_context() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    source_rows = _read_source_rows()
    hhl_rows = _hhl_rows(source_rows)
    n_values = sorted({row["n_value"] for row in hhl_rows})
    classical_rows = _classical_context_rows(n_values)
    generated_utc = datetime.now(timezone.utc).isoformat()

    _write_csv(classical_rows)
    _write_contract(hhl_rows=hhl_rows, classical_rows=classical_rows, generated_utc=generated_utc)
    _write_figure(hhl_rows, classical_rows)
    _write_scaling_index_figure(hhl_rows, classical_rows)

    status_counts: dict[str, int] = {}
    for row in hhl_rows:
        status = str(row["status"])
        status_counts[status] = status_counts.get(status, 0) + 1

    payload = {
        "schema": "phase8d_hhl_classical_context.1.0",
        "generated_utc": generated_utc,
        "purpose": "Appendix-only fair-comparison contract and classical linear-system context for Phase 8d HHL.",
        "source_csv": SOURCE_CSV.relative_to(ROOT).as_posix(),
        "outputs": {
            "comparison_contract_md": OUT_MD.relative_to(ROOT).as_posix(),
            "classical_context_csv": OUT_CSV.relative_to(ROOT).as_posix(),
            "figure_png": OUT_PNG.relative_to(ROOT).as_posix(),
            "scaling_index_png": OUT_SCALING_INDEX_PNG.relative_to(ROOT).as_posix(),
        },
        "qdk_hhl_filters": {
            "family": "hhl",
            "hardware_profile": "maj_e6_floquet",
            "qdk_epsilon": QDK_EPSILON,
        },
        "qdk_hhl_status_counts": status_counts,
        "configuration_boundaries": _configuration_boundaries(hhl_rows),
        "n_values": n_values,
        "classical_models": {
            "dense_direct_lu_full_vector": {
                "work_proxy_ops": "(2/3) * N^3",
                "memory_proxy_bytes": "8 * N^2",
                "output_contract": "full_solution_vector",
            },
            "sparse_cg_context": {
                "work_proxy_ops": "3*N * ceil(sqrt(kappa) * log(2/tol))",
                "condition_numbers": CONDITION_NUMBERS,
                "tolerances": CG_TOLERANCES,
                "output_contract": "full solution or observable after classical solution; depends on task",
            },
        },
        "non_claims": [
            "No direct QDK-runtime versus CPU/GPU wall-clock speedup is claimed.",
            "No HHL state-output versus full-vector classical solve comparison is claimed without readout cost.",
            "No one-to-one equivalence is claimed between QDK epsilon, HHL clock precision, and classical residual tolerance.",
            "No finance-specific HHL advantage is claimed from the current proxy U template.",
            "HHL N is a work-register proxy size, not a validated finance matrix dimension.",
        ],
        "hhl_rows": hhl_rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = make_context()
    print(json.dumps({
        "classical_context_csv": payload["outputs"]["classical_context_csv"],
        "comparison_contract_md": payload["outputs"]["comparison_contract_md"],
        "figure_png": payload["outputs"]["figure_png"],
        "scaling_index_png": payload["outputs"]["scaling_index_png"],
        "hhl_status_counts": payload["qdk_hhl_status_counts"],
        "n_values": payload["n_values"],
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())