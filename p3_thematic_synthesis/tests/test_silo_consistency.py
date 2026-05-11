"""Silo-consistency tests for P3 (added 2026-05-02).

Asserts that the filtered consensus summary references only silos marked
``active`` in ``shared/config/silo_inclusion.json``. Run after
``scripts/filter_consensus.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_P3_ROOT = _TESTS_DIR.parent
_REPO_ROOT = _P3_ROOT.parent

SILO_INCLUSION = _REPO_ROOT / "shared" / "config" / "silo_inclusion.json"
FILTERED = _P3_ROOT / "s3_quantum_advantage" / "combined" / "output" / "consensus_summary.filtered.json"


def _active_silo_keys() -> set[str]:
    raw = json.loads(SILO_INCLUSION.read_text(encoding="utf-8"))
    keys: set[str] = set()
    for silo in raw.get("active_silos", []):
        f = silo.get("folder", "").strip().lower()
        keys |= {f, f.replace("_", "-")}
    return keys


@pytest.mark.skipif(not FILTERED.is_file(),
                    reason="run scripts/filter_consensus.py first")
def test_filtered_consensus_only_references_active_silos():
    payload = json.loads(FILTERED.read_text(encoding="utf-8"))
    active = _active_silo_keys()
    seen = set(payload.get("by_silo", {}).keys())
    bad = {k for k in seen if k.lower() not in active}
    assert not bad, f"filtered consensus still references inactive silos: {sorted(bad)}"
