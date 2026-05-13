"""Generate Chapter 7 reader-clarity tables/figures (T4, F1).

Reads from p4_experiments/canonical/outputs/manuscript_artifacts and writes:
  - manuscript_artifacts/table_h4_per_criterion.tex  (T4)
  - canonical/outputs/figures/fig_h4_regimes_scatter.{png,pdf}  (F1)

T2 reuses the existing table_h4_tcost_bifurcation.tex; this script does not
regenerate it.

Visual policy: routed through ``shared.style.figure_style`` (audit
2026-05-12, R-3).
"""
from __future__ import annotations

import sys
from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "p4_experiments/canonical/outputs/manuscript_artifacts"
FIG_DIR = ROOT / "p4_experiments/canonical/outputs/figures"

# Shared visual policy facade (audit Module 6, R-3 migration).
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.style.figure_style import (  # noqa: E402  -- after Agg backend
    ACCENT_NEUTRAL,
    ACCENT_PRIMARY,
    ACCENT_SECONDARY,
    ACCENT_WARN,
    apply_house_style,
    display_epsilon,
    display_profile,
    figure_size,
    place_legend,
    save_figure,
    style_axes,
    validate_no_raw_identifiers,
    validate_pdf_png_pair,
)

apply_house_style()

CRITERIA = [
    ("C1_tau_runtime_lt_10", r"$C_1$"),
    ("C2_full_runtime_lt_baseline", r"$C_2$"),
    ("C3_full_t_count_gt_0", r"$C_3$"),
    ("C4_tau_tdepth_ge_10", r"$C_4$"),
    ("C5_baseline_ge_0_01s", r"$C_5$"),
]


def write_t4() -> None:
    """Per-criterion C1-C5 attribution for the 13 H4 family-template candidates."""
    df = pd.read_csv(ART / "figure_h4_criterion_heatmap.csv")
    audit = pd.read_csv(ART / "h4_anchor_tcost_label_audit.csv")

    # H4-eligible (family-template) labels only, sorted with SD3 last so the
    # Regime 2 case visually concludes the table.
    elig = audit.loc[audit["h4_eligible"] == True, ["label", "t_count_regime", "runtime_tau"]]
    elig["regime_label"] = elig["t_count_regime"].map(
        {"zero_logical_t_count": "1", "nonzero_logical_t_count": "2"}
    )
    # Order: Regime 1 (alphabetical), then Regime 2 labels (SD3 only).
    r1 = sorted(elig.loc[elig["regime_label"] == "1", "label"].tolist())
    r2 = sorted(elig.loc[elig["regime_label"] == "2", "label"].tolist())
    label_order = r1 + r2
    assert len(label_order) == 13, f"expected 13 H4 candidates, got {len(label_order)}"

    pivot = df.pivot_table(
        index="label", columns="criterion", values="passed", aggfunc="first"
    )
    pivot = pivot.loc[label_order, [c for c, _ in CRITERIA]]

    regime_of = elig.set_index("label")["regime_label"].to_dict()
    tau_of = elig.set_index("label")["runtime_tau"].to_dict()

    def cell(v: int) -> str:
        return r"\checkmark" if int(v) == 1 else r"$\times$"

    lines: list[str] = []
    lines.append(r"\begin{tabular}{@{}llrccccc l@{}}")
    lines.append(r"\toprule")
    lines.append(
        r"\textbf{Label} & \textbf{Regime} & \textbf{Runtime $\tau$} & "
        + " & ".join(h for _, h in CRITERIA)
        + r" & \textbf{Outcome} \\"
    )
    lines.append(r"\midrule")
    for lbl in label_order:
        row = pivot.loc[lbl]
        regime = regime_of[lbl]
        tau = tau_of[lbl]
        cells = " & ".join(cell(row[c]) for c, _ in CRITERIA)
        outcome = r"$\times$ fail"  # all 13 fail; explicit
        lines.append(
            f"\\artifact{{{lbl}}} & {regime} & {tau:.2f} & {cells} & {outcome} \\\\"
        )
    # Totals row: passes per criterion
    totals = (pivot.sum(axis=0)).astype(int)
    totals_cells = " & ".join(f"{int(totals[c])}/13" for c, _ in CRITERIA)
    lines.append(r"\midrule")
    lines.append(
        r"\multicolumn{3}{@{}l}{\textbf{Passes per criterion}} & "
        + totals_cells
        + r" & 0/13 winners \\"
    )
    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    out = ART / "table_h4_per_criterion.tex"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out.relative_to(ROOT)}")


