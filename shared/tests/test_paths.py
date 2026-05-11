"""Tests for shared.tools._paths.find_project_root (added 2026-05-02)."""

from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.tools._paths import find_project_root  # noqa: E402


def test_find_project_root_returns_project_root():
    root = find_project_root()
    assert (root / "README.md").is_file(), f"expected project README under {root}"
    assert (root / "docs" / "PROJECT_STATE.yaml").is_file(), f"expected PROJECT_STATE.yaml under {root}"
    assert (root / "shared" / "config" / "unified_taxonomy.json").is_file(), f"expected taxonomy under {root}"


def test_env_override_takes_precedence(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANTUM_FINANCE_PROJECT_ROOT", str(tmp_path))
    assert find_project_root() == tmp_path
    monkeypatch.delenv("QUANTUM_FINANCE_PROJECT_ROOT", raising=False)
