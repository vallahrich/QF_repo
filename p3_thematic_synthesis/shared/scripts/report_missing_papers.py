"""Generate a human-readable missing papers report from the citation index.

Usage examples:
    # Generate report with default threshold (≥2 citations)
    python scripts/report_missing_papers.py

    # Use a higher threshold
    python scripts/report_missing_papers.py --threshold 3
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
_STEP3_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP3_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from shared.tools.logger import get_logger  # noqa: E402

logger = get_logger("report_missing_papers")

CROSS_CUTTING_DIR = os.path.join(_STEP3_ROOT, "cross_cutting")


def _escape_pipe(text: str) -> str:
    """Escape pipe characters for markdown table cells."""
    return text.replace("|", "\\|")


def generate_report(root: str = None, threshold: int = 2) -> str:
    """Read citation_index.json and return the missing papers report as markdown."""
    if root is None:
        root = _STEP3_ROOT
    index_path = os.path.join(root, "cross_cutting", "citation_index.json")
    if not os.path.isfile(index_path):
        logger.error("Citation index not found at %s. Run build_citation_graph.py first.", index_path)
        sys.exit(1)

    with open(index_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    papers_count = data.get("papers_with_dois", 0) + data.get("papers_without_dois", 0)
    missing = data.get("missing_papers", [])

    # Filter by threshold
    missing = [m for m in missing if m.get("citation_count_in_collection", 0) >= threshold]

    # Group by citation count
    groups: dict[str, list[dict]] = {
        "high": [],   # 5+
        "medium": [],  # 3-4
        "low": [],     # 2 (or threshold to 2)
    }

    for paper in missing:
        count = paper["citation_count_in_collection"]
        if count >= 5:
            groups["high"].append(paper)
        elif count >= 3:
            groups["medium"].append(paper)
        else:
            groups["low"].append(paper)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        "# Missing Papers Report",
        "",
        "Papers cited by multiple papers in the collection but not present in the Zotero library.",
        "",
        f"Generated: {now}",
        "",
        "## Summary",
        "",
        f"- Papers in collection: {papers_count}",
        f"- Missing papers cited by ≥{threshold} collection papers: {len(missing)}",
        "",
        "## Missing Papers",
        "",
    ]

    def _write_table(papers: list[dict]) -> list[str]:
        """Build a markdown table for a group of missing papers."""
        table = [
            "| Paper | Year | Cited By | DOI |",
            "|-------|------|----------|-----|",
        ]
        for p in papers:
            author = _escape_pipe(p.get("first_author", "Unknown"))
            title = _escape_pipe(p.get("title", "Unknown"))
            year = p.get("year") or "—"
            count = p["citation_count_in_collection"]
            doi = p.get("doi", "")
            if doi:
                doi_display = f"[{_escape_pipe(doi)}](https://doi.org/{doi})"
            else:
                doi_display = "—"
            label = f"{author} — {title}"
            table.append(f"| {label} | {year} | {count} papers | {doi_display} |")
        return table

    if groups["high"]:
        lines.append("### Cited by 5+ papers in collection")
        lines.append("")
        lines.extend(_write_table(groups["high"]))
        lines.append("")

    if groups["medium"]:
        lines.append("### Cited by 3-4 papers in collection")
        lines.append("")
        lines.extend(_write_table(groups["medium"]))
        lines.append("")

    if groups["low"]:
        lines.append(f"### Cited by {threshold}-2 papers in collection" if threshold < 2
                     else "### Cited by 2 papers in collection")
        lines.append("")
        lines.extend(_write_table(groups["low"]))
        lines.append("")

    if not missing:
        lines.append("No missing papers found above the threshold.")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a human-readable missing papers report."
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=2,
        help="Minimum collection citations to include a paper (default: 2).",
    )
    args = parser.parse_args()

    root = _STEP3_ROOT
    report = generate_report(root, threshold=args.threshold)

    output_path = os.path.join(root, "cross_cutting", "missing_papers.md")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Missing papers report written to {output_path}")
    logger.info("Report written to %s", output_path)


if __name__ == "__main__":
    main()
