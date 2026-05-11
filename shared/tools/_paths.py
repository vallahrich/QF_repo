"""Single shared `find_project_root()` used across `shared/tools/`.

Previously each of `logger.py`, `env_loader.py`, `paper_selector.py`, and
`openalex_client.py` re-implemented this. Centralised 2026-05-02 to reduce
drift surface; behaviour is unchanged (env override → walk-up `.git` →
parents[2] fallback).
"""

import os
from pathlib import Path


def find_project_root() -> Path:
    """Find the quantum-finance project root.

    Strategy:
    1. ``QUANTUM_FINANCE_PROJECT_ROOT`` env var (explicit override).
    2. Walk up from this file to find a directory containing ``.git``.
    3. Fallback: two levels up from ``shared/tools/``.
    """
    override = os.getenv("QUANTUM_FINANCE_PROJECT_ROOT")
    if override:
        return Path(override)

    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / ".git").exists():
            return current
        current = current.parent

    return Path(__file__).resolve().parents[2]


# Backwards-compatible alias for callers that imported the underscored name.
_find_project_root = find_project_root
