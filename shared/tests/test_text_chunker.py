"""Tests for shared.tools.text_chunker (added 2026-05-02)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from shared.tools import text_chunker  # noqa: E402


def test_truncate_tokens_zero_returns_full_text():
    text = "hello world " * 10
    assert text_chunker.truncate_tokens(text, 0) == text


def test_truncate_tokens_short_text_unchanged():
    text = "hello world"
    assert text_chunker.truncate_tokens(text, 100) == text


def test_truncate_tokens_long_text_is_truncated():
    text = "abcdefgh " * 1000  # 9000 chars
    out = text_chunker.truncate_tokens(text, max_tokens=10)
    assert len(out) <= len(text)
    assert out  # non-empty


def test_chunk_by_sections_no_split_when_under_budget():
    text = "# Heading\n\nbody body body\n"
    chunks = text_chunker.chunk_by_sections(text, max_tokens=1000)
    assert chunks == [text]


def test_chunk_by_sections_splits_on_headings():
    body = "lorem ipsum " * 50  # ~600 chars per section
    text = f"# A\n\n{body}\n\n# B\n\n{body}\n\n# C\n\n{body}\n"
    chunks = text_chunker.chunk_by_sections(text, max_tokens=200)
    assert len(chunks) >= 2  # forced to split
    assert all(c.strip() for c in chunks)


def test_chunk_by_sections_oversized_section_hard_cut():
    # Single long paragraph with no headings — exercises the hard-cut path.
    text = "wordone " * 5000  # ~40_000 chars
    chunks = text_chunker.chunk_by_sections(text, max_tokens=200)
    assert len(chunks) > 1
    # No chunk should be wildly over the heuristic budget (heuristic = 4 chars/token).
    assert all(len(c) <= 200 * text_chunker._CHARS_PER_TOKEN + 5 for c in chunks)


def test_fallback_path_when_encoder_unavailable(monkeypatch):
    """Force the heuristic fallback by making _get_encoder return None."""
    monkeypatch.setattr(text_chunker, "_get_encoder", lambda model: None)
    text = "abcd" * 1000  # 4000 chars
    out = text_chunker.truncate_tokens(text, max_tokens=10)
    # heuristic: 10 tokens * 4 chars/token = 40 chars
    assert len(out) == 40


def test_count_tokens_returns_positive_integer():
    n = text_chunker._count_tokens("hello world", model=None)
    assert isinstance(n, int) and n >= 1
