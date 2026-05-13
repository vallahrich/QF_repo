"""Generate the Phase 2 screening and corpus workflow figure.

The figure is designed as an academic process board: concise labels in the
graphic, with methodological detail left to the surrounding prose and caption.
It shows calibration, split human screening, AI validation/recall checking,
human-led reconciliation, and the handoff into full-text and corpus processing.

Visual policy: routed through ``shared.style.figure_style`` Palette B and
flowchart tokens (audit 2026-05-12 design-system unification) so this figure,
the PRISMA flow diagram, and the Ch4 TikZ pipeline schematic share one
visual language.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parents[1]
P2_FIGURES = SCRIPT_DIR / "04_figures"
MANUSCRIPT_FIGURES = ROOT / "manuscript" / "05_Figures"
OUTPUT_STEM = "fig5_p2_corpus_workflow"
CLASSIFICATION_OUTPUT_STEM = "fig5_p2_llm_classification_workflow"

# Shared visual policy facade (Palette B + flowchart tokens).
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.style.figure_style import (  # noqa: E402  -- after Agg backend
    FLOW_ARROW_MSCALE,
    FLOW_ARROW_STYLE,
    FLOW_BOXSTYLE,
    FLOW_LW_ARROW,
    FLOW_LW_BOX,
    FLOW_LW_OUTER,
    LAYER_BLUE,
    LAYER_CORAL,
    LAYER_GOLD,
    LAYER_GRAY,
    LAYER_GREEN,
    LINE_GRAY,
    TEXT_MAIN,
    TEXT_MUTED,
    apply_house_style,
)

# Semantic role mapping (matches the PRISMA figure and Ch4 pipeline TikZ).
INK = TEXT_MAIN
MUTED = TEXT_MUTED
EDGE = LINE_GRAY
FILL = "#ffffff"          # plain neutral fill for backbone steps
HUMAN = LAYER_BLUE        # human / process step
AI = LAYER_GREEN          # automated / AI / LLM step
RECONCILE = LAYER_GOLD    # reconciliation / handover
EXCLUDED = LAYER_GRAY     # excluded
ACTIVE = LAYER_CORAL      # final / active-outcome corpus

apply_house_style()
# Smaller font/pad overrides specific to this dense process-board layout;
# everything else inherits from the house style.
plt.rcParams.update({
    "font.size": 8.5,  # Audit P0-1: was 7.2
    "savefig.pad_inches": 0.05,
})


def wrapped(text: str, width: int) -> str:
    return "\n".join(
        "\n".join(textwrap.wrap(line, width=width, break_long_words=False)) if line else ""
        for line in text.splitlines()
    )


def draw_box(
    ax,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    *,
    facecolor: str = FILL,
    fontsize: float = 8.5,
    weight: str = "normal",
    wrap: int = 28,
    outer: bool = False,
) -> None:
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle=FLOW_BOXSTYLE,
        linewidth=FLOW_LW_OUTER if outer else FLOW_LW_BOX,
        edgecolor=EDGE,
        facecolor=facecolor,
        zorder=1,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y,
        wrapped(text, wrap),
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight=weight,
        color=INK,
        linespacing=1.05,
        zorder=2,
    )


def draw_arrow(
    ax,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    rad: float = 0.0,
    shrink_a: float = 7,
    shrink_b: float = 7,
) -> None:
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle=FLOW_ARROW_STYLE,
        mutation_scale=FLOW_ARROW_MSCALE,
        linewidth=FLOW_LW_ARROW,
        color=EDGE,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=shrink_a,
        shrinkB=shrink_b,
        zorder=0,
    )
    ax.add_patch(arrow)


def section_label(ax, x: float, y: float, text: str) -> None:
    ax.text(
        x,
        y,
        text.upper(),
        ha="center",
        va="center",
        fontsize=6.6,
        fontweight="bold",
        color=MUTED,
    )


def _draw_titled_outer_frame(ax, x0, y0, x1, y1, label):
    """Pipeline-style group framing: thin rounded outline plus label-above."""
    ax.add_patch(
        FancyBboxPatch(
            (x0, y0), x1 - x0, y1 - y0,
            boxstyle="round,pad=0.4,rounding_size=2.0",
            linewidth=FLOW_LW_BOX,
            edgecolor=LINE_GRAY, facecolor="none", zorder=-1,
        )
    )
    ax.text((x0 + x1) / 2, y1 + 1.6, label, ha="center", va="bottom",
            fontsize=8.5, color=TEXT_MUTED)


def build_figure() -> plt.Figure:
    fig, ax = plt.subplots(figsize=(8.0, 6.8))  # Audit P0-1
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")


    draw_box(ax, 50, 94.0, 50, 6.4, "3,010 unique records after deduplication", weight="bold", wrap=42)
    draw_box(
        ax,
        50,
        85.0,
        64,
        7.2,
        "Calibration sample (n = 49)\ncriteria aligned before split screening",
        facecolor=LAYER_GRAY,
        wrap=58,
    )

    draw_box(ax, 29, 69.5, 34, 8.2, "Human split screening\nReviewer A and Reviewer B", facecolor=HUMAN, wrap=34)
    draw_box(ax, 71, 69.5, 34, 8.2, "AI validation and recall check\n100-record validation subset", facecolor=AI, wrap=34)

    draw_box(
        ax,
        50,
        58.0,
        68,
        8.2,
        "Human-led reconciliation\nhuman includes retained; AI-rescue cases re-reviewed",
        facecolor=RECONCILE,
        wrap=62,
    )

    draw_box(ax, 30, 47.0, 30, 6.8, "2,135 title/abstract exclusions", facecolor=EXCLUDED, wrap=28)
    draw_box(ax, 70, 47.0, 30, 6.8, "875 full-text candidates", weight="bold", wrap=26)

    draw_box(ax, 70, 38.0, 35, 6.8, "Human full-text eligibility", facecolor=HUMAN, wrap=30)
    draw_box(ax, 26, 38.0, 28, 6.6, "98 full-text exclusions", facecolor=EXCLUDED, wrap=26)
    draw_box(ax, 70, 29.0, 35, 6.2, "777 processed audit corpus", weight="bold", wrap=32)
    draw_box(ax, 70, 20.4, 35, 6.8, "Text extraction + Pipeline C outputs", facecolor=AI, wrap=30)
    draw_box(ax, 70, 11.6, 35, 6.6, "Post-classification audit", facecolor=RECONCILE, wrap=30)
    draw_box(ax, 26, 3.8, 35, 6.4, "22 off-scope retained for audit", facecolor=EXCLUDED, wrap=30)
    draw_box(ax, 70, 3.8, 35, 6.4, "755 downstream-active papers", facecolor=ACTIVE, weight="bold", wrap=30, outer=True)

    draw_arrow(ax, (50, 90.8), (50, 88.6), shrink_a=4, shrink_b=4)
    draw_arrow(ax, (42, 81.4), (30, 73.6), rad=0.03)
    draw_arrow(ax, (58, 81.4), (70, 73.6), rad=-0.03)
    draw_arrow(ax, (29, 65.5), (44, 62.0), rad=-0.02)
    draw_arrow(ax, (71, 65.5), (56, 62.0), rad=0.02)
    draw_arrow(ax, (43, 53.9), (32, 50.3), rad=0.03)
    draw_arrow(ax, (57, 53.9), (68, 50.3), rad=-0.03)
    draw_arrow(ax, (70, 43.6), (70, 41.4), shrink_a=4, shrink_b=4)
    draw_arrow(ax, (52.5, 38.0), (40.0, 38.0), rad=0.0, shrink_a=3, shrink_b=3)
    draw_arrow(ax, (70, 34.6), (70, 32.1), shrink_a=4, shrink_b=4)
    draw_arrow(ax, (70, 25.9), (70, 23.8), shrink_a=4, shrink_b=4)
    draw_arrow(ax, (70, 17.0), (70, 14.9), shrink_a=4, shrink_b=4)
    draw_arrow(ax, (57, 8.6), (39, 5.8), rad=0.06, shrink_a=4, shrink_b=4)
    draw_arrow(ax, (70, 8.2), (70, 7.0), shrink_a=4, shrink_b=4)

    return fig


def build_classification_figure() -> plt.Figure:
    figure, axis = plt.subplots(figsize=(8.0, 6.8))  # Audit P0-1
    axis.set_xlim(0, 100)
    axis.set_ylim(0, 100)
    axis.axis("off")


    draw_box(axis, 50, 94.0, 50, 6.4, "777 processed Markdown profiles", weight="bold", wrap=42)
    draw_box(
        axis,
        50,
        85.0,
        64,
        7.2,
        "Pipeline C cached-prefix architecture: paper text reused across six sequential LLM calls",
        facecolor=LAYER_GRAY,
        wrap=58,
    )

    step_boxes = [
        (29, 69.5, "1. Source classification", "paper type and confidence"),
        (71, 69.5, "2. Metadata extraction", "title, authors, year, venue, DOI"),
        (71, 56.4, "3. Methodology extraction", "algorithms, data, hardware, setup"),
        (29, 56.4, "4. Findings extraction", "claims, results, advantage label"),
        (29, 43.3, "5. Limitations extraction", "limits, open questions, future work"),
        (71, 43.3, "6. Synthesis and tagging", "PD/SA tags, quant flag, evaluation type"),
    ]

    for x_coord, y_coord, title, detail in step_boxes:
        draw_box(
            axis,
            x_coord,
            y_coord,
            34,
            8.2,
            f"{title}\n{detail}",
            facecolor=AI,
            fontsize=8.5,
            wrap=32,
        )

    draw_box(
        axis,
        50,
        30.2,
        68,
        8.2,
        "Per-paper outputs: structured Markdown profile plus companion extraction JSON",
        facecolor=RECONCILE,
        wrap=62,
    )
    draw_box(
        axis,
        50,
        17.8,
        68,
        7.2,
        "Use in Chapter 5: descriptive corpus tables over 755 downstream-active papers after post-classification triage",
        facecolor=ACTIVE,
        weight="bold",
        wrap=62,
        outer=True,
    )
    draw_box(
        axis,
        50,
        6.6,
        68,
        6.6,
        "Boundary: single-LLM, single-pass extraction; limitations carried into interpretation",
        facecolor=LAYER_GRAY,
        fontsize=8.0,
        wrap=62,
    )

    draw_arrow(axis, (50, 90.8), (50, 88.6), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (42, 81.4), (30, 73.6), rad=0.03)
    draw_arrow(axis, (46, 69.5), (54, 69.5), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (71, 65.5), (71, 60.6), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (54, 56.4), (46, 56.4), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (29, 52.4), (29, 47.5), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (46, 43.3), (54, 43.3), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (71, 39.1), (57, 34.3), rad=-0.02)
    draw_arrow(axis, (50, 26.1), (50, 21.4), shrink_a=4, shrink_b=4)
    draw_arrow(axis, (50, 14.2), (50, 10.0), shrink_a=4, shrink_b=4)

    return figure


def main() -> None:
    for output_dir in (P2_FIGURES, MANUSCRIPT_FIGURES):
        output_dir.mkdir(parents=True, exist_ok=True)

    fig = build_figure()
    for output_dir in (P2_FIGURES, MANUSCRIPT_FIGURES):
        fig.savefig(output_dir / f"{OUTPUT_STEM}.pdf")
        fig.savefig(output_dir / f"{OUTPUT_STEM}.png", dpi=300)
    plt.close(fig)

    classification_fig = build_classification_figure()
    for output_dir in (P2_FIGURES, MANUSCRIPT_FIGURES):
        classification_fig.savefig(output_dir / f"{CLASSIFICATION_OUTPUT_STEM}.pdf")
        classification_fig.savefig(output_dir / f"{CLASSIFICATION_OUTPUT_STEM}.png", dpi=300)
    plt.close(classification_fig)

    print(f"Generated {OUTPUT_STEM}.pdf/.png in:")
    print(f"  {P2_FIGURES}")
    print(f"  {MANUSCRIPT_FIGURES}")
    print(f"Generated {CLASSIFICATION_OUTPUT_STEM}.pdf/.png in:")
    print(f"  {P2_FIGURES}")
    print(f"  {MANUSCRIPT_FIGURES}")


if __name__ == "__main__":
    main()