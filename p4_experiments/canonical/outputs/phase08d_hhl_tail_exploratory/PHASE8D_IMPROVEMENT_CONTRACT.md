# Phase 8d Improvement Contract

Generated UTC: `2026-04-28`

Purpose: convert the critical assessment into concrete manuscript and research
guardrails. This file should be read before Phase 8d is cited, promoted, or used
as input to a stronger HHL experiment.

## Decision

Keep Phase 8d as an appendix-level resource-estimation and comparison-contract
study. Do not use it as a headline quantum-advantage result.

The section gives actual research value because it records:

- QDK fault-tolerant resource estimates for fixed-precision HHL proxy circuits.
- Configuration-specific estimator and exact-decomposition failure boundaries.
- Measured dense and sparse SciPy scaffold baselines with residuals.
- Output-contract adjustments that separate state preparation, scalar
  observable estimation, and full-vector output.
- A negative/control result: no observed measured-grid quantum/classical
  crossover under the current proxy/scaffold comparison.

## Allowed And Forbidden Claims

| Topic | Allowed claim | Forbidden claim | Reason |
| --- | --- | --- | --- |
| Phase 8d scope | Phase 8d is appendix-only resource-estimation and comparison-discipline evidence. | Phase 8d is H1-H4 headline evidence. | The experiment is proxy-scoped and not finance-semantic. |
| HHL `N` | HHL `N` is proxy work-register size. | HHL `N` is a finance matrix dimension. | No finance matrix-to-register mapping is implemented. |
| QDK runtime | QDK `runtime_seconds` are fault-tolerant resource-estimator seconds. | QDK seconds are measured hardware wall-clock. | They are model outputs under an error-correction and hardware assumption set. |
| Classical timing | SciPy rows are local measured scaffold baselines with residuals. | SciPy rows solve the same matrix as the proxy HHL unitary. | The classical matrix is a synthetic SPD scaffold. |
| Dense baseline | Dense rows show dense-storage direct-solve context. | Dense rows are the optimal classical solver for the tridiagonal scaffold. | The same scaffold is sparse; dense storage is intentionally contextual. |
| Sparse baseline | Sparse CG shows a strong classical scaffold baseline to `N=1000000`. | Sparse CG proves HHL is impossible or universally worse. | It is one matrix family and one output contract. |
| Output | HHL state preparation, scalar observables, and full-vector output are different tasks. | Raw HHL state preparation is comparable to a classical full-vector solve. | Full-vector classical output requires quantum readout or tomography costs. |
| Precision | QDK `epsilon`, HHL clock precision `m`, and classical residual tolerance must be bridged explicitly. | These quantities can be treated as the same error parameter. | They control different physical or numerical objects. |
| Crossover | No crossover is observed in the common measured grid. | Projected crossing points are measured evidence. | Power-law fits outside support are extrapolations. |
| Finance value | Phase 8d identifies what a fair finance HHL comparison would require. | Phase 8d proves finance quantum advantage. | No finance-semantic linear-system family is yet implemented. |

## Tolerance And Output Bridge

Any claim-ready HHL comparison must specify the requested output first. The
required comparison changes depending on the output.

| Output task | Classical object | Quantum object | Required bridge |
| --- | --- | --- | --- |
| Full solution vector | Vector `x` with residual `||Ax-b||/||b|| <= tau`. | Quantum state proportional to `x`, plus readout/tomography. | Bound state-preparation error, phase-estimation error, Hamiltonian-simulation error, and readout error so the reconstructed vector meets a comparable residual or norm error. |
| Scalar observable | Scalar `f(x)` or `x^T C x` computed from a classical solve or direct method. | Measurement estimate of an observable on the HHL output state. | Bound observable error directly, including state-preparation error and sampling or amplitude-estimation error. |
| Sampling task | Samples from a distribution induced by the solution state. | Quantum samples from the prepared solution state. | Define total variation, Wasserstein, or task-specific error and compare against the best classical sampler. |

For Phase 8d, the safest target is a scalar observable because full-vector HHL
readout destroys the usual HHL advantage story. If a finance example is added,
prefer a risk statistic or pricing functional over recovering every coordinate
of a large vector.

Minimum bridge language for the current appendix:

> The classical tolerance is a residual tolerance on a synthetic SPD solve. The
> HHL precision parameters and QDK error budget are not residual tolerances. We
> therefore report Phase 8d as resource and output-contract evidence only, not
> as a matched-accuracy solver comparison.

## Finance-Semantic Pilot Plan

The next upgrade should add one small, explicit finance-relevant matrix family.
Do not attempt a large claim-ready experiment first. Use a pilot that establishes
semantics and contracts.

Recommended pilot: one-dimensional PDE pricing operator.

