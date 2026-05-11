"""Model comparison — generate side-by-side review files for the same papers across iterations.

Picks papers processed by both iterations (with non-empty codes) and produces
a comparison markdown showing codes, memos, and L3 results side by side.

Usage:
    python -m p3_thematic_synthesis.scripts.model_comparison \
        --silo trading_execution \
        --iter-a iter_03_gpt-5_4-mini_v07e4fb5 \
        --iter-b iter_04_gpt-5_1_vd5b5e8c \
        --sample 10
"""

import argparse
import json
import logging
import os
import random
from datetime import datetime, timezone
from pathlib import Path

import yaml

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
CODING_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s4_thematic_coding")
P2_PROCESSED_DIR = os.path.join(_PROJECT_ROOT, "p2_systematic_review", "output", "processed")

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


def load_codes(path: str) -> list[dict]:
    codes = []
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        codes.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
    return codes


def load_json_safe(path: str) -> dict:
    if os.path.isfile(path):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
    return {}


def summarise_codes(codes: list[dict]) -> dict:
    """Quick stats for a code set."""
    if not codes:
        return {"count": 0, "l1_pass": 0, "l1_fuzzy": 0, "l1_fail": 0, "dimensions": {}}
    dims = {}
    l1 = {"pass": 0, "pass_fuzzy": 0, "fail": 0}
    for c in codes:
        s = c.get("l1_status", "")
        if s in l1:
            l1[s] += 1
        d = c.get("dimension_hint", "unknown")
        dims[d] = dims.get(d, 0) + 1
    return {"count": len(codes), **l1, "dimensions": dims}


def summarise_memo(memo: dict) -> list[tuple[str, str, list[str]]]:
    """Extract (dimension, text, support_codes) tuples."""
    dims = []
    for key, value in memo.items():
        if isinstance(value, dict) and "text" in value:
            dims.append((key, value.get("text", ""), value.get("support_codes", [])))
    return dims


