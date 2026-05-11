"""Release-time invariants test for the P3 freeze (added 2026-05-02).

These are not behavioural tests; they are *structural* invariants that must
hold at the freeze point. They run cheaply, surface drift fast, and act as
the freeze gate's last line of defence.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_P3_ROOT = _TESTS_DIR.parent
_REPO_ROOT = _P3_ROOT.parent

S6_DIR = _P3_ROOT / "s6_silo_framing"
README = _P3_ROOT / "README.md"
ARCHIVE = _P3_ROOT / "_archive"
FILTERED_CONSENSUS = _P3_ROOT / "s3_quantum_advantage" / "combined" / "output" / "consensus_summary.filtered.json"
RAW_CONSENSUS = _P3_ROOT / "s3_quantum_advantage" / "combined" / "output" / "consensus_summary.json"


def test_s6_silo_framing_state_is_disclosed():
    """s6 must carry a status banner that matches its disk state.

    s6 is pilot-complete (trading_execution only) as of 2026-05-02; the
    folder contains scaffolding (briefs/, extractions/, prompts/, scripts/)
    plus a README. Either the README declares the pilot/deferred status
    explicitly, or the test fails (catches a future drift where someone
    silently expands s6 without updating the status doc).
    """
    assert S6_DIR.is_dir(), f"{S6_DIR} should exist"
    s6_readme = S6_DIR / "README.md"
    assert s6_readme.is_file(), "s6_silo_framing/README.md must exist"
    s6_text = s6_readme.read_text(encoding="utf-8").lower()
    assert ("pilot" in s6_text or "deferred" in s6_text or "pending" in s6_text), \
        "s6 README must disclose its pilot/deferred/pending state"

    # Top-level README must also reference s6 honestly (deferred OR pilot).
    text = README.read_text(encoding="utf-8")
    assert "s6_silo_framing" in text, "top-level README must mention s6"


def test_no_active_python_imports_archive():
    """Active Python code must not import from _archive/.

    Walks every .py under p3_thematic_synthesis/ (excluding _archive/ itself
    and __pycache__) and asserts no `from ... _archive` / `import ... _archive`.
    """
    if not ARCHIVE.is_dir():
        pytest.skip("_archive/ does not exist")

    # Match real import statements only; skip when `_archive` appears inside
    # a string literal, comment, or assertion message.
    pat = re.compile(r"^\s*(?:from|import)\s+[A-Za-z_.][\w.]*_archive\b", re.MULTILINE)
    offenders: list[str] = []
    for py in _P3_ROOT.rglob("*.py"):
        # Skip files under _archive/ itself and pycache
        if "_archive" in py.parts or "__pycache__" in py.parts:
            continue
        # Skip this test file itself — the regex literal would self-flag.
        if py == Path(__file__):
            continue
        text = py.read_text(encoding="utf-8", errors="replace")
        if pat.search(text):
            offenders.append(str(py.relative_to(_P3_ROOT)))
    assert not offenders, f"active code imports from _archive/: {offenders}"

def test_filtered_consensus_post_dates_raw_consensus():
    """If both files exist, the filtered view must not be older than the raw.

    Otherwise the filter has gone stale relative to a post-filter
    re-aggregation and downstream consumers may read inconsistent views.
    """
    if not (RAW_CONSENSUS.is_file() and FILTERED_CONSENSUS.is_file()):
        pytest.skip("consensus files not present")
    raw_mtime = RAW_CONSENSUS.stat().st_mtime
    filtered_mtime = FILTERED_CONSENSUS.stat().st_mtime
    assert filtered_mtime >= raw_mtime, (
        f"consensus_summary.filtered.json (mtime={filtered_mtime}) is older "
        f"than consensus_summary.json (mtime={raw_mtime}); "
        f"re-run scripts/filter_consensus.py"
    )