def write_f1() -> None:
    """Regime scatter: full T-count (log) vs runtime tau (log) at H4 anchor."""
    audit = pd.read_csv(ART / "h4_anchor_tcost_label_audit.csv")
    # Only success/success records in the active anchor population.
    df = audit.loc[
        (audit["bare_status"] == "success") & (audit["full_status"] == "success")
    ].copy()

    # x-axis: full T-count; map zero T-count to a left "zero band" pseudo-x for plotting on log scale.
    zero_x = 0.5  # placeholder x for the zero-T band (log-scale-safe)
    df["x_plot"] = df["full_t_count"].apply(lambda v: zero_x if v == 0 else v)
    df["zero_t"] = df["full_t_count"] == 0

    fig, ax = plt.subplots(figsize=figure_size("scatter"))

    elig = df["h4_eligible"] == True
    # Background: non-H4-eligible labels (faint).
    ax.scatter(
        df.loc[~elig, "x_plot"],
        df.loc[~elig, "runtime_tau"],
        s=22,
        c=ACCENT_NEUTRAL,
        alpha=0.7,
        marker="o",
        label="Active grid (non-candidate)",
        zorder=1,
    )
    # H4 candidates highlighted.
    ax.scatter(
        df.loc[elig, "x_plot"],
        df.loc[elig, "runtime_tau"],
        s=55,
        c=ACCENT_PRIMARY,
        marker="o",
        edgecolor="black",
        linewidth=0.6,
        label="H4 family-template candidate",
        zorder=3,
    )

    # Label SD3 specifically.
    sd3 = df.loc[df["label"] == "SD3"]
    if not sd3.empty:
        x = float(sd3["x_plot"].iloc[0])
        y = float(sd3["runtime_tau"].iloc[0])
        ax.annotate(
            "SD3",
            xy=(x, y),
            xytext=(8, 6),
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
        )

    # House style: log scales, dotted grid, threshold line at tau=10.
    style_axes(ax, log_x=True, log_y=True, threshold=10.0,
               threshold_axis="y", threshold_label=r"$\tau=10$")

    # Mark the "zero-T band" on the x-axis.
    ax.axvspan(0.3, 0.8, color="#f0f0f0", zorder=0)
    ax.text(
        0.5,
        1000,
        "zero $T$",
        ha="center",
        va="top",
        fontsize=9,
        color=ACCENT_NEUTRAL,
    )

    # H4 winner quadrant: nonzero-T AND tau below ~10. Shade lightly with
    # the green ACCENT_SECONDARY at low alpha to match the audit template
    # for log-scale scatter (template 5.3).
    ax.axhspan(1.0, 10.0, xmin=0.5, xmax=1.0,
               color=ACCENT_SECONDARY, alpha=0.15, zorder=0)
    ax.text(
        100,
        3.0,
        "H4 winning region\n(empty)",
        ha="center",
        va="center",
        fontsize=9,
        color=ACCENT_SECONDARY,
        style="italic",
    )

    # x-axis label uses display_profile so the anchor cell does not leak
    # the raw 'maj_e6_floquet' identifier into reader-visible text (V-10).
    ax.set_xlabel(
        r"Full-circuit logical $T$-count (anchor: "
        + display_profile("maj_e6_floquet")
        + r", $\varepsilon=$" + display_epsilon("1e-04") + r")"
    )
    ax.set_ylabel(r"Runtime oracle tax $\tau$")
    # House style: empty title; LaTeX caption carries the description.
    place_legend(ax, location="inside_upper_right")

    fig.tight_layout()
    out_png = FIG_DIR / "fig_h4_regimes_scatter.png"
    written = save_figure(fig, [out_png])
    plt.close(fig)

    # V-10 + V-08 acceptance gates (audit Module 12).
    offenders = validate_no_raw_identifiers(fig)
    if offenders:
        raise RuntimeError(
            f"fig_h4_regimes_scatter: raw snake_case in reader-visible text: {offenders}"
        )
    if not validate_pdf_png_pair(out_png):
        raise RuntimeError(
            f"fig_h4_regimes_scatter: missing PNG/PDF sibling at {out_png}"
        )
    for path in written:
        print(f"wrote {Path(path).relative_to(ROOT)}")


if __name__ == "__main__":
    write_t4()
    write_f1()
