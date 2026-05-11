#!/usr/bin/env python3
"""Push classification results to Zotero — add tags and assign to collections.

Reads processed paper markdown files, extracts topic/methodology/idea tags and
the zotero_key from frontmatter, then:
  1. Adds all tags to each Zotero item
  2. Assigns items to the matching tier-2 collection(s) based on topic_tags

Usage:
    python -m p2_systematic_review.s2_classification.scripts.push_tags_to_zotero
    python -m p2_systematic_review.s2_classification.scripts.push_tags_to_zotero --dry-run
    python -m p2_systematic_review.s2_classification.scripts.push_tags_to_zotero --paper 2024_Author_Title.md
"""

import argparse
import json
import os
import sys
from pathlib import Path

_STEP2_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP2_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from shared.tools.env_loader import load_env
from shared.tools.logger import get_logger
from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter
from p2_systematic_review.s2_classification.scripts.fetch_from_zotero import ZoteroClient

logger = get_logger("push_tags_to_zotero")

load_env()

PROCESSED_DIR = os.path.join(_STEP2_ROOT, "output", "processed")
COLLECTION_MAP = os.path.join(_PROJECT_ROOT, "shared", "config", "zotero_collection_map.json")


def _load_collection_map() -> dict:
    """Load the tier-2 group → collection key mapping."""
    with open(COLLECTION_MAP, encoding="utf-8") as f:
        cmap = json.load(f)
    return cmap.get("tiers", {}).get("tier-2", {}).get("groups", {})


def _collect_papers(paper_name: str | None = None) -> list[dict]:
    """Read frontmatter from processed papers. Returns list of dicts."""
    papers = []
    if paper_name:
        path = os.path.join(PROCESSED_DIR, paper_name)
        if not os.path.isfile(path):
            logger.error("Paper not found: %s", path)
            return []
        fm = read_frontmatter(path)
        if fm:
            papers.append({"path": path, "name": paper_name, **fm})
    else:
        if not os.path.isdir(PROCESSED_DIR):
            logger.warning("Processed directory does not exist: %s", PROCESSED_DIR)
            return []
        for fname in sorted(os.listdir(PROCESSED_DIR)):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(PROCESSED_DIR, fname)
            fm = read_frontmatter(path)
            if fm:
                papers.append({"path": path, "name": fname, **fm})
    return papers


def _resolve_collections(topic_tags: list[str], group_map: dict) -> list[str]:
    """Resolve topic tags to Zotero collection keys."""
    keys = []
    for tag in topic_tags:
        if tag in group_map:
            keys.append(group_map[tag])
    return keys


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push classification tags and collection assignments to Zotero.",
    )
    parser.add_argument(
        "--paper", default=None,
        help="Process a single paper (filename, e.g. 2024_Author_Title.md)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without making API calls",
    )
    args = parser.parse_args()

    group_map = _load_collection_map()
    papers = _collect_papers(args.paper)
    logger.info("Found %d papers to process", len(papers))

    if not papers:
        print("No papers found.")
        return

    client = None if args.dry_run else ZoteroClient()

    stats = {"tags_pushed": 0, "collections_assigned": 0, "skipped_no_key": 0, "errors": 0}

    for paper in papers:
        zotero_key = paper.get("zotero_key", "")
        if not zotero_key:
            logger.warning("No zotero_key in %s — skipping", paper["name"])
            stats["skipped_no_key"] += 1
            continue

        # Collect all tags
        all_tags = []
        for tag_field in ("topic_tags", "methodology_tags", "idea_tags"):
            tags = paper.get(tag_field, [])
            if isinstance(tags, list):
                all_tags.extend(tags)

        # Resolve collections
        topic_tags = paper.get("topic_tags", []) or []
        collection_keys = _resolve_collections(topic_tags, group_map)

        if args.dry_run:
            print(f"  {paper['name']}:")
            print(f"    zotero_key: {zotero_key}")
            print(f"    tags to add: {all_tags}")
            print(f"    collections: {collection_keys}")
            continue

        # Push tags
        try:
            if all_tags:
                client.add_tags(zotero_key, all_tags)
                stats["tags_pushed"] += 1
        except Exception as exc:
            logger.error("Failed to add tags to %s: %s", zotero_key, exc)
            stats["errors"] += 1

        # Assign to collections
        for coll_key in collection_keys:
            try:
                client.add_to_collection(zotero_key, coll_key)
                stats["collections_assigned"] += 1
            except Exception as exc:
                logger.error("Failed to assign %s to collection %s: %s", zotero_key, coll_key, exc)
                stats["errors"] += 1

    print(f"\nDone: {stats['tags_pushed']} tagged, "
          f"{stats['collections_assigned']} collection assignments, "
          f"{stats['skipped_no_key']} skipped (no key), "
          f"{stats['errors']} errors")


if __name__ == "__main__":
    main()
