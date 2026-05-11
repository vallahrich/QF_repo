# HHL Apples-to-Apples Comparison Contract

Generated UTC: `2026-04-28T12:17:41.019872+00:00`

This artifact adds output-contract accounting to the Phase 8d HHL estimates. It
does not change the raw QDK resource estimates. It makes explicit that HHL state
preparation, a scalar observable estimate, and a full classical solution vector
are different computational tasks.

It also preserves the size-contract caveat: HHL `N` is the current template
work-register proxy size, while classical `N` is a matched scaffold matrix
dimension. The shared `N` grid is not a matrix-semantics equivalence claim.

## Scenarios

- `state_preparation_only`: the raw QDK HHL runtime. This is not comparable to a
  classical solver returning a full vector.
- `single_scalar_observable_sampling`: repeats HHL by `1/error^2` for one bounded scalar observable, using error `0.01` under plain measurement sampling; comparable only if the classical task is the same scalar observable. Amplitude-estimation variants are not modeled here.
- `full_vector_readout_lower_bound`: charges at least `N` HHL preparations. This
  is a lower bound for emitting `N` classical coordinates and is still not enough
  for signed-amplitude accuracy.
- `full_vector_tomography_proxy`: charges `N/error^2` preparations with error
  `0.01`. This is a crude full-vector output proxy, not
  a theorem about optimal tomography.

## Interpretation

The measured scipy rows return full classical vectors with residuals. The QDK HHL
rows return fault-tolerant estimates for quantum-state preparation. Therefore,
the full-vector scenarios are the relevant rows when comparing against dense or
sparse classical linear solves. The scalar-observable scenario is only relevant
for a finance task whose requested output is a single expectation value or risk
statistic, not the whole solution vector.

## Remaining Mismatch

Even after these output adjustments, this is still appendix context because the
current HHL circuit is a proxy resource template. A final apples-to-apples finance
claim still needs a finance-specific matrix family, block encoding/data-loading
model, an explicit matrix-dimension-to-work-register mapping, matched `kappa`,
matched sparsity, and a matched tolerance bridge.

Rows generated: `616`
CSV: `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/hhl_apples_to_apples_adjustments.csv`
Projection CSV to N=`1000000`: `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/hhl_apples_to_apples_projection_to_1e6.csv`
JSON: `p4_experiments/canonical/outputs/phase08d_hhl_tail_exploratory/hhl_apples_to_apples_adjustments.json`
