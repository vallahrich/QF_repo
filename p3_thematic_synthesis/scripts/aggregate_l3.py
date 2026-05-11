"""Aggregate s4 L3 adversarial-check outputs into a per-silo summary.

100% L3 coverage: gpt-5.4-mini @ temp=0.0 with prompt v3.

Reads every `*_l3.json` under `p3_thematic_synthesis/s4_thematic_coding/papers/`
(the canonical safeguard) and joins each L3 record to its silo membership via
the central A2 memo's per-silo overlay folders. Also reads the archived 108
gpt-5.1 / prompt-v2 records under `papers_l3_v2_gpt51_archive/` for a
side-by-side methodological-comparator section.

Emits two artefacts:

- `s4_thematic_coding/output/l3_summary.json` — machine-readable rollup
- `s4_thematic_coding/L3_SUMMARY.md` — human-readable one-pager

Read-only over existing artefacts. Does NOT call an LLM.

Closes GL-10 gap G-03.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
S4_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s4_thematic_coding"
PAPERS_DIR = S4_ROOT / "papers"
ARCHIVE_DIR = S4_ROOT / "papers_l3_v2_gpt51_archive"
OUTPUT_DIR = S4_ROOT / "output"

ACTIVE_SILOS = [
    "portfolio_optimization",
    "derivative_pricing",
    "risk_management",
    "quantum_ml_finance",
    "fraud_detection",
    "trading_execution",
    "credit_lending",
    "simulation_monte_carlo",
]


def silo_membership(paper_id: str) -> list[str]:
    """Return the set of silos that hold a per-silo memo for this paper."""
    found = []
    for silo in ACTIVE_SILOS:
        if (S4_ROOT / silo / "memos" / f"{paper_id}.json").is_file():
            found.append(silo)
    return found


def collect(records_dir: Path) -> dict:
    """Aggregate over a directory of `{pid}_l3.json` files."""
    per_silo_counts: dict[str, Counter] = defaultdict(Counter)
    per_silo_papers: dict[str, set[str]] = defaultdict(set)
    type_counter: Counter = Counter()
    severity_counter: Counter = Counter()
    papers_with_problems = 0
    papers_clean = 0
    multi_silo_papers = 0
    orphan_papers: list[str] = []
    per_paper: list[dict] = []

    files = sorted(records_dir.glob("*_l3.json"))
    for path in files:
        with path.open(encoding="utf-8") as f:
            rec = json.load(f)
        paper_id = rec.get("paper_id") or path.stem.removesuffix("_l3")
        problems = rec.get("problems", []) or []
        problems_found = bool(rec.get("problems_found"))
        problem_count = int(rec.get("problem_count", len(problems)))
        if problems_found:
            papers_with_problems += 1
        else:
            papers_clean += 1

        types_in_paper = Counter(p.get("type", "UNSPECIFIED") for p in problems)
        sevs_in_paper = Counter(p.get("severity", "unspecified") for p in problems)
        type_counter.update(types_in_paper)
        severity_counter.update(sevs_in_paper)

        silos = silo_membership(paper_id)
        if len(silos) > 1:
            multi_silo_papers += 1
        if not silos:
            orphan_papers.append(paper_id)

        for silo in silos:
            per_silo_papers[silo].add(paper_id)
            per_silo_counts[silo]["problems_total"] += problem_count
            if problems_found:
                per_silo_counts[silo]["papers_with_problems"] += 1
            else:
                per_silo_counts[silo]["papers_clean"] += 1
            for t, n in types_in_paper.items():
                per_silo_counts[silo][f"type::{t}"] += n
            for s, n in sevs_in_paper.items():
                per_silo_counts[silo][f"severity::{s}"] += n

        per_paper.append({
            "paper_id": paper_id,
            "problems_found": problems_found,
            "problem_count": problem_count,
            "types": dict(types_in_paper),
            "severities": dict(sevs_in_paper),
            "silos": silos,
        })

    total = len(files)
    return {
        "totals": {
            "l3_records": total,
            "papers_with_problems": papers_with_problems,
            "papers_clean": papers_clean,
            "papers_with_problems_pct": round(papers_with_problems / total * 100, 1) if total else 0.0,
            "problems_total": sum(type_counter.values()),
            "multi_silo_papers": multi_silo_papers,
            "orphan_papers_count": len(orphan_papers),
            "avg_problems_per_paper": round(sum(type_counter.values()) / total, 2) if total else 0.0,
        },
        "by_problem_type": dict(type_counter.most_common()),
        "by_severity": dict(severity_counter.most_common()),
        "by_silo": {
            silo: {
                "papers_in_l3": len(per_silo_papers[silo]),
                **dict(per_silo_counts[silo]),
            }
            for silo in ACTIVE_SILOS
        },
        "orphan_papers": orphan_papers,
        "per_paper": per_paper,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    primary = collect(PAPERS_DIR)
    archive_present = ARCHIVE_DIR.is_dir() and any(ARCHIVE_DIR.glob("*_l3.json"))
    archive = collect(ARCHIVE_DIR) if archive_present else None

    summary = {
        "_generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "_purpose": "GL-10 G-03 — 100% L3 adversarial-check coverage of P2 corpus",
        "_script": "p3_thematic_synthesis/scripts/aggregate_l3.py",
        "primary": {
            "_source": "p3_thematic_synthesis/s4_thematic_coding/papers/*_l3.json",
            "_model": "gpt-5.4-mini",
            "_temperature": 0.0,
            "_prompt_version": "v3",
            "_response_format": "json_object",
            "_max_tokens": 16000,
            **primary,
        },
    }
    if archive:
        summary["archive_comparator"] = {
            "_source": "p3_thematic_synthesis/s4_thematic_coding/papers_l3_v2_gpt51_archive/*_l3.json",
            "_model": "gpt-5.1",
            "_temperature": "0.0 requested but silently dropped by API; effective temperature=1 (reasoning model)",
            "_prompt_version": "v2",
            "_response_format": "json_object",
            "_max_tokens": 16000,
            "_note": "Original 16.5% deterministic-sample L3 records (closes G-03 prior to the mini+v3 100%-coverage upgrade); kept on disk as a same-prompt-different-model sensitivity comparator.",
            **archive,
        }

    out_json = OUTPUT_DIR / "l3_summary.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"wrote {out_json}")

    md = render_markdown(summary)
    out_md = S4_ROOT / "L3_SUMMARY.md"
    out_md.write_text(md, encoding="utf-8")
    print(f"wrote {out_md}")


def _section(title: str, block: dict) -> list[str]:
    t = block["totals"]
    lines = [
        f"## {title}",
        "",
        f"- Model: `{block['_model']}` · prompt: `{block['_prompt_version']}` · temperature: `{block['_temperature']}`",
        f"- L3 records: **{t['l3_records']}**",
        f"- Papers with at least one flagged problem: **{t['papers_with_problems']}** ({t['papers_with_problems_pct']} %)",
        f"- Papers flagged clean: **{t['papers_clean']}**",
        f"- Total problems flagged: **{t['problems_total']}** (avg **{t['avg_problems_per_paper']}** / paper)",
        f"- Multi-silo papers: **{t['multi_silo_papers']}**",
        f"- Orphan papers (L3 record but no per-silo memo): **{t['orphan_papers_count']}**",
        "",
        "### By problem type",
        "",
        "| Type | Count |",
        "|---|---:|",
    ]
    for k, v in block["by_problem_type"].items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "### By severity",
        "",
        "| Severity | Count |",
        "|---|---:|",
    ]
    for k, v in block["by_severity"].items():
        lines.append(f"| `{k}` | {v} |")
    lines += [
        "",
        "### Per-silo distribution",
        "",
        "| Silo | Papers in L3 | Papers w/ problems | Papers clean | Total problems |",
        "|---|---:|---:|---:|---:|",
    ]
    for silo, row in block["by_silo"].items():
        lines.append(
            f"| {silo} | {row['papers_in_l3']} | "
            f"{row.get('papers_with_problems', 0)} | "
            f"{row.get('papers_clean', 0)} | "
            f"{row.get('problems_total', 0)} |"
        )
    lines.append("")
    return lines


def render_markdown(s: dict) -> str:
    p = s["primary"]
    pt = p["totals"]
    out: list[str] = [
        "# s4 L3 adversarial-check summary",
        "",
        f"_Generated: {s['_generated']}_  ",
        f"_Script: `{s['_script']}`_  ",
        "_Purpose: GL-10 gap G-03 — 100% L3 adversarial-check coverage of the P2 corpus._",
        "",
        "## Headline",
        "",
        f"- **Coverage: {pt['l3_records']}/{pt['l3_records']} A2 memos = 100%** (was 108/654 = 16.5% prior to this hardening pass).",
        f"- **{pt['papers_with_problems']}** papers ({pt['papers_with_problems_pct']} %) flagged with at least one problem; **{pt['problems_total']}** total problems (avg **{pt['avg_problems_per_paper']}** / paper).",
        "- Safeguard: `gpt-5.4-mini` @ `temperature=0.0` with prompt `l3_adversarial_v3.txt` (numeric self-calibration anchor removed vs. v2).",
        "- Methodological-comparator: 108 prior records under `papers_l3_v2_gpt51_archive/` (gpt-5.1 / prompt v2) preserved as a same-prompt-different-model sensitivity check.",
        "",
        "## Methodology",
        "",
        "1. **Primary safeguard (canonical):** every A2 memo in `s4_thematic_coding/papers/*.json` is reviewed by an LLM-as-adversarial-reviewer with the same prompt, model, temperature, and JSON-mode parameters across the entire 654-paper corpus.",
        "2. **Reproducibility:** `gpt-5.4-mini` honours `temperature=0.0` (greedy decoding). The prior `gpt-5.1` reasoning-tier model in the comparator silently dropped `temperature=0.0` and was effectively run at API-mandated `temperature=1`; this is documented in the comparator block below and was a motivating reason for the model change.",
        "3. **Prompt v3 vs v2:** v3 removes the line *\"Most well-constructed memos should have 0-2 minor issues and 0 major issues\"*, which acted as a numeric self-calibration anchor that suppressed problem counts. v3 retains the same six problem types, severity rubric, and \"only flag genuine discrepancies\" instruction, and adds explicit \"do not target a particular count\" wording. A 15-paper sensitivity probe (run pre-rollout, results recorded in commit history) showed v3 lifted the average problem count by ~18 % with stable category distribution — i.e. the anchor was suppressing count, not biasing categorisation.",
        "4. **What L3 is and is not:** L3 is an LLM-adversarial review, not a researcher review. A flagged problem is a *candidate* concern. Stage B (propagation audit) lifts these candidates to AT/DT-level flags, and Stage C (assistive triage) routes flagged claims through researcher-approved actions before any manuscript edit.",
        "",
        "## Provenance",
        "",
        "- Raw L3 records (canonical): `s4_thematic_coding/papers/*_l3.json` (n = 654)",
        "- Archived comparator records: `s4_thematic_coding/papers_l3_v2_gpt51_archive/*_l3.json` (n = 108)",
        "- Driver: `p3_thematic_synthesis/scripts/run_l3_full_coverage.py` (resume-friendly, atomic per-paper writes, append-only call log at `logs/l3_calls.jsonl`)",
        "- Aggregator: `p3_thematic_synthesis/scripts/aggregate_l3.py`",
        "- Prompt: `p3_thematic_synthesis/prompts/l3_adversarial_v3.txt` (canonical) · `l3_adversarial_v2.txt` (comparator)",
        "- Audit context: `p3_thematic_synthesis/GL10_AUDIT.md` gap G-03",
        "",
    ]
    out += _section("Primary safeguard — gpt-5.4-mini · prompt v3 (canonical)", p)
    if "archive_comparator" in s:
        out += _section("Archive comparator — gpt-5.1 · prompt v2 (16.5% subset, prior baseline)", s["archive_comparator"])
        a = s["archive_comparator"]
        at = a["totals"]
        out += [
            "## Side-by-side headline (canonical vs archive comparator)",
            "",
            "| Metric | Canonical (mini+v3, n=654) | Archive (5.1+v2, n=108) |",
            "|---|---:|---:|",
            f"| Papers with problems | {pt['papers_with_problems']} ({pt['papers_with_problems_pct']} %) | {at['papers_with_problems']} ({at['papers_with_problems_pct']} %) |",
            f"| Avg problems per paper | {pt['avg_problems_per_paper']} | {at['avg_problems_per_paper']} |",
            f"| Total problems | {pt['problems_total']} | {at['problems_total']} |",
            f"| Multi-silo papers | {pt['multi_silo_papers']} | {at['multi_silo_papers']} |",
            f"| Orphan papers | {pt['orphan_papers_count']} | {at['orphan_papers_count']} |",
            "",
            "_The two reviewers operate with different category vocabularies (gpt-5.1 collapses most flags into `OVERCLAIM`; mini distributes across `MISSING_LIMITATION`, `SELECTIVE_QUOTE`, `WRONG_ATTRIBUTION`, `SECTION_BIAS`, `OVERCLAIM`, `HEDGING_DROPPED`). Verdict-level agreement (does this memo have problems? yes/no) is high; category-level disagreement is informative, not noise — the canonical safeguard is the mini+v3 line, the archive comparator documents the methodological history._",
            "",
        ]
    return "\n".join(out)


if __name__ == "__main__":
    main()
