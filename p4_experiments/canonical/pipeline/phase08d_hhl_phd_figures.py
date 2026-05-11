"""Generate PhD-safe Phase 8d HHL appendix figures.

These figures are deliberately more conservative than the exploratory working
plots. They separate quantum resource estimates from classical scaffolds, mark
extrapolated regions, and state the evidence boundary directly in the visual
artifacts.
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

HHL_SOURCE_CSV = OUTPUT_DIR / "figure_phase8d_scaling_with_tail_exploratory.csv"
CLASSICAL_CSV = OUTPUT_DIR / "hhl_classical_measured_baselines.csv"
APPLES_PROJECTION_CSV = OUTPUT_DIR / "hhl_apples_to_apples_projection_to_1e6.csv"
CROSSOVER_CSV = OUTPUT_DIR / "hhl_classical_crossover_points.csv"

OUT_RESOURCE = OUTPUT_DIR / "p4_phase8d_hhl_resource_boundary_phd.png"
OUT_CLASSICAL = OUTPUT_DIR / "p4_phase8d_classical_baseline_diagnostics_phd.png"
OUT_APPLES = OUTPUT_DIR / "p4_phase8d_apples_to_apples_phd.png"
OUT_PROJECTION = OUTPUT_DIR / "p4_phase8d_projection_boundary_phd.png"
OUT_GUIDE = OUTPUT_DIR / "PHASE8D_PHD_FIGURE_GUIDE.md"
OUT_ASSESSMENT = OUTPUT_DIR / "PHASE8D_CRITICAL_ASSESSMENT.md"
OUT_IMPROVEMENT_CONTRACT = OUTPUT_DIR / "PHASE8D_IMPROVEMENT_CONTRACT.md"
OUT_JSON = OUTPUT_DIR / "phase8d_phd_figure_pack.json"

PROJECTION_MAX_N = 1_000_000

HHL_CONFIGS = [
    ("hhl_s1_fixed_m", 4),
    ("hhl_s1_fixed_m", 6),
    ("hhl_s1_fixed_m", 8),
    ("hhl_s2_fixed_m", 4),
    ("hhl_s2_fixed_m", 6),
    ("hhl_s2_fixed_m", 8),
]

ENTITY_COLORS = {
    "hhl_s1_fixed_m": "#1f66ad",
    "hhl_s2_fixed_m": "#b45a24",
}

PRECISION_MARKERS = {
    4: "o",
    6: "s",
    8: "^",
}

CLASSICAL_STYLES = {
    ("dense_direct", 100): ("#333333", "D", "dense scipy kappa=100"),
    ("dense_direct", 1000): ("#666666", "d", "dense scipy kappa=1000"),
    ("sparse_iterative", 100): ("#7e57c2", "x", "sparse CG kappa=100"),
    ("sparse_iterative", 1000): ("#d62728", "+", "sparse CG kappa=1000"),
}


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _int(value: Any) -> int | None:
    number = _float(value)
    if number is None:
        return None
    return int(number)


def _fit_power_law(points: list[tuple[float, float]]) -> dict[str, float]:
    clean = sorted((float(x), float(y)) for x, y in points if x > 0 and y > 0)
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


def _predict(fit: dict[str, float], n_value: float) -> float:
    return float(math.exp(fit["intercept"] + fit["exponent"] * math.log(n_value)))


def _hhl_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _read_csv(HHL_SOURCE_CSV):
        if row.get("family") != "hhl" or row.get("hardware_profile") != "maj_e6_floquet":
            continue
        n_value = _int(row.get("n_value"))
        precision = _int(row.get("m_precision_qubits"))
        if n_value is None or precision is None:
            continue
        rows.append({
            "entity_id": row.get("entity_id") or "",
            "n_value": n_value,
            "m_precision_qubits": precision,
            "status": row.get("status") or "",
            "runtime_seconds": _float(row.get("runtime_seconds")),
            "physical_qubits": _float(row.get("physical_qubits")),
            "t_depth": _float(row.get("t_depth")),
            "wall_clock_total_seconds": _float(row.get("wall_clock_total_seconds")),
            "reason": row.get("reason") or "",
            "exploratory_tail": str(row.get("exploratory_tail") or "").lower() == "true",
        })
    return rows


def _classical_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _read_csv(CLASSICAL_CSV):
        n_value = _int(row.get("n_value"))
        target_kappa = _int(row.get("target_kappa"))
        if n_value is None or target_kappa is None:
            continue
        rows.append({
            "benchmark_id": row.get("benchmark_id") or "",
            "algorithm_family": row.get("algorithm_family") or "",
            "solver": row.get("solver") or "",
            "matrix_model": row.get("matrix_model") or "",
            "n_value": n_value,
            "target_kappa": target_kappa,
            "achieved_kappa": _float(row.get("achieved_kappa")),
            "tolerance": _float(row.get("tolerance")),
            "status": row.get("status") or "",
            "median_total_seconds": _float(row.get("median_total_seconds")),
            "median_relative_residual": _float(row.get("median_relative_residual")),
            "median_iterations": _float(row.get("median_iterations")),
            "memory_proxy_bytes": _float(row.get("memory_proxy_bytes")),
        })
    return rows


def _label(entity_id: str, precision: int) -> str:
    step = "S1" if entity_id == "hhl_s1_fixed_m" else "S2"
    return f"HHL-{step} m={precision}"


def _style(entity_id: str, precision: int) -> tuple[str, str]:
    return ENTITY_COLORS.get(entity_id, "#555555"), PRECISION_MARKERS.get(precision, "o")


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=240, bbox_inches="tight")
    plt.close(fig)


def _plot_hhl_resource_boundary(rows: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.0, 5.4), constrained_layout=True)
    fig.suptitle("Phase 8d HHL Resource Estimates And Estimator Boundary", fontsize=13)

    ax = axes[0]
    for entity_id, precision in HHL_CONFIGS:
        selected = sorted(
            [
                row for row in rows
                if row["entity_id"] == entity_id
                and row["m_precision_qubits"] == precision
                and row["status"] == "ok"
                and row["runtime_seconds"]
            ],
            key=lambda row: row["n_value"],
        )
        if not selected:
            continue
        color, marker = _style(entity_id, precision)
        ax.loglog(
            [row["n_value"] for row in selected],
            [row["runtime_seconds"] for row in selected],
            color=color,
            marker=marker,
            ms=5.2,
            lw=1.35,
            label=_label(entity_id, precision),
        )
        tail = [row for row in selected if row["exploratory_tail"]]
        if tail:
            ax.loglog(
                [row["n_value"] for row in tail],
                [row["runtime_seconds"] for row in tail],
                linestyle="None",
                marker=marker,
                ms=8.0,
                markerfacecolor="none",
                markeredgecolor=color,
                markeredgewidth=1.5,
            )
    ax.set_title("A. Successful QDK estimates only")
    ax.set_xlabel("HHL work-register proxy size N")
    ax.set_ylabel("QDK estimated fault-tolerant runtime (s)")
    ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
    ax.legend(fontsize=7.0, ncol=2, framealpha=0.92)
    ax.text(
        0.02,
        0.03,
        "Open markers denote exploratory VM-tail successes.",
        transform=ax.transAxes,
        fontsize=7.6,
        va="bottom",
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 2.0},
    )

    ax = axes[1]
    y_positions = {config: index for index, config in enumerate(HHL_CONFIGS)}
    for row in rows:
        config = (row["entity_id"], row["m_precision_qubits"])
        if config not in y_positions:
            continue
        y_value = y_positions[config]
        if row["status"] == "ok":
            face = "none" if row["exploratory_tail"] else "#2a9d55"
            ax.scatter(
                row["n_value"],
                y_value,
                s=56 if row["exploratory_tail"] else 34,
                marker="o",
                facecolors=face,
                edgecolors="#2a9d55",
                linewidths=1.4,
                zorder=3,
            )
        else:
            ax.scatter(row["n_value"], y_value, s=62, marker="x", color="#c62828", linewidths=1.8, zorder=4)
    ax.set_xscale("log")
    ax.set_title("B. Estimator status map")
    ax.set_xlabel("HHL work-register proxy size N")
    ax.set_yticks(list(y_positions.values()))
    ax.set_yticklabels([_label(entity_id, precision) for entity_id, precision in HHL_CONFIGS])
    ax.grid(True, axis="x", which="both", ls=":", lw=0.45, alpha=0.55)
    ax.set_ylim(-0.75, len(HHL_CONFIGS) - 0.25)
    ax.invert_yaxis()
    ax.text(
        0.02,
        0.04,
        "green = successful estimate; open green = exploratory tail; red x = engine/OOM boundary",
        transform=ax.transAxes,
        fontsize=7.3,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 2.0},
    )
    _save(fig, OUT_RESOURCE)


def _plot_classical_diagnostics(rows: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 8.2), constrained_layout=True)
    fig.suptitle(
        "Classical Scaffold Diagnostics For Phase 8d HHL Context\n"
        "Synthetic SPD full-vector baselines; not semantic matches to the proxy HHL unitary",
        fontsize=12.2,
    )

    ax = axes[0, 0]
    for key, (color, marker, label) in CLASSICAL_STYLES.items():
        family, kappa = key
        selected = sorted(
            [row for row in rows if row["algorithm_family"] == family and row["target_kappa"] == kappa],
            key=lambda row: row["n_value"],
        )
        if not selected:
            continue
        ax.loglog(
            [row["n_value"] for row in selected],
            [row["median_total_seconds"] for row in selected],
            color=color,
            marker=marker,
            ms=5.0,
            lw=1.4,
            label=label,
        )
    ax.set_title("A. Measured local SciPy time")
    ax.set_xlabel("Classical scaffold matrix dimension N")
    ax.set_ylabel("Median wall-clock seconds")
    ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
    ax.legend(fontsize=7.0, framealpha=0.92)

    ax = axes[0, 1]
    for key, (color, marker, label) in CLASSICAL_STYLES.items():
        family, kappa = key
        selected = sorted(
            [row for row in rows if row["algorithm_family"] == family and row["target_kappa"] == kappa],
            key=lambda row: row["n_value"],
        )
        residual_points = [row for row in selected if row["median_relative_residual"]]
        if not residual_points:
            continue
        ax.loglog(
            [row["n_value"] for row in residual_points],
            [row["median_relative_residual"] for row in residual_points],
            color=color,
            marker=marker,
            ms=5.0,
            lw=1.2,
            label=label,
        )
    ax.axhline(1e-4, color="#111111", ls="--", lw=1.0, alpha=0.7, label="target residual 1e-4")
    ax.set_title("B. Residuals")
    ax.set_xlabel("Classical scaffold matrix dimension N")
    ax.set_ylabel("Median relative residual")
    ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
    ax.legend(fontsize=6.7, framealpha=0.92)

    ax = axes[1, 0]
    for kappa, color, marker in [(100, "#7e57c2", "x"), (1000, "#d62728", "+")]:
        selected = sorted(
            [
                row for row in rows
                if row["algorithm_family"] == "sparse_iterative"
                and row["target_kappa"] == kappa
                and row["median_iterations"]
            ],
            key=lambda row: row["n_value"],
        )
        if not selected:
            continue
        ax.semilogx(
            [row["n_value"] for row in selected],
            [row["median_iterations"] for row in selected],
            color=color,
            marker=marker,
            ms=5.2,
            lw=1.4,
            label=f"sparse CG kappa={kappa}",
        )
    ax.set_title("C. Sparse CG iterations")
    ax.set_xlabel("Classical scaffold matrix dimension N")
    ax.set_ylabel("Median iterations")
    ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
    ax.legend(fontsize=7.0, framealpha=0.92)

    ax = axes[1, 1]
    memory_specs = [("dense_direct", 100, "#333333", "D", "dense storage"), ("sparse_iterative", 100, "#7e57c2", "x", "sparse CSR")]
    for family, kappa, color, marker, label in memory_specs:
        selected = sorted(
            [row for row in rows if row["algorithm_family"] == family and row["target_kappa"] == kappa and row["memory_proxy_bytes"]],
            key=lambda row: row["n_value"],
        )
        if not selected:
            continue
        ax.loglog(
            [row["n_value"] for row in selected],
            [row["memory_proxy_bytes"] / 1_000_000.0 for row in selected],
            color=color,
            marker=marker,
            ms=5.0,
            lw=1.4,
            label=label,
        )
    ax.set_title("D. Memory proxy")
    ax.set_xlabel("Classical scaffold matrix dimension N")
    ax.set_ylabel("Memory proxy (MB)")
    ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
    ax.legend(fontsize=7.0, framealpha=0.92)

    _save(fig, OUT_CLASSICAL)


def _projection_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _read_csv(APPLES_PROJECTION_CSV):
        n_value = _float(row.get("n_value"))
        seconds = _float(row.get("projected_seconds"))
        if n_value is None or seconds is None:
            continue
        rows.append({
            "series_kind": row.get("series_kind") or "",
            "entity_id": row.get("entity_id") or "",
            "m_precision_qubits": _int(row.get("m_precision_qubits")),
            "scenario_id": row.get("scenario_id") or "",
            "classical_algorithm_family": row.get("classical_algorithm_family") or "",
            "classical_target_kappa": _int(row.get("classical_target_kappa")),
            "n_value": n_value,
            "projected_seconds": seconds,
            "source_max_success_n": _float(row.get("source_max_success_n")),
            "projection_status": row.get("projection_status") or "",
        })
    return rows


def _plot_apples_to_apples(projection_rows: list[dict[str, Any]], classical_rows: list[dict[str, Any]]) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.8), sharey=True, constrained_layout=True)
    fig.suptitle("Phase 8d Output-Contract Adjustment: HHL Proxy Versus Sparse Classical Scaffold", fontsize=13)

    scenarios = [
        ("state_preparation_only", "state preparation", "#1f66ad", "-"),
        ("single_scalar_observable_sampling", "one scalar observable", "#f28e2b", "--"),
        ("full_vector_readout_lower_bound", "full-vector readout lower bound", "#b2182b", "-."),
    ]
    measured_sparse = sorted(
        [
            row for row in classical_rows
            if row["algorithm_family"] == "sparse_iterative"
            and row["target_kappa"] == 1000
            and row["median_total_seconds"]
        ],
        key=lambda row: row["n_value"],
    )

    legend_handles = None
    legend_labels = None
    for ax, precision in zip(axes, [4, 6], strict=True):
        last_success_values = [
            row["source_max_success_n"] for row in projection_rows
            if row["series_kind"] == "hhl_projection"
            and row["m_precision_qubits"] == precision
            and row["source_max_success_n"]
        ]
        last_success = max(last_success_values) if last_success_values else None
        if last_success:
            ax.axvspan(last_success, PROJECTION_MAX_N, color="#f2d0a4", alpha=0.18, label="HHL extrapolated region")
            ax.axvline(last_success, color="#8c5a2b", ls=":", lw=1.1)
        for scenario_id, label, color, line_style in scenarios:
            selected = sorted(
                [
                    row for row in projection_rows
                    if row["series_kind"] == "hhl_projection"
                    and row["m_precision_qubits"] == precision
                    and row["scenario_id"] == scenario_id
                ],
                key=lambda row: row["n_value"],
            )
            if not selected:
                continue
            ax.loglog(
                [row["n_value"] for row in selected],
                [row["projected_seconds"] for row in selected],
                color=color,
                ls=line_style,
                lw=1.8,
                label=label,
            )
        if measured_sparse:
            ax.loglog(
                [row["n_value"] for row in measured_sparse],
                [row["median_total_seconds"] for row in measured_sparse],
                color="#555555",
                marker="x",
                ls="-",
                lw=1.55,
                ms=5.8,
                label="measured sparse CG kappa=1000",
            )
        ax.set_title(f"HHL-S1 m={precision}")
        ax.set_xlabel("HHL proxy size / classical scaffold dimension N")
        ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
        ax.text(
            0.03,
            0.03,
            "Full-vector row is a lower bound; tomography proxy omitted for legibility.",
            transform=ax.transAxes,
            fontsize=7.2,
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.82, "pad": 2.0},
        )
        if legend_handles is None:
            legend_handles, legend_labels = ax.get_legend_handles_labels()
    axes[0].set_ylabel("Seconds")
    if legend_handles and legend_labels:
        axes[0].legend(
            legend_handles,
            legend_labels,
            fontsize=7.0,
            framealpha=0.92,
            loc="upper left",
            ncol=1,
            title="Legend applies to both panels",
            title_fontsize=7.0,
        )
    _save(fig, OUT_APPLES)


def _plot_projection_boundary(hhl_rows: list[dict[str, Any]], classical_rows: list[dict[str, Any]], crossover_rows: list[dict[str, str]]) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 6.5), constrained_layout=True)
    fig.suptitle("Phase 8d Projection Boundary: Measured Evidence Versus Extrapolation", fontsize=13)

    ax.axvspan(20, 2_000, color="#d8f3dc", alpha=0.25, label="common measured support for HHL m=4/m=6")
    ax.axvspan(2_000, 10_000, color="#fff3bf", alpha=0.25, label="m=6 extrapolated, m=4 observed")
    ax.axvspan(10_000, PROJECTION_MAX_N, color="#f8d7da", alpha=0.18, label="all HHL extrapolated")

    for precision, color, marker in [(4, "#1f66ad", "o"), (6, "#b45a24", "s")]:
        series = sorted(
            [
                (row["n_value"], row["runtime_seconds"])
                for row in hhl_rows
                if row["entity_id"] == "hhl_s1_fixed_m"
                and row["m_precision_qubits"] == precision
                and row["status"] == "ok"
                and row["runtime_seconds"]
            ],
        )
        if len(series) < 2:
            continue
        fit = _fit_power_law(series)
        last_success = max(n_value for n_value, _ in series)
        grid_observed = np.logspace(math.log10(min(n for n, _ in series)), math.log10(last_success), 160)
        grid_extrapolated = np.logspace(math.log10(last_success), math.log10(PROJECTION_MAX_N), 180)
        ax.loglog([n for n, _ in series], [seconds for _, seconds in series], marker, color=color, ms=5.5, label=f"QDK HHL m={precision} observed")
        ax.loglog(grid_observed, [_predict(fit, value) for value in grid_observed], color=color, lw=1.7, label=f"QDK HHL m={precision} fit within support")
        ax.loglog(grid_extrapolated, [_predict(fit, value) for value in grid_extrapolated], color=color, ls="--", lw=1.7, label=f"QDK HHL m={precision} extrapolated")
        ax.axvline(last_success, color=color, ls=":", lw=1.0)

    sparse = sorted(
        [
            (row["n_value"], row["median_total_seconds"])
            for row in classical_rows
            if row["algorithm_family"] == "sparse_iterative"
            and row["target_kappa"] == 1000
            and row["median_total_seconds"]
        ],
    )
    if len(sparse) >= 2:
        last_classical = max(n for n, _ in sparse)
        ax.loglog(
            [n for n, _ in sparse],
            [seconds for _, seconds in sparse],
            color="#d62728",
            marker="+",
            ms=6.0,
            lw=1.35,
            label="measured sparse CG kappa=1000",
        )
        if last_classical < PROJECTION_MAX_N:
            ax.axvline(last_classical, color="#d62728", ls=":", lw=1.0)

    observed_crossovers = sum(1 for row in crossover_rows if row.get("observed_crossover_n") not in (None, ""))
    ax.text(
        0.02,
        0.96,
        f"Observed crossovers in common measured grid: {observed_crossovers}\n"
        "Dashed HHL segments are extrapolations, not advantage evidence.\n"
        "HHL N is proxy size; classical N is scaffold dimension.",
        transform=ax.transAxes,
        fontsize=8.1,
        va="top",
        bbox={"facecolor": "white", "edgecolor": "#888888", "alpha": 0.9, "pad": 4.0},
    )
    ax.set_xlim(20, PROJECTION_MAX_N)
    ax.set_xlabel("HHL proxy size / classical scaffold dimension N")
    ax.set_ylabel("Seconds")
    ax.grid(True, which="both", ls=":", lw=0.45, alpha=0.55)
    ax.legend(
        fontsize=6.6,
        framealpha=0.94,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.12),
        ncol=3,
    )
    _save(fig, OUT_PROJECTION)


def _write_guide(generated_utc: str) -> None:
    rel = lambda path: path.relative_to(ROOT).as_posix()
    text = f"""# Phase 8d PhD Figure Guide

