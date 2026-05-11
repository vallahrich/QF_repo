"""Apples-to-apples output-contract adjustments for Phase 8d HHL.

The raw QDK HHL resource estimate times preparation of a quantum state. A
classical sparse/dense linear solve usually returns a full classical vector.
Those are different outputs. This script makes that distinction explicit by
adding derived output-contract scenarios to each successful HHL row and joining
them to measured classical rows at matching N values.

The adjustment scenarios are intentionally conservative and labelled as lower
bounds or proxies. They do not repair the fact that the current HHL template is
a resource-scaling proxy rather than a finance-semantic matrix solve.
HHL N is the proxy work-register size; classical N is a matched scaffold
dimension used for context.
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

from p4_experiments.canonical.pipeline.phase08d_hhl_classical_context import (
    OUTPUT_DIR,
    ROOT,
    _hhl_rows,
    _read_source_rows,
)


MEASURED_JSON = OUTPUT_DIR / "hhl_classical_measured_baselines.json"
OUT_CSV = OUTPUT_DIR / "hhl_apples_to_apples_adjustments.csv"
OUT_PROJECTION_CSV = OUTPUT_DIR / "hhl_apples_to_apples_projection_to_1e6.csv"
OUT_JSON = OUTPUT_DIR / "hhl_apples_to_apples_adjustments.json"
OUT_MD = OUTPUT_DIR / "hhl_apples_to_apples_contract.md"
OUT_PNG = OUTPUT_DIR / "p4_hhl_apples_to_apples_adjusted_time.png"

OBSERVABLE_ADDITIVE_ERROR = 1e-2
TOMOGRAPHY_AMPLITUDE_ERROR = 1e-2
PROJECTION_MAX_N = 1_000_000
PROJECTION_GRID_POINTS = 121
PROJECTION_ENTITY_ID = "hhl_s1_fixed_m"
PROJECTION_PRECISION_QUBITS = [4, 6]


def _load_hhl_rows() -> list[dict[str, Any]]:
    return [
        row for row in _hhl_rows(_read_source_rows())
        if row["status"] == "ok" and row["runtime_seconds"]
    ]


def _load_classical_rows() -> list[dict[str, Any]]:
    if not MEASURED_JSON.exists():
        raise FileNotFoundError(f"missing measured classical baseline file: {MEASURED_JSON}")
    payload = json.loads(MEASURED_JSON.read_text(encoding="utf-8"))
    return [row for row in payload.get("rows") or [] if row.get("status") == "ok"]


def _fit_power_law(points: list[tuple[float, float]]) -> dict[str, float]:
    clean = sorted((float(n_value), float(seconds)) for n_value, seconds in points if n_value > 0 and seconds > 0)
    if len(clean) < 2:
        return {"intercept": float("nan"), "exponent": float("nan"), "r2": float("nan")}
    x = np.log([point[0] for point in clean])
    y = np.log([point[1] for point in clean])
    exponent, intercept = np.polyfit(x, y, 1)
    prediction = intercept + exponent * x
    residual_ss = float(np.sum((y - prediction) ** 2))
    total_ss = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1.0 - residual_ss / total_ss if total_ss else 1.0
    return {"intercept": float(intercept), "exponent": float(exponent), "r2": float(r2)}


def _predict_power_law(fit: dict[str, float], n_value: float) -> float:
    return float(math.exp(fit["intercept"] + fit["exponent"] * math.log(n_value)))


def _scenario_rows(hhl_row: dict[str, Any]) -> list[dict[str, Any]]:
    n_value = int(hhl_row["n_value"])
    base_seconds = float(hhl_row["runtime_seconds"])
    observable_shots = math.ceil(1.0 / (OBSERVABLE_ADDITIVE_ERROR ** 2))
    tomography_repetitions = math.ceil(n_value / (TOMOGRAPHY_AMPLITUDE_ERROR ** 2))
    scenarios = [
        {
            "scenario_id": "state_preparation_only",
            "hhl_repetitions": 1,
            "adjusted_hhl_seconds": base_seconds,
            "output_contract": "quantum_state_proportional_to_solution",
            "apples_to_apples_level": "not_comparable_to_classical_full_vector",
            "readout_note": "Raw QDK estimate prepares a quantum state; it does not emit x as classical data.",
        },
        {
            "scenario_id": "single_scalar_observable_sampling",
            "hhl_repetitions": observable_shots,
            "adjusted_hhl_seconds": base_seconds * observable_shots,
            "output_contract": f"one bounded scalar observable to additive error about {OBSERVABLE_ADDITIVE_ERROR:g}",
            "apples_to_apples_level": "conditionally_comparable_only_if_classical_task_is_same_scalar_observable",
            "readout_note": "Uses plain 1/error^2 measurement sampling for a bounded observable; amplitude-estimation variants are not modeled.",
        },
        {
            "scenario_id": "full_vector_readout_lower_bound",
            "hhl_repetitions": n_value,
            "adjusted_hhl_seconds": base_seconds * n_value,
            "output_contract": "full classical solution vector lower-bound readout",
            "apples_to_apples_level": "lower_bound_not_sufficient_for_vector_accuracy",
            "readout_note": "At least O(N) state preparations are needed to emit N classical coordinates; signs/amplitudes require more.",
        },
        {
            "scenario_id": "full_vector_tomography_proxy",
            "hhl_repetitions": tomography_repetitions,
            "adjusted_hhl_seconds": base_seconds * tomography_repetitions,
            "output_contract": f"full classical solution vector tomography-style proxy at amplitude error about {TOMOGRAPHY_AMPLITUDE_ERROR:g}",
            "apples_to_apples_level": "rough_proxy_for_full_vector_output",
            "readout_note": "Uses N/error^2 repetitions as a simple tomography-scale proxy; constants and algorithmic improvements are not modeled.",
        },
    ]
    rows: list[dict[str, Any]] = []
    for scenario in scenarios:
        rows.append({
            "entity_id": hhl_row["entity_id"],
            "n_value": n_value,
            "m_precision_qubits": hhl_row["m_precision_qubits"],
            "hardware_profile": hhl_row["hardware_profile"],
            "qdk_epsilon": hhl_row["epsilon"],
            "base_hhl_runtime_seconds": base_seconds,
            **scenario,
        })
    return rows


def _scenario_projection_seconds(
    *,
    scenario_id: str,
    n_value: float,
    base_seconds: float,
) -> tuple[float, float]:
    if scenario_id == "state_preparation_only":
        return 1.0, base_seconds
    if scenario_id == "single_scalar_observable_sampling":
        repetitions = math.ceil(1.0 / (OBSERVABLE_ADDITIVE_ERROR ** 2))
        return float(repetitions), base_seconds * repetitions
    if scenario_id == "full_vector_readout_lower_bound":
        return n_value, base_seconds * n_value
    repetitions = n_value / (TOMOGRAPHY_AMPLITUDE_ERROR ** 2)
    return repetitions, base_seconds * repetitions


def _projection_grid(min_n_value: int) -> list[float]:
    raw = np.logspace(math.log10(min_n_value), math.log10(PROJECTION_MAX_N), PROJECTION_GRID_POINTS)
    grid = {float(PROJECTION_MAX_N)}
    for value in raw:
        grid.add(float(value))
    return sorted(grid)


def _projection_rows(
    *,
    hhl_rows: list[dict[str, Any]],
    classical_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    projection_rows: list[dict[str, Any]] = []
    selected_hhl = [
        row for row in hhl_rows
        if row["entity_id"] == PROJECTION_ENTITY_ID
        and int(row["m_precision_qubits"]) in PROJECTION_PRECISION_QUBITS
    ]
    min_n_value = min(int(row["n_value"]) for row in selected_hhl)
    grid = _projection_grid(min_n_value)
    scenario_ids = [
        "state_preparation_only",
        "single_scalar_observable_sampling",
        "full_vector_readout_lower_bound",
        "full_vector_tomography_proxy",
    ]

    for precision in PROJECTION_PRECISION_QUBITS:
        precision_rows = sorted(
            [row for row in selected_hhl if int(row["m_precision_qubits"]) == precision],
            key=lambda row: int(row["n_value"]),
        )
        if len(precision_rows) < 2:
            continue
        fit = _fit_power_law([(row["n_value"], row["runtime_seconds"]) for row in precision_rows])
        last_success_n = max(int(row["n_value"]) for row in precision_rows)
        for n_value in grid:
            base_seconds = _predict_power_law(fit, n_value)
            for scenario_id in scenario_ids:
                repetitions, adjusted_seconds = _scenario_projection_seconds(
                    scenario_id=scenario_id,
                    n_value=n_value,
                    base_seconds=base_seconds,
                )
                projection_rows.append({
                    "series_kind": "hhl_projection",
                    "entity_id": PROJECTION_ENTITY_ID,
                    "m_precision_qubits": precision,
                    "scenario_id": scenario_id,
                    "classical_algorithm_family": "",
                    "classical_target_kappa": "",
                    "n_value": n_value,
                    "projected_seconds": adjusted_seconds,
                    "projected_repetitions": repetitions,
                    "source_max_success_n": last_success_n,
                    "fit_exponent": fit["exponent"],
                    "fit_r2": fit["r2"],
                    "projection_status": "inside_observed_success_range" if n_value <= last_success_n else "extrapolated_beyond_successful_hhl_range",
                })

    return projection_rows


def _join_rows(
    hhl_scenarios: list[dict[str, Any]],
    classical_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    joined: list[dict[str, Any]] = []
    for hhl_row in hhl_scenarios:
        for classical_row in classical_rows:
            if int(classical_row["n_value"]) != int(hhl_row["n_value"]):
                continue
            ratio = hhl_row["adjusted_hhl_seconds"] / float(classical_row["median_total_seconds"])
            joined.append({
                **hhl_row,
                "classical_benchmark_id": classical_row["benchmark_id"],
                "classical_algorithm_family": classical_row["algorithm_family"],
                "classical_solver": classical_row["solver"],
                "classical_target_kappa": classical_row["target_kappa"],
                "classical_achieved_kappa": classical_row["achieved_kappa"],
                "classical_tolerance": classical_row["tolerance"],
                "classical_median_seconds": classical_row["median_total_seconds"],
                "classical_median_relative_residual": classical_row["median_relative_residual"],
                "classical_median_iterations": classical_row["median_iterations"],
                "ratio_adjusted_hhl_over_classical": ratio,
                "comparison_status": _comparison_status(hhl_row),
            })
    return joined


def _comparison_status(hhl_row: dict[str, Any]) -> str:
    scenario = hhl_row["scenario_id"]
    if scenario == "state_preparation_only":
        return "not_apples_to_apples_against_full_vector_classical_output"
    if scenario == "single_scalar_observable_sampling":
        return "apples_to_apples_only_for_same_scalar_observable_task"
    if scenario == "full_vector_readout_lower_bound":
        return "minimum_readout_charge_added_but_still_not_full_accuracy_tomography"
    return "rough_full_vector_output_proxy_not_a_theorem"


def _write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "entity_id",
        "n_value",
        "m_precision_qubits",
        "hardware_profile",
        "qdk_epsilon",
        "scenario_id",
        "output_contract",
        "apples_to_apples_level",
        "base_hhl_runtime_seconds",
        "hhl_repetitions",
        "adjusted_hhl_seconds",
        "readout_note",
        "classical_benchmark_id",
        "classical_algorithm_family",
        "classical_solver",
        "classical_target_kappa",
        "classical_achieved_kappa",
        "classical_tolerance",
        "classical_median_seconds",
        "classical_median_relative_residual",
        "classical_median_iterations",
        "ratio_adjusted_hhl_over_classical",
        "comparison_status",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({fieldname: row.get(fieldname) for fieldname in fieldnames})


def _write_projection_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "series_kind",
        "entity_id",
        "m_precision_qubits",
        "scenario_id",
        "classical_algorithm_family",
        "classical_target_kappa",
        "n_value",
        "projected_seconds",
        "projected_repetitions",
        "source_max_success_n",
        "fit_exponent",
        "fit_r2",
        "projection_status",
    ]
    with OUT_PROJECTION_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({fieldname: row.get(fieldname) for fieldname in fieldnames})


def _write_contract(rows: list[dict[str, Any]], generated_utc: str) -> None:
    text = f"""# HHL Apples-to-Apples Comparison Contract

