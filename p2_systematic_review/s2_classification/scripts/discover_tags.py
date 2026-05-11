"""Tag discovery pipeline — analyzes processed papers to suggest new tags.

Usage examples:
    # Analyze all processed papers
    python scripts/discover_tags.py

    # Analyze only 5 papers (for testing)
    python scripts/discover_tags.py --limit 5

    # Analyze a single paper
    python scripts/discover_tags.py --paper 2024_Ghysels_QuantumFinance.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Ensure project root is on sys.path
_STEP2_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP2_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402
from shared.tools.llm_client import LLMClient  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from p2_systematic_review.s2_classification.utils.step_runner import load_config, load_prompt  # noqa: E402

logger = get_logger("discover_tags")

STEP2_ROOT = _STEP2_ROOT


PROCESSED_DIR = os.path.join(STEP2_ROOT, "output", "processed")
TAG_REGISTRY_PATH = os.path.join(_PROJECT_ROOT, "shared", "config", "unified_taxonomy.json")
OUTPUT_PATH = os.path.join(STEP2_ROOT, "output", "tag_suggestions.json")
PROMPT_FILE = "prompts/tag_discovery.txt"

SECTIONS_TO_EXTRACT = ["Methodology", "Findings", "Key ideas", "Limitations"]


def _extract_sections(body: str, section_names: list[str]) -> str:
    """Extract specific ## sections from markdown body."""
    extracted = []
    for name in section_names:
        pattern = re.compile(
            rf"^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)",
            re.MULTILINE | re.DOTALL,
        )
        match = pattern.search(body)
        if match:
            content = match.group(1).strip()
            if content:
                extracted.append(f"## {name}\n{content}")
    return "\n\n".join(extracted)


def _parse_llm_json(response: str) -> dict:
    """Parse JSON from an LLM response, handling code fences and trailing text."""
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", response)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        substring = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(substring)
        except json.JSONDecodeError:
            pass

    return {}


def _list_papers(limit: int | None = None, paper: str | None = None) -> list[str]:
    """List paper .md files to analyze."""
    if paper:
        path = os.path.join(PROCESSED_DIR, paper)
        if not os.path.isfile(path):
            logger.error("Paper not found: %s", paper)
            sys.exit(1)
        return [paper]

    skip = {".gitkeep", ".obsidian"}
    papers = sorted(
        f
        for f in os.listdir(PROCESSED_DIR)
        if f.endswith(".md") and f not in skip and not f.startswith(".")
    )
    if limit is not None:
        papers = papers[:limit]
    return papers


def _load_tag_registry() -> dict:
    """Load the current tag registry as a dict."""
    with open(TAG_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _aggregate_suggestions(
    all_suggestions: list[dict],
) -> list[dict]:
    """Aggregate tag suggestions across papers: group by tag name, count frequency."""
    tag_map: dict[str, dict] = {}
    for item in all_suggestions:
        tag = item["tag"]
        if tag not in tag_map:
            tag_map[tag] = {
                "tag": tag,
                "category": item.get("category", ""),
                "description": item.get("description", ""),
                "frequency": 0,
                "example_papers": [],
                "status": "pending",
            }
        tag_map[tag]["frequency"] += 1
        paper = item.get("paper", "")
        if paper and paper not in tag_map[tag]["example_papers"]:
            if len(tag_map[tag]["example_papers"]) < 5:
                tag_map[tag]["example_papers"].append(paper)

    suggestions = list(tag_map.values())
    suggestions.sort(key=lambda s: s["frequency"], reverse=True)
    return suggestions


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze processed papers and suggest new tags for the registry."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only analyze N papers (for testing).",
    )
    parser.add_argument(
        "--paper",
        type=str,
        default=None,
        help="Analyze a single paper (filename, e.g. 2024_Author_Title.md).",
    )
    args = parser.parse_args()

    papers = _list_papers(limit=args.limit, paper=args.paper)
    if not papers:
        print("No papers found to analyze.")
        return

    registry = _load_tag_registry()
    existing_tags_json = json.dumps(registry, indent=2)

    prompt_template = load_prompt(PROMPT_FILE)

    config = load_config()
    step6_config = config["steps"]["step6"]
    model = step6_config["model"]

    client = LLMClient()
    all_suggestions: list[dict] = []
    total = len(papers)
    errors = 0

    for i, paper_name in enumerate(papers, 1):
        print(f"Analyzing paper {i}/{total}: {paper_name}")
        paper_path = os.path.join(PROCESSED_DIR, paper_name)

        _, body = read_frontmatter(paper_path)
        paper_content = _extract_sections(body, SECTIONS_TO_EXTRACT)

        if not paper_content.strip():
            logger.warning("No relevant sections found in %s, skipping", paper_name)
            continue

        prompt = prompt_template.format(
            existing_tags=existing_tags_json,
            paper_content=paper_content,
        )

        try:
            response = client.call(
                model=model,
                prompt=prompt,
                temperature=0.3,
                max_tokens=1000,
            )
        except RuntimeError as exc:
            logger.warning("LLM call failed for %s: %s", paper_name, exc)
            errors += 1
            continue

        data = _parse_llm_json(response)
        if not data or "suggestions" not in data:
            logger.warning("Invalid JSON response for %s, skipping", paper_name)
            errors += 1
            continue

        for suggestion in data["suggestions"]:
            suggestion["paper"] = paper_name
            all_suggestions.append(suggestion)

    # Aggregate
    aggregated = _aggregate_suggestions(all_suggestions)

    output = {
        "run_date": datetime.now().isoformat(),
        "model": model,
        "papers_analyzed": total - errors,
        "suggestions": aggregated,
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    unique_count = len(aggregated)
    print(
        f"Analyzed {total - errors} papers. "
        f"Found {unique_count} unique tag suggestions. "
        f"Written to analysis/tag_suggestions.json"
    )
    if errors:
        print(f"({errors} papers skipped due to errors)")


if __name__ == "__main__":
    main()
