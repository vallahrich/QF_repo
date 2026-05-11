"""Generate SLR figures for 04_figures/ (Step 1: search & screening)."""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

REPO = Path(__file__).resolve().parent
FIGURES = REPO / "04_figures"
FIGURES.mkdir(exist_ok=True)
SCREENING = REPO / "03_screening"

# Styling
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "figure.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.15,
})

PALETTE = [
    "#2171b5", "#6baed6", "#bdd7e7",  # blues
    "#238b45", "#74c476", "#bae4b3",  # greens
    "#d94801", "#fd8d3c", "#fdd0a2",  # oranges
    "#756bb1", "#bcbddc", "#dadaeb",  # purples
]


def _load_asreview() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "asreview_dataset.csv", dtype=str).fillna("")


def _load_ai_screening() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "ai_screening_decisions.csv", dtype=str).fillna("")


def _load_ta_decisions() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "title_abstract_decisions.csv", dtype=str).fillna("")


def _load_ft_decisions() -> pd.DataFrame:
    return pd.read_csv(SCREENING / "full_text_decisions.csv", dtype=str).fillna("")


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

    # PDFs on disk
    pdf_dir = REPO / "05_full_texts" / "pdfs"
    n_pdfs = len([f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]) if pdf_dir.exists() else 0

    # ── Layout constants ──────────────────────────────────────────────────
    fig_w, fig_h = 11, 11.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis("off")

    cx = 4.2            # centre of main flow boxes
    rx = 8.5            # centre of right-side exclusion boxes
    bw_main = 3.2       # main box width
    bw_excl = 3.0       # exclusion box width
    bh = 0.85           # box height
    sidebar_w = 1.3     # phase sidebar width

    # Phase y-bands
    y_id_top, y_id_bot = 11.0, 8.3
    y_sc_top, y_sc_bot = 8.3, 5.8
    y_el_top, y_el_bot = 5.8, 3.4
    y_in_top, y_in_bot = 3.4, 0.8

    # Box y-centres
    y_ident = 10.2
    y_dup = 9.35
    y_screen = 7.2
    y_excl_ta = 7.2
    y_assess = 4.8
    y_excl_ft = 4.8
    y_incl = 2.2

    # ── Colours (PRISMA 2020 standard: muted, professional) ───────────────
    c_sidebar = "#e8e8e8"
    c_sidebar_text = "#444444"
    c_box_fill = "#ffffff"
    c_box_edge = "#333333"
    c_excl_fill = "#fafafa"
    c_excl_edge = "#888888"
    c_incl_fill = "#f0f7f0"
    c_incl_edge = "#333333"
    c_arrow = "#333333"
    lw_box = 1.2
    lw_arrow = 1.0
    fs_box = 9.5
    fs_phase = 11

    # ── Helpers ───────────────────────────────────────────────────────────
    def _box(x, y, w, h, text, fill, edge, lw=lw_box, fontsize=fs_box,
             fontweight="normal"):
        rect = mpatches.FancyBboxPatch(
            (x - w / 2, y - h / 2), w, h,
            boxstyle="round,pad=0.08",
            facecolor=fill, edgecolor=edge, linewidth=lw,
        )
        ax.add_patch(rect)
        ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
                fontweight=fontweight, linespacing=1.35)

    def _arrow_down(x, y_from, y_to):
        ax.annotate("", xy=(x, y_to), xytext=(x, y_from),
                    arrowprops=dict(arrowstyle="-|>", color=c_arrow,
                                    lw=lw_arrow, mutation_scale=12))

    def _arrow_right(x_from, x_to, y):
        ax.annotate("", xy=(x_to, y), xytext=(x_from, y),
                    arrowprops=dict(arrowstyle="-|>", color=c_arrow,
                                    lw=lw_arrow, mutation_scale=12))

    # ── Phase sidebar bands ───────────────────────────────────────────────
    for top, bot, label in [
        (y_id_top, y_id_bot, "Identification"),
        (y_sc_top, y_sc_bot, "Screening"),
        (y_el_top, y_el_bot, "Eligibility"),
        (y_in_top, y_in_bot, "Included"),
    ]:
        rect = mpatches.FancyBboxPatch(
            (0.15, bot), sidebar_w, top - bot,
            boxstyle="round,pad=0.06",
            facecolor=c_sidebar, edgecolor="#cccccc", linewidth=0.8,
        )
        ax.add_patch(rect)
        ax.text(0.15 + sidebar_w / 2, (top + bot) / 2, label,
                ha="center", va="center", fontsize=fs_phase,
                fontweight="bold", color=c_sidebar_text, rotation=90)

    # ── Identification ────────────────────────────────────────────────────
    src_line = "Openalex: 2,843\nSemantic Scholar: 1,554\nScopus: 1,127\nArxiv: 708"
    id_box_h = 1.8
    _box(cx, y_ident, bw_main, id_box_h,
         f"Records identified through\ndatabase searching\n(n = {n_identified:,})",
         c_box_fill, c_box_edge)
    ax.text(cx, y_ident - 0.55, src_line,
            ha="center", va="center", fontsize=5.5, color="#666666",
            linespacing=1.3)

    # Duplicates removed — junction between ident and screening
    y_junct = y_ident - id_box_h / 2 - 0.45
    _box(rx, y_junct, bw_excl, 0.65,
         f"Duplicates removed\n(n = {n_duplicates:,})",
         c_excl_fill, c_excl_edge)

    # Vertical line: ident bottom → junction → screening top
    ax.plot([cx, cx], [y_ident - id_box_h / 2, y_junct], color=c_arrow,
            lw=lw_arrow, solid_capstyle="butt")
    _arrow_right(cx, rx - bw_excl / 2, y_junct)
    _arrow_down(cx, y_junct, y_screen + bh / 2)

    # ── Screening ─────────────────────────────────────────────────────────
    _box(cx, y_screen, bw_main, bh,
         f"Records screened\n(title/abstract)\n(n = {n_screened:,})",
         c_box_fill, c_box_edge)

    _box(rx, y_excl_ta, bw_excl, 0.65,
         f"Records excluded\n(n = {n_excluded_ta:,})",
         c_excl_fill, c_excl_edge)

    _arrow_down(cx, y_screen - bh / 2, y_assess + bh / 2)
    _arrow_right(cx + bw_main / 2, rx - bw_excl / 2, y_excl_ta)

    # ── Eligibility ───────────────────────────────────────────────────────
    _box(cx, y_assess, bw_main, bh,
         f"Full-text articles assessed\nfor eligibility\n(n = {n_assessed_ft:,})",
         c_box_fill, c_box_edge)

    if n_excluded_ft > 0:
        reason_labels = {
            "EX-NOTEN": "Non-English",
            "EX-NOACCESS": "Full text not retrieved",
        }
        reason_parts = [f"Full-text articles excluded\n(n = {n_excluded_ft})"]
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

    # ── Included ──────────────────────────────────────────────────────────
    _box(cx, y_incl, bw_main, bh,
         f"Studies included in\nsystematic review\n(n = {n_included_ft:,})",
         c_incl_fill, c_incl_edge, fontweight="bold")

    fig.savefig(FIGURES / "fig1_prisma_flow.png")
    fig.savefig(FIGURES / "fig1_prisma_flow.pdf")
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

    ax.set_xlabel("Publication Year")
    ax.set_ylabel("Number of Records")
    ax.set_title("Records Identified by Publication Year (2016–2026)")
    ax.set_xticks(year_counts.index)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.savefig(FIGURES / "fig2_year_distribution.png")
    fig.savefig(FIGURES / "fig2_year_distribution.pdf")
    plt.close(fig)
    print("  fig2_year_distribution")


# ── Figure 3: Source database contribution ────────────────────────────────
def fig_source_distribution():
    """Horizontal bar chart of records by source database."""
    # Source counts from original search logs (hardcoded — master_records.csv
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
