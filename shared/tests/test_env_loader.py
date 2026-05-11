"""Tests for shared.tools.env_loader (added 2026-05-02)."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.tools.env_loader import _sync_env  # noqa: E402


@pytest.fixture
def clean_env(monkeypatch):
    monkeypatch.delenv("AZURE_API_KEY", raising=False)
    monkeypatch.delenv("AZURE_OPENAI_API_KEY", raising=False)
    return monkeypatch


def test_sync_env_populates_b_from_a(clean_env):
    clean_env.setenv("AZURE_API_KEY", "abc")
    _sync_env("AZURE_API_KEY", "AZURE_OPENAI_API_KEY")
    import os
    assert os.environ["AZURE_OPENAI_API_KEY"] == "abc"


def test_sync_env_populates_a_from_b(clean_env):
    clean_env.setenv("AZURE_OPENAI_API_KEY", "def")
    _sync_env("AZURE_API_KEY", "AZURE_OPENAI_API_KEY")
    import os
    assert os.environ["AZURE_API_KEY"] == "def"


def test_sync_env_warns_on_divergence(clean_env, caplog):
    clean_env.setenv("AZURE_API_KEY", "alpha")
    clean_env.setenv("AZURE_OPENAI_API_KEY", "beta")
    with caplog.at_level(logging.WARNING, logger="qfin.env_loader"):
        _sync_env("AZURE_API_KEY", "AZURE_OPENAI_API_KEY")
    import os
    # Both preserved as-is.
    assert os.environ["AZURE_API_KEY"] == "alpha"
    assert os.environ["AZURE_OPENAI_API_KEY"] == "beta"
    # And a warning was emitted.
    assert any("divergence" in r.message.lower() for r in caplog.records)


def test_sync_env_noop_when_both_unset(clean_env):
    _sync_env("AZURE_API_KEY", "AZURE_OPENAI_API_KEY")
    import os
    assert "AZURE_API_KEY" not in os.environ
    assert "AZURE_OPENAI_API_KEY" not in os.environ
