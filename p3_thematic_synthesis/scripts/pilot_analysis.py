"""Pilot analysis — auto-generates comparison report across iterations.

Scans all iter_*/ folders in the pilot directory, reads manifests and
code/memo files, and produces a pilot_analysis.md with side-by-side metrics.

Run after each pilot iteration to update the report.

Usage:
    python -m p3_thematic_synthesis.scripts.pilot_analysis
    python -m p3_thematic_synthesis.scripts.pilot_analysis --silo trading_execution
"""

import argparse
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
CODING_DIR = os.path.join(_PROJECT_ROOT, "p3_thematic_synthesis", "s4_thematic_coding")
PILOT_DIR = os.path.join(CODING_DIR, "pilot")

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
logger = logging.getLogger(__name__)


def analyse_iteration(iter_dir: str) -> dict:
    """Compute metrics for one iteration folder."""
    codes_dir = os.path.join(iter_dir, "codes")
    memos_dir = os.path.join(iter_dir, "memos")

    # Load manifest
    manifest_path = os.path.join(iter_dir, "run_manifest.json")
    manifest = {}
    if os.path.isfile(manifest_path):
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

    # Analyse codes
    total_papers = 0
    papers_with_codes = 0
    papers_empty = 0
    total_codes = 0
    l1 = {"pass": 0, "pass_fuzzy": 0, "fail": 0}
    dimension_hints = {}
    per_paper_counts = []
    all_labels = set()

    if os.path.isdir(codes_dir):
        for f in sorted(Path(codes_dir).glob("*.jsonl")):
            total_papers += 1
            codes = []
            for line in open(f, encoding="utf-8"):
                if line.strip():
                    try:
                        codes.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            if codes:
                papers_with_codes += 1
                total_codes += len(codes)
                per_paper_counts.append(len(codes))
                for c in codes:
                    s = c.get("l1_status", "")
                    if s in l1:
                        l1[s] += 1
                    dim = c.get("dimension_hint", "unknown")
                    dimension_hints[dim] = dimension_hints.get(dim, 0) + 1
                    label = c.get("code_label", c.get("label", ""))
                    if label:
                        all_labels.add(label.lower().strip())
            else:
                papers_empty += 1

    unique_labels = len(all_labels)

    # Analyse memos
    memos_count = 0
    l3_problems_total = 0
    l3_clean = 0
    l3_major = 0
    l3_minor = 0
    if os.path.isdir(memos_dir):
        for f in Path(memos_dir).glob("*.json"):
            if f.name.endswith("_l3.json"):
                with open(f, encoding="utf-8") as fh:
                    try:
                        l3 = json.load(fh)
                        # Handle both old schema (problems_found) and new (verdict)
                        verdict = l3.get("verdict", "")
                        if verdict:
                            if verdict == "clean":
                                l3_clean += 1
                            else:
                                l3_problems_total += 1
                                for p in l3.get("issues", []):
                                    l3_major += 1  # new schema has no severity — all are material
                        elif l3.get("problems_found"):
                            l3_problems_total += 1
                            for p in l3.get("problems", []):
                                sev = p.get("severity", "unknown")
                                if sev == "major":
                                    l3_major += 1
                                elif sev == "minor":
                                    l3_minor += 1
                        else:
                            l3_clean += 1
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        pass
            elif not f.name.startswith("run_"):
                memos_count += 1

    l1_total = l1["pass"] + l1["pass_fuzzy"] + l1["fail"]

    return {
        "iteration": os.path.basename(iter_dir),
        "model": manifest.get("model", "unknown"),
        "prompt_version": manifest.get("prompt_version", manifest.get("note", "unknown")),
        "timestamp": manifest.get("timestamp", "unknown"),
        "git_commit": manifest.get("git_commit", "unknown"),
        "temperature": manifest.get("temperature", "unknown"),
        "response_format": manifest.get("response_format", "unknown"),
        "total_papers": total_papers,
        "papers_with_codes": papers_with_codes,
        "papers_empty": papers_empty,
        "papers_errors": total_papers - papers_with_codes - papers_empty if total_papers > papers_with_codes + papers_empty else 0,
        "json_parse_rate": round(papers_with_codes / total_papers * 100, 1) if total_papers else 0,
        "total_codes": total_codes,
        "avg_codes_per_paper": round(total_codes / papers_with_codes, 1) if papers_with_codes else 0,
        "median_codes_per_paper": round(sorted(per_paper_counts)[len(per_paper_counts) // 2], 0) if per_paper_counts else 0,
        "min_codes_per_paper": min(per_paper_counts) if per_paper_counts else 0,
        "max_codes_per_paper": max(per_paper_counts) if per_paper_counts else 0,
        "unique_code_labels": unique_labels,
        "l1_exact_pass": l1["pass"],
        "l1_fuzzy_pass": l1["pass_fuzzy"],
        "l1_fail": l1["fail"],
        "l1_total": l1_total,
        "l1_pass_rate": round((l1["pass"] + l1["pass_fuzzy"]) / l1_total * 100, 1) if l1_total else 0,
        "l1_fail_rate": round(l1["fail"] / l1_total * 100, 1) if l1_total else 0,
        "l3_total": l3_clean + l3_problems_total,
        "l3_clean": l3_clean,
        "l3_problems": l3_problems_total,
        "l3_problem_rate": round(l3_problems_total / (l3_clean + l3_problems_total) * 100, 1) if (l3_clean + l3_problems_total) else 0,
        "l3_major": l3_major,
        "l3_minor": l3_minor,
        "dimension_distribution": dict(sorted(dimension_hints.items(), key=lambda x: -x[1])),
        "memos_count": memos_count,
    }


def generate_report(silo: str, iterations: list[dict]) -> str:
    """Generate markdown comparison report."""
    lines = [
        f"# Pilot Analysis — {silo}",
        "",
        f"*Auto-generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        f"*{len(iterations)} iterations compared*",
        "",
        "## Comparison Table",
        "",
    ]

    # Header
    cols = ["Metric"] + [it["iteration"] for it in iterations]
    lines.append("| " + " | ".join(cols) + " |")
    lines.append("| " + " | ".join(["---"] * len(cols)) + " |")

    # Rows
    metrics = [
        ("Model", "model"),
        ("**Prompt version**", "prompt_version"),
        ("Git commit", "git_commit"),
        ("Temperature", "temperature"),
        ("Response format", "response_format"),
        ("Papers processed", "total_papers"),
        ("**JSON parse rate**", "json_parse_rate"),
        ("Papers with codes", "papers_with_codes"),
        ("Papers empty", "papers_empty"),
        ("Total codes", "total_codes"),
        ("**Avg codes/paper**", "avg_codes_per_paper"),
        ("Median codes/paper", "median_codes_per_paper"),
        ("Min codes/paper", "min_codes_per_paper"),
        ("Max codes/paper", "max_codes_per_paper"),
        ("**Unique code labels**", "unique_code_labels"),
        ("L1 exact pass", "l1_exact_pass"),
        ("L1 fuzzy pass", "l1_fuzzy_pass"),
        ("L1 fail", "l1_fail"),
        ("**L1 pass rate**", "l1_pass_rate"),
        ("**L1 fail rate**", "l1_fail_rate"),
        ("L3 clean", "l3_clean"),
        ("L3 with problems", "l3_problems"),
        ("L3 major flags", "l3_major"),
        ("L3 minor flags", "l3_minor"),
        ("**L3 problem rate**", "l3_problem_rate"),
        ("Memos generated", "memos_count"),
    ]

    for label, key in metrics:
        vals = [str(it.get(key, "—")) for it in iterations]
        # Add % suffix for rate fields
        if "rate" in key:
            vals = [f"{v}%" if v != "—" else v for v in vals]
        lines.append(f"| {label} | " + " | ".join(vals) + " |")

    # Decision gate
    lines.extend([
        "",
        "## Decision Gate Thresholds",
        "",
        "| Threshold | Target | " + " | ".join(it["iteration"] for it in iterations) + " |",
        "| --- | --- | " + " | ".join(["---"] * len(iterations)) + " |",
    ])

    for it in iterations:
        pass  # build per-iteration

    gate_metrics = [
        ("L1 fail rate", "< 10%", "l1_fail_rate", 10),
        ("JSON parse rate", "> 90%", "json_parse_rate", None),
        ("L3 problem rate", "< 15%", "l3_problem_rate", 15),
    ]

    for label, target, key, threshold in gate_metrics:
        vals = []
        for it in iterations:
            v = it.get(key, 0)
            if threshold is not None:
                if key == "json_parse_rate":
                    status = "✅" if v >= 90 else "❌"
                elif "fail" in key or "problem" in key:
                    status = "✅" if v < threshold else "❌"
                else:
                    status = "—"
            else:
                status = "✅" if v >= 90 else "❌"
            vals.append(f"{v}% {status}")
        lines.append(f"| {label} | {target} | " + " | ".join(vals) + " |")

    # Anchoring check (miscellaneous dimension)
    lines.extend(["", "## Anchoring Check (dimension_hint distribution)", ""])
    for it in iterations:
        dd = it.get("dimension_distribution", {})
        total = sum(dd.values())
        misc = dd.get("cross_cutting", 0) + dd.get("other", 0)
        misc_pct = round(misc / total * 100, 1) if total else 0
        status = "✅" if misc_pct >= 5 else "⚠️ possible anchoring"
        lines.append(f"**{it['iteration']}**: miscellaneous/cross_cutting = {misc_pct}% {status}")
        for dim, count in list(dd.items())[:8]:
            lines.append(f"  - {dim}: {count} ({round(count/total*100, 1)}%)")
        lines.append("")

    # Recommendation section
    lines.extend(["---", "", "## Recommendation Summary", ""])

    # Find best iterations by key metrics
    best_parse = max(iterations, key=lambda x: x.get("json_parse_rate", 0))
    best_l1 = min(iterations, key=lambda x: x.get("l1_fail_rate", 100))
    best_codes = max(iterations, key=lambda x: x.get("avg_codes_per_paper", 0))
    best_diversity = max(iterations, key=lambda x: x.get("unique_code_labels", 0))
    best_l3 = min(iterations, key=lambda x: x.get("l3_problem_rate", 100))

    lines.extend([
        "| Category | Best iteration | Value |",
        "| --- | --- | --- |",
        f"| Highest parse rate | {best_parse['iteration']} | {best_parse['json_parse_rate']}% |",
        f"| Lowest L1 fail rate | {best_l1['iteration']} | {best_l1['l1_fail_rate']}% |",
        f"| Most codes/paper | {best_codes['iteration']} | {best_codes['avg_codes_per_paper']} |",
        f"| Most unique labels | {best_diversity['iteration']} | {best_diversity['unique_code_labels']} |",
        f"| Fewest L3 problems | {best_l3['iteration']} | {best_l3['l3_problem_rate']}% |",
        "",
        "**Next step**: Run L4 human audit on the top 1-2 iterations to compare code quality.",
        "Use `generate_audit_reviews.py` and `model_comparison.py`.",
        "",
    ])

    lines.extend([
        "---",
        "",
        "*Run `python -m p3_thematic_synthesis.scripts.pilot_analysis` to regenerate this report.*",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate pilot comparison analysis")
    parser.add_argument("--silo", default="trading_execution", help="Silo to analyse")
    args = parser.parse_args()

    silo_pilot_dir = os.path.join(PILOT_DIR, args.silo)
    if not os.path.isdir(silo_pilot_dir):
        logger.error("No pilot directory found: %s", silo_pilot_dir)
        return

    # Find all iteration folders
    iter_dirs = sorted([
        os.path.join(silo_pilot_dir, d)
        for d in os.listdir(silo_pilot_dir)
        if d.startswith("iter_") and os.path.isdir(os.path.join(silo_pilot_dir, d))
    ])

    if not iter_dirs:
        logger.error("No iteration folders found in %s", silo_pilot_dir)
        return

    logger.info("Found %d iterations in %s", len(iter_dirs), silo_pilot_dir)

    iterations = []
    for d in iter_dirs:
        logger.info("Analysing %s", os.path.basename(d))
        stats = analyse_iteration(d)
        iterations.append(stats)

    # Generate report
    report = generate_report(args.silo, iterations)
    report_path = os.path.join(silo_pilot_dir, "pilot_analysis.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    logger.info("Report written: %s", report_path)

    # Also save structured data
    data_path = os.path.join(silo_pilot_dir, "pilot_analysis.json")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(iterations, f, indent=2, ensure_ascii=False)
    logger.info("Data written: %s", data_path)


if __name__ == "__main__":
    main()
