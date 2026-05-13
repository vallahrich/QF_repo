# P4 Canonical Decisions Log

## 2026-05-12 - Cosmetic figure regeneration

- Decision: Re-rendered `canonical/outputs/figures/h_figures_sidecar.json` (and its 7 PNG outputs) and `canonical/outputs/figures/p4_hoefler_crossover.json` (and its 3 PNG/PDF outputs) for visual presentation tweaks.
- Rationale: Cosmetic only — colour scheme / layout / labelling adjustments to match the manuscript figure conventions.
- Scope: Source inputs (`stats_report.json`, `oracle_tax_table.json`, `cohort.json`, `evidence_report.json`) unchanged. No data, hypothesis, or numerical claim affected. The two regenerated sidecar JSONs carry `generated_utc` 2026-05-12T14:24Z and 2026-05-12T17:53Z respectively to attest the cosmetic re-render; their `source_inputs` paths and structural content are otherwise unchanged.
- Result direction: unchanged. All Phase-9 / Phase-10 numbers identical to the 2026-04-26 evidence pack.

## 2026-04-28 - H2 active-P3-silo scope amendment

- Decision: Path A accepted. H2 headline Kruskal-Wallis and the H2 MixedLM sensitivity now restrict silo-level inference to the active Phase 3 problem-domain silos declared in `shared/config/silo_inclusion.json` and recorded in `cohort.json::_p3_scope_disposition`.
- Rationale: H2 is the statistical companion to the Phase 3 propositions, so it must test the same silo universe argued in the Phase 3 chapter. The cohort silo `other` has Faithful labels but is not a Phase 3 problem-domain silo; including it created a structural mismatch between the propositions and the hypothesis test.
- Scope: out-of-P3-scope labels remain in full-corpus coverage, appendix, and sensitivity reporting where appropriate, but are excluded from H2 inference.
- Implementation: `phase09_stats.py` applies the active-P3-silo filter to H2 and its MixedLM sensitivity; `audit_phase03.py` now checks the scope-disposition metadata against `shared/config/silo_inclusion.json` and the live cohort labels.
- Result direction: unchanged. H2 remains not accepted after excluding out-of-P3-scope labels.

## 2026-04-26 - Phase 9/10 evidence pack and documentation cleanup

- Phase 8 canonical grid is complete: 2556 records, 2519 OK, 37 documented `engine_failure`, 0 missing.
- Phase 9 now writes `evidence_report.json` and keeps H1-H4 headline inference on `canonical_s2_backed_label_grid`.
- Phase 10 now writes a 27-artifact manuscript pack plus H figures, including claim-evidence, H1/H2/H3/H4, engine-failure, and regime-boundary artifacts.
- Phase 8d HHL/QAE is explicitly `qae_hhl_fixed_precision_high_n`, appendix-only, and excluded from headline H1-H4 pooling.
- Root and canonical P4 markdown were refreshed to remove pilot-era size/fidelity language and to point readers to `evidence_report.json` and `manuscript_artifacts/key_numbers.json` as the current Results/Discussion source of truth.

## 2026-04-25 - S2-backed canonical repair

- Current source of truth: `p3_thematic_synthesis/s2_quantitative/output/extractions/`.
- Current resolution key: `paper_id + experiment_id`.
- Current adjudication layer: Vincent review worksheets plus completed joint triage in `p4_experiments/experiments/review/phase8_faithfulness_review/`.
- Current checked P4 data file: `p4_experiments/canonical/cohort.json`.
- Current cohort: 71 labels, `F=13`, `P=58`.
- Current faithful labels: `SD3`, `SD7`, `SD8`, `SD10`, `SD12`, `SD13`, `SM5`, `SQ5`, `SQ17`, `SQ18`, `SX2`, `SX3`, `SX5`.
- Retired generated outputs and obsolete subphase scripts were removed from the active P4 tree.
- Downstream Phase 6-11 artifacts must be regenerated before use.

Historical decision prose is intentionally not maintained in the active P4
workspace once it conflicts with the S2-backed state. Use git history for
archeology; use the files listed in [README.md](README.md) for current work.
