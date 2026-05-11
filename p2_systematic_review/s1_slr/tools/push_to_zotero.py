#!/usr/bin/env python3
"""Push SLR-included papers to Zotero — create a collection and add items.

Reads included_for_coding.csv + paper_id_bridge.csv to find Zotero item keys
for all included papers, creates an "SLR Included" collection under slr_results,
and adds each paper to it.

Usage:
    python -m p2_systematic_review.s1_slr.tools.push_to_zotero
    python -m p2_systematic_review.s1_slr.tools.push_to_zotero --dry-run
    python -m p2_systematic_review.s1_slr.tools.push_to_zotero --collection-name "SLR Included v2"
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.env_loader import load_env
from shared.tools.logger import get_logger
from p2_systematic_review.s2_classification.scripts.fetch_from_zotero import ZoteroClient

logger = get_logger("push_to_zotero")

load_env()

SLR_ROOT = str(Path(__file__).resolve().parents[1])
INCLUDED_CSV = os.path.join(SLR_ROOT, "05_screening", "included_for_coding.csv")
BRIDGE_CSV = os.path.join(_PROJECT_ROOT, "shared", "bridge", "paper_id_bridge.csv")
COLLECTION_MAP = os.path.join(_PROJECT_ROOT, "shared", "config", "zotero_collection_map.json")


def load_included_ids() -> set[str]:
    """Load paper IDs from included_for_coding.csv."""
    ids = set()
    with open(INCLUDED_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("final_decision") == "include":
                ids.add(row["paper_id"])
    return ids


def load_bridge() -> dict[str, dict]:
    """Load paper_id_bridge.csv into a dict keyed by slr_paper_id."""
    bridge = {}
    with open(BRIDGE_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bridge[row["slr_paper_id"]] = row
    return bridge


def get_slr_parent_key() -> str:
    """Read the SLR results parent collection key from the collection map."""
    with open(COLLECTION_MAP, encoding="utf-8") as f:
        cmap = json.load(f)
    return cmap["slr_results"]["collection_key"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push SLR-included papers to a Zotero collection.",
    )
    parser.add_argument(
        "--collection-name", default="SLR Included",
        help="Name for the Zotero collection (default: 'SLR Included')",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without making API calls",
    )
    args = parser.parse_args()

    # Load data
    included_ids = load_included_ids()
    bridge = load_bridge()
    logger.info("Included papers: %d, Bridge entries: %d", len(included_ids), len(bridge))

    # Resolve Zotero item keys
    item_keys = []
    missing = []
    for paper_id in sorted(included_ids):
        entry = bridge.get(paper_id)
        if entry and entry.get("zotero_item_key"):
            item_keys.append(entry["zotero_item_key"])
        else:
            missing.append(paper_id)

    logger.info("Resolved %d Zotero item keys, %d missing", len(item_keys), len(missing))
    if missing:
        logger.warning("Papers without Zotero keys (first 10): %s", missing[:10])

    if args.dry_run:
        print(f"Would create collection '{args.collection_name}' under slr_results")
        print(f"Would add {len(item_keys)} items to the collection")
        print(f"Missing from bridge: {len(missing)} papers")
        return

    # Create collection and add items
    client = ZoteroClient()
    parent_key = get_slr_parent_key()

    collection_key = client.create_collection(args.collection_name, parent_key)
    print(f"Created collection: {args.collection_name} → {collection_key}")

    result = client.add_items_to_collection(item_keys, collection_key)
    print(f"Added {result['added']} items, {result['skipped']} failed")
    if missing:
        print(f"{len(missing)} included papers not in Zotero (no bridge entry)")


if __name__ == "__main__":
    main()
