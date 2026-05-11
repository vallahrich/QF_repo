# Reproducibility Protocol - Phase 4 Canonical Pipeline

This protocol rebuilds the current S2-backed P4 canonical pipeline and its audit trail. It supersedes older pilot-era instructions from the pre-S2 repair state.

## Current Guarantees

The canonical run is designed to provide:

1. Deterministic record generation under seed `0x50414D50`.
2. Complete cell accounting for the canonical grid: every expected cell is either OK or a documented `engine_failure`.
3. Traceability from each manuscript claim back to `cohort.json`, Phase 8 records, Phase 9 statistics, and Phase 10 artifacts.

Current audited state:

| Item | Value |
|---|---:|
| Labels | 71 |
| Faithful labels | 13 |
| Proxy-declared labels | 58 |
| Silos | 8 |
| Expected Phase 8 cells | 2556 |
| OK Phase 8 records | 2519 |
| Documented `engine_failure` records | 37 |
| Missing Phase 8 records | 0 |
| H4 canonical winners | 0 |
| Phase 10 manuscript artifacts | 27 |

## Environment

Use the repository root as the working directory:

```powershell
cd quantum-finance
$py = if (Test-Path ".\.venv\Scripts\python.exe") { ".\.venv\Scripts\python.exe" } elseif (Test-Path "..\.venv\Scripts\python.exe") { "..\.venv\Scripts\python.exe" } else { "python" }
& $py -m p4_experiments.canonical.run_pipeline --dry-run
```

The checked environment for the current local run used:

| Dependency | Version |
|---|---|
| Python | 3.13.13 |
| qsharp / QDK | 1.27.0 |
| qiskit | 2.3.0 |
| qiskit-aer | 0.17.2 |

For portable replication, use [Dockerfile](Dockerfile) and [requirements.lock](requirements.lock). Keep BLAS/Aer threading pinned to one thread for reproducible wall-clock baseline measurements.

## Rebuild Commands

Run all non-external phases that are not already complete:

```powershell
python -m p4_experiments.canonical.run_pipeline --resume
```

Run a fresh local rebuild from the checked cohort state:

```powershell
python -m p4_experiments.canonical.run_pipeline --from-scratch --seed 0x50414D50
```

Run selected phases after editing the analysis/artifact layer:

```powershell
python -m p4_experiments.canonical.run_pipeline --phases phase9,phase10
python -m p4_experiments.canonical.audits.audit_phase09
python -m p4_experiments.canonical.audits.audit_phase10
```

Phase 8d is an external, appendix-only HHL/QAE scout. It is not launched by the default orchestrator. The current local scout is finalized under [outputs/phase08d_qae_hhl_scout/results/](outputs/phase08d_qae_hhl_scout/results/). VM setup, sync, monitor, and helper tooling lives under [../infra/azure/phase8_6vm_20260425/](../infra/azure/phase8_6vm_20260425/). After future VM results are synced there, finalize and audit it with:

```powershell
python -m p4_experiments.canonical.pipeline.phase08d_select_experiments
python -m p4_experiments.canonical.pipeline.phase08d_finalize_qae_hhl
python -m p4_experiments.canonical.audits.audit_phase08d
```

To include Phase 8d in an orchestrated run:

```powershell
python -m p4_experiments.canonical.run_pipeline --resume --include-phase8d
```

## Phase Ladder

The active orchestrator executes this order:

1. `phase3_compare` - resolve the 71-label cohort against S2 quantitative extraction files by `paper_id + experiment_id`.
2. `phase3` - write the checked cohort from S2, Vincent/manual review, and joint triage adjudication.
3. `phase4` - write proxy justifications for the 58 P-tier labels and clear stale proxy metadata from the 13 F labels.
4. `phase5` - assign paper-stated or silo-default classical baselines.
5. `phase6` - record timeout, skip-cell, and `engine_failure` policy.
6. `phase8` - run the 2556-cell canonical resource-estimation matrix.
7. `phase8b_run` / `phase8b_cohort` - measure and backfill classical baselines.
8. `phase8c_alternatives` - run top-3 classical alternatives for coverage and H4 sensitivity.
9. `phase9` - write `stats_report.json`, `oracle_tax_table.json`, `sensitivity_grid.json`, and `evidence_report.json`.
10. `phase8d_select` / `phase8d` - optional external appendix-only fixed-precision HHL/QAE scout.
11. `phase10` - emit manuscript tables, figure data, key numbers, markdown briefs, and figures.
12. `phase8e` - emit per-silo synthesis cards and LaTeX tables.
13. `phase11` - build the Zenodo bundle and manifest.

## Artifact Map

| Artifact | Purpose |
|---|---|
| [cohort.json](cohort.json) | Checked cohort and phase status |
| [../common/output/results/](../common/output/results/) | 2556 Phase 8 result records |
| [reports/stats_report.json](reports/stats_report.json) | H1-H4 statistical results |
| [reports/oracle_tax_table.json](reports/oracle_tax_table.json) | Oracle-tax ratios by label/profile/epsilon |
| [reports/sensitivity_grid.json](reports/sensitivity_grid.json) | H4 sensitivity across thresholds and baselines |
| [reports/evidence_report.json](reports/evidence_report.json) | Structured Phase 9 evidence for Results/Discussion |
| [outputs/manuscript_artifacts/](outputs/manuscript_artifacts/) | Phase 10 tables, figure CSVs, briefs, captions, key numbers |
| [outputs/phase08c_alternatives/](outputs/phase08c_alternatives/) | Phase 8c top-3 classical alternatives |
| [outputs/phase08d_qae_hhl_scout/](outputs/phase08d_qae_hhl_scout/) | Appendix-only HHL/QAE fixed-precision high-N scout |
| [outputs/phase08e_per_silo/](outputs/phase08e_per_silo/) | Per-silo synthesis cards |
| [release/zenodo_bundle/](release/zenodo_bundle/) | Generated Phase 11 release snapshot |

## Numerical Checks

Exact-match required for the current local audit:

- The set of expected Phase 8 filenames.
- Record schemas and status fields.
- H1-H4 keys in `stats_report.json`.
- Regime keys in `evidence_report.json`.
- Required Phase 10 artifact filenames and well-formed CSV/LaTeX/Markdown outputs.

Known non-deterministic fields, such as wall-clock timestamps and local git hashes, should not be used as byte-identity evidence.

## Zenodo Bundle

Phase 11 creates [release/zenodo_bundle/](release/zenodo_bundle/), [release/zenodo_bundle.tar.gz](release/zenodo_bundle.tar.gz), and the SHA-256 sidecar. The bundle is generated and hash-stamped, so do not edit files inside it manually.

After final Phase 9/10/8e changes, rebuild the bundle explicitly:

```powershell
python -m p4_experiments.canonical.pipeline.phase11_zenodo_bundle
python -m p4_experiments.canonical.audits.audit_phase11
```

The current bundle generator includes `evidence_report.json`, all Phase 10 manuscript artifacts, all figures, `surviving_engine_failures.json`, and the 2556 Phase 8 result records.

## Manuscript Statement Template

All records, tables, and figures reported for P4 are reproducible from the canonical pipeline under seed `0x50414D50`. The headline H1-H4 inference uses only the `canonical_s2_backed_label_grid` regime; the `qae_hhl_fixed_precision_high_n` HHL/QAE scout is appendix-only scaling evidence and is not pooled into H1-H4. The current Phase 8 grid contains 2556 cells with 2519 OK records and 37 documented `engine_failure` records, and the Phase 9/10 audits pass with no blocker failures.
