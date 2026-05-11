"""Per-silo paper inclusion — Step 3.2.

Generates inclusion lists per silo using the three-lens logic:
  (a) Quantitative scope (FROZEN) — papers with extraction + triangulation
  (b) Thematic scope — P2 papers with silo topic_tag AND relevance_phase3 in {high, medium}
  (c) Researcher discretion — logged add/remove (applied manually after this script runs)

Also assigns tiering (A/B/C) based on mechanical rules.

Rule: thematic_scope >= quantitative_scope ∩ silo  (always)

Outputs to shared/phase3/inclusion/<silo>.json

Usage:
    python -m p3_thematic_synthesis.scripts.build_inclusion_lists
"""

import json
import logging
import os
import sys
from collections import defaultdict
from pathlib import Path

import yaml

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])

SILO_INCLUSION_PATH = os.path.join(_PROJECT_ROOT, "shared", "config", "silo_inclusion.json")
P2_PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")
QUANT_EXTRACTIONS_DIR = os.path.join(
    _PROJECT_ROOT, "p3_thematic_synthesis", "s2_quantitative", "output", "extractions_preQ0_20260417_095811"
)
OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "shared", "phase3", "inclusion")

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)

# Tier assignment criteria (mechanical, documented ex-ante)
TIER_A_RELEVANCE = "high"
TIER_A_EMPIRICAL_TYPES = {"peer-reviewed-empirical", "conference-paper"}
TIER_BC_RELEVANCE = {"high", "medium"}
TIER_C_RELEVANCE = {"low", "not-yet-assessed", ""}


def read_frontmatter(filepath: str) -> dict:
    """Read YAML frontmatter from a markdown file."""
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


def load_active_silos() -> list[dict]:
    """Load active silo definitions."""
    with open(SILO_INCLUSION_PATH, encoding="utf-8") as f:
        config = json.load(f)
    return config["active_silos"]


def load_quantitative_paper_ids() -> set[str]:
    """Load paper IDs that have quantitative extractions (FROZEN scope)."""
    quant_dir = Path(QUANT_EXTRACTIONS_DIR)
    if not quant_dir.exists():
        logger.warning("Quantitative extractions dir not found: %s", QUANT_EXTRACTIONS_DIR)
        return set()
    ids = {f.stem for f in quant_dir.glob("*.json")}
    logger.info("Loaded %d quantitative paper IDs", len(ids))
    return ids


def load_p2_corpus() -> dict[str, dict]:
    """Load all P2 papers, keyed by paper_id."""
    papers = {}
    processed_dir = Path(P2_PROCESSED_DIR)
    for md_file in sorted(processed_dir.glob("*.md")):
        meta = read_frontmatter(str(md_file))
        if meta:
            papers[md_file.stem] = meta
    logger.info("Loaded %d P2 papers", len(papers))
    return papers


def assign_tier(meta: dict, in_quantitative: bool) -> str:
    """Assign tier based on mechanical rules.

    Tier A: relevance_phase3 == high AND (has_quantitative_results OR empirical source_type)
    Tier B: relevance_phase3 in {high, medium} AND not Tier A
    Tier C: relevance_phase3 in {low, not-yet-assessed} OR excluded from thematic
    """
    relevance = str(meta.get("relevance_phase3", "")).strip()
    source_type = str(meta.get("source_type", "")).strip()
    has_quant = bool(meta.get("has_quantitative_results", False))

    if relevance == TIER_A_RELEVANCE and (has_quant or source_type in TIER_A_EMPIRICAL_TYPES):
        return "A"
    if relevance in TIER_BC_RELEVANCE:
        return "B"
    return "C"


def build_silo_inclusion(silo_code: str, silo_folder: str, silo_tag: str,
                         p2_corpus: dict[str, dict], quant_ids: set[str]) -> dict:
    """Build inclusion list for one silo."""
    papers = []
    silo_quant_count = 0
    silo_thematic_count = 0
    tier_counts = defaultdict(int)

    for paper_id, meta in p2_corpus.items():
        topic_tags = meta.get("topic_tags", [])
        if silo_tag not in topic_tags:
            continue

        in_quantitative = paper_id in quant_ids
        if in_quantitative:
            silo_quant_count += 1

        relevance = str(meta.get("relevance_phase3", "")).strip()
        in_thematic = relevance in TIER_BC_RELEVANCE or relevance == TIER_A_RELEVANCE

        tier = assign_tier(meta, in_quantitative)
        tier_counts[tier] += 1

        if in_thematic or in_quantitative:
            silo_thematic_count += 1

        papers.append({
            "paper_id": paper_id,
            "in_quantitative_scope": in_quantitative,
            "in_thematic_scope": in_thematic or in_quantitative,
            "relevance_phase3": relevance,
            "has_quantitative_results": bool(meta.get("has_quantitative_results", False)),
            "source_type": meta.get("source_type", ""),
            "evaluation_type": meta.get("evaluation_type", ""),
            "quantum_advantage_claim": meta.get("quantum_advantage_claim", ""),
            "year": meta.get("year", ""),
            "tier": tier,
            "researcher_action": "default",
            "action_rationale": "",
        })

    # Sort: Tier A first, then B, then C; within tier by paper_id
    tier_order = {"A": 0, "B": 1, "C": 2}
    papers.sort(key=lambda p: (tier_order.get(p["tier"], 9), p["paper_id"]))

    return {
        "silo_code": silo_code,
        "silo_folder": silo_folder,
        "silo_tag": silo_tag,
        "total_papers_in_silo": len(papers),
        "in_quantitative_scope": silo_quant_count,
        "in_thematic_scope": silo_thematic_count,
        "tier_distribution": dict(sorted(tier_counts.items())),
        "papers": papers,
    }


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    active_silos = load_active_silos()
    quant_ids = load_quantitative_paper_ids()
    p2_corpus = load_p2_corpus()

    for silo in active_silos:
        silo_code = silo["code"]
        silo_folder = silo["folder"]
        silo_tag = silo_folder.replace("_", "-")

        result = build_silo_inclusion(silo_code, silo_folder, silo_tag, p2_corpus, quant_ids)

        output_path = os.path.join(OUTPUT_DIR, f"{silo_folder}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        thematic_count = sum(1 for p in result["papers"] if p["in_thematic_scope"])
        logger.info(
            "%-25s  total=%3d  quant=%3d  thematic=%3d  tiers: A=%d B=%d C=%d",
            silo_folder,
            result["total_papers_in_silo"],
            result["in_quantitative_scope"],
            thematic_count,
            result["tier_distribution"].get("A", 0),
            result["tier_distribution"].get("B", 0),
            result["tier_distribution"].get("C", 0),
        )

    logger.info("Inclusion lists written to %s", OUTPUT_DIR)


if __name__ == "__main__":
    main()
