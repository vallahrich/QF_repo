# Chakrabarti et al. 2021 — Framework Interpretation

**Paper:** Chakrabarti, Krishnakumar, Mazzola, Stamatopoulos, Woerner, Zeng. *A threshold for quantum advantage in derivative pricing.* Quantum 5, 463 (2021). arXiv:2012.03819. Goldman Sachs / QC Ware.

## Core contribution

The **only** framework in our triangulation that was purpose-built for **finance**. Provides end-to-end resource estimates for QAE-based derivative pricing on production-grade contracts (autocallable options, TARFs) — not toy 2-asset examples.

Key innovation: the **re-parameterization method** (loading stochastic processes via log-return space instead of price space), which drops resource requirements by orders of magnitude compared to Riemann-sum approaches.

## Threshold numbers (Table 1, re-parameterization)

| Derivative | T-count | T-depth | Logical qubits | Target error |
|---|---|---|---|---|
| Autocallable (3 underlyings, 5 dates) | 1.2×10^10 | 5.4×10^7 | 8,000 | 2×10^-3 |
| TARF (1 underlying, 26 dates) | 9.8×10^9 | 8.2×10^7 | 11,500 | 2×10^-3 |

**Hardware target:** 10 MHz T-gate rate → 1-second pricing wallclock.
**Current state-of-art:** ~10 kHz (1,000× gap).
**Code distance:** must support 10^10 error-free logical operations.

## How this assessor implements it

**Scoped:** only runs on `derivative-pricing`, `risk-management`, `simulation-monte-carlo`, `insurance-actuarial`. Everything else → `not_applicable`.

For each in-scope experiment:

1. Read `quantum_resources.num_qubits`, `quantum_resources.t_count` (or derived `oracle_complexity_M` as T-count proxy).
2. Compare against the Chakrabarti envelope:
   - *Below min* (8k qubits / 9.8e9 T-count): `fails` — problem hasn't reached derivative-pricing complexity floor.
   - *Within envelope* (between re-param and Riemann no-norm): `potentially_viable` — Chakrabarti says this is the target resource regime.
   - *Above max* (>23k qubits / >1.6e11 T-count): `conditional` — resources exceed known-efficient methods; may indicate an algorithm gap.
   - *No resources reported*: `insufficient_data`.
3. Also check algorithm family: if the algorithm isn't QAE-based (e.g., VQE, QAOA for derivative pricing), emit `conditional` with a note that Chakrabarti's analysis assumes QAE.

## Why it matters for the triangulation

Chakrabarti is the source paper for Dalzell's Section 8.2 finance numbers. **High agreement** between Chakrabarti and Dalzell on derivative pricing is expected — they share the same underlying resource estimates. **Disagreement** with Hoefler and Babbush is expected on cubic-speedup experiments where Hoefler says "oracle too complex" but Chakrabarti's more refined circuit analysis shows the T-depth is feasible (just needs a faster clock).

For the thesis, Chakrabarti provides the **industry credibility** bridge: it's a Goldman Sachs paper, peer-reviewed in *Quantum*, and gives exact hardware targets the industry is building toward.

## Caveats

- Only covers geometric Brownian motion stochastic models. Stochastic volatility, jump-diffusion, etc. would change resource estimates.
- Target error ε=2×10^-3 is production-relevant but not competitive with classical's double-precision arithmetic.
- The 10 MHz target assumes *all* T-gates are sequential. Parallelism across factories could change the picture.
