# Dalzell et al. 2023 — Framework Interpretation

**Paper:** Dalzell, McArdle, Berta, Bienias, Chen, Gilyén, Hann, Kastoryano, Khabiboulline, Kubica, Salton, Wang, Brandão. *Quantum algorithms: A survey of applications and end-to-end complexities.* arXiv:2310.03011 (2023). 337 pp., Amazon AWS Center for Quantum Computing.

## Core contribution

Dalzell is the industry's most comprehensive **end-to-end complexity catalog** for fault-tolerant quantum algorithms. For each major application area (finance, chemistry, optimization, ML, cryptography, …) the survey synthesizes the best-known logical-qubit and T-count / T-depth estimates from dozens of underlying primitives (QPE, QAE, QLSS, block encodings, QSP, QSVT, QRAM, …).

Unlike Hoefler (generic thresholds) or Babbush (dimensionless clock-ratio argument), Dalzell gives **concrete per-application resource floors** that a device must cross before quantum advantage is plausible in that problem area.

## Finance-specific numbers Dalzell endorses

| Silo | Min logical qubits | Min T-count | Min T-depth | Source chapter |
|---|---|---|---|---|
| Derivative pricing (autocallable/TARF) | 4.7k (QSP) – 12k | 2.4e9 – 9.8e9 | 4.5e7 – 8.2e7 | §8.2 |
| Monte Carlo (option pricing) | 4.7k – 12k | 2.4e9 – 9.8e9 | 4.5e7 – 8.2e7 | §8.2 |
| Risk management / VaR / CVA | ~12k (+ Greeks) | ~9.8e9 | ~1e8 | §8.0 |
| Portfolio optimization (SOCP/QIPM) | **8 million** | **~1e29** | ~1e24 | §22 |
| Cryptanalysis (RSA-2048 via Shor) | 6k | 1.1e8 Toffoli | ~1e7 | §19 |

**Key observation:** Dalzell's finance estimates are 10^3 – 10^25 times larger than what current devices can deliver, and portfolio optimization via QIPM is **effectively infeasible** even with an idealized fault-tolerant machine.

## How this assessor implements it

For each experiment:

1. Look up the silo's Minimum Scale for Advantage (MSA) = `(min_logical_qubits, min_t_count, min_t_depth)`.
2. Read the reported `quantum_resources.num_qubits` and `quantum_resources.t_count` (or derived `oracle_complexity_M` as a loose T-count proxy).
3. Decide:
   - No MSA for silo (trading-execution, fraud-detection, …) → `not_applicable`.
   - Silo flagged `is_infeasible` (portfolio-optimization) → `fails` regardless of reported numbers (Dalzell's end-to-end estimate is ~10^29 T-gates).
   - Both qubits and T-count reported AND both ≥ MSA → `likely_viable`.
   - Both reported AND both < MSA → `fails` (problem classically trivial at this scale).
   - Mixed (one above, one below) → `conditional`.
   - Either missing → `insufficient_data`.

4. `framework_specific` records: `logical_qubits_reported`, `t_count_reported`, `min_logical_qubits`, `min_t_count`, `qubit_margin` (ratio), `t_count_margin` (ratio), `silo_analyzed_in_dalzell` (bool).

## Why it matters for the triangulation

Dalzell is the only framework that directly checks whether the **problem instance size** a paper claims is at the scale Dalzell thinks is needed for advantage. This catches two error modes that Hoefler and Babbush miss:

- **Over-scoping**: a paper claims 50-qubit option pricing "demonstrates quantum advantage" — Dalzell says you need 4.7k qubits before the QAE crossover matters.
- **Under-scoping**: a paper estimates 10^8 qubits for portfolio QIPM — Dalzell confirms this is the published best-known number and emits `fails`.

Agreement with Chakrabarti on derivative pricing will be very high (Chakrabarti is the source of Dalzell's numbers). Disagreement with Hoefler will be concentrated in the QIPM portfolio-optimization silo, where Dalzell's hard `fails` conflicts with Hoefler's "cubic_conditional" when oracle M is unreported.

## Caveats

- Dalzell's numbers are **upper bounds on what's known**; future algorithmic improvements will lower them. Thresholds in this file should be revisited each time a new end-to-end resource estimate appears.
- Dalzell explicitly declines to give QML-in-finance numbers, so those experiments emit `not_applicable`.
- The "infeasible" flag on QIPM is a **framework-specific** judgment — Babbush and Hoefler would handle the same experiment via oracle-complexity tables without declaring infeasibility.
