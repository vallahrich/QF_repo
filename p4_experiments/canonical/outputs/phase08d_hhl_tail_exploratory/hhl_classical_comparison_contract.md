# HHL Classical-Comparison Contract

Generated UTC: `2026-04-28T12:17:34.752719+00:00`

## Status

This is an appendix-only Phase 8d comparison contract. It supports discussion of
fixed-precision HHL resource scaling, but it must not be pooled into H1-H4 and
must not be used as a standalone quantum-advantage claim.

## Quantum Object Being Compared

- Source data: `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/figure_phase8d_scaling_with_tail_exploratory.csv`
- Quantum family: HHL fixed-precision proxy circuits only
- Hardware profile: `maj_e6_floquet`
- QDK resource-estimator error budget: `0.0001`
- Successful HHL rows used for quantum-resource context: `39`
- Successful exploratory tail rows: `6`
- Failed/OOM or engine-failure HHL rows retained as boundary evidence: `10`
- Largest successful proxy `N` in these rows: `10000`

In this contract, HHL `N` is the current template work-register proxy size
(`n_b`). It must not be read as the dimension of a finance linear system. The
classical rows use a matched numeric scaffold dimension only to provide scaling
context.

Failure boundaries are configuration-specific, not a single monotone threshold:

- `hhl_s1_fixed_m` m=`4`: max successful proxy N=`10000`, max successful exploratory-tail proxy N=`10000`, minimum failed proxy N=`20000`, minimum failed exploratory-tail proxy N=`20000`.
- `hhl_s1_fixed_m` m=`6`: max successful proxy N=`2000`, max successful exploratory-tail proxy N=`2000`, minimum failed proxy N=`5000`, minimum failed exploratory-tail proxy N=`5000`.
- `hhl_s1_fixed_m` m=`8`: max successful proxy N=`500`, no successful exploratory-tail row for this configuration, minimum failed proxy N=`1000`, no failed exploratory-tail row for this configuration.
- `hhl_s2_fixed_m` m=`4`: max successful proxy N=`5000`, max successful exploratory-tail proxy N=`5000`, minimum failed proxy N=`10000`, minimum failed exploratory-tail proxy N=`10000`.
- `hhl_s2_fixed_m` m=`6`: max successful proxy N=`1000`, no successful exploratory-tail row for this configuration, minimum failed proxy N=`2000`, minimum failed exploratory-tail proxy N=`2000`.
- `hhl_s2_fixed_m` m=`8`: max successful proxy N=`250`, no successful exploratory-tail row for this configuration, minimum failed proxy N=`500`, no failed exploratory-tail row for this configuration.

The HHL template emits a quantum state proportional to the solution vector. It
does not by itself emit the full classical vector. A full-vector comparison is
therefore only fair if the quantum-side readout or tomography cost is included.

## Precision Rules

Do not equate these quantities without an explicit derivation:

1. QDK `epsilon`: a fault-tolerant resource-estimator error budget split across
   logical, T-state, and rotation-synthesis failures.
2. HHL `m_precision_qubits`: a phase-estimation clock precision parameter.
3. Classical solver tolerance: usually reported as a residual such as
   `||Ax - b|| / ||b||`.

For any reviewer-facing speedup claim, the classical residual tolerance and the
HHL phase-estimation/output error must be matched at the level of the requested
observable or solution vector. This artifact does not make that match; it only
records the required contract.

## Classical Context Included Here

The CSV `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/hhl_classical_context.csv` contains `100`
classical model rows:

- Dense direct solve: work proxy `(2/3) N^3`, memory proxy `8 N^2` bytes.
- Sparse iterative solve: tridiagonal SPD proxy with CG/MINRES-style work
  `nnz * ceil(sqrt(kappa) * log(2/tol))`, using `kappa in [10, 100, 1000]`
  and `tol in [0.01, 0.0001, 1e-06]`.

These are context curves, not measured competitors. They are intentionally kept
separate from the QDK runtime axis in the figure.

## Measured Classical Timing Addendum

If present, `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/hhl_classical_measured_baselines.json` records a
time-bound local scipy baseline scaffold: shifted 1D-Laplacian SPD systems,
fixed-seed normalized Gaussian right-hand sides, dense Cholesky-family solves
through the configured dense grid, and sparse CG solves through the configured sparse grid. Those rows are
useful because they provide seconds, residuals, iteration counts, memory proxies,
thread settings, and hardware metadata. They remain appendix context because the
synthetic SPD matrix is a matched-size classical scaffold, not a demonstrated
semantic match to the current proxy HHL unitary.

## Apples-to-Apples Output Addendum

If present, `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/hhl_apples_to_apples_contract.md` records
the output-contract adjustment layer. It separates raw HHL state preparation,
single scalar-observable sampling, full-vector readout lower bounds, and a
tomography-style full-vector proxy. This is the artifact to cite when explaining
why HHL state preparation alone should not be compared against a classical solver
that returns the full vector.

## Allowed Statements

- The Phase 8d HHL scout provides QDK resource estimates for fixed-precision
  proxy circuits under a pinned hardware profile and error budget.
- The exploratory VM tail shows successful estimates through selected rows up
    to proxy `N=10000`, while exact decomposition becomes memory-bound for larger
    or more precise cells on the tested 84 GB VM class.
- Classical dense and sparse curves provide scaling context under explicitly
  stated matrix, tolerance, and output assumptions.
- The measured scipy addendum gives a time-bound local classical reference on a shared proxy/scaffold size grid with residual reporting, but does not by itself establish a quantum/classical advantage conclusion.

## Statements To Avoid

- Do not say the QDK `runtime_seconds` is a direct measured speedup over CPU or
  GPU wall-clock.
- Do not compare HHL state preparation to a classical full-vector solve unless
  quantum readout cost is included.
- Do not claim finance-specific HHL advantage from the current proxy `U`; the
  current template records resource scaling, not a calibrated finance matrix.
- Do not collapse QDK `epsilon`, HHL clock precision, and classical residual
  tolerance into one interchangeable precision parameter.

## Missing Before A Full PhD-Level HHL Comparison

1. A finance-relevant matrix family with documented sparsity, condition number,
   Hermitian embedding or block encoding, data-loading assumptions, and an
   explicit matrix-dimension-to-work-register mapping.
2. A matched observable-output task, or a full-vector task with quantum readout
   cost included.
3. A tolerance bridge from HHL phase-estimation error and QDK error budget to a
   classical residual tolerance.
4. Measured classical dense/sparse baselines on the matched task, with residuals,
   iteration counts, memory footprint where feasible, and fixed threading.
5. A small QDK sensitivity slice over `epsilon` and `m` that is explicitly
   reported as resource sensitivity rather than solution-accuracy equivalence.
