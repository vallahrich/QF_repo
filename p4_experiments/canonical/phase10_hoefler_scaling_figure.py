"""Compatibility wrapper for `p4_experiments.canonical.pipeline.phase10_hoefler_scaling_figure`."""

from __future__ import annotations

from p4_experiments.canonical.pipeline.phase10_hoefler_scaling_figure import *  # noqa: F401,F403
from p4_experiments.canonical.pipeline.phase10_hoefler_scaling_figure import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())