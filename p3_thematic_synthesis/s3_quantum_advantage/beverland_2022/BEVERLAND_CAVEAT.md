# Beverland 2022 Implementation — Fidelity Caveat

**Date:** 2026-04-20
**Status:** Documented limitation; future revision planned.

## What this layer actually does

`assess_beverland.py` applies **Babbush 2021 Equation (5)** — a polynomial
crossover formula — across the **six hardware-scenario *names*** introduced by
Beverland et al. (2022). For each experiment × scenario cell:

1. Look up `toffoli_time_us` from the scenario.
2. Compute `M_min = (tQ·S/tC)^(1/(d-1))` and `T* = tQ·M_min` (Babbush Eq. 5).
3. Compare against budget; emit per-scenario verdict.
4. Aggregate the 6 verdicts via the configured policy (default: median /
   `balanced`).

## What Beverland 2022 *actually* introduces

The Beverland paper introduces a **modular, layered resource estimation
methodology** that became the Azure Quantum Resource Estimator. Faithful
application requires per-experiment inputs:

| Input | Purpose |
|---|---|
| Logical qubit count Q | Algorithm-specific |
| Logical time steps C_min | Algorithm-specific |
| T-count M | Algorithm-specific |
| T-depth | Algorithm-specific |
| Required logical error rate P_max | Application-specific |
| Required T-state error rate P_T,max | Application-specific |

…then *computes*:

- Surface-code distance `d` such that `P(d) ≤ P_max` (formula:
  `P(d) = 0.03·(p/0.01)^((d+1)/2)`)
- Logical time step `τ_sur(d) = (4·t_gate + 2·t_meas)·d`
- Physical qubits = `Q·n(d) + F·n_factory(d)` where `n_sur(d) = 2d²`
- T-factory configuration to achieve `P_T,max`
- End-to-end runtime including T-factory scheduling

**None of the above is implemented in `assess_beverland.py`.**

## Why we kept the Babbush-proxy approach for the 2026-04-17 freeze

1. The corpus extractions don't reliably contain Q, C_min, M, T-depth for
   every experiment; switching to a true Beverland implementation would
   reduce coverage from 1185 to a much smaller subset.
2. The Babbush proxy (`d × 5.5 × t_gate`) produces Toffoli times within ~10%
   of the Beverland surface-code formula in the regimes considered, so the
   verdicts are not arithmetically wrong — only conceptually mislabelled.
3. Aggregation policy was correctly changed to `balanced` (median) per the
   freeze, addressing the worst overclaim risk (best-case selection).

## What we honestly tell a PhD committee

> "The L3 layer is a **screening proxy**: it applies Babbush 2021's polynomial
> crossover formula at six hardware-scenario points named after Beverland 2022.
> It is not a full-stack resource estimator; we did not perform code-distance
> selection, T-factory modelling, or physical-qubit/runtime estimation. A
> subsequent revision will integrate the Azure Quantum Resource Estimator
> (`qsharp.estimator`) once all assessable experiments report Q, C_min, M, and
> T-depth in their structured extractions."

This caveat is now also surfaced in every Beverland verdict via
`assumptions.fidelity_caveat` in the result JSON.

## Future work (out of scope for this freeze)

1. Enrich extraction schema to require Q, C_min, M, T-depth for all FT-claim
   experiments.
2. Replace `_compute_crossover` with a call to the Azure QRE Python API.
3. Re-run Beverland layer on the subset of experiments with complete inputs;
   keep Babbush proxy as fallback for the rest, with explicit annotation.
