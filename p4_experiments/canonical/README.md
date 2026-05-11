# P4 Canonical Pipeline

This directory is the active S2-backed Phase 4 canonical state. The source of truth for paper facts is the S2 quantitative extraction directory, resolved by `paper_id + experiment_id`; P4 adds Vincent/manual review and joint triage adjudication before any resource-estimation result is treated as evidence.

> ⚠️ **Mixed historical / current content** (banner added 2026-05-02 freeze).
>
> The active 2026-05-02 hardening state uses explicit implementation tiers.
> **Treat [../FREEZE.md](../FREEZE.md), [PRE_REGISTRATION.md](PRE_REGISTRATION.md),
> [reports/evidence_report.json](reports/evidence_report.json), and
> [outputs/manuscript_artifacts/key_numbers.json](outputs/manuscript_artifacts/key_numbers.json)
> as the controlling artifact sources:**
>
> - active estimator-cohort paper-faithful-strict labels: **0**
> - active estimator-cohort paper-family-template labels: **13**
> - active estimator-cohort proxy labels: **58**
> - canonical Phase-8 grid: 71 × 6 profiles × 3 ε × 2 modes = **2556** cells
>   (2519 OK + 37 documented engine failures)
>
> The legacy "13 Faithful / 58 Proxy" phrasing below is retained only as a
> compatibility shorthand; it must not be read as paper-exact evidence.

## Current Counts

- Total labels: 71
- Family/template labels: 13
- Proxy-declared labels: 58
- Strict-tier estimator labels: 0
- Active silos: 8
- Canonical Phase 8 cells: 2556
- Phase 8 outcomes: 2519 OK, 37 documented `engine_failure`, 0 missing
- Phase 9 audit: 9 PASS / 0 FAIL
- Phase 10 audit: 7 PASS / 0 FAIL, with all 27 manuscript artifacts present
- Appendix Phase 8d scout: 108 records, 72 OK, 36 documented `engine_failure`, audit clean

Family/template labels: `SD3`, `SD7`, `SD8`, `SD10`, `SD12`, `SD13`, `SM5`, `SQ5`, `SQ17`, `SQ18`, `SX2`, `SX3`, `SX5`.

## Result Regimes

P4 now carries two explicitly separated experiment regimes:

| Regime | Role | Included in headline H1-H4? |
|---|---|---|
| `canonical_s2_backed_label_grid` | Pre-registered 71-label canonical grid over profiles, epsilons, and bare/full modes | Yes |
| `qae_hhl_fixed_precision_high_n` | Appendix-only fixed-precision HHL/QAE high-N scout in [outputs/phase08d_qae_hhl_scout/](outputs/phase08d_qae_hhl_scout/) | No |

The HHL/QAE scout varies problem size `N` while holding precision qubits `m` on an explicit grid. It is scaling evidence for the appendix and discussion, not a modifier of the headline Phase 8/9 verdict.

## Active Files

| File or folder | Purpose |
|---|---|
| [PRE_REGISTRATION.md](PRE_REGISTRATION.md) | Active canonical contract and reporting rules |
| [REPRODUCE.md](REPRODUCE.md) | Rebuild, audit, and release-bundle instructions |
| [THREATS_TO_VALIDITY.md](THREATS_TO_VALIDITY.md) | Current threats, mitigations, and residual risks |
| [DECISIONS_LOG.md](DECISIONS_LOG.md) | Dated decisions and operator notes |
| [cohort.json](cohort.json) | Checked 71-label cohort and phase status |
| [reports/phase3_compare.json](reports/phase3_compare.json) | S2-backed Phase 3 comparison |
| [reports/stats_report.json](reports/stats_report.json) | Phase 9 H1-H4 statistical results |
| [reports/oracle_tax_table.json](reports/oracle_tax_table.json) | Phase 9 oracle-tax ratios |
| [reports/sensitivity_grid.json](reports/sensitivity_grid.json) | Phase 9 H4 sensitivity grid |
| [reports/evidence_report.json](reports/evidence_report.json) | Phase 9 evidence layer for manuscript claims and regime boundaries |
| [reports/surviving_engine_failures.json](reports/surviving_engine_failures.json) | Documented Phase 8 engine failures |
| [reports/audit/](reports/audit/) | Generated audit JSON reports |
| [outputs/manuscript_artifacts/](outputs/manuscript_artifacts/) | Phase 10 tables, figure CSVs, briefs, captions, and key numbers |
| [outputs/phase08c_alternatives/](outputs/phase08c_alternatives/) | Phase 8c top-3 classical-alternative records |
| [pipeline/](pipeline/) | Authoritative Phase 3-11 executable phase scripts |
| [audits/](audits/) | Authoritative audit scripts |
| [data/](data/) | Canonical data helpers, including the S2 extraction index |
| [reports/](reports/) | Generated report namespace |
| [release/](release/) | Phase 11 release bundle, tarball, and checksum sidecar |
| [outputs/phase08d_qae_hhl_scout/](outputs/phase08d_qae_hhl_scout/) | Appendix-only Phase 8d HHL/QAE scout |
| [outputs/phase08e_per_silo/](outputs/phase08e_per_silo/) | Phase 8e per-silo synthesis cards |

