"""Compatibility wrapper for `p4_experiments.canonical.pipeline.phase10_manuscript_artifacts`."""

from __future__ import annotations

from p4_experiments.canonical.pipeline.phase10_manuscript_artifacts import *  # noqa: F401,F403
from p4_experiments.canonical.pipeline.phase10_manuscript_artifacts import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())