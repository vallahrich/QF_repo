"""Compatibility wrapper for `p4_experiments.canonical.pipeline.phase08b_update_cohort`."""

from __future__ import annotations

from p4_experiments.canonical.pipeline.phase08b_update_cohort import *  # noqa: F401,F403
from p4_experiments.canonical.pipeline.phase08b_update_cohort import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())