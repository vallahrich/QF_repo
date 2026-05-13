"""Compatibility wrapper for `p4_experiments.canonical.audits.audit_phase06`."""

from __future__ import annotations

from p4_experiments.canonical.audits.audit_phase06 import *  # noqa: F401,F403
from p4_experiments.canonical.audits.audit_phase06 import main as _main


if __name__ == "__main__":
    raise SystemExit(_main())