#!/usr/bin/env python3
"""Fetch documents per-silo from Zotero and save local copies.

For each problem silo, reads config.yaml → resolves tier2_group to a Zotero
collection key → fetches papers → saves PDFs and processed markdown into
the silo's documents/ folder.

Also copies the matching processed markdown from p2_systematic_review/output/processed/
if it exists locally.

Usage:
    # Fetch all silos
    python -m p3_thematic_synthesis.shared.scripts.fetch_silo_docs

    # Fetch a single silo
    python -m p3_thematic_synthesis.shared.scripts.fetch_silo_docs --silo portfolio_optimization

    # Dry run (no downloads)
    python -m p3_thematic_synthesis.shared.scripts.fetch_silo_docs --dry-run

    # List available silos
    python -m p3_thematic_synthesis.shared.scripts.fetch_silo_docs --list
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

import yaml

_STEP3_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP3_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from shared.tools.env_loader import load_env
from shared.tools.logger import get_logger
from p2_systematic_review.s2_classification.scripts.fetch_from_zotero import ZoteroClient
from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter

logger = get_logger("fetch_silo_docs")

load_env()

PROBLEMS_DIR = os.path.join(_STEP3_ROOT, "problems")
PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")
COLLECTION_MAP = os.path.join(_PROJECT_ROOT, "shared", "config", "zotero_collection_map.json")


def _load_tier2_groups() -> dict[str, str]:
    """Load tier-2 group → Zotero collection key mapping."""
    with open(COLLECTION_MAP, encoding="utf-8") as f:
        cmap = json.load(f)
    return cmap.get("tiers", {}).get("tier-2", {}).get("groups", {})


def _discover_silos() -> list[dict]:
    """Find all problem silos with config.yaml files."""
    silos = []
    if not os.path.isdir(PROBLEMS_DIR):
        return silos
    for name in sorted(os.listdir(PROBLEMS_DIR)):
        config_path = os.path.join(PROBLEMS_DIR, name, "config.yaml")
        if os.path.isfile(config_path):
            with open(config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            silos.append({
                "name": name,
                "path": os.path.join(PROBLEMS_DIR, name),
                "config": config,
            })
    return silos


def _copy_local_processed(silo_name: str, topic_tag: str, docs_dir: str) -> int:
    """Copy processed markdown files matching this silo's topic tag.

    Returns the number of files copied.
    """
    copied = 0
    if not os.path.isdir(PROCESSED_DIR):
        return copied

    for fname in os.listdir(PROCESSED_DIR):
        if not fname.endswith(".md"):
            continue
        path = os.path.join(PROCESSED_DIR, fname)
        fm = read_frontmatter(path)
        if not fm:
            continue
        topic_tags = fm.get("topic_tags", []) or []
        if topic_tag in topic_tags:
            dest = os.path.join(docs_dir, fname)
            if not os.path.isfile(dest):
                shutil.copy2(path, dest)
                copied += 1
    return copied


def _fetch_from_zotero(
    client: ZoteroClient,
    collection_key: str,
    docs_dir: str,
) -> dict:
    """Fetch PDFs from a Zotero collection into docs_dir/pdfs/."""
    pdfs_dir = os.path.join(docs_dir, "pdfs")
    os.makedirs(pdfs_dir, exist_ok=True)

    items = client.get_collection_items(collection_key)
    stats = {"fetched": 0, "cached": 0, "no_pdf": 0}

    for item in items:
        data = item["data"]
        item_key = item["key"]

        # Generate filename
        year = data.get("date", "")[:4] or "XXXX"
        creators = data.get("creators", [])
        author = creators[0].get("lastName", "Unknown") if creators else "Unknown"
        title_words = data.get("title", "Untitled").split()[:3]
        short = "_".join(w for w in title_words if w.isalpha())[:30]
        pdf_name = f"{year}_{author}_{short}.pdf"
        pdf_path = os.path.join(pdfs_dir, pdf_name)

        if os.path.isfile(pdf_path):
            stats["cached"] += 1
            continue

        attachments = client.get_attachments(item_key)
        if not attachments:
            stats["no_pdf"] += 1
            continue

        att_key = attachments[0]["key"]
        if client.download_pdf(att_key, pdf_path):
            stats["fetched"] += 1
        else:
            stats["no_pdf"] += 1

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch per-silo documents from Zotero and local processed files.",
    )
    parser.add_argument(
        "--silo", default=None,
        help="Process a single silo (folder name, e.g. portfolio_optimization)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be done without downloading",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List available silos and exit",
    )
    parser.add_argument(
        "--skip-zotero", action="store_true",
        help="Only copy local processed files, skip Zotero downloads",
    )
    args = parser.parse_args()

    silos = _discover_silos()
    tier2_groups = _load_tier2_groups()

    if args.list:
        print(f"{'Silo':<30} {'tier2_group':<30} {'Collection Key'}")
        print("-" * 80)
        for silo in silos:
            group = silo["config"].get("tier2_group", "")
            coll = tier2_groups.get(group, "NOT FOUND")
            print(f"{silo['name']:<30} {group:<30} {coll}")
        print(f"\nTotal: {len(silos)} silos")
        return

    if args.silo:
        silos = [s for s in silos if s["name"] == args.silo]
        if not silos:
            print(f"Silo '{args.silo}' not found.")
            return

    client = None
    if not args.dry_run and not args.skip_zotero:
        client = ZoteroClient()

    for silo in silos:
        name = silo["name"]
        config = silo["config"]
        topic_tag = config.get("tier2_group", config.get("domain", ""))
        docs_dir = os.path.join(silo["path"], "documents")

        collection_key = tier2_groups.get(topic_tag)
        if not collection_key:
            logger.warning("No Zotero collection for silo %s (group: %s)", name, topic_tag)

        print(f"\n{'='*60}")
        print(f"Silo: {name} (topic: {topic_tag})")
        print(f"  Collection key: {collection_key or 'NONE'}")

        if args.dry_run:
            print(f"  Would save documents to: {docs_dir}")
            continue

        os.makedirs(docs_dir, exist_ok=True)

        # Copy local processed markdown
        local_copied = _copy_local_processed(name, topic_tag, docs_dir)
        print(f"  Local processed: {local_copied} copied")

        # Fetch from Zotero
        if client and collection_key:
            zotero_stats = _fetch_from_zotero(client, collection_key, docs_dir)
            print(f"  Zotero PDFs: {zotero_stats['fetched']} new, "
                  f"{zotero_stats['cached']} cached, "
                  f"{zotero_stats['no_pdf']} no PDF")
        elif args.skip_zotero:
            print("  Zotero: skipped (--skip-zotero)")
        else:
            print("  Zotero: skipped (no collection key)")


if __name__ == "__main__":
    main()
