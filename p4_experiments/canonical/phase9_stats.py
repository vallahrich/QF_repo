"""Compatibility wrapper for `p4_experiments.canonical.pipeline.phase09_stats`."""

from __future__ import annotations

from p4_experiments.canonical.pipeline.phase09_stats import *  # noqa: F401,F403
from p4_experiments.canonical.pipeline.phase09_stats import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())