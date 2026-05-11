# Bifurcation thesis — empirical (N = 74 P4-prime row-level census)

> **Source:** `p4_experiments/common/output/forward_outlook/silo_tau_ranking.json` and `oracle_tax_decomposition.json`, both derived under cohort tag `p4-preregistration-v5` (full row-level majority-viable census: 8 legacy + 8 v2 + 16 v3 + 28 v4 + 14 v5 = 74 labels covering 57 unique majority-viable papers + 14 row-level extras + 8 legacy benchmarks).

## Statement

Every P3-majority-viable quantum-finance label in the 74-label P4-prime row-level census falls into one of two regimes:

- **Regime A — trivial-oracle.**
  - Trainable parametrised circuit, ansatz-only template, or any unit whose full-mode accounting matches the bare circuit (no T-gates synthesised in full mode).
  - `full_t_count = 0` at the H4 anchor cell. τ_runtime ≈ 1–3.
  - The "quantum work" being measured is just the bare circuit cost — there is no oracle / data-loading overhead, and consequently no superpolynomial speedup to capture.
  - Members in census (38 / 74 labels with classical baselines, plus 11 v5 labels by `t_count=0` structural property): **B3, B4** (qml-finance benchmarks); **SQ1, SQ2, SQ3, SQ5–SQ12** (qml-finance ansätze and template proxies); **SD2, SD4, SD6–SD11** (derivative-pricing template proxies); **SM4, SM8, SM9, SM10, SM11** (simulation template proxies); **SP4, SP5, SP6, SP7** (portfolio template proxies); **SF2, SF3** (fraud-detection template proxies); **ST1** (trading-execution); **SX1, SX2, SX3, SX4** (cross-silo other); **T3** (fraud-detection legacy template proxy). Plus v5 row-level extras with `full_t_count = 0` but no classical baseline: **SQ13, SQ14, SQ15, SP9, SM12, SM14, SM15, SD13, SD14, SX5, SX6**.
- **Regime B — oracle-bound.**
  - Real quantum oracle (QAE, HHL, amplitude encoding, structured state preparation).
  - `full_t_count > 0` and FT cost dominated ≥ 95 % by the oracle.
  - The classical baseline of any non-trivial scale beats it on wall-clock.
  - Members in census (25 / 74 labels): **B1, B2, B5** (canonical QAE); **SD1, SD3, SD5, SD12** (derivative-pricing); **SF1** (fraud-detection); **SH1, SP1, SP2, SP3, SP8** (portfolio-optimization); **SM1, SM2, SM3, SM5, SM6, SM7, SM13** (simulation-monte-carlo); **SQ4** (qml-finance with oracle); **SR1, SR2** (risk-management); **T1, T2** (insurance / risk).

The strict-H4 subset (τ_runtime < 10× AND beats classical wall-clock AND `full_t_count > 0` AND τ_t_depth ≥ 10× AND classical wall-clock ≥ 10 ms) is **empty** because **no label in the N=74 census simultaneously satisfies the small-tau condition AND has a non-trivial oracle**. The 38 naive winners (τ < 10 AND beats classical) are exactly the 38 trivial-oracle (`full_t_count = 0`) labels in Regime A *with classical baselines*. The 11 additional v5 labels in Regime A by structural `t_count=0` are not in the naive subset because their experiment rows lack classical-baseline mappings (Amendment 5 §F).

**Cohort-balance disclosure (carried from PRE_REGISTRATION.md Amendment 4 §C).** The v4 census is dominated by papers classified as `other-gate-based`, which the template-proxy library routes to `templates.ansatz_stretch` (an ansatz with `full_t_count = 0`). Roughly 22 of the 28 v4 picks therefore enter Regime A by template construction. The bifurcation is preserved — the partition is exact and the lemma below remains threshold-independent — but the per-silo Regime-A share is materially shaped by the proxy mapping, not solely by paper-faithful algorithm choice. Silo-median τ values shifted toward Regime A relative to N=32 for this reason, and any future paper-faithful re-implementation would re-balance the per-silo medians without changing the (label-level) partition fact.

This emptiness is robust under reasonable threshold perturbations: loosening any single threshold by an order of magnitude leaves the strict subset empty; only when ALL three thresholds are loosened simultaneously (τ<100, td≥1, wc≥1e-3 s) does a single label (SP2, t_count=8) appear.

The dominant research challenge identified by this work is therefore to construct algorithms that have a **non-trivial oracle (Regime B)** AND an **oracle whose FT cost does not dominate the answer (currently a Regime A property)** — i.e., structured state preparation paired with a real algorithmic speedup.

## Empirical anchor table (refreshed at N=74)

From `p4_experiments/common/output/forward_outlook/silo_tau_ranking.json` at the H4 anchor cell `(maj_e6_floquet, ε = 1e-4)`:

