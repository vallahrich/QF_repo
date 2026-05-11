"""Re-export validation helpers for the processed-paper schema.

Promoted out of `tests/test_schema_validation.py` on 2026-05-02 so that
production code (and other test modules) can validate frontmatter without
importing from a sibling test module.

The canonical implementations live in `tests/test_schema_validation.py`
(REQUIRED_FIELDS / ENUM_RULES / REQUIRED_SECTIONS / validate_frontmatter /
validate_body_sections / validate_tags / validate_file). This module simply
re-exports them at a stable, non-test import path.
"""

from __future__ import annotations

import sys
from pathlib import Path

# The test module already does its own sys.path bootstrap; mirror it here so
# this re-export module works whether called from the repo root, from inside
# `p2_systematic_review/`, or from another package.
_P2_ROOT = Path(__file__).resolve().parents[2]
if str(_P2_ROOT) not in sys.path:
    sys.path.insert(0, str(_P2_ROOT))

from tests.test_schema_validation import (  # noqa: E402
    ENUM_RULES,
    REQUIRED_FIELDS,
    REQUIRED_SECTIONS,
    validate_body_sections,
    validate_file,
    validate_frontmatter,
    validate_tags,
)

__all__ = [
    "ENUM_RULES",
    "REQUIRED_FIELDS",
    "REQUIRED_SECTIONS",
    "validate_body_sections",
    "validate_file",
    "validate_frontmatter",
    "validate_tags",
]
