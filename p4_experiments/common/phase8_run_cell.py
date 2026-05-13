"""Compatibility wrapper for `p4_experiments.core.phase8_run_cell`."""

from __future__ import annotations

from p4_experiments.core.phase8_run_cell import *  # noqa: F401,F403
from p4_experiments.core.phase8_run_cell import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())