Generated UTC: `{generated_utc}`

This guide separates manuscript-safe appendix figures from exploratory working
plots. The figures below do not turn Phase 8d into headline H1-H4 evidence; they
are appendix material for resource-estimation and comparison-contract discussion.

## Recommended Figure Pack

| Figure | Recommended use | Main claim it can support |
| --- | --- | --- |
| `{rel(OUT_RESOURCE)}` | Main Phase 8d appendix figure | QDK HHL proxy resource estimates and estimator/failure boundary, without classical timing overlay. |
| `{rel(OUT_CLASSICAL)}` | Classical-baseline appendix diagnostic | The SciPy scaffold baselines are measured full-vector classical solves with residual, iteration, and memory diagnostics. |
| `{rel(OUT_APPLES)}` | Fair-comparison appendix figure | HHL state preparation, scalar-observable sampling, and full-vector readout are different output contracts. |
| `{rel(OUT_PROJECTION)}` | Projection-boundary appendix figure | There are zero observed crossovers in the common measured grid; extrapolated regions are visibly separated. |

## Context-Only Or Exploratory Figures

The superseded figures below have been moved to
`archive_superseded_20260428/` for auditability. They should not be cited from
the top-level Phase 8d output directory.

| Figure | Status | Reason |
| --- | --- | --- |
| `archive_superseded_20260428/p4_hhl_classical_context.png` | Context only | Useful overview, but it combines resource estimates and classical model curves in one artifact. |
| `archive_superseded_20260428/p4_hhl_classical_scaling_index.png` | Context only | Normalized scaling is intuitive but not an absolute evidence figure. |
| `archive_superseded_20260428/p4_hhl_classical_measured_time.png` | Context only | It overlays QDK estimator seconds and local SciPy wall-clock seconds. |
| `archive_superseded_20260428/p4_hhl_classical_crossover_projection.png` | Superseded by `{rel(OUT_PROJECTION)}` | The new projection-boundary figure labels measured and extrapolated regions more explicitly. |
| `archive_superseded_20260428/p4_hhl_apples_to_apples_adjusted_time.png` | Superseded by `{rel(OUT_APPLES)}` | The new figure omits the tomography proxy from the main legend for legibility. |
| `archive_superseded_20260428/p4_hoefler_crossover_working_hhl_tail.png` | Exploratory only | It is a Hoefler-style sketch and should not be cited as Phase 8d evidence of speedup or advantage. |

