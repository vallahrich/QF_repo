"""L4 Human Audit — generate review files for researcher validation.

Produces one review_<paper_id>.md per sampled paper containing:
- Paper metadata (from P2)
- A1 codes with L1 verification status
- A2 memo dimensions
- L3 adversarial flags
- Scoring fields for researcher to fill in

After review, run with --collect to aggregate scores into audit_results.json.

Usage:
    # Generate review files from a pilot iteration
    python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
        --iteration iter_04_gpt-5_1_vd5b5e8c \
        --silo trading_execution \
        --sample 20

    # Generate for ALL papers in an iteration (no sampling)
    python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
        --iteration iter_04_gpt-5_1_vd5b5e8c \
        --silo trading_execution \
        --all

    # Collect researcher scores after review
    python -m p3_thematic_synthesis.scripts.generate_audit_reviews \
        --iteration iter_04_gpt-5_1_vd5b5e8c \
        --silo trading_execution \
        --collect

Output layout:
    Pilot:      pilot/<silo>/audit/<iteration>/review_*.md
    Production: <silo>/audit/review_*.md  (alongside codes/ and memos/)
"""

import argparse
import json
import logging
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
CODING_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s4_thematic_coding")
P2_PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")
TEXT_DIR = os.path.join(_PROJECT_ROOT, "shared", "extracted_text", "text")

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def read_frontmatter(filepath: str) -> dict:
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


