"""Validate every processed paper against the schema + tag vocabulary.

Loads every `output/processed/*.md`, runs `validate_file()`, and asserts that
all `topic_tags` and `methodology_tags` are present in the canonical
`shared/config/unified_taxonomy.json`. Skips papers listed in
`output/audit/excluded_post_classification.csv` (the documented retro-exclusion
mechanism per the 2026-05-02 amendment).

Added 2026-05-02 to surface tag-projection false positives as test failures.
"""

from __future__ import annotations

import csv
import json
import os
import sys
from pathlib import Path

import pytest

_TESTS_DIR = Path(__file__).resolve().parent
_P2_ROOT = _TESTS_DIR.parent
_REPO_ROOT = _P2_ROOT.parent

if str(_P2_ROOT) not in sys.path:
    sys.path.insert(0, str(_P2_ROOT))

from s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402

# Re-use validators from the existing schema test
from tests.test_schema_validation import (  # noqa: E402
    validate_frontmatter,
    validate_tags,
)

PROCESSED_DIR = _P2_ROOT / "output" / "processed"
EXCLUSION_CSV = _P2_ROOT / "output" / "audit" / "excluded_post_classification.csv"
TAXONOMY_PATH = _REPO_ROOT / "shared" / "config" / "unified_taxonomy.json"


@pytest.fixture(scope="module")
def tag_registry() -> dict:
    return json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def excluded_ids() -> set[str]:
    if not EXCLUSION_CSV.is_file():
        return set()
    with EXCLUSION_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        # Be liberal about column name (paper_id, id, ...).
        ids: set[str] = set()
        for row in reader:
            for key in ("paper_id", "id", "filename"):
                if key in row and row[key]:
                    ids.add(Path(row[key]).stem)
                    break
        return ids


def _processed_files() -> list[Path]:
    if not PROCESSED_DIR.is_dir():
        return []
    return sorted(p for p in PROCESSED_DIR.glob("*.md") if p.name != "README.md")


@pytest.mark.parametrize("md_path", _processed_files(), ids=lambda p: p.stem)
def test_processed_paper_schema_and_tags(md_path: Path, tag_registry, excluded_ids):
    """Each processed paper must have valid frontmatter and registered tags.

    Papers listed in `excluded_post_classification.csv` are skipped (these are
    known false-positive inclusions retroactively excluded from downstream
    consumers per the 2026-05-02 amendment).
    """
    if md_path.stem in excluded_ids:
        pytest.skip(f"{md_path.stem} is in excluded_post_classification.csv")

    metadata, _ = read_frontmatter(str(md_path))
    assert metadata, f"{md_path.name}: empty or missing frontmatter"

    fm_errors = validate_frontmatter(metadata)
    tag_errors = validate_tags(metadata, tag_registry)
    errors = fm_errors + tag_errors
    assert not errors, f"{md_path.name}: {errors}"
