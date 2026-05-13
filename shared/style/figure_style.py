"""Shared visual-style facade for QF figure generators.

Re-exports the canonical Phase 4 ``_figure_style`` module so Phase 2
(``p2_systematic_review/s1_slr/generate_figures.py``) and any future
generator can reach the same Palette A, accent slots, rcParams, and
``display_*`` helpers without duplicating the constants.

Implementation note: the canonical implementation lives at
``p4_experiments/canonical/pipeline/_figure_style.py`` because the
Phase 4 pipeline scripts import it via a bare ``from _figure_style
import ...`` after ``sys.path.insert`` (a pattern that pre-dates the
shared/ package and is intentionally kept stable for the Zenodo
bundle). This wrapper imports the file by absolute path so callers
outside Phase 4 do not need the same sys.path dance.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_CANONICAL = (
    Path(__file__).resolve().parents[2]
    / "p4_experiments"
    / "canonical"
    / "pipeline"
    / "_figure_style.py"
)

if not _CANONICAL.exists():  # pragma: no cover - environment misconfig guard
    raise ImportError(
        f"shared.style.figure_style: cannot locate canonical module at {_CANONICAL}"
    )

_spec = importlib.util.spec_from_file_location(
    "shared.style._canonical_figure_style", _CANONICAL
)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError("shared.style.figure_style: failed to build module spec")
_module = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _module
_spec.loader.exec_module(_module)

# Re-export the public surface used by figure generators.
PALETTE = _module.PALETTE
ACCENT_PRIMARY = _module.ACCENT_PRIMARY
ACCENT_SECONDARY = _module.ACCENT_SECONDARY
ACCENT_WARN = _module.ACCENT_WARN
ACCENT_NEUTRAL = _module.ACCENT_NEUTRAL
HEATMAP_CMAP_SEQUENTIAL = _module.HEATMAP_CMAP_SEQUENTIAL
HEATMAP_CMAP_DIVERGING = _module.HEATMAP_CMAP_DIVERGING
HEATMAP_CMAP_BINARY = _module.HEATMAP_CMAP_BINARY
apply_house_style = _module.apply_house_style
display_profile = _module.display_profile
display_epsilon = _module.display_epsilon
display_criterion = _module.display_criterion
save_figure = _module.save_figure
# House-style helpers (audit 2026-05-12, R-6).
figure_size = _module.figure_size
style_axes = _module.style_axes
place_legend = _module.place_legend
validate_no_raw_identifiers = _module.validate_no_raw_identifiers
validate_pdf_png_pair = _module.validate_pdf_png_pair
# Palette B + flowchart tokens (audit 2026-05-12 design-system unification).
LAYER_GRAY = _module.LAYER_GRAY
LAYER_BLUE = _module.LAYER_BLUE
LAYER_GREEN = _module.LAYER_GREEN
LAYER_GOLD = _module.LAYER_GOLD
LAYER_CORAL = _module.LAYER_CORAL
LINE_GRAY = _module.LINE_GRAY
TEXT_MAIN = _module.TEXT_MAIN
TEXT_MUTED = _module.TEXT_MUTED
FLOW_LW_BOX = _module.FLOW_LW_BOX
FLOW_LW_OUTER = _module.FLOW_LW_OUTER
FLOW_LW_ARROW = _module.FLOW_LW_ARROW
FLOW_BOXSTYLE = _module.FLOW_BOXSTYLE
FLOW_ARROW_STYLE = _module.FLOW_ARROW_STYLE
FLOW_ARROW_MSCALE = _module.FLOW_ARROW_MSCALE

__all__ = [
    "PALETTE",
    "ACCENT_PRIMARY",
    "ACCENT_SECONDARY",
    "ACCENT_WARN",
    "ACCENT_NEUTRAL",
    "HEATMAP_CMAP_SEQUENTIAL",
    "HEATMAP_CMAP_DIVERGING",
    "HEATMAP_CMAP_BINARY",
    "apply_house_style",
    "display_profile",
    "display_epsilon",
    "display_criterion",
    "save_figure",
    "figure_size",
    "style_axes",
    "place_legend",
    "validate_no_raw_identifiers",
    "validate_pdf_png_pair",
    "LAYER_GRAY",
    "LAYER_BLUE",
    "LAYER_GREEN",
    "LAYER_GOLD",
    "LAYER_CORAL",
    "LINE_GRAY",
    "TEXT_MAIN",
    "TEXT_MUTED",
    "FLOW_LW_BOX",
    "FLOW_LW_OUTER",
    "FLOW_LW_ARROW",
    "FLOW_BOXSTYLE",
    "FLOW_ARROW_STYLE",
    "FLOW_ARROW_MSCALE",
]
