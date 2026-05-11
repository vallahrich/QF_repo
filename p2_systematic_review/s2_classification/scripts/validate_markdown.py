"""CLI tool to validate markdown paper files against the frontmatter schema."""

import argparse
import glob
import json
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path
_STEP2_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP2_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from p2_systematic_review.tests.test_schema_validation import (  # noqa: E402
    validate_body_sections,
    validate_frontmatter,
    validate_tags,
)

logger = get_logger("validate_markdown")

# Use unified_taxonomy.json instead of the old tag_registry.json
_TAXONOMY_PATH = os.path.join(_PROJECT_ROOT, "shared", "config", "unified_taxonomy.json")


def _load_tag_registry() -> dict:
    with open(_TAXONOMY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_file(filepath: str) -> list[str]:
    """Run all validations on a single markdown file. Returns list of errors."""
    metadata, body = read_frontmatter(filepath)
    if not metadata and not body:
        return [f"File not found or empty: {filepath}"]

    tag_registry = _load_tag_registry()
    errors: list[str] = []
    errors.extend(validate_frontmatter(metadata))
    errors.extend(validate_body_sections(body))
    errors.extend(validate_tags(metadata, tag_registry))
    return errors


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate markdown paper files against the frontmatter schema."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to a single markdown file to validate.")
    group.add_argument(
        "--batch",
        action="store_true",
        help="Validate all .md files in papers/processed/.",
    )
    args = parser.parse_args()

    if args.file:
        files = [args.file]
    else:
        processed_dir = os.path.join(_STEP2_ROOT, "output", "processed")
        files = sorted(glob.glob(os.path.join(processed_dir, "*.md")))
        if not files:
            logger.info("No markdown files found in papers/processed/")
            print("No markdown files found in papers/processed/")
            return

    any_failed = False

    for filepath in files:
        errors = validate_file(filepath)
        basename = os.path.relpath(filepath, _PROJECT_ROOT)
        if errors:
            any_failed = True
            print(f"FAIL: {basename}")
            for error in errors:
                print(f"  - {error}")
            logger.warning("Validation failed", extra={"file": basename, "errors": errors})
        else:
            print(f"PASS: {basename}")
            logger.info("Validation passed", extra={"file": basename})

    if any_failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
