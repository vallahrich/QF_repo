"""Cross-paper contradiction detection — groups papers by topic, uses LLM to
identify contradictions between claims.

Usage examples:
    # Analyze all topics
    python scripts/detect_contradictions.py

    # Analyze a single topic
    python scripts/detect_contradictions.py --topic portfolio-optimisation

    # Rebuild from scratch (ignore cached results)
    python scripts/detect_contradictions.py --rebuild

    # Filter report output by severity
    python scripts/detect_contradictions.py --severity high

    # Write contradiction entries back into individual paper files
    python scripts/detect_contradictions.py --update-papers
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is on sys.path
_STEP3_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP3_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from p2_systematic_review.s2_classification.utils.frontmatter import read_frontmatter, write_frontmatter  # noqa: E402
from shared.tools.llm_client import LLMClient  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from shared.tools.text_chunker import truncate_tokens  # noqa: E402

logger = get_logger("detect_contradictions")

BATCH_SIZE = 15
INPUT_TOKEN_LIMIT = 12000
SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}

# Directories
STEP2_ROOT = os.path.join(_PROJECT_ROOT, "p2_systematic_review")
PROCESSED_DIR = os.path.join(STEP2_ROOT, "output", "processed")
STEP3_ROOT = _STEP3_ROOT
CROSS_CUTTING_DIR = os.path.join(STEP3_ROOT, "cross_cutting")
OUTPUT_JSON = os.path.join(CROSS_CUTTING_DIR, "contradictions_index.json")
OUTPUT_MD = os.path.join(CROSS_CUTTING_DIR, "contradictions.md")
PROMPT_FILE = os.path.join(STEP3_ROOT, "shared", "prompts", "contradiction_detection.txt")

SKIP_FILES = {".gitkeep", ".obsidian"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_section(body: str, section_name: str) -> str:
    """Extract a ## section from markdown body."""
    pattern = re.compile(
        rf"^## {re.escape(section_name)}\s*\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(body)
    if match:
        content = match.group(1).strip()
        if content.startswith("<!--") and content.endswith("-->"):
            return ""
        return content
    return ""


def _parse_llm_json(response: str) -> dict:
    """Parse JSON from an LLM response, handling code fences and trailing text."""
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", response).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(cleaned[first : last + 1])
        except json.JSONDecodeError:
            pass

    return {}


def _wiki_link(filename: str) -> str:
    """Return an Obsidian wiki-link for a paper filename."""
    return f"[[{filename.removesuffix('.md')}]]"


def _write_body_section(paper_path: str, section_name: str, content: str) -> None:
    """Write (replace or append) a ## section in a paper markdown file."""
    meta, body = read_frontmatter(paper_path)
    pattern = re.compile(
        r"(## " + re.escape(section_name) + r")\s*\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )
    header = f"## {section_name}"
    replacement = f"{header}\n{content}"
    if pattern.search(body):
        new_body = pattern.sub(replacement, body, count=1)
    else:
        new_body = body.rstrip() + f"\n\n{replacement}\n"
    write_frontmatter(paper_path, meta, new_body)


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------

def _list_papers() -> list[str]:
    """List paper .md files in the processed directory."""
    return sorted(
        f
        for f in os.listdir(PROCESSED_DIR)
        if f.endswith(".md")
        and f not in SKIP_FILES
        and not f.startswith(".")
        and not f.startswith("Untitled")
    )


def _collect_paper_claims(papers: list[str]) -> dict[str, dict]:
    """Read frontmatter + findings for each paper. Returns {filename: info}."""
    result: dict[str, dict] = {}
    for filename in papers:
        filepath = os.path.join(PROCESSED_DIR, filename)
        meta, body = read_frontmatter(filepath)

        findings_text = _extract_section(body, "Findings")
        if not findings_text:
            continue

        topic_tags = meta.get("topic_tags") or []
        qa_claim = meta.get("quantum_advantage_claim", "not-applicable")

        result[filename] = {
            "topic_tags": topic_tags,
            "qa_claim": qa_claim,
            "findings": findings_text,
        }
    return result


def _group_by_topic(paper_claims: dict[str, dict]) -> dict[str, list[str]]:
    """Group paper filenames by topic tag."""
    groups: dict[str, list[str]] = defaultdict(list)
    for filename, info in paper_claims.items():
        for tag in info["topic_tags"]:
            groups[tag].append(filename)
    return dict(groups)


# ---------------------------------------------------------------------------
# Prompt formatting
# ---------------------------------------------------------------------------

def _format_paper_block(filename: str, info: dict) -> str:
    """Format a single paper's claims for the prompt."""
    lines = [f"Paper: {filename}"]
    lines.append("Findings:")
    for line in info["findings"].splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(stripped if stripped.startswith("- ") else f"- {stripped}")
    lines.append(f"Quantum advantage claim: {info['qa_claim']}")
    return "\n".join(lines)


def _format_claims_block(
    filenames: list[str], paper_claims: dict[str, dict]
) -> str:
    """Format claims for a batch of papers."""
    blocks = []
    for fn in filenames:
        info = paper_claims.get(fn)
        if info:
            blocks.append(_format_paper_block(fn, info))
    return "\n\n---\n\n".join(blocks)


# ---------------------------------------------------------------------------
# LLM analysis
# ---------------------------------------------------------------------------

def _analyze_batch(
    topic: str,
    filenames: list[str],
    paper_claims: dict[str, dict],
    prompt_template: str,
    client: LLMClient,
    model: str,
) -> list[dict]:
    """Run contradiction detection on one batch of papers for a topic."""
    claims_block = _format_claims_block(filenames, paper_claims)
    claims_block = truncate_tokens(claims_block, INPUT_TOKEN_LIMIT)

    prompt = prompt_template.format(topic=topic, paper_claims=claims_block)

    try:
        response = client.call(
            model=model,
            prompt=prompt,
            temperature=0.3,
            max_tokens=2000,
        )
    except RuntimeError as exc:
        logger.warning("LLM call failed for topic '%s': %s", topic, exc)
        return []

    data = _parse_llm_json(response)
    if not data:
        logger.warning("Invalid JSON response for topic '%s', skipping batch", topic)
        return []

    contradictions = data.get("contradictions", [])
    # Ensure topic is set on each contradiction
    for c in contradictions:
        c["topic"] = topic
    return contradictions


def _analyze_topic(
    topic: str,
    filenames: list[str],
    paper_claims: dict[str, dict],
    prompt_template: str,
    client: LLMClient,
    model: str,
) -> list[dict]:
    """Analyze a single topic, batching if the group is large."""
    if len(filenames) <= BATCH_SIZE:
        print(f"  Analyzing topic: {topic} ({len(filenames)} papers, 1 batch)")
        return _analyze_batch(
            topic, filenames, paper_claims, prompt_template, client, model
        )

    # Split into batches
    batches = [
        filenames[i : i + BATCH_SIZE]
        for i in range(0, len(filenames), BATCH_SIZE)
    ]
    num_batches = len(batches)
    print(
        f"  Analyzing topic: {topic} ({len(filenames)} papers, {num_batches} batches)"
    )

    all_contradictions: list[dict] = []
    batch_summaries: list[tuple[list[str], list[dict]]] = []

    for idx, batch in enumerate(batches, 1):
        print(f"    Batch {idx}/{num_batches} ({len(batch)} papers)")
        batch_results = _analyze_batch(
            topic, batch, paper_claims, prompt_template, client, model
        )
        all_contradictions.extend(batch_results)
        batch_summaries.append((batch, batch_results))

    # Cross-batch comparison: take top findings from each batch and compare
    if num_batches > 1:
        print(f"    Running cross-batch comparison...")
        cross_batch_papers = _select_cross_batch_papers(batch_summaries, paper_claims)
        if len(cross_batch_papers) >= 2:
            cross_results = _analyze_batch(
                topic,
                cross_batch_papers,
                paper_claims,
                prompt_template,
                client,
                model,
            )
            all_contradictions.extend(cross_results)

    return all_contradictions


def _select_cross_batch_papers(
    batch_summaries: list[tuple[list[str], list[dict]]],
    paper_claims: dict[str, dict],
) -> list[str]:
    """Select 3-5 papers from each batch for cross-batch comparison.

    Priority: papers that appeared in contradictions, then papers with the
    longest findings sections (more claims = more potential contradictions).
    """
    selected: list[str] = []
    for batch_filenames, batch_contradictions in batch_summaries:
        # Papers involved in contradictions first
        involved = set()
        for c in batch_contradictions:
            involved.add(c.get("paper_a", ""))
            involved.add(c.get("paper_b", ""))
        involved = involved & set(batch_filenames)

        candidates = list(involved)
        remaining = [f for f in batch_filenames if f not in involved]
        # Sort remaining by findings length descending
        remaining.sort(
            key=lambda f: len(paper_claims.get(f, {}).get("findings", "")),
            reverse=True,
        )
        candidates.extend(remaining)

        # Take up to 5 from this batch
        for fn in candidates[:5]:
            if fn not in selected:
                selected.append(fn)

    return selected


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------

def _deduplicate(contradictions: list[dict]) -> list[dict]:
    """Deduplicate contradictions: same paper pair keeps highest severity."""
    best: dict[tuple[str, str], dict] = {}
    for c in contradictions:
        a = c.get("paper_a", "")
        b = c.get("paper_b", "")
        if not a or not b:
            continue
        key = tuple(sorted([a, b]))
        existing = best.get(key)
        if existing is None:
            best[key] = c
        else:
            existing_sev = SEVERITY_ORDER.get(existing.get("severity", "low"), 2)
            new_sev = SEVERITY_ORDER.get(c.get("severity", "low"), 2)
            if new_sev < existing_sev:
                best[key] = c

    # Sort: high severity first, then by topic
    result = list(best.values())
    result.sort(key=lambda c: (SEVERITY_ORDER.get(c.get("severity", "low"), 2), c.get("topic", "")))
    return result


# ---------------------------------------------------------------------------
# Output generation
# ---------------------------------------------------------------------------

def _write_json(contradictions: list[dict], model: str, topics_analyzed: int) -> None:
    """Write the contradictions index JSON."""
    os.makedirs(CROSS_CUTTING_DIR, exist_ok=True)

    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "topics_analyzed": topics_analyzed,
        "total_contradictions": len(contradictions),
        "contradictions": contradictions,
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    logger.info("Wrote %s with %d contradictions", OUTPUT_JSON, len(contradictions))


def _write_markdown(
    contradictions: list[dict], topics_analyzed: int, severity_filter: str | None = None
) -> None:
    """Write the human-readable contradictions report."""
    os.makedirs(CROSS_CUTTING_DIR, exist_ok=True)

    filtered = contradictions
    if severity_filter:
        filtered = [c for c in contradictions if c.get("severity") == severity_filter]

    by_severity: dict[str, list[dict]] = {"high": [], "medium": [], "low": []}
    for c in filtered:
        sev = c.get("severity", "low")
        by_severity.setdefault(sev, []).append(c)

    counts = {sev: len(items) for sev, items in by_severity.items()}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# Contradiction Detection Report",
        "",
        f"Generated: {today}",
        "",
        "## Summary",
        "",
        f"- Topics analyzed: {topics_analyzed}",
        f"- Total contradictions found: {len(filtered)}",
        f"- High severity: {counts.get('high', 0)}",
        f"- Medium severity: {counts.get('medium', 0)}",
        f"- Low severity: {counts.get('low', 0)}",
        "",
    ]

    for severity in ["high", "medium", "low"]:
        items = by_severity.get(severity, [])
        if not items:
            continue
        lines.append(f"## {severity.capitalize()} Severity Contradictions")
        lines.append("")
        for c in items:
            ctype = c.get("type", "unknown")
            pa = c.get("paper_a", "unknown")
            pb = c.get("paper_b", "unknown")
            topic = c.get("topic", "unknown")
            claim_a = c.get("claim_a", "")
            claim_b = c.get("claim_b", "")
            explanation = c.get("explanation", "")

            link_a = _wiki_link(pa)
            link_b = _wiki_link(pb)

            lines.append(f"### {ctype} — {link_a} vs {link_b}")
            lines.append("")
            lines.append(f"**Topic:** {topic}")
            lines.append("")
            lines.append(f"**Paper A** ({link_a}):")
            lines.append(f"> {claim_a}")
            lines.append("")
            lines.append(f"**Paper B** ({link_b}):")
            lines.append(f"> {claim_b}")
            lines.append("")
            lines.append(f"**Analysis:** {explanation}")
            lines.append("")
            lines.append("---")
            lines.append("")

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    logger.info("Wrote %s", OUTPUT_MD)


# ---------------------------------------------------------------------------
# Paper update
# ---------------------------------------------------------------------------

def _update_papers(contradictions: list[dict]) -> None:
    """Write contradiction entries back into individual paper files."""
    # Group contradictions by paper
    paper_entries: dict[str, list[str]] = defaultdict(list)
    for c in contradictions:
        pa = c.get("paper_a", "")
        pb = c.get("paper_b", "")
        ctype = c.get("type", "unknown")
        topic = c.get("topic", "")
        explanation = c.get("explanation", "")
        brief = explanation[:120] + "..." if len(explanation) > 120 else explanation

        if pa:
            entry = f"- #contradiction:{ctype} — contradicts {_wiki_link(pb)} on {topic}: {brief}"
            paper_entries[pa].append(entry)
        if pb:
            entry = f"- #contradiction:{ctype} — contradicts {_wiki_link(pa)} on {topic}: {brief}"
            paper_entries[pb].append(entry)

    updated = 0
    for filename, new_entries in paper_entries.items():
        filepath = os.path.join(PROCESSED_DIR, filename)
        if not os.path.isfile(filepath):
            logger.warning("Paper file not found for update: %s", filename)
            continue

        _, body = read_frontmatter(filepath)
        existing_section = _extract_section(body, "Contradictions")
        existing_lines = set(existing_section.splitlines()) if existing_section else set()

        # Only add entries not already present
        additions = [e for e in new_entries if e not in existing_lines]
        if not additions:
            continue

        if existing_section:
            content = existing_section.rstrip() + "\n" + "\n".join(additions)
        else:
            content = "\n".join(additions)

        _write_body_section(filepath, "Contradictions", content)
        updated += 1
        logger.info("Updated contradictions in %s (+%d entries)", filename, len(additions))

    print(f"Updated {updated} paper files with contradiction entries.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    global PROCESSED_DIR

    parser = argparse.ArgumentParser(
        description="Detect contradictions across papers grouped by topic."
    )
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Analyze only this topic (e.g. portfolio-optimisation).",
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="Ignore cached results and reanalyze everything.",
    )
    parser.add_argument(
        "--severity",
        type=str,
        default=None,
        choices=["high", "medium", "low"],
        help="Filter the markdown report to this severity level.",
    )
    parser.add_argument(
        "--update-papers",
        action="store_true",
        help="Write contradiction entries back into individual paper files.",
    )
    parser.add_argument(
        "--silo",
        type=str,
        default=None,
        help="Read from a silo's local documents/ folder (e.g. portfolio_optimization).",
    )
    args = parser.parse_args()

    # Optionally override source directory to a silo's local documents
    if args.silo:
        silo_docs = os.path.join(_STEP3_ROOT, "problems", args.silo, "documents")
        if not os.path.isdir(silo_docs):
            print(f"Silo documents not found: {silo_docs}")
            print("Run fetch_silo_docs.py first to populate local copies.")
            return
        PROCESSED_DIR = silo_docs
        logger.info("Using silo documents: %s", silo_docs)

    # Load config from shared
    config_path = os.path.join(_PROJECT_ROOT, "shared", "config", "extraction_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    step6_config = config["steps"]["step6"]
    model = step6_config["model"]

    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompt_template = f.read()
    client = LLMClient()

    # Collect data
    print("Reading processed papers...")
    papers = _list_papers()
    if not papers:
        print("No processed papers found.")
        return

    paper_claims = _collect_paper_claims(papers)
    print(f"Found {len(paper_claims)} papers with findings sections.")

    topic_groups = _group_by_topic(paper_claims)

    # Filter to requested topic if specified
    if args.topic:
        if args.topic not in topic_groups:
            print(f"Topic '{args.topic}' not found. Available topics:")
            for t in sorted(topic_groups):
                print(f"  - {t} ({len(topic_groups[t])} papers)")
            return
        topic_groups = {args.topic: topic_groups[args.topic]}

    # Load existing results if not rebuilding
    existing_contradictions: list[dict] = []
    existing_topics: set[str] = set()
    if not args.rebuild and os.path.isfile(OUTPUT_JSON):
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
            existing_contradictions = existing_data.get("contradictions", [])
            existing_topics = {c.get("topic", "") for c in existing_contradictions}
            logger.info(
                "Loaded %d existing contradictions from cache",
                len(existing_contradictions),
            )
        except (json.JSONDecodeError, OSError):
            pass

    # Analyze topics
    all_contradictions: list[dict] = []
    topics_analyzed = 0

    # Keep existing results for topics we're not reanalyzing
    if not args.rebuild and existing_contradictions:
        topics_to_skip = existing_topics - set(topic_groups.keys())
        for c in existing_contradictions:
            if c.get("topic", "") in topics_to_skip:
                all_contradictions.append(c)

    for topic in sorted(topic_groups):
        filenames = topic_groups[topic]
        if len(filenames) < 2:
            logger.info("Skipping topic '%s' — only %d paper(s)", topic, len(filenames))
            continue

        # Use cache for topics not being reanalyzed
        if (
            not args.rebuild
            and topic in existing_topics
            and not args.topic
        ):
            cached = [c for c in existing_contradictions if c.get("topic") == topic]
            all_contradictions.extend(cached)
            topics_analyzed += 1
            continue

        topic_results = _analyze_topic(
            topic, filenames, paper_claims, prompt_template, client, model
        )
        all_contradictions.extend(topic_results)
        topics_analyzed += 1

    # Deduplicate
    all_contradictions = _deduplicate(all_contradictions)

    # Write outputs
    _write_json(all_contradictions, model, topics_analyzed)
    _write_markdown(all_contradictions, topics_analyzed, severity_filter=args.severity)

    # Optionally update paper files
    if args.update_papers:
        _update_papers(all_contradictions)

    # Summary
    severity_counts = defaultdict(int)
    for c in all_contradictions:
        severity_counts[c.get("severity", "low")] += 1

    print(
        f"\nContradiction detection complete. "
        f"Found {len(all_contradictions)} contradictions across {topics_analyzed} topics."
    )
    for sev in ["high", "medium", "low"]:
        if severity_counts[sev]:
            print(f"  {sev}: {severity_counts[sev]}")


if __name__ == "__main__":
    main()
