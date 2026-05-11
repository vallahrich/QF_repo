"""Generate per-silo R1 _disposition.json files.

Materialises the GL-10 G-01 acceptance evidence as a JSON artefact in
`s4_thematic_coding/<silo>/reviewed/_disposition.json`. The file records:

- The R1 disposition mode for the silo (batch_approval).
- The pipeline-quality evidence the disposition rests on
  (L3 sample, c2 grounding check, B2 rubric, prompt SHAs, model identity).
- The list of paper_ids covered by the silo (from per-silo memos/).
- An empty papers_individually_reviewed list with an honest note that the
  2026-04-22 spot-check (~15 papers across all silos) did not preserve
  per-paper IDs, so backfilling them would be a fabrication.

This is the audit gesture described in
`docs/PRODUCTION_ARCHITECTURE.md` line 192. The file is the disposition
record; no memos move into a `reviewed/` subdirectory because the s4
freeze (2026-05-02) precedes the introduction of this artefact.

Run once after the freeze; safe to re-run (overwrites).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
S4_ROOT = REPO_ROOT / "p3_thematic_synthesis" / "s4_thematic_coding"
MANIFEST_PATH = S4_ROOT / "campaign_manifest.json"

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


def main() -> None:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        manifest = json.load(f)

    common_evidence = {
        "campaign_id": manifest["campaign_id"],
        "git_commit": manifest["git_commit"],
        "models": manifest["models"],
        "prompt_version": manifest["prompt_version"],
        "temperature": manifest["temperature"],
        "l3_adversarial_sample": {
            "scope": "central, applied across silos",
            "records": 108,
            "fraction_of_a2_memos_pct": 16.5,
            "summary_artefact": "s4_thematic_coding/L3_SUMMARY.md",
        },
        "c2_grounding_check": {
            "scope": "per-silo theme-to-code grounding verification",
            "artefact_per_silo": "themes/c2_grounding_check.json (+ .raw_response, .meta)",
        },
        "b1_min_papers_per_theme": 3,
        "b2_rubric_script": "p3_thematic_synthesis/scripts/score_b2_rubric.py",
        "spot_check": {
            "date": "2026-04-22",
            "scope_text": "~15 papers across all silos (~5 production + ~10 pilot)",
            "verdict": "All the ones I read look ready for me, pretty happy with the result.",
            "reviewer": "Aleix",
            "evidence_path": "p3_thematic_synthesis/docs/AUDIT_LOG.md (17:30 entry)",
            "paper_ids_recorded": False,
            "paper_ids_note": "The original spot-check did not record per-paper IDs. Backfilling a list now would be a fabrication. Honest disclosure preferred.",
        },
        "deferred_validation": {
            "l4_rubric_review_10pct": {
                "status": "deferred",
                "scope": "~65 papers with rubric scores",
                "where_disclosed": "p3_thematic_synthesis/FREEZE.md (Deferred section, GL-10 caveats)",
            },
            "inter_rater_kappa": {
                "status": "not_performed",
                "rationale": "Single-coder design; LLM-adversarial L3 + c2 grounding act as bias-mitigation substitute.",
                "where_disclosed": "p3_thematic_synthesis/FREEZE.md (Deferred section, GL-10 caveats)",
            },
            "a3_contradiction_scan": {
                "status": "deferred",
                "rationale": "Prompt retained for traceability; not executed in v2026-05-02 freeze.",
                "where_disclosed": "p3_thematic_synthesis/FREEZE.md (Deferred section, GL-10 caveats)",
            },
        },
    }

    written = 0
    for silo in ACTIVE_SILOS:
        memos_dir = S4_ROOT / silo / "memos"
        if not memos_dir.is_dir():
            print(f"skip {silo}: no memos/")
            continue
        paper_ids = sorted(
            p.stem
            for p in memos_dir.glob("*.json")
            if not p.stem.endswith("_l3")
        )
        reviewed_dir = S4_ROOT / silo / "reviewed"
        reviewed_dir.mkdir(parents=True, exist_ok=True)

        disposition = {
            "_schema": "p3.s4.r1_disposition.v1",
            "_generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "_purpose": "GL-10 G-01 — materialise R1 acceptance evidence post-freeze",
            "_freeze_status": "Generated AFTER the 2026-05-02 s4 freeze. No memos are moved or modified; this file IS the disposition record.",
            "silo": silo,
            "disposition_mode": "batch_approval",
            "disposition_verdict": "approved",
            "disposition_basis": (
                "Acceptance rests on (a) the per-silo pipeline-quality artefacts "
                "(L3 adversarial sample summarised in L3_SUMMARY.md, c2 grounding "
                "check, B1 min-3-papers-per-theme rule, B2 rubric availability, "
                "deterministic temperature=0 with prompt-SHA-locked rendering) "
                "and (b) the 2026-04-22 researcher spot-check noted in "
                "docs/AUDIT_LOG.md. The 10 % rubric-scored review is deferred "
                "to pre-defence with disclosure in FREEZE.md."
            ),
            "papers_in_silo_count": len(paper_ids),
            "papers_individually_reviewed": [],
            "papers_individually_reviewed_note": (
                "Empty by design. The 2026-04-22 spot-check covered ~15 papers "
                "across all silos but did not preserve per-paper IDs; honest "
                "disclosure is preferred over reconstructing a list. The "
                "batch-approval verdict above applies uniformly to every paper "
                "listed in `papers_in_silo`."
            ),
            "papers_in_silo": paper_ids,
            "reviewer": {
                "name_initials": "AT",
                "role": "researcher",
                "date_of_disposition": "2026-04-22",
                "disposition_recorded_on": datetime.now(timezone.utc).date().isoformat(),
            },
            "evidence": common_evidence,
            "compliance_pillars_addressed": {
                "P1_declaration": "FREEZE.md + Appendix H (pending) + this file",
                "P2_role_framing": "Researcher acceptance recorded as batch approval; LLM framed as candidate-producer",
                "P3_audit_trail": "campaign_manifest.json + per-call prompt/raw/meta/sanitize_log siblings",
                "P4_reproducibility": "campaign_manifest.json `parameters_used` block (G-04 patch)",
                "P5_validation": "L3 sample (16.5 %) + c2 grounding + B1 rules + spot-check",
            },
        }

        out_path = reviewed_dir / "_disposition.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(disposition, f, indent=2, ensure_ascii=False)
        written += 1
        print(f"wrote {out_path}")

    print(f"\nTotal silos written: {written}")


if __name__ == "__main__":
    main()
