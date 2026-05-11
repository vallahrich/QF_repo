"""Optional Phase 10 H1-H4 figure renderer.

Rendered figures are excluded from the P4 handoff because final figure files
live in the thesis and appendix. The canonical package keeps figure source CSVs
under ``canonical/outputs/manuscript_artifacts``.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
OUTPUTS = CANON / "outputs"
FIG_DIR = OUTPUTS / "figures"
DOC_FIG_DIR = ROOT / "docs" / "figures"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
STATS = REPORTS / "stats_report.json"
ORACLE = REPORTS / "oracle_tax_table.json"
EVIDENCE = REPORTS / "evidence_report.json"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = ["1e-03", "1e-04", "1e-06"]


def _read(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"required input missing: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _save(fig, name: str) -> dict:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    DOC_FIG_DIR.mkdir(parents=True, exist_ok=True)
    out_can = FIG_DIR / name
    out_doc = DOC_FIG_DIR / name
    fig.savefig(out_can, dpi=160, bbox_inches="tight")
    fig.savefig(out_doc, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return {
        "canonical": str(out_can.relative_to(ROOT)).replace("\\", "/"),
        "docs": str(out_doc.relative_to(ROOT)).replace("\\", "/"),
    }


def _fig_h1(stats: dict) -> dict:
    h1 = stats.get("H1") or {}
    xs: list[str] = []
    ys: list[float] = []
    for profile in PROFILES:
        for eps in EPSILONS:
            cell = ((h1.get(f"{profile}|{eps}") or {}).get("runtime_seconds") or {})
            median = cell.get("median_tau")
            if isinstance(median, (int, float)) and median > 0:
                xs.append(f"{profile}\n{eps}")
                ys.append(math.log10(median))
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.bar(range(len(xs)), ys, color="#4069a8")
    ax.axhline(1.0, color="#b23b3b", linestyle="--", linewidth=1.2, label="tau=10")
    ax.set_xticks(range(len(xs)))
    ax.set_xticklabels(xs, rotation=75, ha="right", fontsize=7)
    ax.set_ylabel("log10 median tau_runtime")
    ax.set_title("H1 oracle-tax medians by hardware profile and epsilon")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    ax.legend(loc="upper right")
    return _save(fig, "fig_h1_oracle_tax.png")


def _fig_h2(cohort: dict, oracle: dict) -> dict:
    table = oracle.get("table_faithful") or {}
    cell = "maj_e6_floquet|1e-04"
    grouped: dict[str, list[float]] = {}
    for label, by_cell in table.items():
        tau = (by_cell.get(cell) or {}).get("runtime_seconds")
        if isinstance(tau, (int, float)) and tau > 0:
            silo = (cohort["labels"].get(label) or {}).get("silo", "unknown")
            grouped.setdefault(silo, []).append(math.log10(tau))
    labels = sorted(grouped)
    fig, ax = plt.subplots(figsize=(10, 4.8))
    if labels:
        ax.boxplot([grouped[label] for label in labels], labels=labels, vert=True)
    ax.axhline(1.0, color="#b23b3b", linestyle="--", linewidth=1.2)
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("log10 tau_runtime")
    ax.set_title("H2 silo separation at H4 anchor cell")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    return _save(fig, "fig_h2_silo_anchor.png")


def _fig_h3(oracle: dict) -> dict:
    table = oracle.get("table_faithful") or {}
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    for profile in PROFILES:
        vals = []
        for by_cell in table.values():
            tau = (by_cell.get(f"{profile}|1e-04") or {}).get("runtime_seconds")
            if isinstance(tau, (int, float)) and tau > 0:
                vals.append(math.log10(tau))
        vals.sort()
        if vals:
            ys = [(index + 1) / len(vals) for index in range(len(vals))]
            ax.step(vals, ys, where="post", label=profile)
    ax.axvline(1.0, color="#b23b3b", linestyle="--", linewidth=1.2)
    ax.set_xlabel("log10 tau_runtime")
    ax.set_ylabel("ECDF")
    ax.set_title("H3 runtime oracle-tax ECDF across hardware profiles")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(fontsize=7)
    return _save(fig, "fig_h3_runtime_ecdf.png")


def _fig_h4(stats: dict) -> dict:
    rows = (((stats.get("H4") or {}).get("per_criterion_breakdown") or {}).get("per_label") or {})
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for label, payload in rows.items():
        metrics = payload.get("metrics") or {}
        tau = metrics.get("tau_runtime")
        t_count = metrics.get("full_t_count")
        passes = bool(payload.get("passes_all"))
        if isinstance(tau, (int, float)) and tau > 0 and isinstance(t_count, (int, float)):
            color = "#2b8a3e" if passes else "#6b7280"
            y_value = max(float(t_count), 0.0)
            ax.scatter(math.log10(tau), y_value, color=color, s=48)
            ax.annotate(label, (math.log10(tau), y_value), fontsize=7, xytext=(3, 3), textcoords="offset points")
    ax.axvline(1.0, color="#b23b3b", linestyle="--", linewidth=1.2, label="tau=10")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_xlabel("log10 tau_runtime")
    ax.set_ylabel("full T-count")
    ax.set_title("H4 bifurcation: small tau vs non-trivial oracle")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.legend(loc="upper right")
    return _save(fig, "fig_h4_bifurcation_scatter.png")


def _fig_h1_heatmap(evidence: dict) -> dict:
    rows = [
        row for row in ((evidence.get("H1") or {}).get("rows") or [])
        if row.get("axis") == "runtime_seconds"
    ]
    # Use the canonical "<profile>|<eps>" cell key to avoid float-vs-string
    # mismatches between EPSILONS (strings) and row["epsilon"] (JSON floats).
    value_by_cell = {row.get("cell"): row.get("median_log10_tau") for row in rows}
    matrix = [
        [value_by_cell.get(f"{profile}|{eps}") for eps in EPSILONS]
        for profile in PROFILES
    ]
    numeric = [[float(v) if isinstance(v, (int, float)) else float("nan") for v in line] for line in matrix]
    fig, ax = plt.subplots(figsize=(7.2, 5.2))
    image = ax.imshow(numeric, cmap="viridis", aspect="auto")
    ax.set_xticks(range(len(EPSILONS)))
    ax.set_xticklabels(EPSILONS)
    ax.set_yticks(range(len(PROFILES)))
    ax.set_yticklabels(PROFILES, fontsize=8)
    ax.set_xlabel("epsilon")
    ax.set_title("H1 runtime median log10 oracle tax")
    for y, profile in enumerate(PROFILES):
        for x, eps in enumerate(EPSILONS):
            value = value_by_cell.get(f"{profile}|{eps}")
            if isinstance(value, (int, float)):
                ax.text(x, y, f"{value:.2f}", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(image, ax=ax, label="median log10 tau_runtime")
    return _save(fig, "fig_h1_oracle_tax_heatmap.png")


def _fig_h4_criteria_heatmap(evidence: dict) -> dict:
    rows = (evidence.get("H4") or {}).get("rows") or []
    if not rows:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.text(0.5, 0.5, "No H4 rows", ha="center", va="center")
        ax.axis("off")
        return _save(fig, "fig_h4_criteria_heatmap.png")
    criteria = list((rows[0].get("criteria") or {}).keys())
    labels = [row.get("label") for row in rows]
    matrix = [[1 if (row.get("criteria") or {}).get(c) else 0 for c in criteria] for row in rows]
    fig, ax = plt.subplots(figsize=(8.0, 6.0))
    image = ax.imshow(matrix, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(criteria)))
    ax.set_xticklabels(criteria, rotation=45, ha="right", fontsize=7)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=7)
    ax.set_title("H4 strict-criterion pass/fail heatmap")
    fig.colorbar(image, ax=ax, ticks=[0, 1], label="criterion passed")
    return _save(fig, "fig_h4_criteria_heatmap.png")


def _fig_h4_funnel(evidence: dict) -> dict:
    funnel = (evidence.get("H4") or {}).get("criteria_funnel") or []
    criteria = [row.get("criterion") for row in funnel]
    counts = [row.get("n_remaining") or 0 for row in funnel]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.bar(range(len(criteria)), counts, color="#4f7c65")
    ax.set_xticks(range(len(criteria)))
    ax.set_xticklabels(criteria, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Faithful labels remaining")
    ax.set_title("H4 strict-advantage criterion funnel")
    ax.grid(axis="y", linestyle=":", alpha=0.4)
    for index, count in enumerate(counts):
        ax.text(index, count + 0.15, str(count), ha="center", va="bottom", fontsize=9)
    return _save(fig, "fig_h4_funnel.png")


def make_figures() -> dict:
    cohort = _read(COHORT)
    stats = _read(STATS)
    oracle = _read(ORACLE)
    evidence = _read(EVIDENCE)
    outputs = {
        "fig_h1_oracle_tax.png": _fig_h1(stats),
        "fig_h1_oracle_tax_heatmap.png": _fig_h1_heatmap(evidence),
        "fig_h2_silo_anchor.png": _fig_h2(cohort, oracle),
        "fig_h3_runtime_ecdf.png": _fig_h3(oracle),
        "fig_h4_bifurcation_scatter.png": _fig_h4(stats),
        "fig_h4_criteria_heatmap.png": _fig_h4_criteria_heatmap(evidence),
        "fig_h4_funnel.png": _fig_h4_funnel(evidence),
    }
    sidecar = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_inputs": [
            str(STATS.relative_to(ROOT)).replace("\\", "/"),
            str(ORACLE.relative_to(ROOT)).replace("\\", "/"),
            str(COHORT.relative_to(ROOT)).replace("\\", "/"),
            str(EVIDENCE.relative_to(ROOT)).replace("\\", "/"),
        ],
        "outputs": outputs,
    }
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    (FIG_DIR / "h_figures_sidecar.json").write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    print(f"[h-figures] wrote {len(outputs)} H figures -> {FIG_DIR.relative_to(ROOT)}")
    return sidecar


def main() -> int:
    make_figures()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())