def load_codes(codes_path: str) -> list[dict]:
    codes = []
    if os.path.isfile(codes_path):
        with open(codes_path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        codes.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return codes


def load_json(path: str) -> dict:
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            try:
                return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                return {}
    return {}


def generate_review_md(paper_id: str, p2_meta: dict, codes: list[dict],
                       memo: dict, l3: dict) -> str:
    """Generate a review markdown file for one paper."""
    lines = [
        f"# Audit Review: {paper_id}",
        "",
        f"**Title**: {p2_meta.get('title', 'Unknown')}",
        f"**Year**: {p2_meta.get('year', '?')}",
        f"**Source type**: {p2_meta.get('source_type', '?')}",
        f"**Topics**: {', '.join(p2_meta.get('topic_tags', []))}",
        f"**Methods**: {', '.join(p2_meta.get('methodology_tags', []))}",
        f"**QA claim**: {p2_meta.get('quantum_advantage_claim', '?')}",
        "",
        "### Paper Summary (from P2 extraction)",
        "",
        f"> {p2_meta.get('abstract_summary', 'No summary available.')}",
        "",
        f"📄 **Source text**: `shared/extracted_text/text/{paper_id}*.md`",
        "",
        "---",
        "",
        "## Review Guide",
        "",
        "1. **Read the summary above** to understand the paper's topic",
        "2. **Skim the A1 codes** — do the labels and quotes make sense?",
        "3. **Check 3-5 quotes** against the source paper (focus on ❌ L1-fail and 🟡 fuzzy)",
        "4. **Read the A2 memo** — does it accurately reflect the paper?",
        "5. **Review L3 flags** — are the flagged problems real?",
        "6. **Fill in scores** at the bottom and save",
        "",
        "---",
        "",
    ]

    # A1 Codes
    l1_pass = sum(1 for c in codes if c.get("l1_status") in ("pass", "pass_fuzzy"))
    l1_fail = sum(1 for c in codes if c.get("l1_status") == "fail")

    lines.extend([
        f"## A1 Codes ({len(codes)} codes, L1: {l1_pass} pass / {l1_fail} fail)",
        "",
    ])

    for c in codes:
        l1 = c.get("l1_status", "?")
        l1_icon = {"pass": "✅", "pass_fuzzy": "🟡", "fail": "❌"}.get(l1, "❓")
        lines.extend([
            f"### {c.get('code_id', '?')}: {c.get('code_label', c.get('label', '?'))}",
            "",
            f"- **L1**: {l1_icon} {l1}",
            f"- **Dimension**: {c.get('dimension_hint', '?')}",
            f"- **Quote**: \"{c.get('text_span', '?')}\"",
            f"- **Locator**: {c.get('locator', '?')}",
            f"- **Rationale**: {c.get('rationale', '?')}",
            "",
        ])

    # A2 Memo
    lines.extend(["---", "", "## A2 Memo", ""])

    for key, value in memo.items():
        if not isinstance(value, dict) or "text" not in value:
            continue
        lines.extend([
            f"### {key}",
            "",
            f"**Text**: {value.get('text', '—')}",
            f"**Support codes**: {', '.join(value.get('support_codes', []))}",
            f"**Support type**: {value.get('support_type', '?')}",
            "",
        ])

    # L3 Adversarial
    lines.extend(["---", "", "## L3 Adversarial Findings", ""])

    if l3.get("problems_found"):
        lines.append(f"**{l3.get('problem_count', 0)} problems found:**\n")
        for p in l3.get("problems", []):
            lines.extend([
                f"- **{p.get('type', '?')}** ({p.get('severity', '?')})",
                f"  - Memo: \"{p.get('memo_sentence', '?')}\"",
                f"  - Source: \"{p.get('source_evidence', '?')}\"",
                f"  - Explanation: {p.get('explanation', '?')}",
                "",
            ])
    else:
        lines.append("No problems found by L3.\n")

    # Scoring section
    lines.extend([
        "---",
        "",
        "## Researcher Scoring",
        "",
        "Fill in after reading the source paper:",
        "",
        "### Overall Memo Accuracy",
        "",
        "- [ ] **Accurate** — memo faithfully represents the paper",
        "- [ ] **Minor issues** — small overclaims or omissions, acceptable",
        "- [ ] **Major issues** — hallucination, wrong interpretation, missing key content",
        "",
        "### Code Coverage",
        "",
        "- [ ] **Good** — all major claims/findings captured",
        "- [ ] **Partial** — some significant claims missed",
        "- [ ] **Poor** — many important claims missing",
        "",
        "### L3 Assessment",
        "",
        "- [ ] **L3 flags are valid** — the adversarial pass caught real issues",
        "- [ ] **L3 flags are false positives** — flagged issues are not real problems",
        "- [ ] **L3 missed issues** — I found problems L3 didn't catch",
        "",
        "### Specific Notes",
        "",
        "```",
        "RESEARCHER_NOTES: ",
        "```",
        "",
        "### Disposition",
        "",
        "- [ ] **approved** — memo is usable for thematic synthesis",
        "- [ ] **approved_with_edits** — usable after corrections noted above",
        "- [ ] **requires_manual_read** — memo too unreliable, need full paper read",
        "- [ ] **excluded** — paper should not feed thematic claims",
        "",
        f"**Reviewer**: ",
        f"**Date**: ",
        "",
        "---",
        f"*Generated by L4 audit tool, {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
    ])

    return "\n".join(lines)


def collect_scores(audit_dir: str) -> dict:
    """Parse completed review files and aggregate scores."""
    results = {"papers": [], "summary": {}}
    score_pattern = re.compile(r"- \[x\] \*\*(\w+[\w\s]*)\*\*", re.IGNORECASE)

    for f in sorted(Path(audit_dir).glob("review_*.md")):
        paper_id = f.stem.replace("review_", "")
        content = f.read_text(encoding="utf-8")

        scores = {}
        # Find checked boxes
        matches = score_pattern.findall(content)
        for m in matches:
            m_lower = m.strip().lower()
            if m_lower in ("accurate", "minor issues", "major issues"):
                scores["memo_accuracy"] = m_lower
            elif m_lower in ("good", "partial", "poor"):
                scores["code_coverage"] = m_lower
            elif m_lower.startswith("l3 flags are valid"):
                scores["l3_assessment"] = "valid"
            elif m_lower.startswith("l3 flags are false"):
                scores["l3_assessment"] = "false_positive"
            elif m_lower.startswith("l3 missed"):
                scores["l3_assessment"] = "missed"
            elif m_lower in ("approved", "approved_with_edits", "requires_manual_read", "excluded"):
                scores["disposition"] = m_lower

        # Extract researcher notes
        notes_match = re.search(r"RESEARCHER_NOTES:\s*(.*?)```", content, re.DOTALL)
        if notes_match:
            scores["notes"] = notes_match.group(1).strip()

        results["papers"].append({"paper_id": paper_id, **scores})

    # Aggregate
    total = len(results["papers"])
    if total > 0:
        acc = [p.get("memo_accuracy", "") for p in results["papers"]]
        results["summary"] = {
            "total_reviewed": total,
            "memo_accuracy": {
                "accurate": acc.count("accurate"),
                "minor": acc.count("minor issues"),
                "major": acc.count("major issues"),
                "accurate_rate": round(acc.count("accurate") / total * 100, 1),
            },
            "dispositions": {
                d: sum(1 for p in results["papers"] if p.get("disposition") == d)
                for d in ("approved", "approved_with_edits", "requires_manual_read", "excluded")
            },
        }

    return results


def main():
    parser = argparse.ArgumentParser(description="L4 Human Audit — review file generator")
    parser.add_argument("--iteration", required=True, help="Iteration folder name")
    parser.add_argument("--silo", default="trading_execution", help="Silo name")
    parser.add_argument("--sample", type=int, help="Number of papers to sample (overrides --pct)")
    parser.add_argument("--pct", type=float, default=10.0, help="Percentage of papers to sample (default: 10%%)")
    parser.add_argument("--min-sample", type=int, default=5, help="Minimum papers in sample (default: 5)")
    parser.add_argument("--all", action="store_true", help="Generate for all papers")
    parser.add_argument("--collect", action="store_true", help="Collect scores from completed reviews")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    args = parser.parse_args()

    iter_dir = os.path.join(CODING_DIR, "pilot", args.silo, args.iteration)
    # Audit lives in a centralised folder next to iterations, not inside them
    audit_dir = os.path.join(CODING_DIR, "pilot", args.silo, "audit", args.iteration)

    if args.collect:
        if not os.path.isdir(audit_dir):
            logger.error("No audit directory found: %s", audit_dir)
            return
        results = collect_scores(audit_dir)
        results_path = os.path.join(audit_dir, "audit_results.json")
        with open(results_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        logger.info("Collected %d reviews → %s", len(results["papers"]), results_path)
        if results.get("summary"):
            s = results["summary"]
            logger.info("  Accuracy: %d accurate, %d minor, %d major (%.1f%% accurate)",
                        s["memo_accuracy"]["accurate"], s["memo_accuracy"]["minor"],
                        s["memo_accuracy"]["major"], s["memo_accuracy"]["accurate_rate"])
        return

    if not os.path.isdir(iter_dir):
        logger.error("Iteration directory not found: %s", iter_dir)
        return

    codes_dir = os.path.join(iter_dir, "codes")
    memos_dir = os.path.join(iter_dir, "memos")

    # Find papers with codes
    paper_ids = [f.stem for f in sorted(Path(codes_dir).glob("*.jsonl")) if f.stat().st_size > 0]
    logger.info("Found %d papers with codes in %s", len(paper_ids), args.iteration)

    if args.sample and not args.all:
        random.seed(args.seed)
        sample_size = min(args.sample, len(paper_ids))
        paper_ids = sorted(random.sample(paper_ids, sample_size))
        logger.info("Sampled %d papers (fixed count, seed=%d)", sample_size, args.seed)
    elif not args.all:
        random.seed(args.seed)
        sample_size = max(args.min_sample, int(len(paper_ids) * args.pct / 100))
        sample_size = min(sample_size, len(paper_ids))
        paper_ids = sorted(random.sample(paper_ids, sample_size))
        logger.info("Sampled %d papers (%.0f%% of %d, min=%d, seed=%d)",
                     sample_size, args.pct, len(paper_ids) + (len(paper_ids) - sample_size),
                     args.min_sample, args.seed)

    os.makedirs(audit_dir, exist_ok=True)

    for paper_id in paper_ids:
        p2_path = os.path.join(P2_PROCESSED_DIR, f"{paper_id}.md")
        p2_meta = read_frontmatter(p2_path) if os.path.isfile(p2_path) else {}

        codes = load_codes(os.path.join(codes_dir, f"{paper_id}.jsonl"))
        memo = load_json(os.path.join(memos_dir, f"{paper_id}.json"))
        l3 = load_json(os.path.join(memos_dir, f"{paper_id}_l3.json"))

        review = generate_review_md(paper_id, p2_meta, codes, memo, l3)

        review_path = os.path.join(audit_dir, f"review_{paper_id}.md")
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(review)

    logger.info("Generated %d review files in %s", len(paper_ids), audit_dir)
    logger.info("Next: open review files, read source papers, fill in scores, then run with --collect")


if __name__ == "__main__":
    main()
