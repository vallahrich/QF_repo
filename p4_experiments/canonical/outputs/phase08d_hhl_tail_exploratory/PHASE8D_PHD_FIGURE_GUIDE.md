# Phase 8d PhD Figure Guide

Generated UTC: `2026-04-28T12:39:52.064160+00:00`

This guide separates manuscript-safe appendix figures from exploratory working
plots. The figures below do not turn Phase 8d into headline H1-H4 evidence; they
are appendix material for resource-estimation and comparison-contract discussion.

## Recommended Figure Pack

| Figure | Recommended use | Main claim it can support |
| --- | --- | --- |
| `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/p4_phase8d_hhl_resource_boundary_phd.png` | Main Phase 8d appendix figure | QDK HHL proxy resource estimates and estimator/failure boundary, without classical timing overlay. |
| `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/p4_phase8d_classical_baseline_diagnostics_phd.png` | Classical-baseline appendix diagnostic | The SciPy scaffold baselines are measured full-vector classical solves with residual, iteration, and memory diagnostics. |
| `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/p4_phase8d_apples_to_apples_phd.png` | Fair-comparison appendix figure | HHL state preparation, scalar-observable sampling, and full-vector readout are different output contracts. |
| `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/p4_phase8d_projection_boundary_phd.png` | Projection-boundary appendix figure | There are zero observed crossovers in the common measured grid; extrapolated regions are visibly separated. |

## Context-Only Or Exploratory Figures

The superseded figures below have been moved to
`archive_superseded_20260428/` for auditability. They should not be cited from
the top-level Phase 8d output directory.

| Figure | Status | Reason |
| --- | --- | --- |
| `archive_superseded_20260428/p4_hhl_classical_context.png` | Context only | Useful overview, but it combines resource estimates and classical model curves in one artifact. |
| `archive_superseded_20260428/p4_hhl_classical_scaling_index.png` | Context only | Normalized scaling is intuitive but not an absolute evidence figure. |
| `archive_superseded_20260428/p4_hhl_classical_measured_time.png` | Context only | It overlays QDK estimator seconds and local SciPy wall-clock seconds. |
| `archive_superseded_20260428/p4_hhl_classical_crossover_projection.png` | Superseded by `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/p4_phase8d_projection_boundary_phd.png` | The new projection-boundary figure labels measured and extrapolated regions more explicitly. |
| `archive_superseded_20260428/p4_hhl_apples_to_apples_adjusted_time.png` | Superseded by `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/p4_phase8d_apples_to_apples_phd.png` | The new figure omits the tomography proxy from the main legend for legibility. |
| `archive_superseded_20260428/p4_hoefler_crossover_working_hhl_tail.png` | Exploratory only | It is a Hoefler-style sketch and should not be cited as Phase 8d evidence of speedup or advantage. |

## Review Artifact

`p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/PHASE8D_CRITICAL_ASSESSMENT.md` records the professor-style critical assessment of what
Phase 8d can and cannot claim.

## Improvement Contract

`p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/PHASE8D_IMPROVEMENT_CONTRACT.md` records the allowed/forbidden claim table,
tolerance bridge, finance-semantic pilot plan, and preconditioning guidance for
the next claim-ready upgrade.

## Caption Rules

- Say `HHL proxy work-register size N`, not finance matrix dimension.
- Say QDK values are fault-tolerant resource-estimator seconds, not measured
  hardware wall-clock.
- Say classical rows are synthetic SPD scaffold baselines with full-vector output.
- State that no measured quantum/classical crossover is observed.
- Treat all fitted curves beyond the marked support region as extrapolations.
