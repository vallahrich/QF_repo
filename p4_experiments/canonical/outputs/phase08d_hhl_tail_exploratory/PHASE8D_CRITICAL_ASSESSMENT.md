# Phase 8d Critical Academic Assessment

Generated UTC: `2026-04-28`

Reviewer stance: quantum-computing and quantum-finance methods review. The goal
is not to defend Phase 8d as a quantum-advantage result. The goal is to decide
whether it is academically correct, whether it has research value, which pieces
should be kept, and how it should be framed in a dissertation or paper.

## Executive Verdict

Phase 8d is academically useful and now contains actual numerical values, but it
is not a complete finance-semantic HHL experiment. It is strongest as an
appendix-level resource-estimation and comparison-discipline study. It should be
kept if framed as evidence about fault-tolerant HHL proxy resource growth,
estimator/failure boundaries, output-contract mismatch, and classical baseline
context. It should not be used as headline evidence for quantum advantage,
finance-specific acceleration, or an end-to-end HHL solver result.

The current safe claim is:

> Phase 8d shows that fixed-precision HHL proxy circuits can be resource
> estimated over a controlled QDK grid, that exact decomposition becomes
> memory-bound for larger or more precise proxy instances on the tested VM
> class, and that measured classical full-vector scaffold baselines remain far
> faster in the common measured grid. The study clarifies what would be required
> before a fair HHL/classical finance comparison could be claimed.

The unsafe claim is:

> Phase 8d demonstrates quantum advantage for HHL in finance.

That unsafe claim is not supported.

## Evidence Inventory

Current primary outputs:

- `p4_phase8d_hhl_resource_boundary_phd.png`: recommended HHL resource and
  estimator-boundary figure.
- `p4_phase8d_classical_baseline_diagnostics_phd.png`: recommended measured
  classical scaffold diagnostics.
- `p4_phase8d_apples_to_apples_phd.png`: recommended output-contract comparison
  figure.
- `p4_phase8d_projection_boundary_phd.png`: recommended projection-boundary
  figure.
- `hhl_classical_measured_baselines.csv`: measured SciPy dense/sparse baselines.
- `hhl_classical_comparison_contract.md`: comparison contract and caveats.
- `hhl_apples_to_apples_contract.md`: output-contract contract.
- `PHASE8D_PHD_FIGURE_GUIDE.md`: figure-use guide.

Numerical basis at this review point:

- HHL QDK rows: `49` selected HHL rows under `maj_e6_floquet`.
- HHL statuses: `39` successful estimates and `10` engine failures.
- HHL maximum successful proxy size by configuration:
  - `hhl_s1_fixed_m`, `m=4`: success to `N=10000`, first failure at `N=20000`.
  - `hhl_s1_fixed_m`, `m=6`: success to `N=2000`, first failure at `N=5000`.
  - `hhl_s1_fixed_m`, `m=8`: success to `N=500`, first failure at `N=1000`.
  - `hhl_s2_fixed_m`, `m=4`: success to `N=5000`, first failure at `N=10000`.
  - `hhl_s2_fixed_m`, `m=6`: success to `N=1000`, first failure at `N=2000`.
  - `hhl_s2_fixed_m`, `m=8`: success to `N=250`, first failure at `N=500`.
- Classical measured rows: `48`.
- Dense direct SciPy scaffold: measured to `N=5000` for `kappa=100` and
  `kappa=1000`.
- Sparse CG scaffold: measured to `N=1000000` for `kappa=100` and `kappa=1000`.
- Observed measured-grid quantum/classical crossovers: `0`.
- Apples-to-apples rows: `616`, with four scenarios per joined case.

Representative classical endpoint values:

- Dense direct, `N=5000`, `kappa=100`: median `2.002 s`, residual about
  `1.11e-15`, memory proxy about `200 MB`.
- Dense direct, `N=5000`, `kappa=1000`: median `1.877 s`, residual about
  `7.75e-15`, memory proxy about `200 MB`.
- Sparse CG, `N=1000000`, `kappa=100`: median about `0.861 s`, residual about
  `9.28e-05`, `48` iterations, memory proxy about `56 MB`.
- Sparse CG, `N=1000000`, `kappa=1000`: median about `2.642 s`, residual about
  `9.43e-05`, `152` iterations, memory proxy about `56 MB`.

## Academic Correctness Assessment

### 1. QDK Resource Estimates

The QDK HHL data are meaningful resource-estimator values under a pinned
fault-tolerant hardware model. They are not measured hardware runtimes. This is
academically acceptable if the manuscript says exactly that.

Strengths:

- Fixed hardware profile and error budget are recorded.
- Successful and failed cells are both retained.
- Failure boundaries are configuration-specific and not collapsed into a false
  monotone threshold.