The 2556 canonical Phase 8 result records live in [../common/output/results/](../common/output/results/), not in this directory.

## Phase Order

The orchestrator [run_pipeline.py](run_pipeline.py) owns the active order:

1. `phase3_compare` - resolve the cohort against S2 quantitative extraction files.
2. `phase3` - write the checked cohort.
3. `phase4` - maintain proxy justifications for P-tier labels.
4. `phase5` - assign paper-stated or silo-default classical baselines.
5. `phase6` - record skip-cell and engine-failure policy.
6. `phase8` - run the 2556-cell resource-estimation grid.
7. `phase8b_run` / `phase8b_cohort` - measure and backfill classical baselines.
8. `phase8c_alternatives` - run top-3 classical alternatives.
9. `phase9` - compute H1-H4 statistics, sensitivity, and evidence report.
10. `phase8d_select` / `phase8d` - optional external appendix-only HHL/QAE scout.
11. `phase10` - generate manuscript artifacts and figure source data.
12. `phase8e` - generate per-silo synthesis cards.
13. `phase11` - build a hash-stamped Zenodo bundle.

Phase 8d is external VM-backed compute and is not run by the default orchestrator. The current local Phase 8d scout is finalized and audited; use `--include-phase8d` only after synced scout result records are present for a future rerun. VM setup, sync, monitor, and helper scripts live under [../infra/azure/phase8_6vm_20260425/](../infra/azure/phase8_6vm_20260425/).

[run_pipeline.py](run_pipeline.py) dispatches the implementation modules under [pipeline/](pipeline/) and [audits/](audits/). Use those structured namespaces for direct execution; the older flat `phase*.py`, `audit_phase*.py`, `finalize_phase8_results.py`, and `s2_extraction_index.py` wrapper layer has been removed from the handoff tree.

## Generated Evidence Artifacts

These generated files are repository evidence artifacts and claim-support inputs:

- [outputs/manuscript_artifacts/key_numbers.json](outputs/manuscript_artifacts/key_numbers.json) for exact headline counts and p-values.
- [outputs/manuscript_artifacts/results_brief.md](outputs/manuscript_artifacts/results_brief.md) for compact Results prose.
- [outputs/manuscript_artifacts/discussion_claims.md](outputs/manuscript_artifacts/discussion_claims.md) for claim-by-claim interpretation.
- [outputs/manuscript_artifacts/caption_pack.md](outputs/manuscript_artifacts/caption_pack.md) for artifact captions.
- [outputs/manuscript_artifacts/table_claims_evidence_matrix.tex](outputs/manuscript_artifacts/table_claims_evidence_matrix.tex) for the claim-evidence matrix.
- [outputs/manuscript_artifacts/table_experiment_regimes.tex](outputs/manuscript_artifacts/table_experiment_regimes.tex) for the regime boundary.

## Generated and Superseded Layers

The active canonical tree no longer treats old planning docs, pilot reports, or pre-S2 generated summaries as current evidence. Use git history for historical context.

[release/zenodo_bundle/](release/zenodo_bundle/) and [release/zenodo_bundle.tar.gz](release/zenodo_bundle.tar.gz) are generated Phase 11 release artifacts. Do not hand-edit files inside the bundle because the manifest hashes would no longer match. Rebuild Phase 11 after final Phase 9/10/8e changes when a fresh release hash is needed.
Phase 11 / Zenodo bundle artifacts were not regenerated in this hardening pass; rebuild Phase 11 before publishing a new release hash.
