# Quantum Advantage Triangulation — FROZEN 2026-04-17

> Historical freeze note (2026-04-28): this document describes the 2026-04-17
> frozen S3 run. It is not the current active P3 baseline. Current active S2/S3
> state is 501 extraction files / 1046 experiments, with S2 under
> `p3_thematic_synthesis/s2_quantitative/` and S3 under
> `p3_thematic_synthesis/s3_quantum_advantage/`. See
> `../../P3_P4_STATUS_BASELINE.md` and `../P3_AUDIT_STATUS.md` before using any
> counts or reproduction commands here.

## Scope

4-core + 1-optional-veto triangulation of the P3 quantitative corpus against
seven advantage-assessment frameworks.

- **Upstream corpus:** 459 papers / 1185 experiments
  (`p3_thematic_synthesis/quantitative/output/extractions/`), 100% schema-valid
  as of the 2026-04-17 quantitative freeze.
- **Frameworks (active):** Rønnow 2014, Hoefler 2023, Babbush 2021,
  Beverland 2022, Chakrabarti 2021, Dalzell 2023, Stilck França 2021.
- **Legacy (not in triangulation):** Montanaro 2015, Dequantization.

## Verdict distribution

| Consensus label         | Count | Percent |
|-------------------------|------:|--------:|
| majority_fails          |   425 |  35.9 % |
| low_coverage_fails      |   285 |  24.1 % |
| unanimous_fails         |   153 |  12.9 % |
| split                   |   139 |  11.7 % |
| insufficient_data       |    95 |   8.0 % |
| majority_viable         |    87 |   7.3 % |
| low_coverage_viable     |     1 |   0.1 % |
| **Total**               | **1185** | **100 %** |

Schema validation: **1185/1185 rows pass** `triangulation_row_v1.0`.

NISQ veto applied: **0** experiments (see `consensus_summary.json`
→ `nisq_veto_diagnostic` for eligibility breakdown — the veto does not fire
because no `majority_viable` variational-algorithm row has a Stilck verdict
of `conditional` or `fails`).

## Key methodology changes in this freeze

1. **Duplicate experiment_ids deduplicated at load time.** 51 papers had
   within-paper duplicate `experiment_id` values (e.g. two `exp_4`); the
   QA loader now suffixes duplicates with `__dupN` to preserve every row.
   Previous triangulation silently dropped 71 rows.
2. **Beverland aggregation policy.** Top-level verdict is now the *median*
   scenario (`aggregation_policy=balanced`), not best-case. Conservative
   and optimistic policies are selectable in `beverland_scenarios.json`.
   Full per-scenario grid remains in `framework_specific.scenario_verdicts`.
3. **Chakrabarti honors T-depth.** Assessor now reads T-depth from
   `quantum_resources.t_depth` (or `circuit_depth` as proxy) and compares
   against the envelope T-depth bounds; missing T-depth downgrades an
   otherwise-passing row from `potentially_viable` to `conditional`.
4. **Dalzell honors T-depth.** Same treatment: `min_t_depth` from each
   silo's MSA now participates in the three-dimensional resource check.
5. **Stilck França coverage broadened.** Applicable-families list now
   includes `quantum-ml`, `quantum-svm`, `qnn`/`qcbm`/`qgan`, and their
   common aliases. Noise inference now also considers hardware platform
   strings and maturity level (L3/L4 QPU → superconducting default).
   Variational-family coverage grew 261 → 368 experiments.
6. **Triangulation matrix is schema-validated.** Every row checked against
   `combined/triangulation_row_schema.json` on every run.

## File fingerprints (sha256, first 16 chars)

```
b8b25684ab7a0255  combined/output/triangulation_matrix.json
aa533fe0e08c4204  combined/output/consensus_summary.json
675404582158360c  combined/output/disagreement_cases.json
1e1db51267d9bc2a  ronnow/results/ronnow_results.json
9c5359e4a726c4e0  hoefler_assessment/results/hoefler_results.json
9a7b7ed9356e2438  babbush_2021/results/babbush_results.json
cc93eeeec87d65bb  beverland_2022/results/beverland_results.json
46531956a71c513b  chakrabarti_2021/results/chakrabarti_results.json
57ddcb0ae1ffe8bd  dalzell_2023/results/dalzell_results.json
9d9bdb44bd38a6c8  stilck_franca_2021/results/stilck_franca_results.json
fa1732b2a2c4f582  derived_fields/enriched/derived_fields.json
```

## Reproduction

```powershell
cd quantum-finance
python -m p3_thematic_synthesis.s3_quantum_advantage.derived_fields.compute_derived_fields
python -m p3_thematic_synthesis.s3_quantum_advantage.ronnow.assess_ronnow
python -m p3_thematic_synthesis.s3_quantum_advantage.hoefler_assessment.assess_hoefler
python -m p3_thematic_synthesis.s3_quantum_advantage.babbush_2021.assess_babbush
python -m p3_thematic_synthesis.s3_quantum_advantage.beverland_2022.assess_beverland
python -m p3_thematic_synthesis.s3_quantum_advantage.chakrabarti_2021.assess_chakrabarti
python -m p3_thematic_synthesis.s3_quantum_advantage.dalzell_2023.assess_dalzell
python -m p3_thematic_synthesis.s3_quantum_advantage.stilck_franca_2021.assess_stilck_franca
python -m p3_thematic_synthesis.s3_quantum_advantage.combined.triangulate
```

All seven assessors process 1185 experiments; triangulation emits 1185 rows
with 100 % schema validation.

## Deferred items (not blocking freeze)

These were listed in the QA plan but are not required for the frozen output.
They may be addressed in a follow-up iteration:

- **QA-8** — Confidence-weighted consensus (per-framework `confidence` is
  emitted but not yet folded into majority counts).
- **QA-9** — Explicit silo × algorithm_family routing table.
- **QA-11** — Regression fixture set for landmark papers.
- **QA-12** — Manual review of top-50 disagreement cases.
- **QA-13** — LaTeX per-silo consensus tables for the manuscript.
- **QA-14** — Hardware Pareto-frontier plots from Beverland scenarios.