- Matrix: finite-difference discretization of a one-dimensional elliptic or
  parabolic pricing operator after time-step reduction to an SPD or Hermitian
  embedded linear system.
- Dimension: classical matrix dimension `d`; quantum work-register mapping
  should be stated explicitly, for example `n_b = ceil(log2(d))` if a true
  amplitude-encoded state-register model is used, or another documented mapping
  if the template remains proxy-based.
- Sparsity: tridiagonal or banded, recorded as `s`.
- Conditioning: estimate or bound `kappa(A)` for the chosen discretization and
  grid spacing.
- Normalization: record the scaling used to make the operator admissible for a
  block encoding or Hamiltonian simulation model.
- Right-hand side: define a payoff, boundary condition, or forcing vector.
- Output: prefer a scalar price/risk statistic, not the whole solution vector.
- Classical baselines: dense direct, sparse CG/MINRES, and at least one
  preconditioned iterative method.
- Quantum accounting: include state preparation, block-encoding/data-loading,
  phase estimation, Hamiltonian simulation, and measurement/readout contract.

Alternative pilots, in increasing difficulty:

1. Shrunk covariance linear system for portfolio weights.
2. Ridge regression or least-squares normal equations.
3. Multi-asset PDE or basket option operator.

The PDE pilot is preferred because it keeps sparsity and finance meaning visible
without requiring a large data-loading story immediately.

## Preconditioning Guidance

A reviewer will ask whether the classical baseline is unfairly weak without
preconditioning. The current tridiagonal shifted Laplacian is already favorable
to sparse CG and has stable iteration counts, but the manuscript should still
address preconditioning.

Recommended language for current Phase 8d:

> We do not treat the unpreconditioned sparse CG scaffold as the final best
> classical competitor for a finance-semantic HHL study. It is a transparent
> measured reference on the current synthetic SPD scaffold. A claim-ready study
> must include preconditioned classical baselines matched to the finance matrix
> family.

For the next pilot, add at least one of:

- Jacobi scaling, mainly as a sanity baseline.
- Incomplete Cholesky or incomplete LU, if stable for the chosen matrix family.
- Problem-specific preconditioning, such as multigrid or circulant/spectral
  preconditioning for PDE-like systems.

Do not add a weak preconditioner just to check a box. If the preconditioner does
not change the iteration count, report that explicitly.

## Sensitivity Slice

The current Phase 8d uses a fixed QDK error budget. A small sensitivity slice
would improve reviewer confidence without turning this into a new main result.

Recommended slice:

- Hold one representative HHL configuration fixed, preferably `hhl_s1_fixed_m`,
  `m=4`, and a successful mid-to-high proxy `N` such as `N=1000` or `N=2000`.
- Re-estimate at `epsilon in {1e-3, 1e-4, 1e-5}` if estimator runtime permits.
- Optionally repeat across two hardware profiles, for example the current
  `maj_e6_floquet` and one gate-based profile.
- Plot physical qubits, runtime seconds, T states, and logical qubits versus
  `epsilon`.
- Label the result as resource-estimator sensitivity, not solution-accuracy
  equivalence.

This should be a small robustness check, not a new claim stack.

## Manuscript Placement

Recommended section title:

> Appendix: Fixed-Precision HHL Proxy Resource Estimation And Comparison
> Contracts

Recommended first paragraph:

> Phase 8d is included as a resource-estimation and comparison-contract study,
> not as evidence of quantum advantage. HHL `N` denotes the proxy work-register
> size in the current template, while classical `N` denotes the dimension of a
> synthetic SPD scaffold matrix. QDK runtimes are fault-tolerant resource
> estimates under a specified hardware model; SciPy timings are local measured
> wall-clock baselines with residuals. The role of Phase 8d is to report resource
> growth, estimator boundaries, and the output-contract costs that must be
> included before any finance HHL comparison can be fair.

Recommended conclusion sentence:

> The value of Phase 8d is therefore methodological: it identifies the evidence
> boundary and prevents an overclaim, while setting up the requirements for a
> future finance-semantic HHL experiment.

## Implementation Priority

1. Keep the PhD-safe figures and archive superseded plots.
2. Use the allowed/forbidden claims table in the appendix.
3. Add the tolerance/output bridge paragraph to captions or text.
4. Add preconditioning discussion now; add measured preconditioning only when a
   finance-semantic matrix family exists.
5. Build the small finance pilot next.
6. Add the QDK sensitivity slice after the pilot or as a small robustness
   appendix if time allows.

## Stop Criteria

Do not spend more Phase 8d effort on larger proxy HHL tail runs unless the goal
is explicitly estimator-boundary mapping. The current scholarly bottleneck is
not another larger proxy `N`; it is semantic alignment: matrix, output,
tolerance, data loading, and classical preconditioning.