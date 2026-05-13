"""Compatibility wrapper for `p4_experiments.canonical.pipeline.phase10_h_figures`."""

from __future__ import annotations

from p4_experiments.canonical.pipeline.phase10_h_figures import *  # noqa: F401,F403
from p4_experiments.canonical.pipeline.phase10_h_figures import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())