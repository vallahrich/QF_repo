# `p3_thematic_synthesis/scripts/` — Phase 3 pipeline scripts

Cross-silo orchestration, persistence, and reporting code for Phase 3.

| Script | Purpose |
|--------|---------|
| `run_thematic_pipeline.py` | Top-level driver for the per-silo a1→b2 ladder. |
| `run_production.py` | Production batch entrypoint used to generate the frozen P3 outputs. |
| `run_a2_l3_only.py` | Re-run only the a2 + l3 stages (used during remediation). |
| `render_c1_prompt.py`, `render_c2_prompts.py`, `render_c3_prompt.py` | Build the cross-silo C1/C2/C3 prompts from per-silo b2 outputs. |
| `validate_and_persist_b1.py` / `b2.py` / `c1.py` / `c2.py` | Schema-validate and write per-stage outputs. |
| `sanitize_and_persist_b1.py` | Pre-persist normalisation for b1. |
| `score_b2_rubric.py` | Apply the B2 quality rubric to analytical themes. |
| `b1_b2_lib.py` | Shared helpers used by the b1/b2 scripts. |
| `build_code_memo_index.py` | Index of codes + memos across silos. |
| `build_crosswalk_shortlist.py` | Shortlist for the C3 theme↔literature crosswalk. |
| `build_inclusion_lists.py` | Per-silo paper inclusion lists from P2 outputs. |
| `build_p3_p4_cohort_join.py` | Join P3 silo membership with the P4 experiment cohort. |
| `build_silo_data_sheets.py` | Per-silo data-sheet markdowns under `output/`. |
| `bibliometric_landscape.py` | Phase-level bibliometric summaries. |
| `generate_audit_reviews.py` | Audit-trail rendering for stage outputs. |
| `model_comparison.py` | LLM model A/B comparison utility. |
| `pilot_analysis.py` | Pre-production pilot diagnostics. |
| `text_readiness_gate.py` | Gate that input texts are LLM-ready before a stage runs. |
| `fetch_silo_docs.py` | Pull per-silo paper texts into the silo working dirs. |
| `report_missing_papers.py` | Diagnose missing-paper coverage. |
| `output/` | Generated silo data-sheets and other script outputs (see [`output/README.md`](output/README.md)). |

See parent [`../README.md`](../README.md) and
[`../docs/PRODUCTION_ARCHITECTURE.md`](../docs/PRODUCTION_ARCHITECTURE.md).