Generated UTC: `{generated_utc}`

This artifact adds output-contract accounting to the Phase 8d HHL estimates. It
does not change the raw QDK resource estimates. It makes explicit that HHL state
preparation, a scalar observable estimate, and a full classical solution vector
are different computational tasks.

It also preserves the size-contract caveat: HHL `N` is the current template
work-register proxy size, while classical `N` is a matched scaffold matrix
dimension. The shared `N` grid is not a matrix-semantics equivalence claim.

## Scenarios

- `state_preparation_only`: the raw QDK HHL runtime. This is not comparable to a
  classical solver returning a full vector.
- `single_scalar_observable_sampling`: repeats HHL by `1/error^2` for one bounded scalar observable, using error `{OBSERVABLE_ADDITIVE_ERROR:g}` under plain measurement sampling; comparable only if the classical task is the same scalar observable. Amplitude-estimation variants are not modeled here.
- `full_vector_readout_lower_bound`: charges at least `N` HHL preparations. This
  is a lower bound for emitting `N` classical coordinates and is still not enough
  for signed-amplitude accuracy.
- `full_vector_tomography_proxy`: charges `N/error^2` preparations with error
  `{TOMOGRAPHY_AMPLITUDE_ERROR:g}`. This is a crude full-vector output proxy, not
  a theorem about optimal tomography.

