# Phase 8d Academic Guardrails

Phase 8d is an appendix-only fixed-precision QAE/HHL proxy resource-estimation
stress test. It is useful as resource-scaling evidence, failure-boundary
evidence, and fair-comparison discipline. It is not headline H1-H4 evidence and
not a finance-semantic HHL advantage result.

## Required Framing

- Describe Phase 8d as `qae_hhl_fixed_precision_high_n` or as a fixed-precision
  QAE/HHL proxy resource-estimation stress test.
- State that it is appendix-only and excluded from H1-H4 pooling.
- State that QDK `runtime_seconds` are fault-tolerant resource-estimator values,
  not measured quantum hardware wall-clock.
- State that HHL `N` / `n_b` is the proxy work-register size in the current
  template, not a validated finance linear-system matrix dimension.
- State that the measured SciPy rows are classical scaffold timings on matched
  numeric sizes, not the same matrix solved by the proxy HHL unitary.
- State that raw HHL state preparation is not comparable to a classical solver
  returning a full solution vector unless readout or tomography cost is charged.

## Allowed Claims

- Phase 8d provides QDK resource estimates for fixed-precision QAE/HHL proxy
  circuits under pinned hardware profiles and error budgets.
- The canonical Phase 8d grid completed its expected records and records both
  successful estimates and engine failures.
- The exploratory HHL tail produced selected successful estimates up to proxy
  work-register size `N=10000` while larger or more precise cells became
  memory-bound in exact decomposition on the tested VM class.
- No measured-grid quantum/classical crossover is observed in the current
  measured SciPy comparison scaffold.
- The apples-to-apples layer identifies output-contract costs that must be
  included before comparing HHL with classical full-vector solvers.

## Forbidden Claims

- Do not claim Phase 8d proves quantum advantage.
- Do not claim the current HHL proxy solves a calibrated finance matrix.
- Do not call HHL `N` a finance linear-system dimension without adding a matrix
  construction and qubit-to-dimension mapping.
- Do not compare QDK resource-estimator seconds directly against CPU/GPU
  wall-clock as a speedup denominator.
- Do not equate QDK `epsilon`, HHL clock precision `m`, and classical residual
  tolerance.
- Do not cite projected crossover points as measured evidence.

## Minimum Checklist Before Manuscript Use

- `phase8d_status.json` reports appendix-only, no missing cells, and no
  nonfinal records.
- `audit_phase8d.json` passes schema, fixed-precision coupling, completeness,
  and exclusion checks.
- Manuscript text says `proxy N`, `work-register size`, or `scaffold dimension`
  where appropriate.
- Figures mark the last successful HHL estimate before extrapolation.
- Captions distinguish QDK model estimates from measured local classical times.
- Tables do not pool Phase 8d records into H1-H4 results.
- Any HHL/classical comparison cites the output-contract layer.

## Upgrade Path To A Claim-Ready HHL Study

- Define a finance-relevant matrix family, such as a discretized PDE operator,
  covariance/portfolio system, or regression/least-squares system.
- Record matrix dimension, sparsity, condition number, normalization, and data
  loading or block-encoding assumptions.
- Define the requested output: scalar observable or full solution vector.
- Bridge HHL clock precision, Hamiltonian-simulation or block-encoding error,
  and QDK error budget to a classical residual tolerance.
- Run matched dense, sparse, and preconditioned classical baselines with
  residuals, iterations, memory footprint, and fixed threading.
- Only then evaluate whether any quantum advantage statement is supportable.