# Babbush et al. 2021 — Framework Interpretation

**Paper:** Babbush, McClean, Newman, Gidney, Boixo, Neven. *Focus beyond quadratic speedups for error-corrected quantum advantage.* PRX Quantum 2, 010103 (2021). arXiv:2011.04149

## Core argument

Under fault tolerance via the surface code, a logical Toffoli/CCZ gate costs ~170 µs (code distance 30, 1 µs surface cycle, 5.5 cycles per Toffoli). Clifford gates are effectively free. A single classical 64-bit op takes ~330 ps (a few clock cycles on a 3 GHz CPU). This gives an ~5×10^5 primitive-time ratio tQ/tC that any quantum algorithm must amortize across M primitive calls before quantum runtime beats classical runtime.

**Master equation (Eq. 5):**

```
M > (tQ · S / tC)^(1/(d-1))          advantage condition
T* = tQ · (tQ · S / tC)^(1/(d-1))    breakeven time
```

Where `d` is the polynomial speedup order (quantum runtime ∝ M · tQ vs classical runtime ∝ M^d · tC / S), and `S` is classical parallelism.

## Scorecard vs Hoefler 2023

| Dimension | Hoefler | Babbush |
|---|---|---|
| Speedup granularity | Fixed M_max table per (speedup, op_type) | Formula scales with tQ, tC, S |
| Clock model | Implicit 10 µs gate time | Explicit 170 µs Toffoli time (surface code) |
| Classical parallelism | Single core | S up to 10^6 (Amdahl-bound) |
| Verdict on quadratic | `quadratic_insufficient` (fails) | `fails` (even more pessimistic under parallel classical) |
| Verdict on cubic | Depends on oracle M ≤ 12.5M | **More optimistic**: M_min ≈ 720 for S=1 |
| Verdict on quartic | `likely_viable` | `likely_viable` (M_min ≈ 80 for S=1) |

Babbush is **tighter on quadratic** (classical parallelism makes it worse) and **looser on cubic+** (the polynomial power d-1 in the denominator means cubic only needs ~10^3 calls to crossover, not 10^7).

## How this assessor implements it

For each experiment:

1. Infer speedup order `d` from (a) paper complexity claims, (b) derived-field theory, (c) algorithm family mapping (Grover→2, Shor→exp, VQE→none_proven, …).
2. Read oracle call count M from paper (`quantum_resources.t_count` or derived `oracle_complexity_M`).
3. Compute **M_min** under the default regime (tQ=17 ms, tC=33 ns, S=10^3) and **T*** (breakeven time in seconds).
4. Decide:
   - `quadratic` → default `fails` (paper's central claim). If M reported AND in [M_min, M_max(budget)] under the more generous S=1 regime, downgrade to `potentially_viable`.
   - `cubic` → if M ≥ M_min and T* ≤ budget, `potentially_viable`. If M unknown, `conditional`.
   - `quartic` / higher polynomial → `likely_viable`.
   - `exponential` / `logarithmic` → `viable`.
   - `none_proven` → `fails`.

5. `framework_specific` records: `d`, `M_min`, `T_star_seconds`, `S_used`, `regime` ("lower_bound" vs "sa"), `oracle_M_reported`.

## Why it matters for the triangulation

Hoefler gives a binary pass/fail against a fixed clock model. Babbush shows **how the verdict moves when you change the clock or classical parallelism** — the two frameworks should agree on quadratic (both fail) and on exponential (both viable), but **disagree on cubic** (Babbush says many cubic algorithms cross over quickly; Hoefler's Table 2 says few beat the oracle-complexity cap). These cubic disagreements are the most interesting rows for Phase 4 candidate selection.

## Out of scope

- I/O bandwidth (Hoefler handles this; Babbush assumes it's not the bottleneck).
- Specific logical-qubit counts (Babbush works in a dimensionless primitive-time ratio; finer per-application estimates are Dalzell's and Chakrabarti's job).
- Near-term heuristic algorithms (QAOA/VQE): Babbush's framework assumes a proven polynomial speedup and emits `fails` otherwise.
