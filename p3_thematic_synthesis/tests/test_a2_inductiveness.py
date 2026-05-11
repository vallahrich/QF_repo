"""Inductiveness safeguard test for s4 A2 memo compression.

Per `docs/EXECUTION_CHECKLIST.md` item 3.3 and writing-guide R-03, the A2
prompt must not receive Phase 2 taxonomy tags (PD/SA codes) as input — those
deductive anchors would compromise the inductive open-coding stance of
Phase 3.

Two surfaces are checked:

1. The A2 prompt template itself contains no taxonomy-anchor placeholders
   beyond the generic `{p2_frontmatter}` slot.
2. The production runner (`run_production.py`) strips `topic_tags`,
   `methodology_tags`, and `tags` from the frontmatter dict before
   substitution.

If either surface drifts, the inductiveness claim in §4.5 of the manuscript
becomes indefensible.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPT_PATH = REPO_ROOT / "p3_thematic_synthesis" / "prompts" / "a2_memo_compression_v2.txt"
RUNNER_PATH = REPO_ROOT / "p3_thematic_synthesis" / "scripts" / "run_production.py"


def test_a2_prompt_has_no_taxonomy_anchors() -> None:
    text = PROMPT_PATH.read_text(encoding="utf-8")
    forbidden = ["{topic_tags}", "{methodology_tags}", "topic_tags:", "methodology_tags:"]
    found = [token for token in forbidden if token in text]
    assert not found, (
        f"A2 prompt template contains forbidden taxonomy anchors: {found}. "
        "Phase 3 inductiveness requires PD/SA codes never to be fed into open coding."
    )


def test_runner_strips_taxonomy_tags_from_frontmatter() -> None:
    src = RUNNER_PATH.read_text(encoding="utf-8")
    # All three tag families must be popped from the loaded P2 frontmatter
    # before it is rendered into the A2 prompt.
    for key in ("topic_tags", "methodology_tags", "tags"):
        needle = f'meta.pop("{key}"'
        assert needle in src, (
            f"run_production.py must call {needle}, ...) before rendering A2. "
            "Inductiveness safeguard would otherwise be bypassed."
        )
