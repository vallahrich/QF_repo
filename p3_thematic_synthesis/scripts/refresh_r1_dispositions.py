"""Phase 3 — refresh per-silo _disposition.json with stratified-review schema.

Closes step 3 of GL10_AUDIT.md G-02. After all 8 silos completed R1 review via
.github/skills/p3-r1-review, this script reads the per-silo decision logs +
worklists and rewrites each `{silo}/reviewed/_disposition.json` to record:

  - disposition_mode = "stratified_review" (was "batch_approval")
  - papers_individually_reviewed = sorted list of paper_ids in r1_review.jsonl
  - r1_coverage = {reviewed, total, pct, by_tier}
  - verdict_distribution = {approved, approved_with_caveat, requires_revision, flag_for_pull}
  - rubric_distribution = per-axis tally of yes/partial/no
  - r1_review_window = {first_decision, last_decision}
  - flagged_for_pull_paper_ids (if any) and requires_revision_paper_ids (if any)

Also writes a top-level aggregate at:
  p3_thematic_synthesis/s4_thematic_coding/r1_review_summary.json

Pre-existing fields (silo, papers_in_silo, papers_in_silo_count, reviewer,
evidence, compliance_pillars_addressed) are preserved verbatim. The freeze
header is updated to note the post-freeze R1 execution.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
S4 = REPO / "p3_thematic_synthesis" / "s4_thematic_coding"
SILOS = [
    "credit_lending",
    "derivative_pricing",
    "fraud_detection",
    "portfolio_optimization",
    "quantum_ml_finance",
    "risk_management",
    "simulation_monte_carlo",
    "trading_execution",
]
RUBRIC_AXES = (
    "memo_accuracy",
    "memo_completeness",
    "attribution_accuracy",
    "hedging_fidelity",
)
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def refresh_silo(silo: str) -> dict:
    silo_dir = S4 / silo / "reviewed"
    disp_path = silo_dir / "_disposition.json"
    log_path = silo_dir / "r1_review.jsonl"
    wl_path = silo_dir / "r1_review_worklist.jsonl"

    disp = json.loads(disp_path.read_text(encoding="utf-8"))
    log = _load_jsonl(log_path)
    wl = _load_jsonl(wl_path)

    pending = [w for w in wl if w.get("status") == "pending"]
    assert not pending, f"{silo}: worklist has {len(pending)} pending rows"

    log_by_pid = {row["paper_id"]: row for row in log}
    assert len(log_by_pid) == len(log), f"{silo}: duplicate paper_id in r1_review.jsonl"

    verdicts = Counter(r["verdict"] for r in log)
    verdict_dist = {
        "approved": verdicts.get("approved", 0),
        "approved_with_caveat": verdicts.get("approved_with_caveat", 0),
        "requires_revision": verdicts.get("requires_revision", 0),
        "flag_for_pull": verdicts.get("flag_for_pull", 0),
    }

    rubric_dist: dict[str, dict[str, int]] = {a: Counter() for a in RUBRIC_AXES}
    for r in log:
        scores = r.get("rubric_scores") or {}
        for axis in RUBRIC_AXES:
            v = scores.get(axis)
            if v:
                rubric_dist[axis][v] += 1
    rubric_dist = {a: dict(c) for a, c in rubric_dist.items()}

    by_tier = Counter(w.get("sampling_tier", "unspecified") for w in wl)
    flagged_pull = sorted(p for p, r in log_by_pid.items() if r["verdict"] == "flag_for_pull")
    revise = sorted(p for p, r in log_by_pid.items() if r["verdict"] == "requires_revision")

    timestamps = sorted(r["reviewed_at"] for r in log if r.get("reviewed_at"))
    review_window = {
        "first_decision": timestamps[0] if timestamps else None,
        "last_decision": timestamps[-1] if timestamps else None,
    }

    n_total = disp["papers_in_silo_count"]
    n_reviewed = len(log)

    new = dict(disp)  # preserve key order where possible
    new["_schema"] = "p3.s4.r1_disposition.v2"
    new["_generated"] = NOW
    new["_purpose"] = (
        "GL-10 G-02 closure — per-paper R1 stratified review at planned coverage. "
        "Replaces v1 batch-approval record."
    )
    new["_freeze_status"] = (
        "Generated AFTER the 2026-05-02 s4 freeze and AFTER the post-freeze R1 "
        "execution (2026-05-07 to 2026-05-08). No memos, themes, or projection "
        "manifests are modified by this refresh; this file IS the disposition record. "
        "R1-approved memo copies live under reviewed/{paper_id}.json; "
        "flag_for_pull memo copies (if any) live under reviewed/_pulled/{paper_id}.json."
    )
    new["disposition_mode"] = "stratified_review"
    new["disposition_verdict"] = (
        "approved" if (verdict_dist["requires_revision"] == 0 and verdict_dist["flag_for_pull"] == 0)
        else "approved_with_exceptions"
    )
    new["disposition_basis"] = (
        "Per-paper R1 review of a propagation-prioritised stratified sample under "
        "the four-axis rubric (memo accuracy / memo completeness / attribution accuracy / "
        "hedging fidelity), executed via .github/skills/p3-r1-review. Sample frame, "
        "sampling tiers, and verdicts are recorded below; per-paper decisions are "
        "appended in r1_review.jsonl."
    )
    new["papers_individually_reviewed"] = sorted(log_by_pid.keys())
    new.pop("papers_individually_reviewed_note", None)
    new["r1_coverage"] = {
        "reviewed": n_reviewed,
        "total_in_silo": n_total,
        "pct": round(100.0 * n_reviewed / n_total, 2),
        "sample_frame": "propagating subset (papers feeding ≥1 B1/B2 theme)",
        "by_sampling_tier": dict(sorted(by_tier.items())),
    }
    new["verdict_distribution"] = verdict_dist
    new["rubric_distribution"] = rubric_dist
    new["r1_review_window"] = review_window
    new["requires_revision_paper_ids"] = revise
    new["flagged_for_pull_paper_ids"] = flagged_pull
    new["r1_artefacts"] = {
        "decision_log": f"s4_thematic_coding/{silo}/reviewed/r1_review.jsonl",
        "worklist": f"s4_thematic_coding/{silo}/reviewed/r1_review_worklist.jsonl",
        "approved_memo_store": f"s4_thematic_coding/{silo}/reviewed/",
        "pulled_memo_store": f"s4_thematic_coding/{silo}/reviewed/_pulled/",
        "skill": ".github/skills/p3-r1-review/SKILL.md",
        "sampler": "p3_thematic_synthesis/scripts/r1_sample_worklist.py",
    }
    if "evidence" in new and isinstance(new["evidence"], dict):
        ev = new["evidence"]
        ev["r1_stratified_review"] = {
            "status": "executed",
            "reviewed": n_reviewed,
            "total_in_silo": n_total,
            "pct": round(100.0 * n_reviewed / n_total, 2),
            "rubric_axes": list(RUBRIC_AXES),
            "verdict_distribution": verdict_dist,
        }
        if "deferred_validation" in ev and isinstance(ev["deferred_validation"], dict):
            if "l4_rubric_review_10pct" in ev["deferred_validation"]:
                ev["deferred_validation"]["l4_rubric_review_10pct"]["status"] = "executed"
                ev["deferred_validation"]["l4_rubric_review_10pct"]["closure_note"] = (
                    "Renamed in v2 to 'r1_stratified_review' and executed 2026-05-07 to 2026-05-08; "
                    "see r1_coverage and verdict_distribution above."
                )

    disp_path.write_text(
        json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "silo": silo,
        "reviewed": n_reviewed,
        "total": n_total,
        "pct": round(100.0 * n_reviewed / n_total, 2),
        "verdicts": verdict_dist,
        "rubric": rubric_dist,
        "by_tier": dict(sorted(by_tier.items())),
        "flag_for_pull": flagged_pull,
        "requires_revision": revise,
    }


def main() -> None:
    summaries = [refresh_silo(s) for s in SILOS]
    total_reviewed = sum(s["reviewed"] for s in summaries)
    total_in_silos = sum(s["total"] for s in summaries)
    overall_verdicts = Counter()
    overall_rubric: dict[str, Counter] = {a: Counter() for a in RUBRIC_AXES}
    overall_tiers: Counter = Counter()
    pulls: list[dict] = []
    revisions: list[dict] = []
    for s in summaries:
        overall_verdicts.update(s["verdicts"])
        for axis in RUBRIC_AXES:
            overall_rubric[axis].update(s["rubric"].get(axis, {}))
        overall_tiers.update(s["by_tier"])
        for pid in s["flag_for_pull"]:
            pulls.append({"silo": s["silo"], "paper_id": pid})
        for pid in s["requires_revision"]:
            revisions.append({"silo": s["silo"], "paper_id": pid})

    aggregate = {
        "_schema": "p3.s4.r1_review_summary.v1",
        "_generated": NOW,
        "_purpose": "Aggregate roll-up of per-silo R1 stratified review (GL10 G-02 closure).",
        "aggregate_coverage": {
            "reviewed": total_reviewed,
            "total_in_silos": total_in_silos,
            "pct": round(100.0 * total_reviewed / total_in_silos, 2),
            "by_sampling_tier": dict(sorted(overall_tiers.items())),
        },
        "verdict_distribution": dict(overall_verdicts),
        "rubric_distribution": {a: dict(c) for a, c in overall_rubric.items()},
        "per_silo": [
            {
                "silo": s["silo"],
                "reviewed": s["reviewed"],
                "total_in_silo": s["total"],
                "pct": s["pct"],
                "verdicts": s["verdicts"],
                "by_sampling_tier": s["by_tier"],
            }
            for s in summaries
        ],
        "flagged_for_pull": pulls,
        "requires_revision": revisions,
    }
    out = S4 / "r1_review_summary.json"
    out.write_text(json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"R1 disposition refresh — {NOW}")
    print(
        f"{'silo':<25} {'rev':>4} {'tot':>4} {'pct':>6}  {'A':>3} {'C':>3} {'R':>3} {'P':>3}"
    )
    for s in summaries:
        v = s["verdicts"]
        print(
            f"{s['silo']:<25} {s['reviewed']:>4} {s['total']:>4} {s['pct']:>6}  "
            f"{v['approved']:>3} {v['approved_with_caveat']:>3} "
            f"{v['requires_revision']:>3} {v['flag_for_pull']:>3}"
        )
    print(
        f"\nTotal reviewed: {total_reviewed} / {total_in_silos} "
        f"({round(100.0 * total_reviewed / total_in_silos, 2)} %)"
    )
    print(f"Verdicts: {dict(overall_verdicts)}")
    print(f"Tiers:    {dict(overall_tiers)}")
    print(f"Pulls:    {len(pulls)}  Revisions: {len(revisions)}")
    print(f"Aggregate written: {out.relative_to(REPO)}")


if __name__ == "__main__":
    main()