def generate_comparison(paper_id: str, p2_meta: dict,
                        codes_a: list[dict], memo_a: dict, l3_a: dict, label_a: str,
                        codes_b: list[dict], memo_b: dict, l3_b: dict, label_b: str,
                        quant_summary: str = "", tri_summary: str = "") -> str:
    """Generate side-by-side comparison markdown."""
    stats_a = summarise_codes(codes_a)
    stats_b = summarise_codes(codes_b)
    dims_a = summarise_memo(memo_a)
    dims_b = summarise_memo(memo_b)

    lines = [
        f"# Model Comparison: {paper_id}",
        "",
        "## Paper Context",
        "",
        f"**Title**: {p2_meta.get('title', 'Unknown')}",
        f"**Year**: {p2_meta.get('year', '?')} | **Source type**: {p2_meta.get('source_type', '?')}",
        "",
        f"### P2 Classification",
        f"- **Topic tags**: {', '.join(p2_meta.get('topic_tags', []))}",
        f"- **Method tags**: {', '.join(p2_meta.get('methodology_tags', []))}",
        f"- **QA claim**: {p2_meta.get('quantum_advantage_claim', '?')}",
        f"- **Evaluation type**: {p2_meta.get('evaluation_type', '?')}",
        f"- **Has quantitative results**: {p2_meta.get('has_quantitative_results', '?')}",
        f"- **Relevance Phase 3**: {p2_meta.get('relevance_phase3', '?')}",
        "",
        f"### Abstract Summary (from P2 Step 2)",
        f"> {p2_meta.get('abstract_summary', 'No summary available.')}",
        "",
        f"📄 **Source text**: `shared/extracted_text/text/{paper_id}*.md`",
        f"📋 **P2 processed**: `p2_systematic_review/output/processed/{paper_id}.md`",
        "",
        f"### Quantitative & Triangulation Context",
        f"- **Quantitative extraction**: {quant_summary or 'Not in quantitative scope'}",
        f"- **Triangulation verdict**: {tri_summary or 'Not triangulated'}",
        "",
        "---",
        "",
        "## Quick Comparison",
        "",
        f"| Metric | {label_a} | {label_b} |",
        f"| --- | --- | --- |",
        f"| **Codes generated** | {stats_a['count']} | {stats_b['count']} |",
        f"| L1 exact pass | {stats_a['pass']} | {stats_b['pass']} |",
        f"| L1 fuzzy pass | {stats_a['pass_fuzzy']} | {stats_b['pass_fuzzy']} |",
        f"| L1 fail | {stats_a['fail']} | {stats_b['fail']} |",
        f"| **L1 pass rate** | {_pct(stats_a['pass']+stats_a['pass_fuzzy'], stats_a['count'])} | {_pct(stats_b['pass']+stats_b['pass_fuzzy'], stats_b['count'])} |",
        f"| Memo dimensions | {len(dims_a)} | {len(dims_b)} |",
        f"| L3 problems | {l3_a.get('problem_count', '?')} | {l3_b.get('problem_count', '?')} |",
        "",
        "---",
        "",
        "## Code Labels Comparison",
        "",
        f"### {label_a} ({stats_a['count']} codes)",
        "",
    ]

    for c in codes_a[:15]:
        l1_icon = {"pass": "✅", "pass_fuzzy": "🟡", "fail": "❌"}.get(c.get("l1_status", ""), "❓")
        lines.append(f"- {l1_icon} **{c.get('code_label', c.get('label', '?'))}** [{c.get('dimension_hint', '?')}]")
    if len(codes_a) > 15:
        lines.append(f"- *...and {len(codes_a) - 15} more*")

    lines.extend([
        "",
        f"### {label_b} ({stats_b['count']} codes)",
        "",
    ])

    for c in codes_b[:15]:
        l1_icon = {"pass": "✅", "pass_fuzzy": "🟡", "fail": "❌"}.get(c.get("l1_status", ""), "❓")
        lines.append(f"- {l1_icon} **{c.get('code_label', c.get('label', '?'))}** [{c.get('dimension_hint', '?')}]")
    if len(codes_b) > 15:
        lines.append(f"- *...and {len(codes_b) - 15} more*")

    # Memo comparison
    lines.extend(["", "---", "", "## Memo Comparison", ""])

    all_dims = set()
    memo_a_dict = {d[0]: d for d in dims_a}
    memo_b_dict = {d[0]: d for d in dims_b}
    all_dims = list(dict.fromkeys(list(memo_a_dict.keys()) + list(memo_b_dict.keys())))

    for dim in all_dims:
        lines.append(f"### {dim}")
        lines.append("")

        da = memo_a_dict.get(dim)
        db = memo_b_dict.get(dim)

        lines.append(f"**{label_a}**: {da[1] if da else '*(not present)*'}")
        if da:
            lines.append(f"  - Codes cited: {', '.join(da[2][:5])}")
        lines.append("")
        lines.append(f"**{label_b}**: {db[1] if db else '*(not present)*'}")
        if db:
            lines.append(f"  - Codes cited: {', '.join(db[2][:5])}")
        lines.append("")

    # Researcher assessment
    lines.extend([
        "---",
        "",
        "## Researcher Assessment",
        "",
        "After reading the source paper, which model performed better?",
        "",
        "### Coverage (which model captured more important content?)",
        f"- [ ] **{label_a}** is better",
        f"- [ ] **{label_b}** is better",
        "- [ ] **About equal**",
        "",
        "### Accuracy (which model is more faithful to the source?)",
        f"- [ ] **{label_a}** is better",
        f"- [ ] **{label_b}** is better",
        "- [ ] **About equal**",
        "",
        "### Usefulness (which output would you rather use for thematic synthesis?)",
        f"- [ ] **{label_a}**",
        f"- [ ] **{label_b}**",
        "- [ ] **Either is fine**",
        "",
        "### Notes",
        "",
        "```",
        "COMPARISON_NOTES: ",
        "```",
        "",
        "---",
        f"*Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
    ])

    return "\n".join(lines)


def _pct(num: int, denom: int) -> str:
    return f"{num/denom*100:.1f}%" if denom > 0 else "—"