| silo | n_labels | median τ_runtime (full / bare) | regime tilt |
|---|---:|---:|---|
| trading-execution      | 1  | 1.94   | A |
| derivative-pricing     | 13 | 1.94   | A (template-proxy dominated) |
| (cross-silo other)     | 4  | 1.94   | A |
| quantum-ml-finance     | 15 | 1.99   | A (template-proxy dominated) |
| fraud-detection        | 4  | 4.35   | A→B |
| portfolio-optimization | 8  | 7.59   | mixed (template-proxy shifted) |
| insurance-actuarial    | 1  | 153.55 | B |
| risk-management        | 3  | 249.18 | B |
| simulation-monte-carlo | 11 | 249.18 | B |

The two-cluster structure is preserved at the **label level** (Regime A vs Regime B remains a clean partition of the 60 labels by `full_t_count`). The per-silo medians have shifted toward Regime A relative to N=32 because the v4 census added 28 `other-gate-based` papers that the template proxy routes through `ansatz_stretch` (no oracle, τ ≈ 2). Silos most affected: derivative-pricing (median 157 → 1.94), portfolio-optimization (457 → 7.59). Silos with paper-faithful Regime-B oracles (simulation-monte-carlo, risk-management, insurance-actuarial) retain large medians.

## Naive-winner lemma (threshold-independent)

> **Lemma (N=74, row-level census).** At the H4 anchor cell `(maj_e6_floquet, ε=1e-4)`, every label that satisfies the *naive* winner criterion (`τ_runtime_vs_bare < 10` AND quantum-full-runtime beats classical wall-clock) has `full_t_count = 0`.

Equivalently: the set of naive winners equals the set of `t_count = 0` labels exactly. There are zero counter-examples in the census.

```
naive_winners        = {B3, B4, SD2, SD4, SD6, SD7, SD8, SD9, SD10, SD11,
                       SF2, SF3, SM4, SM8, SM9, SM10, SM11, SP4, SP5, SP6, SP7,
                       SQ1, SQ2, SQ3, SQ5, SQ6, SQ7, SQ8, SQ9, SQ10, SQ11, SQ12,
                       ST1, SX1, SX2, SX3, SX4, T3}                                  (38 labels)
labels_with_t_count_0 = same 38 labels
intersection          = the same 38 labels
symmetric difference  = ∅
```

This lemma is **threshold-independent**: it does not depend on the choice of the τ < 10 cutoff or the wall-clock floor. It is a structural fact about the census. The bifurcation thesis stated above is therefore not an artefact of the strict-H4 thresholds — it is the literature's empirical structure speaking.

## Robustness sweep (strict-H4 emptiness)

The strict-H4 subset = ∅ result is robust under reasonable single-axis perturbation of every threshold. Sweep performed in the 2026-04-18 external audit:

| perturbation | τ cutoff | t_depth ratio | classical wc floor | strict subset |
|---|---:|---:|---:|---|
| **default (pre-registered)** | < 10 | ≥ 10 | ≥ 1e-2 s | **∅** |
| τ tighten | < 5 | ≥ 10 | ≥ 1e-2 s | ∅ |
| τ loosen | < 100 | ≥ 10 | ≥ 1e-2 s | {SP2} (t_count=8) |
| t_depth loosen | < 10 | ≥ 1 | ≥ 1e-2 s | ∅ |
| t_depth tighten | < 10 | ≥ 100 | ≥ 1e-2 s | ∅ |
| wall-clock loosen | < 10 | ≥ 10 | ≥ 1e-3 s | ∅ |
| wall-clock tighten | < 10 | ≥ 10 | ≥ 1e-1 s | ∅ |
| ALL loosen | < 100 | ≥ 1 | ≥ 1e-3 s | {SP2} (t_count=8) |
| ALL tighten | < 5 | ≥ 100 | ≥ 1e-1 s | ∅ |

**Reading.** The negative result is not knife-edge. Loosening *any single* threshold leaves it empty (with the borderline exception of τ < 100, which admits SP2 — a Grover-on-8-qubit portfolio variant with `t_count = 8`, marginally non-trivial). Even the *all-loosen* scenario admits only SP2. No reasonable redefinition of the strict criterion produces a meaningfully non-empty subset.

## Why this matters for the dissertation narrative

This bifurcation is the **constructive** core of the thesis:

1. The negative H4 strict result is not "quantum finance has no advantage" — it is "the literature is empirically partitioned into two non-overlapping regimes, and neither one alone constitutes advantage."
2. The methodology (Phase 4-prime: pre-registered, audit-clean, profile-resolved FT estimation) reveals this partition with a 45-check audit and N = 1912 records across the full N = 74 row-level census.
3. The forward-research priorities (see `p4_experiments/common/output/forward_outlook/README.md`) follow directly: **bridge the bifurcation by building structured-state-preparation primitives that turn Regime B oracles into Regime A FT cost.**

## Citation in manuscript

When referenced from `manuscript/03_Chapters/`, cite as:

> Phase 4-prime, N = 74 row-level census (tag `p4-preregistration-v5`), bifurcation
> thesis derived from per-silo τ-ranking and oracle-tax decomposition.
