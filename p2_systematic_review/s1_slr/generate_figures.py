"""Generate SLR figures for 04_figures/ (Step 1: search & screening).

Visual style is sourced from the shared ``shared.style.figure_style``
facade (see ``docs/figures-tables-visual-policy.md`` rule V-08, V-09).
This avoids drift between the Phase 2 SLR figures and the Phase 4
canonical pipeline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

REPO = Path(__file__).resolve().parent
ROOT = REPO.parents[1]

# Make the repo root importable so we can pull in ``shared.style``.
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.style.figure_style import (  # noqa: E402
    FLOW_ARROW_MSCALE,
    FLOW_ARROW_STYLE,
    FLOW_BOXSTYLE,
    FLOW_LW_ARROW,
    FLOW_LW_BOX,
    FLOW_LW_OUTER,
    LAYER_BLUE,
    LAYER_CORAL,
    LAYER_GRAY,
    LINE_GRAY,
    PALETTE,
    TEXT_MUTED,
    apply_house_style,
)

FIGURES = REPO / "04_figures"
FIGURES.mkdir(exist_ok=True)
MANUSCRIPT_FIGURES = ROOT / "manuscript" / "05_Figures"
MANUSCRIPT_FIGURES.mkdir(exist_ok=True)
SCREENING = REPO / "03_screening"

# Apply the canonical Palette A + serif rcParams used by Phase 4 figures.
apply_house_style()


def _load_asreview() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "asreview_dataset.csv", dtype=str).fillna("")


def _load_ai_screening() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "ai_screening_decisions.csv", dtype=str).fillna("")


def _load_ta_decisions() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "title_abstract_decisions.csv", dtype=str).fillna("")


def _load_ft_decisions() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "full_text_decisions.csv", dtype=str).fillna("")


def _save_figure(fig: plt.Figure, stem: str, *, include_manuscript: bool = False) -> None:
    for output_dir in ([FIGURES, MANUSCRIPT_FIGURES] if include_manuscript else [FIGURES]):
        fig.savefig(output_dir / f"{stem}.png")
        fig.savefig(output_dir / f"{stem}.pdf")


# ── Figure 1: PRISMA flow diagram ─────────────────────────────────────────
def fig_prisma_flow():
    """Generate a PRISMA 2020 flow diagram (thesis-quality)."""
    import os

    ai = _load_ai_screening()
    n_screened = len(ai)

    # Full-text decisions (updated with EX-NOTEN)
    ft = _load_ft_decisions()
    n_assessed_ft = len(ft)
    n_excluded_ft = int((ft["final_decision"].str.strip().str.lower() == "exclude").sum())
    n_included_ft = int((ft["final_decision"].str.strip().str.lower() == "include").sum())

    # Full-text exclusion reason breakdown
    ft_exc = ft[ft["final_decision"].str.strip().str.lower() == "exclude"]
    ft_reasons = ft_exc["exclusion_reason"].value_counts().to_dict() if n_excluded_ft > 0 else {}

    n_excluded_ta = n_screened - n_assessed_ft

    # Hardcoded identification numbers (from original search logs)
    n_identified = 6232
    n_duplicates = 3222

    # Layout constants - audit P0 v2: canvas tightened from 11x11.5 to
    # 11x8.5 so phase bands hug their content with consistent ~0.4-unit
    # vertical padding above and below each box.
    fig_w, fig_h = 11, 8.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    # Audit P0 v2: ylim tightened to the actual content range so the
    # tight-bbox saved PDF/PNG does not carry a tall empty footer.
    ax.set_ylim(0.0, 8.7)
    ax.axis("off")

    cx = 4.2            # centre of main flow boxes
    rx = 8.5            # centre of right-side exclusion boxes
    bw_main = 3.2       # main box width
    bw_excl = 3.0       # exclusion box width
    bh = 0.85           # main-column box height
    bh_excl = 0.95      # right-column exclusion box height (ft has 3 lines)
    sidebar_w = 1.3     # phase sidebar width
    pad = 0.40          # vertical padding inside each phase band

    # Box y-centres (top to bottom). Identification has the main + the
    # duplicates junction; Eligibility has the main + the ft-exclusions.
    y_ident = 7.8
    y_junct_band = 6.95   # duplicates junction y-band
    y_screen = 5.65
    y_excl_ta = 5.65
    y_assess = 3.65
    y_excl_ft = 3.65
    y_incl = 1.55

    # Phase y-bands (each = box top/bottom +/- pad).
    y_id_top = y_ident + bh / 2 + pad
    y_id_bot = y_junct_band - 0.65 / 2 - pad
    y_sc_top = y_screen + bh / 2 + pad
    y_sc_bot = y_screen - bh / 2 - pad
    y_el_top = y_assess + bh / 2 + pad
    y_el_bot = y_assess - bh_excl / 2 - pad
    y_in_top = y_incl + bh / 2 + pad
    y_in_bot = y_incl - bh / 2 - pad

    # Colours: Palette B (audit 2026-05-12 design-system unification) — same
    # vocabulary as the Phase 2 corpus workflow and the Ch4 pipeline TikZ.
    c_sidebar = LAYER_GRAY
    c_sidebar_text = TEXT_MUTED
    c_box_fill = LAYER_BLUE          # process / human step
    c_box_edge = LINE_GRAY
    c_excl_fill = LAYER_GRAY         # excluded
    c_excl_edge = LINE_GRAY
    c_incl_fill = LAYER_CORAL        # final / active outcome
    c_incl_edge = LINE_GRAY
    c_arrow = LINE_GRAY
    lw_box = FLOW_LW_BOX
    lw_arrow = FLOW_LW_ARROW
    fs_box = 9.5
    fs_phase = 11

    # Helpers — note: PRISMA uses small data-unit boxes (height ≈ 0.85 in an
    # 11.5-unit canvas), so we use a tighter ``rounding_size`` than the
    # ``FLOW_BOXSTYLE`` token (which is calibrated for the 100-unit
    # process-board canvas). Stroke/edge/arrow tokens still come from the
    # shared facade, keeping visual unification with the workflow figure.
    _prisma_boxstyle = "round,pad=0.08,rounding_size=0.30"

    def _box(x, y, w, h, text, fill, edge, lw=lw_box, fontsize=fs_box,
             fontweight="normal"):
        rect = mpatches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle=_prisma_boxstyle,
            facecolor=fill, edgecolor=edge, linewidth=lw,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
                fontweight=fontweight, linespacing=1.35)

    def _arrow_down(x, y_from, y_to):
        ax.annotate("", xy=(x, y_to), xytext=(x, y_from),
                    arrowprops=dict(arrowstyle=FLOW_ARROW_STYLE, color=c_arrow,
                                    lw=lw_arrow, mutation_scale=FLOW_ARROW_MSCALE))

    def _arrow_right(x_from, x_to, y):
        ax.annotate("", xy=(x_to, y), xytext=(x_from, y),
                    arrowprops=dict(arrowstyle=FLOW_ARROW_STYLE, color=c_arrow,
                                    lw=lw_arrow, mutation_scale=FLOW_ARROW_MSCALE))

    # Phase sidebar bands
    for top, bot, label in [
        (y_id_top, y_id_bot, "Identification"),
        (y_sc_top, y_sc_bot, "Screening"),
        (y_el_top, y_el_bot, "Eligibility"),
        (y_in_top, y_in_bot, "Included"),
    ]:
        rect = mpatches.FancyBboxPatch(
            (0.15, bot), sidebar_w, top - bot,
            boxstyle=_prisma_boxstyle,
            facecolor="none", edgecolor=LINE_GRAY, linewidth=FLOW_LW_BOX,
        )
        ax.add_patch(rect)
        ax.text(0.15 + sidebar_w / 2, (top + bot) / 2, label,
                ha="center", va="center", fontsize=fs_phase,
                fontweight="bold", color=c_sidebar_text, rotation=90)

    # Identification - Audit P0-2: uniform main-column box height.
    _box(cx, y_ident, bw_main, bh,
         f"Records identified through database searching\n(n = {n_identified:,})",
         c_box_fill, c_box_edge)

    # Duplicates removed at the junction between identification and screening.
    y_junct = y_ident - bh / 2 - 0.45
    _box(rx, y_junct, bw_excl, 0.65,
         f"Duplicates removed\n(n = {n_duplicates:,})",
         c_excl_fill, c_excl_edge)

    # Vertical line from identification to screening.
    ax.plot([cx, cx], [y_ident - bh / 2, y_junct], color=c_arrow,
            lw=lw_arrow, solid_capstyle="butt")
    _arrow_right(cx, rx - bw_excl / 2, y_junct)
    _arrow_down(cx, y_junct, y_screen + bh / 2)

    # Screening
    _box(cx, y_screen, bw_main, bh,
         f"Records screened\n(title/abstract)\n(n = {n_screened:,})",
         c_box_fill, c_box_edge)

    _box(rx, y_excl_ta, bw_excl, 0.65,
         f"Records excluded\n(n = {n_excluded_ta:,})",
         c_excl_fill, c_excl_edge)

    _arrow_down(cx, y_screen - bh / 2, y_assess + bh / 2)
    _arrow_right(cx + bw_main / 2, rx - bw_excl / 2, y_excl_ta)

        # Eligibility
    _box(cx, y_assess, bw_main, bh,
            f"Full-text records assessed\nfor eligibility\n(n = {n_assessed_ft:,})",
         c_box_fill, c_box_edge)

    if n_excluded_ft > 0:
        reason_labels = {
            "EX-NOTEN": "Non-English",
            "EX-NOACCESS": "Full text not retrieved",
        }
        reason_parts = [f"Full-text records excluded\n(n = {n_excluded_ft})"]
        for reason, count in sorted(ft_reasons.items(), key=lambda x: -x[1]):
            label = reason_labels.get(reason, reason)
            reason_parts.append(f"{label}: {count}")
        excl_text = "\n".join(reason_parts)
        excl_h = 0.65 + 0.22 * len(ft_reasons)
        _box(rx, y_excl_ft, bw_excl, excl_h,
             excl_text,
             c_excl_fill, c_excl_edge, fontsize=8.5)
        _arrow_right(cx + bw_main / 2, rx - bw_excl / 2, y_excl_ft)

    _arrow_down(cx, y_assess - bh / 2, y_incl + bh / 2)

    # Included
    _box(cx, y_incl, bw_main, bh,
         f"Processed Phase 2 corpus\n(n = {n_included_ft:,})",
         c_incl_fill, c_incl_edge, lw=FLOW_LW_OUTER, fontweight="bold")

    _save_figure(fig, "fig1_prisma_flow", include_manuscript=True)
    plt.close(fig)
    print("  fig1_prisma_flow")


# ── Figure 2: Publication year distribution ───────────────────────────────
def fig_year_distribution():
    """Bar chart of publications by year."""
    asr = _load_asreview()
    asr["year_int"] = pd.to_numeric(asr["year"], errors="coerce")
    asr = asr.dropna(subset=["year_int"])
    asr["year_int"] = asr["year_int"].astype(int)

    # Focus on 2016+ (SLR scope)
    recent = asr[asr["year_int"] >= 2016]
    year_counts = recent["year_int"].value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(year_counts.index, year_counts.values, color="#2171b5", edgecolor="white", width=0.8)

    # Add count labels
    for bar, count in zip(bars, year_counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
                str(count), ha="center", va="bottom", fontsize=9)

    ax.set_xlabel("Publication year")
    ax.set_ylabel("Records")
    ax.set_xticks(year_counts.index)
    ax.set_ylim(0, max(year_counts.values) * 1.12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    _save_figure(fig, "fig2_year_distribution", include_manuscript=True)
    plt.close(fig)
    print("  fig2_year_distribution")


# ── Figure 3: Source database contribution ────────────────────────────────
def fig_source_distribution():
    """Horizontal bar chart of records by source database."""
    # Source counts from original search logs. master_records.csv
    # was in a previous branch structure; these values match the search logs)
    sources = {"Openalex": 2843, "Semantic Scholar": 1554, "Scopus": 1127, "Arxiv": 708}

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#2171b5", "#6baed6", "#bdd7e7", "#d4e4f3"]
    names = list(sources.keys())
    vals = list(sources.values())
    bars = ax.barh(names, vals, color=colors[:len(sources)], edgecolor="white")

    for bar, count in zip(bars, vals):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height() / 2,
                f"{count:,}", ha="left", va="center", fontsize=10)

    ax.set_xlabel("Number of Records Identified")
    ax.set_title("Records by Source Database")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(FIGURES / "fig3_source_distribution.png")
    fig.savefig(FIGURES / "fig3_source_distribution.pdf")
    plt.close(fig)
    print("  fig3_source_distribution")


# ── Figure 4: Screening exclusion reasons ─────────────────────────────────
def fig_exclusion_reasons():
    """Horizontal bar chart of exclusion reasons (T/A stage + full-text stage)."""
    from collections import Counter

    ai = _load_ai_screening()

    # T/A exclusion reasons from AI screening
    ta_reasons = Counter()
    for _, row in ai.iterrows():
        if row.get("ai_decision", "") == "exclude":
            code = row.get("reason_code", "EX-OTHER")
            ta_reasons[code] += 1

    # Full-text exclusion reasons
    ft = _load_ft_decisions()
    ft_reasons = Counter()
    for _, row in ft.iterrows():
        if row.get("final_decision", "") == "exclude":
            code = row.get("exclusion_reason", "EX-OTHER")
            ft_reasons[code] += 1

    # Combine: label T/A vs full-text
    labels_map = {
        "EX-NONFIN": "Not finance\napplication",
        "EX-NOMETHOD": "Survey/review,\nno original method",
        "EX-TOOSHORT": "Insufficient\nmethodological detail",
        "EX-PARADIGM": "Annealing only /\nquantum-inspired",
        "EX-REVERSED": "Excluded after\ndiscrepancy review",
        "EX-OTHER": "Other",
        "EX-NOTEN": "Non-English",
    }

    ordered = ta_reasons.most_common()
    # Add full-text exclusion reasons that aren't already in T/A
    for code, count in ft_reasons.most_common():
        if code not in ta_reasons:
            ordered.append((code, 0))  # T/A count is 0, will be shown separately

    codes = [r for r, _ in ordered]
    ta_counts = [ta_reasons.get(r, 0) for r in codes]
    ft_counts = [ft_reasons.get(r, 0) for r in codes]
    labels = [labels_map.get(r, r) for r in codes]

    fig, ax = plt.subplots(figsize=(9, 5))
    y_pos = range(len(codes))

    # Stacked bars: T/A in orange, full-text in blue
    bars_ta = ax.barh(y_pos, ta_counts, color="#fd8d3c", edgecolor="white", label="Title/Abstract stage")
    bars_ft = ax.barh(y_pos, ft_counts, left=ta_counts, color="#2171b5", edgecolor="white", label="Full-text stage")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)

    for i, (ta_c, ft_c) in enumerate(zip(ta_counts, ft_counts)):
        total = ta_c + ft_c
        ax.text(total + 5, i, f"{total:,}", ha="left", va="center", fontsize=10)

    ax.set_xlabel("Number of Records Excluded")
    ax.set_title("Screening Exclusion Reasons (Title/Abstract + Full-Text)")
    ax.invert_yaxis()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(loc="lower right", fontsize=9)

    fig.savefig(FIGURES / "fig4_exclusion_reasons.png")
    fig.savefig(FIGURES / "fig4_exclusion_reasons.pdf")
    plt.close(fig)
    print("  fig4_exclusion_reasons")


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    print("Generating figures in 04_figures/...")
    fig_prisma_flow()
    fig_year_distribution()
    fig_source_distribution()
    fig_exclusion_reasons()
    print(f"\nDone. {len(list(FIGURES.glob('*.png')))} PNG + {len(list(FIGURES.glob('*.pdf')))} PDF files generated.")


if __name__ == "__main__":
    main()
