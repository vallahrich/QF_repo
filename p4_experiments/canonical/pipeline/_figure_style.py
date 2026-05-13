"""Shared matplotlib style for Phase 4 manuscript figures.

Implements the visual policy defined in
``docs/figures-tables-visual-policy.md`` (rules V-08 / V-09 / V-10 / V-13).
Mirrors the rcParams block used by
``p2_systematic_review/s1_slr/generate_figures.py`` so that all manuscript
figures share one register (serif font, 300 dpi, controlled palette).

Import contract::

    from _figure_style import apply_house_style, PALETTE, save_figure
    apply_house_style()

The module is import-side-effect free; callers must invoke
``apply_house_style()`` explicitly so test harnesses that import the
pipeline modules do not silently mutate global rcParams.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


# --- V-09 Palette A (sequential / categorical for matplotlib) -------------
# Same hex codes as p2_systematic_review/s1_slr/generate_figures.py.
PALETTE: list[str] = [
    "#2171b5", "#6baed6", "#bdd7e7",   # blues
    "#238b45", "#74c476", "#bae4b3",   # greens
    "#d94801", "#fd8d3c", "#fdd0a2",   # oranges
    "#756bb1", "#bcbddc", "#dadaeb",   # purples
]

# Named accent slots used across Phase 4 figures so individual call sites
# don't pick ad-hoc hex values that drift from the palette over time.
ACCENT_PRIMARY = PALETTE[0]   # #2171b5  — primary blue
ACCENT_SECONDARY = PALETTE[3]  # #238b45 — primary green
ACCENT_WARN = PALETTE[6]       # #d94801 — orange (used for threshold lines)
ACCENT_NEUTRAL = "#5F6670"     # match TikZ linegray / textmuted

# --- V-09 Palette B (TikZ schematic / matplotlib flowchart parity) ---------
# Mirrored from manuscript/05_Figures/research_onion.tex and
# manuscript/01_Preamble/A_Settings.tex so matplotlib-generated flowcharts
# (PRISMA, Phase 2 corpus workflow, LLM classification workflow) share one
# colour vocabulary with the TikZ schematics (research onion, Ch4 pipeline).
# Audit 2026-05-12 design-system unification.
LAYER_GRAY  = "#F2F2F0"        # excluded / sidebar / muted backdrop
LAYER_BLUE  = "#D9E6F2"        # process / human step
LAYER_GREEN = "#DDEAD9"        # automated / AI step
LAYER_GOLD  = "#F3E8C8"        # reconciliation / handover
LAYER_CORAL = "#EED8CF"        # final / active-outcome corpus
LINE_GRAY   = "#5F6670"        # all box / arrow strokes (== ACCENT_NEUTRAL)
TEXT_MAIN   = "#1F2328"        # primary text
TEXT_MUTED  = "#59636E"        # phase labels, secondary text

# Stroke / box / arrow tokens for matplotlib flowcharts mirroring TikZ V-11.
FLOW_LW_BOX       = 0.45
FLOW_LW_OUTER     = 0.65
FLOW_LW_ARROW     = 0.55
FLOW_BOXSTYLE     = "round,pad=0.18,rounding_size=1.25"
FLOW_ARROW_STYLE  = "-|>"
FLOW_ARROW_MSCALE = 8

# Sequential colormaps for heatmaps. Keep this list short — V-09 forbids
# introducing new colormaps figure-by-figure.
HEATMAP_CMAP_SEQUENTIAL = "Blues"
HEATMAP_CMAP_DIVERGING = "RdBu_r"
# Binary pass/fail colormap built from the named accent slots so it stays
# visually consistent with the rest of the Phase 4 figure set
# (grey = fail, green = pass). Used by the H4 criteria heatmap.
HEATMAP_CMAP_BINARY = ListedColormap([ACCENT_NEUTRAL, ACCENT_SECONDARY])


def apply_house_style() -> None:
    """Set rcParams for the V-08 manuscript-figure style.

    Idempotent. Safe to call multiple times in a session.
    """
    plt.rcParams.update({
        "font.family":       "serif",
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.labelsize":    12,
        "axes.spines.top":   False,
        "axes.spines.right": False,
        "axes.grid":         False,
        "legend.fontsize":   9,
        "xtick.labelsize":   9,
        "ytick.labelsize":   9,
        "figure.dpi":        300,
        "savefig.bbox":      "tight",
        "savefig.pad_inches": 0.15,
    })


# --- V-10 label cleanup ----------------------------------------------------
# Centralised replacements so titles, ticks, and legends share one
# vocabulary. Keep this small: the goal is to remove raw snake-case from
# user-visible text, not to re-render upstream identifiers.
PROFILE_DISPLAY: dict[str, str] = {
    "sc_e3_surface":  r"SC $10^{-3}$ surface",
    "sc_e4_surface":  r"SC $10^{-4}$ surface",
    "ti_e3_surface":  r"TI $10^{-3}$ surface",
    "ti_e4_surface":  r"TI $10^{-4}$ surface",
    "maj_e6_surface": r"Maj $10^{-6}$ surface",
    "maj_e6_floquet": r"Maj $10^{-6}$ floquet",
}

EPSILON_DISPLAY: dict[str, str] = {
    "1e-03": r"$10^{-3}$",
    "1e-04": r"$10^{-4}$",
    "1e-06": r"$10^{-6}$",
}


def display_profile(profile: str) -> str:
    """Return the human-readable label for a hardware-profile identifier."""
    return PROFILE_DISPLAY.get(profile, profile.replace("_", " "))


def display_epsilon(eps: str) -> str:
    """Return the math-mode label for an epsilon string identifier."""
    return EPSILON_DISPLAY.get(eps, eps)


def display_criterion(name: str | None) -> str:
    """Render a Phase 4 H4 criterion identifier as readable LaTeX/mathtext.

    Keys correspond to the H4 criterion names emitted by
    ``pipeline/phase08e_per_silo_synthesis.py`` (see lines 64-68 of that
    module for the canonical definitions).

    Examples:
        ``C1_tau_runtime_lt_10``       -> ``C1: $\\tau_{\\mathrm{runtime}} < 10$``
        ``C2_full_runtime_lt_baseline``-> ``C2: full runtime $<$ baseline``
        ``C3_full_t_count_gt_0``       -> ``C3: full $T$-count $> 0$``
        ``C4_tau_tdepth_ge_10``        -> ``C4: $\\tau_{T\\text{-depth}} \\geq 10$``
        ``C5_baseline_ge_0_01s``       -> ``C5: baseline $\\geq 0.01$ s``
    """
    if not name:
        return ""
    table = {
        "C1_tau_runtime_lt_10":         r"C1: $\tau_{\mathrm{runtime}} < 10$",
        "C2_full_runtime_lt_baseline":  r"C2: full runtime $<$ baseline",
        "C3_full_t_count_gt_0":         r"C3: full $T$-count $> 0$",
        "C4_tau_tdepth_ge_10":          r"C4: $\tau_{T\text{-depth}} \geq 10$",
        "C5_baseline_ge_0_01s":         r"C5: baseline $\geq 0.01$ s",
    }
    return table.get(name, name.replace("_", " "))


# --- V-08 dual-format save -------------------------------------------------

def save_figure(fig, paths: Iterable[Path]) -> list[str]:
    """Save ``fig`` to each ``paths`` location and to a sibling ``.pdf``.

    For each input path with a ``.png`` suffix, also writes the matching
    ``.pdf`` so manuscript ``\\includegraphics`` calls can prefer the
    vector form.

    Returns the list of written paths as strings.
    """
    written: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path)
        written.append(str(path))
        if path.suffix.lower() == ".png":
            pdf_path = path.with_suffix(".pdf")
            fig.savefig(pdf_path)
            written.append(str(pdf_path))
    return written


# --- House-style helpers (audit 2026-05-12, R-6) ---------------------------
# Thin helpers that codify the design-system tokens defined in
# ``docs/figures-design-system-audit-2026-05-12.md`` (sections 4 and 5).
# Each helper exists because the underlying micro-decision was being made
# inconsistently across generators; do not add helpers here without a
# current caller and a documented drift to prevent.

# Standard figsize tokens — keep this table in sync with audit section 4.8.
_FIGURE_SIZES: dict[str, tuple[float, float]] = {
    "single":   (7.0, 4.6),  # single-panel quantitative
    "ecdf":     (8.5, 5.0),
    "heatmap":  (7.2, 5.2),
    "heatmap_binary": (8.0, 6.0),
    "funnel":   (8.5, 4.8),
    "bar":      (8.5, 4.8),
    "scatter":  (7.0, 4.6),
    "two_panel": (13.0, 5.5),
}


def figure_size(kind: str) -> tuple[float, float]:
    """Return the standard ``figsize`` for ``kind``.

    Recognised kinds: ``single``, ``ecdf``, ``heatmap``, ``heatmap_binary``,
    ``funnel``, ``bar``, ``scatter``, ``two_panel``. Unknown kinds fall
    through to ``single`` after a ``UserWarning``.
    """
    import warnings
    if kind not in _FIGURE_SIZES:
        warnings.warn(
            f"figure_size: unknown kind {kind!r}; using 'single'",
            UserWarning,
            stacklevel=2,
        )
        kind = "single"
    return _FIGURE_SIZES[kind]


def style_axes(
    ax,
    *,
    grid: bool = True,
    log_x: bool = False,
    log_y: bool = False,
    threshold: float | None = None,
    threshold_axis: str = "x",
    threshold_label: str | None = None,
) -> None:
    """Apply the house grid + scale + threshold-line conventions to ``ax``.

    - ``grid``: dotted gridlines at ``alpha=0.4`` (template default).
    - ``log_x`` / ``log_y``: switch the corresponding axis to ``log``.
    - ``threshold``: draw a dashed ``ACCENT_WARN`` line at this value.
      ``threshold_axis`` selects ``"x"`` (axvline) or ``"y"`` (axhline).
      ``threshold_label`` is forwarded to ``label=`` so callers can pull
      it into a legend.
    """
    if grid:
        ax.grid(True, linestyle=":", alpha=0.4)
    if log_x:
        ax.set_xscale("log")
    if log_y:
        ax.set_yscale("log")
    if threshold is not None:
        if threshold_axis == "x":
            ax.axvline(threshold, color=ACCENT_WARN, linestyle="--",
                       linewidth=1.2, label=threshold_label)
        elif threshold_axis == "y":
            ax.axhline(threshold, color=ACCENT_WARN, linestyle="--",
                       linewidth=1.2, label=threshold_label)
        else:
            raise ValueError(
                f"threshold_axis must be 'x' or 'y', got {threshold_axis!r}"
            )


_LEGEND_LOCATIONS = {
    "inside_lower_right": dict(loc="lower right", framealpha=0.9, borderpad=0.4),
    "inside_upper_right": dict(loc="upper right", framealpha=0.9, borderpad=0.4),
    "inside_upper_left":  dict(loc="upper left",  framealpha=0.9, borderpad=0.4),
    "below":              dict(loc="upper center", bbox_to_anchor=(0.5, -0.18),
                                ncol=3, frameon=False, borderpad=0.4),
}


def place_legend(ax, location: str = "inside_upper_right") -> None:
    """Place a legend on ``ax`` with the house defaults.

    ``location`` is one of: ``inside_lower_right``, ``inside_upper_right``,
    ``inside_upper_left``, ``below``. Defaults to ``inside_upper_right``.
    """
    if location not in _LEGEND_LOCATIONS:
        raise ValueError(
            f"place_legend: unknown location {location!r}; "
            f"expected one of {sorted(_LEGEND_LOCATIONS)}"
        )
    handles, labels = ax.get_legend_handles_labels()
    if not handles:
        return
    ax.legend(**_LEGEND_LOCATIONS[location])


def validate_no_raw_identifiers(fig) -> list[str]:
    """Return reader-visible strings on ``fig`` that contain raw snake_case.

    Scans every axes title, x/y label, tick label, legend entry, and
    every ``Text`` artist directly attached to the figure. Returns a list
    of offending strings (empty list = clean). V-10 / audit Module 6.

    Note: the check is intentionally conservative — it flags any string
    matching ``[a-z]+_[a-z0-9_]+`` that does not appear inside ``$...$``
    math-mode delimiters or LaTeX text-mode escapes.
    """
    import re
    offenders: list[str] = []
    pattern = re.compile(r"[a-z]+_[a-z0-9_]+")

    def _scan(text: str) -> None:
        if not text:
            return
        # Strip math-mode regions so display_profile/display_epsilon LaTeX
        # output (e.g. r"Maj $10^{-6}$ floquet") is not flagged.
        stripped = re.sub(r"\$[^$]*\$", "", text)
        # Strip \mathrm{...}, \text{...}, \texttt{...} etc.
        stripped = re.sub(r"\\[a-zA-Z]+\{[^}]*\}", "", stripped)
        if pattern.search(stripped):
            offenders.append(text)

    for ax in fig.get_axes():
        _scan(ax.get_title())
        _scan(ax.get_xlabel())
        _scan(ax.get_ylabel())
        for tl in list(ax.get_xticklabels()) + list(ax.get_yticklabels()):
            _scan(tl.get_text())
        legend = ax.get_legend()
        if legend is not None:
            for t in legend.get_texts():
                _scan(t.get_text())
    for artist in fig.texts:
        _scan(artist.get_text())
    return offenders


def validate_pdf_png_pair(path) -> bool:
    """Return True iff ``path`` has both ``.pdf`` and ``.png`` siblings.

    Accepts either sibling as input; checks the other exists. V-08 + V-12
    parity check. Use after ``save_figure`` to fail loudly if a generator
    bypasses the dual-format save.
    """
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix not in (".pdf", ".png"):
        return False
    other = ".png" if suffix == ".pdf" else ".pdf"
    return p.exists() and p.with_suffix(other).exists()