- The resource-boundary figure avoids overlaying classical CPU timings on the
  same axis.

Limitations:

- QDK runtime seconds are model outputs and depend on assumptions about error
  correction, synthesis, and hardware parameters.
- The estimator failure boundary is partly a tooling/exact-decomposition memory
  boundary, not a theorem about HHL complexity.
- The HHL template is a proxy circuit, not a finance matrix solver.

Verdict: correct and valuable as resource-estimation evidence; not sufficient
for an algorithmic speedup claim.

### 2. HHL Problem Semantics

This is the central limitation. The current `N` is a work-register proxy size,
not a validated finance linear-system dimension. The HHL unitary is not yet tied
to a covariance system, PDE discretization, portfolio optimization system,
regression normal equation, or calibrated block encoding.

This does not make Phase 8d useless. It makes the contribution methodological:
it studies resource scaling and comparison discipline before claiming a finance
application. That is a legitimate PhD appendix contribution if stated clearly.

Verdict: academically acceptable only with proxy wording. It would be incorrect
to call it a finance HHL experiment.

### 3. Classical Baselines

The classical baselines now have actual measured values and are substantially
stronger than before. Dense direct solves are measured to `N=5000`; sparse CG is
measured to `N=1000000`; residuals, iterations, memory proxies, repeats, and
thread settings are recorded.

Strengths:

- Baselines return full classical solution vectors.
- Residuals are reported, not just timings.
- Sparse CG high-N tail demonstrates how strong a simple classical solver can be
  on the chosen tridiagonal SPD scaffold.
- Dense and sparse memory behavior are visible.

Limitations:

- The matrix family is synthetic shifted 1D Laplacian SPD, not a finance matrix.
- Sparse CG benefits strongly from tridiagonal structure.
- Classical rows are local SciPy wall-clock; QDK rows are fault-tolerant model
  estimates. These are not directly commensurate speedup denominators.
- The dense implementation stores a tridiagonal problem densely, so it is useful
  as dense-context evidence but not as the best classical solver for that matrix.

Verdict: valuable as a classical scaffold and sanity check. It should be framed
as a conservative classical-context diagnostic, not as the final matched
classical denominator for a finance HHL claim.

### 4. Output-Contract Layer

This is one of the most academically important additions. Raw HHL state
preparation is not the same task as returning a full classical vector. The
contract correctly separates state preparation, one scalar observable, full
vector readout lower bound, and tomography-style proxy.

Strengths:

- Prevents an invalid comparison between quantum state output and classical
  full-vector output.
- Makes the scalar-observable case explicit, which is often the only setting in
  which HHL-style algorithms are plausibly useful.
- Shows that output requirements can dominate the comparison.

Limitations:

- The scalar-observable scenario uses plain sampling, not a fully optimized
  amplitude-estimation workflow.
- The tomography proxy is deliberately crude and should remain in CSV/contract,
  not as the primary figure curve.
- It still does not bridge HHL phase-estimation error to classical residual.

Verdict: keep. It is methodologically strong and prevents reviewer objections.

### 5. Projection And Crossover Analysis

The projection boundary is useful only because it is now visually marked as
projection. The strongest result here is negative: there are zero observed
crossovers in the common measured grid. Projected crossings are not evidence.

Strengths:

- Extrapolated HHL regions are visually separated.
- Classical sparse CG is measured out to `N=1000000`, which greatly reduces the
  temptation to overread a fitted classical curve.
- The figure states no observed measured-grid crossover.

Limitations:

- Power-law fits over proxy HHL points should not be interpreted mechanistically.
- The common x-axis is a presentation device, not proof of matching problem
  dimension.
- The y-axis mixes QDK model seconds and measured local classical seconds in the
  projection-boundary figure, even though the labels and caveats make that clear.

Verdict: keep as a projection-boundary figure, not as a crossover evidence
figure. The caption must explicitly say there is no measured advantage.

## What To Keep

Keep these as primary Phase 8d appendix artifacts:

- `p4_phase8d_hhl_resource_boundary_phd.png`
- `p4_phase8d_classical_baseline_diagnostics_phd.png`
- `p4_phase8d_apples_to_apples_phd.png`
- `p4_phase8d_projection_boundary_phd.png`
- `hhl_classical_measured_baselines.csv/json`
- `hhl_classical_comparison_contract.md`
- `hhl_apples_to_apples_contract.md`
- `PHASE8D_PHD_FIGURE_GUIDE.md`
- `phase8d_phd_figure_pack.json`

Also keep raw `results/`, `logs/`, and `summary.json` for auditability.

## What To Archive Or Avoid Citing

The archived superseded figures should remain in `archive_superseded_20260428/`
for audit trace only:

