#!/usr/bin/env python3
"""Consolidate Phase 1 extraction JSONs into a single review data file.

Reads all extraction JSONs from s1_extractions/ and produces a single
review_data.json in s2_coding/ with review annotations and tag definitions.

Usage:
    python -m p1_framework_synthesis.scripts.build_review_data
    python -m p1_framework_synthesis.scripts.build_review_data --output custom_path.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

PHASE1_ROOT = str(Path(__file__).resolve().parents[1])
EXTRACTIONS_DIR = os.path.join(PHASE1_ROOT, "s1_extractions")
DEFAULT_OUTPUT = os.path.join(PHASE1_ROOT, "s2_coding", "review_data.json")

CATEGORIES = [
    "problem_domains",
    "solution_approaches",
    "problem_solution_mappings",
    "key_claims",
    "maturity_indicators",
    "open_questions",
]

DEFAULT_TAG_DEFINITIONS = {
    "paper_section": [
        "introduction",
        "background",
        "methodology",
        "results",
        "discussion",
        "conclusion",
        "future-work",
    ],
    "code_type": [
        "problem",
        "solution",
        "mapping",
        "claim",
        "maturity",
        "question",
    ],
    "classification": [],
}


def _empty_review() -> dict:
    """Return a blank review annotation object."""
    return {
        "decision": None,
        "tags": {
            "paper_section": [],
            "code_type": [],
            "classification": [],
        },
    }


def load_extractions() -> list[dict]:
    """Load all extraction JSONs sorted by filename."""
    results = []
    for fname in sorted(os.listdir(EXTRACTIONS_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(EXTRACTIONS_DIR, fname)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        data["_filename"] = fname.removesuffix(".json")
        results.append(data)
    return results


def build_review_data(extractions: list[dict]) -> dict:
    """Build the consolidated review data structure."""
    papers = []

    for ext in extractions:
        paper = {
            "id": ext["_filename"],
            "metadata": ext.get("metadata", {}),
        }

        for category in CATEGORIES:
            items = []
            for item in ext.get(category, []):
                entry = dict(item)
                entry["review"] = _empty_review()
                items.append(entry)
            paper[category] = items

        papers.append(paper)

    return {
        "tag_definitions": dict(DEFAULT_TAG_DEFINITIONS),
        "papers": papers,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consolidate extraction JSONs into review_data.json.",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    extractions = load_extractions()
    if not extractions:
        print("No extraction JSONs found in", EXTRACTIONS_DIR)
        sys.exit(1)

    review_data = build_review_data(extractions)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(review_data, f, indent=2, ensure_ascii=False)

    total_items = sum(
        len(p[cat]) for p in review_data["papers"] for cat in CATEGORIES
    )
    print(f"Built review data: {len(review_data['papers'])} papers, {total_items} items")
    print(f"Saved to: {args.output}")


if __name__ == "__main__":
    main()
