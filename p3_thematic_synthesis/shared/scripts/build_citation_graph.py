"""Build a citation index from OpenAlex data for all processed papers.

Usage examples:
    # Build citation graph (uses cache)
    python scripts/build_citation_graph.py

    # Rebuild from scratch, ignoring cache
    python scripts/build_citation_graph.py --rebuild

    # Change minimum citation threshold for missing papers
    python scripts/build_citation_graph.py --missing-threshold 3
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
_STEP3_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP3_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from shared.tools.openalex_client import OpenAlexClient  # noqa: E402

logger = get_logger("build_citation_graph")

PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")
CROSS_CUTTING_DIR = os.path.join(_STEP3_ROOT, "cross_cutting")


def _normalize_doi(doi: str) -> str:
    """Lowercase and strip common URL prefixes from a DOI."""
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/",
                   "https://dx.doi.org/", "http://dx.doi.org/"):
        if doi.lower().startswith(prefix):
            doi = doi[len(prefix):]
            break
    return doi.lower()


def _collect_papers(processed_dir: str) -> list[dict]:
    """Return list of dicts with filename, doi, and filepath for each paper."""
    papers = []
    for fname in sorted(os.listdir(processed_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(processed_dir, fname)
        meta, _ = read_frontmatter(fpath)
        doi = meta.get("doi", "").strip()
        papers.append({"filename": fname, "doi": doi, "filepath": fpath})
    return papers


def build_citation_graph(
    root: str,
    rebuild: bool = False,
    missing_threshold: int = 2,
    email: str | None = None,
) -> dict:
    """Build the citation index and return the full data structure."""

    processed_dir = PROCESSED_DIR
    cache_dir = os.path.join(CROSS_CUTTING_DIR, "openalex_cache")

    if rebuild and os.path.isdir(cache_dir):
        logger.info("Clearing OpenAlex cache for full rebuild")
        shutil.rmtree(cache_dir)

    client = OpenAlexClient(email=email, cache_dir=cache_dir)

    # ---- 1. Collect papers and DOIs ----
    papers = _collect_papers(processed_dir)
    doi_to_filename: dict[str, str] = {}
    papers_with_dois = []
    papers_without_dois = []

    for p in papers:
        if p["doi"]:
            norm = _normalize_doi(p["doi"])
            doi_to_filename[norm] = p["filename"]
            papers_with_dois.append(p)
        else:
            papers_without_dois.append(p)

    logger.info(
        "Found %d papers: %d with DOIs, %d without",
        len(papers), len(papers_with_dois), len(papers_without_dois),
    )

    # ---- 2. Fetch work data and references for each paper ----
    paper_data: dict[str, dict] = {}
    # Map: normalized DOI → list of OpenAlex reference IDs
    all_reference_ids: set[str] = set()
    paper_ref_ids: dict[str, list[str]] = {}  # filename → ref IDs

    for idx, p in enumerate(papers_with_dois, 1):
        norm_doi = _normalize_doi(p["doi"])
        print(f"Processing paper {idx}/{len(papers_with_dois)}: "
              f"{p['filename']} (DOI: {p['doi']})")

        work = client.get_work_by_doi(p["doi"])
        cited_by_count = 0
        ref_ids: list[str] = []
        total_refs = 0

        if work:
            cited_by_count = work.get("cited_by_count", 0)
            ref_ids = work.get("referenced_works", [])
            total_refs = len(ref_ids)
            all_reference_ids.update(ref_ids)

        paper_ref_ids[p["filename"]] = ref_ids
        paper_data[p["filename"]] = {
            "doi": p["doi"],
            "openalex_cited_by_count": cited_by_count,
            "references_in_collection": [],
            "cited_by_in_collection": [],
            "total_references": total_refs,
        }

    # ---- 3. Resolve all reference IDs to DOIs ----
    ref_id_list = sorted(all_reference_ids)
    total_batches = (len(ref_id_list) + OpenAlexClient.BATCH_SIZE - 1) // OpenAlexClient.BATCH_SIZE
    logger.info(
        "Resolving %d unique references in %d batches",
        len(ref_id_list), total_batches,
    )

    # Map OpenAlex ID → resolved info
    openalex_id_to_info: dict[str, dict] = {}
    for batch_idx in range(0, len(ref_id_list), OpenAlexClient.BATCH_SIZE):
        batch_num = batch_idx // OpenAlexClient.BATCH_SIZE + 1
        print(f"Resolving references: batch {batch_num}/{total_batches}...")
        batch = ref_id_list[batch_idx : batch_idx + OpenAlexClient.BATCH_SIZE]
        resolved = client.resolve_openalex_ids(batch)
        for r in resolved:
            openalex_id_to_info[r["openalex_id"]] = r

    # ---- 4. Build cross-reference map ----
    # For each paper, check which of its references are in the collection
    # Also track references NOT in the collection for missing papers analysis
    missing_counter: dict[str, dict] = {}  # normalized_doi → info + citing papers

    for fname, ref_ids in paper_ref_ids.items():
        for ref_id in ref_ids:
            info = openalex_id_to_info.get(ref_id)
            if not info or not info.get("doi"):
                continue
            ref_doi_norm = _normalize_doi(info["doi"])
            if ref_doi_norm in doi_to_filename:
                # Reference is in the collection
                ref_fname = doi_to_filename[ref_doi_norm]
                paper_data[fname]["references_in_collection"].append(ref_fname)
                paper_data[ref_fname]["cited_by_in_collection"].append(fname)
            else:
                # Reference is NOT in the collection — candidate for missing papers
                if ref_doi_norm not in missing_counter:
                    missing_counter[ref_doi_norm] = {
                        "doi": info["doi"],
                        "title": info.get("title", ""),
                        "first_author": info.get("first_author", ""),
                        "year": info.get("year"),
                        "cited_by_in_collection": [],
                        "openalex_id": ref_id,
                    }
                missing_counter[ref_doi_norm]["cited_by_in_collection"].append(fname)

    # Deduplicate lists in paper_data
    for fname in paper_data:
        paper_data[fname]["references_in_collection"] = sorted(
            set(paper_data[fname]["references_in_collection"])
        )
        paper_data[fname]["cited_by_in_collection"] = sorted(
            set(paper_data[fname]["cited_by_in_collection"])
        )

    # ---- 5. Get cited_by_count for missing papers ----
    missing_papers = []
    for doi_norm, info in missing_counter.items():
        count = len(info["cited_by_in_collection"])
        if count >= missing_threshold:
            # Try to get the global cited_by_count from already-resolved data
            openalex_cited = 0
            oa_id = info.get("openalex_id", "")
            if oa_id and oa_id in openalex_id_to_info:
                # We don't have cited_by_count from the batch resolve (select didn't include it)
                # Fetch it individually if we want it — but that's expensive for many papers
                # For now, leave as 0 and note it
                pass

            missing_papers.append({
                "doi": info["doi"],
                "title": info["title"],
                "first_author": info["first_author"],
                "year": info["year"],
                "cited_by_in_collection": sorted(info["cited_by_in_collection"]),
                "citation_count_in_collection": count,
                "openalex_cited_by_count": openalex_cited,
            })

    # Sort by citation_count_in_collection descending
    missing_papers.sort(key=lambda x: (-x["citation_count_in_collection"], x.get("title", "")))

    # ---- 6. Count cross-references ----
    total_cross_refs = sum(
        len(pd["references_in_collection"]) for pd in paper_data.values()
    )

    # ---- 7. Build output ----
    result = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "papers_with_dois": len(papers_with_dois),
        "papers_without_dois": len(papers_without_dois),
        "papers": paper_data,
        "missing_papers": missing_papers,
    }

    # Write output
    output_path = os.path.join(CROSS_CUTTING_DIR, "citation_index.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(
        f"\nCitation graph built. "
        f"{len(papers_with_dois)} papers with DOIs, "
        f"{total_cross_refs} cross-references found, "
        f"{len(missing_papers)} missing papers identified."
    )
    logger.info(
        "Citation graph written to %s", output_path,
    )

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build citation index from OpenAlex API data."
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Ignore cache and re-fetch all data from OpenAlex.",
    )
    parser.add_argument(
        "--missing-threshold",
        type=int,
        default=2,
        help="Minimum collection citations for a paper to appear in missing_papers (default: 2).",
    )
    parser.add_argument(
        "--email",
        type=str,
        default=None,
        help="Email for OpenAlex polite pool (faster rate limits).",
    )
    args = parser.parse_args()

    root = _STEP3_ROOT
    build_citation_graph(
        root=root,
        rebuild=args.rebuild,
        missing_threshold=args.missing_threshold,
        email=args.email,
    )


if __name__ == "__main__":
    main()
