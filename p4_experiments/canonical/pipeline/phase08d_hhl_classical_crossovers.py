"""Crossover analysis for Phase 8d HHL and measured classical baselines.

This script reads the appendix-only QDK HHL resource rows and measured scipy
classical timing rows, then reports whether a quantum/classical runtime crossing
is observed in the measured grid and where a log-log fit would project one.

HHL N is the proxy work-register size. Classical N is a matched scaffold matrix
dimension. The shared x-axis is a context device, not a proof that both methods
solve the same matrix.

The projected values are extrapolations, not evidence of quantum advantage.
They are useful for seeing whether a crossover is inside the measured regime,
near the measured regime, or far outside what the current data support.
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
from matplotlib.ticker import LogFormatterMathtext, LogLocator
import numpy as np

from p4_experiments.canonical.pipeline.phase08d_hhl_classical_context import (
    OUTPUT_DIR,
    ROOT,
    _hhl_rows,
    _read_source_rows,
)


MEASURED_JSON = OUTPUT_DIR / "hhl_classical_measured_baselines.json"
OUT_CSV = OUTPUT_DIR / "hhl_classical_crossover_points.csv"
OUT_JSON = OUTPUT_DIR / "hhl_classical_crossover_points.json"
OUT_PNG = OUTPUT_DIR / "p4_hhl_classical_crossover_projection.png"
PROJECTION_MAX_N = 1_000_000.0
PROJECTION_MAX_SECONDS = 1_000_000.0
PLOT_QUANTUM_SERIES = ["hhl_s1_fixed_m_m4", "hhl_s1_fixed_m_m6"]
PLOT_CLASSICAL_SERIES = ["dense_direct_k100", "sparse_iterative_k100", "sparse_iterative_k1000"]


def _fit_power_law(series: list[tuple[int, float]]) -> dict[str, float]:
    clean = sorted((float(n_value), float(seconds)) for n_value, seconds in series if n_value > 0 and seconds > 0)
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


def _predict_seconds(fit: dict[str, float], n_value: float) -> float:
    return float(math.exp(fit["intercept"] + fit["exponent"] * math.log(n_value)))


def _observed_crossing(
    quantum_series: list[tuple[int, float]],
    classical_series: list[tuple[int, float]],
) -> tuple[float | None, float | None]:
    q_by_n = {int(n_value): float(seconds) for n_value, seconds in quantum_series if seconds > 0}
    c_by_n = {int(n_value): float(seconds) for n_value, seconds in classical_series if seconds > 0}
    common_n = sorted(set(q_by_n) & set(c_by_n))
    if len(common_n) < 2:
        return None, None
    log_ratios = [math.log(q_by_n[n_value] / c_by_n[n_value]) for n_value in common_n]
    for left_index in range(len(common_n) - 1):
        left_ratio = log_ratios[left_index]
        right_ratio = log_ratios[left_index + 1]
        if left_ratio == 0:
            n_value = float(common_n[left_index])
            return n_value, q_by_n[int(n_value)]
        if left_ratio * right_ratio > 0:
            continue
        left_log_n = math.log(common_n[left_index])
        right_log_n = math.log(common_n[left_index + 1])
        weight = abs(left_ratio) / (abs(left_ratio) + abs(right_ratio))
        log_n = left_log_n + weight * (right_log_n - left_log_n)
        n_value = math.exp(log_n)
        q_fit = _fit_power_law([
            (common_n[left_index], q_by_n[common_n[left_index]]),
            (common_n[left_index + 1], q_by_n[common_n[left_index + 1]]),
        ])
        return n_value, _predict_seconds(q_fit, n_value)
    return None, None


def _fit_crossover(
    quantum_fit: dict[str, float],
    classical_fit: dict[str, float],
) -> tuple[float | None, float | None]:
    q_exponent = quantum_fit["exponent"]
    c_exponent = classical_fit["exponent"]
    denominator = q_exponent - c_exponent
    if not np.isfinite(denominator) or abs(denominator) < 1e-12:
        return None, None
    log_n = (classical_fit["intercept"] - quantum_fit["intercept"]) / denominator
    if not np.isfinite(log_n):
        return None, None
    if log_n > math.log(1e308) or log_n < math.log(1e-308):
        return None, None
    n_value = math.exp(log_n)
    if n_value <= 0 or not np.isfinite(n_value):
        return None, None
    return n_value, _predict_seconds(quantum_fit, n_value)


def _series_label(entity_id: str, precision: int | None) -> str:
    return f"{entity_id}_m{precision}"


def _load_quantum_series() -> dict[str, list[tuple[int, float]]]:
    rows = [row for row in _hhl_rows(_read_source_rows()) if row["status"] == "ok" and row["runtime_seconds"]]
    series: dict[str, list[tuple[int, float]]] = {}
    for row in rows:
        label = _series_label(str(row["entity_id"]), row["m_precision_qubits"])
        series.setdefault(label, []).append((int(row["n_value"]), float(row["runtime_seconds"])))
    return {label: sorted(points) for label, points in series.items() if len(points) >= 3}


def _load_classical_series() -> dict[str, list[tuple[int, float]]]:
    if not MEASURED_JSON.exists():
        raise FileNotFoundError(f"missing measured baseline JSON: {MEASURED_JSON}")
    payload = json.loads(MEASURED_JSON.read_text(encoding="utf-8"))
    series: dict[str, list[tuple[int, float]]] = {}
    for row in payload.get("rows") or []:
        if row.get("status") != "ok":
            continue
        family = str(row.get("algorithm_family"))
        kappa = row.get("target_kappa")
        label = f"{family}_k{kappa}"
        series.setdefault(label, []).append((int(row["n_value"]), float(row["median_total_seconds"])))
    return {label: sorted(points) for label, points in series.items() if len(points) >= 3}


def _classify_projection(
    *,
    observed_n: float | None,
    projected_n: float | None,
    quantum_series: list[tuple[int, float]],
    classical_series: list[tuple[int, float]],
    quantum_fit: dict[str, float],
    classical_fit: dict[str, float],
) -> str:
    if observed_n is not None:
        return "observed_in_measured_grid"
    if projected_n is None:
        return "no_finite_power_law_crossover"

    max_measured_n = max(n for n, _ in quantum_series + classical_series)
    min_measured_n = min(n for n, _ in quantum_series + classical_series)
    if projected_n < min_measured_n:
        return "projected_below_measured_range"
    if projected_n <= max_measured_n:
        return "projected_inside_combined_range_but_not_observed_on_common_grid"
    if projected_n <= 100.0 * max_measured_n:
        return "near_extrapolated_crossover"
    if projected_n <= 1e12:
        return "far_extrapolated_crossover"
    return "extreme_extrapolation_not_reliable"


def _write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "quantum_series",
        "classical_series",
        "observed_crossover_n",
        "observed_crossover_seconds",
        "projected_crossover_n",
        "projected_crossover_seconds",
        "classification",
        "quantum_exponent",
        "classical_exponent",
        "quantum_fit_r2",
        "classical_fit_r2",
        "min_common_n",
        "max_common_n",
        "quantum_seconds_at_max_common_n",
        "classical_seconds_at_max_common_n",
        "ratio_quantum_over_classical_at_max_common_n",
        "notes",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({fieldname: row.get(fieldname) for fieldname in fieldnames})


def _write_figure(rows: list[dict[str, Any]]) -> None:
    rows_to_plot = [
        row for row in rows
        if row["quantum_series"] in set(PLOT_QUANTUM_SERIES)
        and row["classical_series"] in set(PLOT_CLASSICAL_SERIES)
    ]
    if not rows_to_plot:
        return
    quantum_by_label = _load_quantum_series()
    classical_by_label = _load_classical_series()

    fig, ax = plt.subplots(figsize=(9.0, 5.9))
    n_min = 20.0
    n_max = PROJECTION_MAX_N
    grid = np.logspace(math.log10(n_min), math.log10(n_max), 300)

    quantum_styles = {
        "hhl_s1_fixed_m_m4": ("#2266aa", "o", "HHL m=4"),
        "hhl_s1_fixed_m_m6": ("#aa5522", "s", "HHL m=6"),
    }
    for quantum_label in PLOT_QUANTUM_SERIES:
        quantum_series = quantum_by_label.get(quantum_label)
        if not quantum_series:
            continue
        color, marker, legend_label = quantum_styles[quantum_label]
        q_fit = _fit_power_law(quantum_series)
        last_success_n = max(n for n, _ in quantum_series)
        ax.axvline(last_success_n, color=color, ls=":", lw=0.8, alpha=0.45)
        ax.loglog(
            [n for n, _ in quantum_series],
            [seconds for _, seconds in quantum_series],
            marker,
            color=color,
            ms=5.0,
            label=f"QDK {legend_label} observed",
        )
        ax.loglog(
            grid,
            [_predict_seconds(q_fit, value) for value in grid],
            color=color,
            lw=1.8,
            label=f"QDK {legend_label} fit to N=1e6",
        )

    styles = {
        "dense_direct_k100": ("#333333", "D", "dense scipy kappa=100"),
        "sparse_iterative_k100": ("#9467bd", "x", "sparse CG kappa=100"),
        "sparse_iterative_k1000": ("#d62728", "+", "sparse CG kappa=1000"),
    }
    for label in PLOT_CLASSICAL_SERIES:
        color, marker, legend_label = styles[label]
        series = classical_by_label[label]
        c_fit = _fit_power_law(series)
        ax.loglog([n for n, _ in series], [seconds for _, seconds in series], marker, color=color, ms=6, label=f"{legend_label} measured")
        ax.loglog(grid, [_predict_seconds(c_fit, value) for value in grid], color=color, ls="--", lw=1.5, label=f"{legend_label} fit")

    ax.set_title(
        "Phase 8d Crossover Projection\n"
        "Proxy/scaffold N grid with log-log fits to N=1e6; HHL m=4 and m=6 shown",
        fontsize=11,
    )
    ax.text(
        0.01,
        0.02,
        "Vertical dotted lines mark last successful HHL estimate before extrapolation.",
        transform=ax.transAxes,
        fontsize=7.4,
        ha="left",
        va="bottom",
        bbox={"facecolor": "white", "alpha": 0.78, "edgecolor": "none", "pad": 2.0},
    )
    ax.set_xlabel("HHL proxy size / classical scaffold dimension N")
    ax.set_ylabel("Seconds")
    ax.set_xlim(n_min, n_max)
    ax.set_ylim(2e-5, PROJECTION_MAX_SECONDS)
    ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=12))
    ax.yaxis.set_major_formatter(LogFormatterMathtext(base=10.0))
    ax.grid(True, which="both", ls=":", lw=0.4, alpha=0.55)
    ax.legend(fontsize=6.6, framealpha=0.92)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=220)
    plt.close(fig)


def make_crossovers() -> dict[str, Any]:
    quantum_series_by_label = _load_quantum_series()
    classical_series_by_label = _load_classical_series()
    rows: list[dict[str, Any]] = []

    for quantum_label, quantum_series in sorted(quantum_series_by_label.items()):
        quantum_fit = _fit_power_law(quantum_series)
        q_by_n = {n: seconds for n, seconds in quantum_series}
        for classical_label, classical_series in sorted(classical_series_by_label.items()):
            classical_fit = _fit_power_law(classical_series)
            observed_n, observed_seconds = _observed_crossing(quantum_series, classical_series)
            projected_n, projected_seconds = _fit_crossover(quantum_fit, classical_fit)
            common_n = sorted(set(n for n, _ in quantum_series) & set(n for n, _ in classical_series))
            c_by_n = {n: seconds for n, seconds in classical_series}
            max_common_n = max(common_n) if common_n else None
            min_common_n = min(common_n) if common_n else None
            q_at_max = q_by_n[max_common_n] if max_common_n else None
            c_at_max = c_by_n[max_common_n] if max_common_n else None
            ratio_at_max = q_at_max / c_at_max if q_at_max and c_at_max else None
            classification = _classify_projection(
                observed_n=observed_n,
                projected_n=projected_n,
                quantum_series=quantum_series,
                classical_series=classical_series,
                quantum_fit=quantum_fit,
                classical_fit=classical_fit,
            )
            rows.append({
                "quantum_series": quantum_label,
                "classical_series": classical_label,
                "observed_crossover_n": observed_n,
                "observed_crossover_seconds": observed_seconds,
                "projected_crossover_n": projected_n,
                "projected_crossover_seconds": projected_seconds,
                "classification": classification,
                "quantum_exponent": quantum_fit["exponent"],
                "classical_exponent": classical_fit["exponent"],
                "quantum_fit_r2": quantum_fit["r2"],
                "classical_fit_r2": classical_fit["r2"],
                "min_common_n": min_common_n,
                "max_common_n": max_common_n,
                "quantum_seconds_at_max_common_n": q_at_max,
                "classical_seconds_at_max_common_n": c_at_max,
                "ratio_quantum_over_classical_at_max_common_n": ratio_at_max,
                "notes": "Projected crossovers are log-log power-law extrapolations and must not be cited as measured quantum advantage.",
            })

    _write_csv(rows)
    _write_figure(rows)
    payload = {
        "schema": "phase8d_hhl_classical_crossovers.1.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Appendix-only crossover accounting for QDK HHL estimates versus measured local scipy baselines.",
        "source_files": {
            "hhl_csv": (OUTPUT_DIR / "figure_phase8d_scaling_with_tail_exploratory.csv").relative_to(ROOT).as_posix(),
            "measured_classical_json": MEASURED_JSON.relative_to(ROOT).as_posix(),
        },
        "outputs": {
            "csv": OUT_CSV.relative_to(ROOT).as_posix(),
            "figure_png": OUT_PNG.relative_to(ROOT).as_posix(),
        },
        "interpretation_guardrails": [
            "Observed crossover means a sign change exists in the measured common N grid.",
            "Projected crossover means equality of fitted log-log power laws, not measured equality.",
            "QDK HHL seconds are fault-tolerant resource-estimator seconds; scipy rows are local classical wall-clock seconds.",
            "M, m_precision_qubits, and kappa are distinct quantities and are not interchangeable.",
            "HHL N is a work-register proxy size; classical N is a scaffold matrix dimension.",
        ],
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = make_crossovers()
    observed = [row for row in payload["rows"] if row["observed_crossover_n"] is not None]
    projected = [row for row in payload["rows"] if row["projected_crossover_n"] is not None]
    print(json.dumps({
        "csv": payload["outputs"]["csv"],
        "figure_png": payload["outputs"]["figure_png"],
        "n_rows": len(payload["rows"]),
        "observed_crossovers": len(observed),
        "projected_crossovers": len(projected),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())