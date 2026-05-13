"""Compatibility namespace for ``p4_experiments.core.templates``."""

from __future__ import annotations

from pathlib import Path

_TARGET = Path(__file__).resolve().parents[2] / "core" / "templates"
__path__ = [str(_TARGET)]