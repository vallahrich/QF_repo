"""Compatibility wrapper for `p4_experiments.core.run_unit`."""

from __future__ import annotations

from p4_experiments.core.run_unit import *  # noqa: F401,F403
from p4_experiments.core.run_unit import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())