- `p4_hoefler_crossover_working_hhl_tail.png`: do not cite. It is too visually
  suggestive of a speedup story.
- `p4_hhl_classical_measured_time.png`: avoid citing because it overlays QDK
  estimator seconds and local SciPy wall-clock seconds.
- `p4_hhl_classical_crossover_projection.png`: superseded by the PhD projection
  boundary figure.
- `p4_hhl_apples_to_apples_adjusted_time.png`: superseded by the cleaner PhD
  apples-to-apples figure.
- `hhl_apples_to_apples_projection_to_1e5.csv`: superseded by the `1e6` file.

Do not delete archived evidence unless repository size becomes a real problem.
Archiving is better than deletion for reproducibility.

## Recommended Manuscript Framing

Use Phase 8d in an appendix or robustness section, not in the main empirical
claim stack. A suitable section title would be:

> Appendix: Fixed-Precision HHL Proxy Resource Estimation And Comparison
> Contracts

Recommended framing paragraph:

> We include Phase 8d as a resource-estimation and comparison-discipline study,
> not as evidence of quantum advantage. The HHL circuits use a fixed-precision
> proxy template whose work-register size `N` is not a finance matrix dimension.
> QDK runtimes are fault-tolerant resource-estimator outputs under a specified
> hardware model, whereas SciPy baselines are measured local wall-clock timings
> on synthetic SPD scaffold systems. The experiment is therefore used to report
> resource growth, estimator/failure boundaries, and the output-contract costs
> that must be accounted for before any HHL/classical finance comparison is fair.

Recommended caption language:

> Phase 8d HHL proxy resource-estimation results. `N` denotes proxy work-register
> size for HHL and scaffold matrix dimension for the classical synthetic SPD
> baselines; it is not a finance matrix-dimension equivalence claim. QDK values
> are fault-tolerant resource-estimator seconds. Classical values are local SciPy
> timings with residuals reported. Dashed quantum curves beyond the last
> successful estimate are extrapolations. No measured-grid quantum/classical
> crossover is observed.

## Research Value

Phase 8d has actual research value in four ways:

1. It documents a negative/control result: naive proxy HHL resource estimates do
   not produce a measured advantage story against simple classical baselines.
2. It provides empirical estimator-boundary evidence: exact decomposition fails
   earlier as precision and Hamiltonian-simulation steps increase.
3. It teaches fair-comparison discipline: output contract, precision contract,
   matrix semantics, and data loading must be specified before HHL claims are
   meaningful.
4. It supports the dissertation's methodological credibility by showing that the
   study did not cherry-pick optimistic quantum plots and ignore classical
   baselines.

That is real value. It is not the value of proving quantum advantage; it is the
value of preventing an incorrect quantum-advantage claim.

## Remaining Threats To Validity

- No finance-semantic matrix family is implemented.
- No block-encoding or data-loading model is costed.
- No matched bridge exists between HHL phase-estimation error, QDK error budget,
  and classical residual tolerance.
- No preconditioned classical baselines are included.
- The current classical matrix is especially favorable to sparse CG because it
  is tridiagonal SPD.
- The HHL proxy circuit may not represent the oracle structure or sparsity model
  of a realistic quantum linear-system algorithm.
- The QDK exact-decomposition failures are partly tool/memory boundary evidence,
  not lower bounds on algorithmic impossibility.

## Highest-Value Improvements

1. Add a small finance-semantic pilot matrix family: for example, a covariance
   shrinkage system, a tridiagonal PDE pricing operator, or a regression normal
   equation. Keep it small but explicit.
2. Define the requested output: scalar risk statistic, expectation value, or full
   vector. HHL is more plausible for scalar observables than full-vector output.
3. Add a tolerance bridge: explain how `m`, Hamiltonian-simulation error, and
   QDK `epsilon` relate to a classical residual or observable error.
4. Add one preconditioned classical baseline, even if only as discussion. A
   reviewer will ask why CG was not preconditioned.
5. Add a short sensitivity slice over QDK `epsilon` or hardware profile, clearly
   labeled as resource sensitivity rather than solution accuracy.
6. Add a table summarizing all allowed and forbidden claims. This can be copied
   directly into the appendix.

## Final Assessment

Phase 8d is academically correct if and only if it remains appendix-scoped and
proxy-scoped. The current figures and contracts are strong enough for a PhD
appendix because they report actual values, retain failures, include classical
baselines, and explicitly block the common HHL comparison mistakes. The section
would become academically incorrect only if it were promoted into a claim that
HHL solved a finance system faster than classical methods.

Recommendation: keep Phase 8d, cite only the PhD-safe figure pack, retain the
archived exploratory figures for auditability, and frame the contribution as a
negative/control and methodology-strengthening result.