## Review Artifact

`{rel(OUT_ASSESSMENT)}` records the professor-style critical assessment of what
Phase 8d can and cannot claim.

## Improvement Contract

`{rel(OUT_IMPROVEMENT_CONTRACT)}` records the allowed/forbidden claim table,
tolerance bridge, finance-semantic pilot plan, and preconditioning guidance for
the next claim-ready upgrade.

## Caption Rules

- Say `HHL proxy work-register size N`, not finance matrix dimension.
- Say QDK values are fault-tolerant resource-estimator seconds, not measured
  hardware wall-clock.
- Say classical rows are synthetic SPD scaffold baselines with full-vector output.
- State that no measured quantum/classical crossover is observed.
- Treat all fitted curves beyond the marked support region as extrapolations.
"""
    OUT_GUIDE.write_text(text, encoding="utf-8")


def make_figures() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generated_utc = datetime.now(timezone.utc).isoformat()
    hhl_rows = _hhl_rows()
    classical_rows = _classical_rows()
    projection_rows = _projection_rows()
    crossover_rows = _read_csv(CROSSOVER_CSV)

    _plot_hhl_resource_boundary(hhl_rows)
    _plot_classical_diagnostics(classical_rows)
    _plot_apples_to_apples(projection_rows, classical_rows)
    _plot_projection_boundary(hhl_rows, classical_rows, crossover_rows)
    _write_guide(generated_utc)

    payload = {
        "schema": "phase8d_phd_figure_pack.1.0",
        "generated_utc": generated_utc,
        "purpose": "PhD-safe appendix figure pack for Phase 8d HHL/QAE proxy comparison discipline.",
        "source_files": {
            "hhl_scaling_csv": HHL_SOURCE_CSV.relative_to(ROOT).as_posix(),
            "classical_measured_csv": CLASSICAL_CSV.relative_to(ROOT).as_posix(),
            "apples_projection_csv": APPLES_PROJECTION_CSV.relative_to(ROOT).as_posix(),
            "crossover_csv": CROSSOVER_CSV.relative_to(ROOT).as_posix(),
        },
        "outputs": {
            "resource_boundary_png": OUT_RESOURCE.relative_to(ROOT).as_posix(),
            "classical_diagnostics_png": OUT_CLASSICAL.relative_to(ROOT).as_posix(),
            "apples_to_apples_png": OUT_APPLES.relative_to(ROOT).as_posix(),
            "projection_boundary_png": OUT_PROJECTION.relative_to(ROOT).as_posix(),
            "figure_guide_md": OUT_GUIDE.relative_to(ROOT).as_posix(),
            "critical_assessment_md": OUT_ASSESSMENT.relative_to(ROOT).as_posix(),
            "improvement_contract_md": OUT_IMPROVEMENT_CONTRACT.relative_to(ROOT).as_posix(),
        },
        "guardrails": [
            "No figure in this pack claims quantum advantage.",
            "HHL N is a proxy work-register size, not a finance matrix dimension.",
            "Classical N is a scaffold matrix dimension for synthetic SPD systems.",
            "QDK runtime seconds and local SciPy wall-clock seconds are separated or explicitly marked.",
            "Projection regions are visually distinguished from measured support.",
        ],
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = make_figures()
    print(json.dumps(payload["outputs"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())