## Interpretation

The measured scipy rows return full classical vectors with residuals. The QDK HHL
rows return fault-tolerant estimates for quantum-state preparation. Therefore,
the full-vector scenarios are the relevant rows when comparing against dense or
sparse classical linear solves. The scalar-observable scenario is only relevant
for a finance task whose requested output is a single expectation value or risk
statistic, not the whole solution vector.

## Classical Reference

The maintained figures draw the sparse CG `kappa=1000` reference from measured
rows directly. They do not draw a global fitted classical curve, because the
small-`N` timings are overhead dominated and the high-`N` rows are already
measured through `N={PROJECTION_MAX_N}`.

## Remaining Mismatch

Even after these output adjustments, this is still appendix context because the
current HHL circuit is a proxy resource template. A final apples-to-apples finance
claim still needs a finance-specific matrix family, block encoding/data-loading
model, an explicit matrix-dimension-to-work-register mapping, matched `kappa`,
matched sparsity, and a matched tolerance bridge.

Rows generated: `{len(rows)}`
CSV: `{OUT_CSV.relative_to(ROOT).as_posix()}`
HHL projection CSV to N=`{PROJECTION_MAX_N}`: `{OUT_PROJECTION_CSV.relative_to(ROOT).as_posix()}`
JSON: `{OUT_JSON.relative_to(ROOT).as_posix()}`
"""
    OUT_MD.write_text(text, encoding="utf-8")


def _write_figure(rows: list[dict[str, Any]], projection_rows: list[dict[str, Any]], classical_rows: list[dict[str, Any]]) -> None:
    selected_observed = [
        row for row in rows
        if row["entity_id"] == PROJECTION_ENTITY_ID
        and int(row["m_precision_qubits"]) in PROJECTION_PRECISION_QUBITS
        and row["classical_algorithm_family"] == "sparse_iterative"
        and int(row["classical_target_kappa"]) == 1000
    ]
    if not selected_observed or not projection_rows:
        return
    fig, ax = plt.subplots(figsize=(8.5, 5.7))
    scenario_styles = {
        "state_preparation_only": ("-", "state prep"),
        "single_scalar_observable_sampling": ("--", "scalar observable"),
        "full_vector_readout_lower_bound": ("-.", "full-vector readout LB"),
        "full_vector_tomography_proxy": (":", "tomography proxy"),
    }
    precision_styles = {
        4: ("#2266aa", "o"),
        6: ("#aa5522", "s"),
    }
    for precision in PROJECTION_PRECISION_QUBITS:
        color, marker = precision_styles[precision]
        last_success_n = max(
            int(row["source_max_success_n"])
            for row in projection_rows
            if row["series_kind"] == "hhl_projection" and int(row["m_precision_qubits"]) == precision
        )
        ax.axvline(last_success_n, color=color, ls=":", lw=0.8, alpha=0.45)
        for scenario_id, (line_style, scenario_label) in scenario_styles.items():
            observed = sorted(
                {
                    int(row["n_value"]): float(row["adjusted_hhl_seconds"])
                    for row in selected_observed
                    if int(row["m_precision_qubits"]) == precision
                    and row["scenario_id"] == scenario_id
                }.items(),
            )
            projected = sorted(
                [
                    row for row in projection_rows
                    if row["series_kind"] == "hhl_projection"
                    and int(row["m_precision_qubits"]) == precision
                    and row["scenario_id"] == scenario_id
                ],
                key=lambda row: float(row["n_value"]),
            )
            if not observed or not projected:
                continue
            ax.loglog(
                [n_value for n_value, _ in observed],
                [seconds for _, seconds in observed],
                marker=marker,
                color=color,
                linestyle="None",
                ms=4.5,
                alpha=0.88,
            )
            ax.loglog(
                [row["n_value"] for row in projected],
                [row["projected_seconds"] for row in projected],
                color=color,
                linestyle=line_style,
                lw=1.35,
                alpha=0.86,
                label=f"HHL m={precision} {scenario_label} projection",
            )
    classical_observed = sorted(
        [
            (int(row["n_value"]), float(row["median_total_seconds"]))
            for row in classical_rows
            if row["algorithm_family"] == "sparse_iterative"
            and int(row["target_kappa"]) == 1000
            and row.get("median_total_seconds")
        ]
    )
    if classical_observed:
        ax.loglog(
            [n_value for n_value, _ in classical_observed],
            [seconds for _, seconds in classical_observed],
            color="#555555",
            marker="x",
            ls="-",
            lw=1.45,
            ms=5.4,
            label="measured sparse CG kappa=1000",
        )
    ax.set_xlim(20, PROJECTION_MAX_N)
    ax.set_title(
        "Phase 8d Apples-to-Apples Projection to N=1e6\n"
        "Observed points plus log-log extrapolations for HHL m=4 and m=6",
        fontsize=11,
    )
    ax.set_xlabel("HHL proxy size / classical scaffold dimension N")
    ax.set_ylabel("Seconds")
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.55)
    ax.legend(fontsize=6.8, framealpha=0.92)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=220)
    plt.close(fig)


def make_adjustments() -> dict[str, Any]:
    hhl_rows = _load_hhl_rows()
    hhl_scenarios = [scenario for row in hhl_rows for scenario in _scenario_rows(row)]
    classical_rows = _load_classical_rows()
    joined = _join_rows(hhl_scenarios, classical_rows)
    projections = _projection_rows(hhl_rows=hhl_rows, classical_rows=classical_rows)
    generated_utc = datetime.now(timezone.utc).isoformat()

    _write_csv(joined)
    _write_projection_csv(projections)
    _write_contract(joined, generated_utc)
    _write_figure(joined, projections, classical_rows)

    payload = {
        "schema": "phase8d_hhl_apples_to_apples.1.0",
        "generated_utc": generated_utc,
        "purpose": "Appendix-only HHL output-contract adjustments for apples-to-apples comparison against measured classical full-vector solvers.",
        "source_files": {
            "hhl_csv": (OUTPUT_DIR / "figure_phase8d_scaling_with_tail_exploratory.csv").relative_to(ROOT).as_posix(),
            "measured_classical_json": MEASURED_JSON.relative_to(ROOT).as_posix(),
        },
        "outputs": {
            "csv": OUT_CSV.relative_to(ROOT).as_posix(),
            "projection_csv": OUT_PROJECTION_CSV.relative_to(ROOT).as_posix(),
            "json": OUT_JSON.relative_to(ROOT).as_posix(),
            "contract_md": OUT_MD.relative_to(ROOT).as_posix(),
            "figure_png": OUT_PNG.relative_to(ROOT).as_posix(),
        },
        "projection_contract": {
            "max_projected_n": PROJECTION_MAX_N,
            "hhl_entity_id": PROJECTION_ENTITY_ID,
            "hhl_m_precision_qubits": PROJECTION_PRECISION_QUBITS,
            "classical_projection": "none; maintained figures use measured sparse_iterative kappa=1000 rows directly through N=1000000",
            "guardrail": "HHL projection rows are log-log extrapolations beyond the successful HHL grid; sparse CG rows in maintained figures are measured, not fitted.",
        },
        "readout_assumptions": {
            "observable_additive_error": OBSERVABLE_ADDITIVE_ERROR,
            "tomography_amplitude_error": TOMOGRAPHY_AMPLITUDE_ERROR,
            "full_vector_lower_bound_repetitions": "N",
            "full_vector_tomography_proxy_repetitions": "N / amplitude_error^2",
        },
        "guardrails": [
            "State preparation alone is not comparable to classical full-vector output.",
            "Scalar observable rows are comparable only to the same scalar classical task.",
            "Full-vector rows add readout/tomography charges but remain proxy-level because the HHL unitary is not a finance-semantic matrix.",
            "HHL N is a work-register proxy size; classical N is a scaffold matrix dimension.",
        ],
        "rows": joined,
        "projection_rows": projections,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = make_adjustments()
    print(json.dumps({
        "csv": payload["outputs"]["csv"],
        "projection_csv": payload["outputs"]["projection_csv"],
        "contract_md": payload["outputs"]["contract_md"],
        "figure_png": payload["outputs"]["figure_png"],
        "rows": len(payload["rows"]),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())