"""Bibliometric landscape analysis — Step 3.1.b.

Generates descriptive statistics and trend tables from P2 frontmatter
for the Phase 3 cross-silo chapter opening and per-silo landscape sections.

Operates at CORPUS scope (all 777 P2 papers). No LLM calls — purely mechanical.

Outputs to shared/phase3/bibliometric/:
  - corpus_summary.json        — aggregate counts
  - silo_year_counts.json      — papers per silo per year
  - method_year_counts.json    — papers per method per year
  - silo_method_matrix.json    — (PD × SA) co-occurrence matrix
  - source_type_by_silo.json   — source type distribution per silo
  - claim_strength_by_year.json — QA claim evolution over time
  - landscape_report.md        — human-readable summary

Usage:
    python -m p3_thematic_synthesis.scripts.bibliometric_landscape
    python -m p3_thematic_synthesis.scripts.bibliometric_landscape --output-dir shared/phase3/bibliometric
"""

import argparse
import json
import logging
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])

SILO_INCLUSION_PATH = os.path.join(_PROJECT_ROOT, "shared", "config", "silo_inclusion.json")
P2_PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")
DEFAULT_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "shared", "phase3", "bibliometric")

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def read_frontmatter(filepath: str) -> dict:
    """Read YAML frontmatter from a markdown file. Returns metadata dict."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    try:
        return yaml.safe_load(content[3:end]) or {}
    except yaml.YAMLError:
        return {}


def load_active_silos() -> set[str]:
    """Return set of active silo topic-tag keys (e.g. 'portfolio-optimization')."""
    with open(SILO_INCLUSION_PATH, encoding="utf-8") as f:
        config = json.load(f)

    # Map folder names to topic-tag keys (folder uses underscores, tags use hyphens)
    return {s["folder"].replace("_", "-") for s in config["active_silos"]}


def load_corpus() -> list[dict]:
    """Load all P2 processed paper frontmatter."""
    papers = []
    processed_dir = Path(P2_PROCESSED_DIR)
    if not processed_dir.exists():
        logger.error("P2 processed directory not found: %s", P2_PROCESSED_DIR)
        return papers

    for md_file in sorted(processed_dir.glob("*.md")):
        meta = read_frontmatter(str(md_file))
        if meta:
            meta["_paper_id"] = md_file.stem
            meta["_filepath"] = str(md_file)
            papers.append(meta)

    logger.info("Loaded %d papers from P2 corpus", len(papers))
    return papers


def compute_corpus_summary(papers: list[dict]) -> dict:
    """Aggregate corpus-level counts."""
    years = [p.get("year", "unknown") for p in papers]
    year_counts = Counter(years)

    source_types = [p.get("source_type", "unknown") for p in papers]
    source_counts = Counter(source_types)

    claims = [p.get("quantum_advantage_claim", "unknown") for p in papers]
    claim_counts = Counter(claims)

    eval_types = [p.get("evaluation_type", "unknown") for p in papers]
    eval_counts = Counter(eval_types)

    quant_count = sum(1 for p in papers if p.get("has_quantitative_results"))

    return {
        "total_papers": len(papers),
        "year_range": [min(y for y in years if y != "unknown"), max(y for y in years if y != "unknown")] if years else [],
        "year_distribution": dict(sorted(year_counts.items())),
        "source_type_distribution": dict(sorted(source_counts.items())),
        "quantum_advantage_claims": dict(sorted(claim_counts.items())),
        "evaluation_types": dict(sorted(eval_counts.items())),
        "papers_with_quantitative_results": quant_count,
        "papers_without_quantitative_results": len(papers) - quant_count,
    }


def compute_silo_year_counts(papers: list[dict], active_silos: set[str]) -> dict:
    """Papers per silo per year."""
    counts = defaultdict(lambda: defaultdict(int))
    for p in papers:
        year = str(p.get("year", "unknown"))
        for tag in p.get("topic_tags", []):
            if tag in active_silos:
                silo = tag.replace("-", "_")
                counts[silo][year] += 1
    return {silo: dict(sorted(years.items())) for silo, years in sorted(counts.items())}


def compute_method_year_counts(papers: list[dict]) -> dict:
    """Papers per methodology tag per year."""
    counts = defaultdict(lambda: defaultdict(int))
    for p in papers:
        year = str(p.get("year", "unknown"))
        for tag in p.get("methodology_tags", []):
            counts[tag][year] += 1
    return {method: dict(sorted(years.items())) for method, years in sorted(counts.items())}


def compute_silo_method_matrix(papers: list[dict], active_silos: set[str]) -> dict:
    """(PD silo × SA method) co-occurrence matrix."""
    matrix = defaultdict(lambda: defaultdict(int))
    for p in papers:
        silos = [t.replace("-", "_") for t in p.get("topic_tags", []) if t in active_silos]
        methods = p.get("methodology_tags", [])
        for silo in silos:
            for method in methods:
                matrix[silo][method] += 1
    return {silo: dict(sorted(methods.items())) for silo, methods in sorted(matrix.items())}


def compute_source_type_by_silo(papers: list[dict], active_silos: set[str]) -> dict:
    """Source type distribution per silo."""
    counts = defaultdict(lambda: defaultdict(int))
    for p in papers:
        source = p.get("source_type", "unknown")
        for tag in p.get("topic_tags", []):
            if tag in active_silos:
                silo = tag.replace("-", "_")
                counts[silo][source] += 1
    return {silo: dict(sorted(sources.items())) for silo, sources in sorted(counts.items())}


def compute_claim_strength_by_year(papers: list[dict]) -> dict:
    """Quantum advantage claim distribution per year."""
    counts = defaultdict(lambda: defaultdict(int))
    for p in papers:
        year = str(p.get("year", "unknown"))
        claim = p.get("quantum_advantage_claim", "unknown")
        counts[year][claim] += 1
    return {year: dict(sorted(claims.items())) for year, claims in sorted(counts.items())}


def generate_report(summary: dict, silo_year: dict, method_year: dict,
                    silo_method: dict, source_by_silo: dict, claim_by_year: dict) -> str:
    """Generate human-readable markdown report."""
    lines = [
        "# Bibliometric Landscape — Phase 3 Step 3.1.b",
        "",
        f"**Corpus**: {summary['total_papers']} papers",
        f"**Year range**: {summary['year_range'][0]}–{summary['year_range'][1]}" if summary.get("year_range") else "",
        f"**With quantitative results**: {summary['papers_with_quantitative_results']}",
        f"**Without quantitative results**: {summary['papers_without_quantitative_results']}",
        "",
        "## Papers per Silo",
        "",
        "| Silo | Total |",
        "|------|------:|",
    ]
    for silo, years in sorted(silo_year.items(), key=lambda x: sum(x[1].values()), reverse=True):
        total = sum(years.values())
        lines.append(f"| {silo} | {total} |")

    lines.extend(["", "## Source Type Distribution", "",
                   "| Source type | Count |", "|------------|------:|"])
    for src, count in sorted(summary["source_type_distribution"].items(), key=lambda x: -x[1]):
        lines.append(f"| {src} | {count} |")

    lines.extend(["", "## Quantum Advantage Claims", "",
                   "| Claim | Count |", "|-------|------:|"])
    for claim, count in sorted(summary["quantum_advantage_claims"].items(), key=lambda x: -x[1]):
        lines.append(f"| {claim} | {count} |")

    lines.extend(["", "## Silo × Method Co-occurrence (top 5 methods per silo)", ""])
    for silo, methods in sorted(silo_method.items()):
        top = sorted(methods.items(), key=lambda x: -x[1])[:5]
        top_str = ", ".join(f"{m} ({c})" for m, c in top)
        lines.append(f"- **{silo}**: {top_str}")

    lines.extend(["", "---", f"*Generated by bibliometric_landscape.py*"])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate bibliometric landscape from P2 frontmatter")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    active_silos = load_active_silos()
    logger.info("Active silos: %s", active_silos)

    papers = load_corpus()
    if not papers:
        logger.error("No papers loaded. Aborting.")
        sys.exit(1)

    summary = compute_corpus_summary(papers)
    silo_year = compute_silo_year_counts(papers, active_silos)
    method_year = compute_method_year_counts(papers)
    silo_method = compute_silo_method_matrix(papers, active_silos)
    source_by_silo = compute_source_type_by_silo(papers, active_silos)
    claim_by_year = compute_claim_strength_by_year(papers)

    outputs = {
        "corpus_summary.json": summary,
        "silo_year_counts.json": silo_year,
        "method_year_counts.json": method_year,
        "silo_method_matrix.json": silo_method,
        "source_type_by_silo.json": source_by_silo,
        "claim_strength_by_year.json": claim_by_year,
    }

    for filename, data in outputs.items():
        path = os.path.join(args.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("Wrote %s", path)

    report = generate_report(summary, silo_year, method_year, silo_method, source_by_silo, claim_by_year)
    report_path = os.path.join(args.output_dir, "landscape_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info("Wrote %s", report_path)

    logger.info("Bibliometric landscape complete: %d papers, %d silos", len(papers), len(silo_year))


if __name__ == "__main__":
    main()
