#!/usr/bin/env python3
"""Batch extraction — fetch PDFs from Zotero Background collection and run extraction.

Usage:
    # Extract first 5 papers (pilot batch)
    python -m p1_framework_synthesis.scripts.run_batch --limit 5

    # Extract all papers in the Background collection
    python -m p1_framework_synthesis.scripts.run_batch

    # List items without extracting
    python -m p1_framework_synthesis.scripts.run_batch --list

    # Skip already-extracted papers (resume mode)
    python -m p1_framework_synthesis.scripts.run_batch --skip-existing
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

import requests

from shared.tools.env_loader import load_env
from shared.tools.logger import get_logger

logger = get_logger("phase1_batch")

load_env()

PHASE1_ROOT = str(Path(__file__).resolve().parents[1])
EXTRACTIONS_DIR = os.path.join(PHASE1_ROOT, "s1_extractions")
PDFS_DIR = os.path.join(PHASE1_ROOT, "s1_extractions", "pdfs")
COLLECTION_MAP = os.path.join(_PROJECT_ROOT, "shared", "config", "zotero_collection_map.json")

API_BASE = "https://api.zotero.org"
GROUP_ID = os.getenv("ZOTERO_GROUP_ID", "")
API_KEY = os.getenv("ZOTERO_API_KEY", "")
HEADERS = {
    "Zotero-API-Key": API_KEY,
    "Zotero-API-Version": "3",
}
_REQUEST_DELAY = 0.25


def _get_background_key() -> str:
    """Read the Background collection key from the collection map."""
    with open(COLLECTION_MAP, encoding="utf-8") as f:
        cmap = json.load(f)
    return cmap["phase1_collection"]["background"]


def _zotero_get(path: str, params: dict | None = None) -> requests.Response:
    """Make a rate-limited GET request to the Zotero API."""
    url = f"{API_BASE}/groups/{GROUP_ID}{path}"
    time.sleep(_REQUEST_DELAY)
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if resp.status_code == 429:
        retry_after = int(resp.headers.get("Retry-After", 5))
        logger.warning("Rate limited, waiting %d seconds", retry_after)
        time.sleep(retry_after)
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    resp.raise_for_status()
    return resp


def fetch_collection_items(collection_key: str, limit: int = 0) -> list[dict]:
    """Fetch items from a Zotero collection (handles pagination)."""
    items = []
    start = 0
    page_size = min(100, limit) if limit > 0 else 100

    while True:
        params = {
            "format": "json",
            "itemType": "-attachment",
            "limit": page_size,
            "start": start,
        }
        resp = _zotero_get(f"/collections/{collection_key}/items", params)
        page_items = resp.json()
        items.extend(page_items)

        total = int(resp.headers.get("Total-Results", 0))
        start += len(page_items)

        if limit > 0 and len(items) >= limit:
            items = items[:limit]
            break
        if start >= total or not page_items:
            break

    return items


def generate_name(item_data: dict) -> str:
    """Generate a clean filename from Zotero item metadata."""
    date_str = item_data.get("date", "")
    # Extract a 4-digit year from the date string (handles ISO, US, and other formats)
    year_match = re.search(r"\b(\d{4})\b", date_str)
    year = year_match.group(1) if year_match else "XXXX"

    creators = item_data.get("creators", [])
    if creators:
        first_author = creators[0].get("lastName", creators[0].get("name", "Unknown"))
    else:
        first_author = "Unknown"
    first_author = re.sub(r"[^a-zA-Z]", "", first_author)

    title = item_data.get("title", "Untitled")
    words = re.findall(r"[A-Za-z]+", title)
    stop_words = {
        "a", "an", "the", "of", "in", "on", "for", "and", "or",
        "to", "with", "by", "from", "is", "are", "was", "were",
    }
    significant = [w for w in words if w.lower() not in stop_words][:4]
    short_title = "_".join(w.capitalize() for w in significant) if significant else "Untitled"

    return f"{year}_{first_author}_{short_title}"


def download_pdf(item_key: str, output_path: str) -> bool:
    """Download the PDF attachment for an item. Returns True on success."""
    # Get child attachments
    resp = _zotero_get(f"/items/{item_key}/children")
    attachments = [
        child for child in resp.json()
        if child["data"].get("itemType") == "attachment"
        and child["data"].get("contentType") == "application/pdf"
    ]

    if not attachments:
        return False

    att_key = attachments[0]["key"]
    url = f"{API_BASE}/groups/{GROUP_ID}/items/{att_key}/file"
    time.sleep(_REQUEST_DELAY)
    resp = requests.get(url, headers=HEADERS, timeout=60, stream=True)
    if resp.status_code != 200:
        logger.warning("Failed to download PDF %s: HTTP %d", att_key, resp.status_code)
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    return True


def extract_pdf(pdf_path: str, name: str, model: str, temperature: float) -> dict | None:
    """Run the Phase 1 extraction prompt on a PDF."""
    from p1_framework_synthesis.scripts.extract_document import extract_document, read_pdf

    try:
        document_text = read_pdf(pdf_path)
    except Exception as exc:
        logger.error("Failed to read PDF %s: %s", pdf_path, exc)
        return None

    if not document_text.strip():
        logger.warning("Empty PDF text: %s", pdf_path)
        return None

    logger.info("Extracting %s (%d chars)", name, len(document_text))
    try:
        return extract_document(document_text, model=model, temperature=temperature)
    except Exception as exc:
        logger.error("Extraction failed for %s: %s", name, exc)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch Phase 1 extraction from Zotero Background collection.",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max papers to process (0 = all). Default: 0",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List items only — no download or extraction",
    )
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="Skip papers that already have an extraction JSON",
    )
    parser.add_argument(
        "--model", default="gpt-5.1",
        help="LLM model to use (default: gpt-5.1)",
    )
    parser.add_argument(
        "--temperature", type=float, default=0.2,
        help="LLM temperature (default: 0.2)",
    )
    parser.add_argument(
        "--download-only", action="store_true",
        help="Download PDFs only — no LLM extraction",
    )
    args = parser.parse_args()

    if not GROUP_ID or not API_KEY:
        logger.error("ZOTERO_GROUP_ID and ZOTERO_API_KEY must be set in .env")
        sys.exit(1)

    collection_key = _get_background_key()
    logger.info("Fetching items from Background collection: %s", collection_key)

    items = fetch_collection_items(collection_key, limit=args.limit)
    logger.info("Found %d items", len(items))

    if args.list:
        for i, item in enumerate(items, 1):
            d = item["data"]
            name = generate_name(d)
            title = d.get("title", "?")[:80]
            print(f"  {i:>3}. [{item['key']}] {name}: {title}")
        return

    # Process each item
    os.makedirs(EXTRACTIONS_DIR, exist_ok=True)
    os.makedirs(PDFS_DIR, exist_ok=True)
    results_summary = {"success": 0, "no_pdf": 0, "failed": 0, "skipped": 0, "low_quality": 0}

    for i, item in enumerate(items, 1):
        data = item["data"]
        item_key = item["key"]
        name = generate_name(data)
        output_json = os.path.join(EXTRACTIONS_DIR, f"{name}.json")

        if args.skip_existing and os.path.isfile(output_json):
            logger.info("[%d/%d] Skipping (exists): %s", i, len(items), name)
            results_summary["skipped"] += 1
            continue

        title = data.get("title", "?")[:60]
        print(f"\n[{i}/{len(items)}] {name}")
        print(f"  Title: {title}")

        # Download PDF to persistent local copy
        pdf_path = os.path.join(PDFS_DIR, f"{name}.pdf")

        try:
            if os.path.isfile(pdf_path):
                logger.info("  Using cached PDF: %s", pdf_path)
            elif not download_pdf(item_key, pdf_path):
                logger.warning("  No PDF attachment for: %s", name)
                results_summary["no_pdf"] += 1
                continue

            pdf_size = os.path.getsize(pdf_path)
            print(f"  PDF: {pdf_size / 1024:.0f} KB  ->  {pdf_path}")

            if args.download_only:
                results_summary["success"] += 1
                continue

            # Run extraction
            result = extract_pdf(pdf_path, name, args.model, args.temperature)

            if result is None:
                results_summary["failed"] += 1
                continue

            # Add Zotero metadata to the result
            result["_zotero"] = {
                "item_key": item_key,
                "collection": collection_key,
            }

            # Save
            with open(output_json, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            n_problems = len(result.get("problem_domains", []))
            n_solutions = len(result.get("solution_approaches", []))
            n_claims = len(result.get("key_claims", []))
            quality = result.get("_extraction_quality", {})
            valid = quality.get("valid", True)
            q_reason = quality.get("reason", "")
            status = "OK" if valid else f"LOW QUALITY ({q_reason})"
            print(f"  Extracted: {n_problems} problems, {n_solutions} solutions, {n_claims} claims -- {status}")
            print(f"  Saved: {output_json}")
            if valid:
                results_summary["success"] += 1
            else:
                results_summary["low_quality"] += 1

        finally:
            pass  # PDFs are kept locally for git tracking

    # Print summary
    print(f"\n{'=' * 50}")
    print(f"Batch complete: {results_summary['success']} success, "
          f"{results_summary['low_quality']} low quality, "
          f"{results_summary['no_pdf']} no PDF, "
          f"{results_summary['failed']} failed, "
          f"{results_summary['skipped']} skipped")


if __name__ == "__main__":
    main()