def main():
    parser = argparse.ArgumentParser(description="Side-by-side model comparison for pilot")
    parser.add_argument("--silo", default="trading_execution")
    parser.add_argument("--iter-a", required=True, help="First iteration folder name")
    parser.add_argument("--iter-b", required=True, help="Second iteration folder name")
    parser.add_argument("--sample", type=int, default=10, help="Number of papers to compare")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    pilot_dir = os.path.join(CODING_DIR, "pilot", args.silo)
    dir_a = os.path.join(pilot_dir, args.iter_a)
    dir_b = os.path.join(pilot_dir, args.iter_b)

    if not os.path.isdir(dir_a) or not os.path.isdir(dir_b):
        logger.error("Iteration directories not found: %s, %s", dir_a, dir_b)
        return

    # Find papers with non-empty codes in BOTH iterations
    papers_a = {f.stem for f in Path(dir_a, "codes").glob("*.jsonl") if f.stat().st_size > 0}
    papers_b = {f.stem for f in Path(dir_b, "codes").glob("*.jsonl") if f.stat().st_size > 0}
    common = sorted(papers_a & papers_b)

    logger.info("Papers with codes: %s=%d, %s=%d, common=%d",
                args.iter_a, len(papers_a), args.iter_b, len(papers_b), len(common))

    if not common:
        logger.error("No common papers with codes found")
        return

    random.seed(args.seed)
    sample = random.sample(common, min(args.sample, len(common)))
    logger.info("Comparing %d papers", len(sample))

    # Extract model labels from iteration names
    label_a = args.iter_a.split("_", 2)[-1] if "_" in args.iter_a else args.iter_a
    label_b = args.iter_b.split("_", 2)[-1] if "_" in args.iter_b else args.iter_b

    # Comparison lives in the centralised audit folder next to iterations
    output_dir = os.path.join(pilot_dir, "audit", "comparison")
    os.makedirs(output_dir, exist_ok=True)

    # Load quantitative extractions and triangulation for context
    QUANT_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s2_quantitative",
                             "output", "extractions_preQ0_20260417_095811")
    TRIANGULATION_PATH = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s3_quantum_advantage",
                                      "combined", "output", "triangulation_matrix.json")
    triangulation_by_paper = {}
    if os.path.isfile(TRIANGULATION_PATH):
        with open(TRIANGULATION_PATH, encoding="utf-8") as f:
            for row in json.load(f):
                pid = row.get("paper_id", "")
                triangulation_by_paper.setdefault(pid, []).append(row)

    for paper_id in sample:
        p2_path = os.path.join(P2_PROCESSED_DIR, f"{paper_id}.md")
        p2_meta = read_frontmatter(p2_path) if os.path.isfile(p2_path) else {}

        # Load quantitative context
        quant_path = os.path.join(QUANT_DIR, f"{paper_id}.json")
        quant_summary = ""
        if os.path.isfile(quant_path):
            try:
                qd = json.load(open(quant_path, encoding="utf-8"))
                n_exp = len(qd.get("experiments", []))
                quant_summary = f"{n_exp} experiments extracted"
            except:
                pass

        # Load triangulation context
        tri_verdicts = triangulation_by_paper.get(paper_id, [])
        tri_summary = ""
        if tri_verdicts:
            verdicts = [r.get("consensus_verdict", "?") for r in tri_verdicts]
            tri_summary = f"{len(tri_verdicts)} experiments: {', '.join(set(verdicts))}"

        codes_a = load_codes(os.path.join(dir_a, "codes", f"{paper_id}.jsonl"))
        memo_a = load_json_safe(os.path.join(dir_a, "memos", f"{paper_id}.json"))
        l3_a = load_json_safe(os.path.join(dir_a, "memos", f"{paper_id}_l3.json"))

        codes_b = load_codes(os.path.join(dir_b, "codes", f"{paper_id}.jsonl"))
        memo_b = load_json_safe(os.path.join(dir_b, "memos", f"{paper_id}.json"))
        l3_b = load_json_safe(os.path.join(dir_b, "memos", f"{paper_id}_l3.json"))

        md = generate_comparison(paper_id, p2_meta,
                                 codes_a, memo_a, l3_a, label_a,
                                 codes_b, memo_b, l3_b, label_b,
                                 quant_summary, tri_summary)

        out_path = os.path.join(output_dir, f"compare_{paper_id}.md")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)

    logger.info("Comparison files written to %s", output_dir)


if __name__ == "__main__":
    main()
