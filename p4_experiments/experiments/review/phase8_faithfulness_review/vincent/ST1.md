# Faithfulness Review: ST1

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Quantitative Trading: High-Frequency Statistical Arbitrage Algorithm
- **Authors:** Xi-Ning Zhuang, Zhao-Yun Chen, Yu-Chun Wu, Guo-Ping Guo
- **Year:** 2021
- **Paper ID:** `3adb18321a79` · **Experiment:** `exp_1` · **Silo:** `trading-execution` · **Algorithm family:** `hhl`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/3adb18321a79.md](p2_systematic_review/output/processed/3adb18321a79.md)
- Circuit: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py](p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py)
- Instance: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json](p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json)

---

## Verdict summary

Paper proposes an HHL/QSP-based Quantum Cointegration Test with QPE measurement and qRAM amplitude encoding; the circuit is a generic 6-qubit RealAmplitudes ansatz (compute-uncompute) with no HHL/QPE/oracle structure, and metadata is internally inconsistent.

## Checks

### ❌ Family-faithful

Cohort/decorator tag the circuit as algorithm_family='hhl' (matching the paper's HHL+qubitization+QSP/QLR pipeline), but the actual implementation is a generic variational RealAmplitudes ansatz with no HHL components (no QPE, no controlled-A, no eigenvalue inversion, no qRAM proxy). This is the explicit family_drift case called out in the rubric.

### ✅ Scale-faithful

Paper claims '>50 qubits' (~35 data + extras); circuit uses 6 qubits, which is within the documented 12-qubit tractability cap for the small-scale Phase-8 cohort, so scale is acceptable per methodology.

- `v2_n_qubits`: `50`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

An HHL/QLR-family proxy should exhibit QPE-shaped structure (clock register, controlled time-evolution of A, inverse QFT, conditional rotation, uncomputation). The circuit only stacks RealAmplitudes . RealAmplitudes^dagger on a single 6-qubit register and measures — a trivial compute-uncompute pair that approximates the identity and carries none of the HHL/QSP signature gates.

### ❌ Metadata-consistent

Internal metadata conflict: instance.json sets algorithm_family='other-gate-based' and explicitly says 'does NOT implement the paper's algorithm', while the @register decorator in circuit.py declares algorithm_family='hhl'. Cohort downstream code keys on the decorator, so the registered family overstates faithfulness.

## Concerns

- Implementation is a template proxy that is explicitly disclaimed in instance.json as not implementing the paper's algorithm, yet is registered under algorithm_family='hhl'.
- No QPE, qubitization, QSP, or qRAM-style oracle structure — none of the HHL/QLR signature components are present even at proxy scale.
- Compute-uncompute of the same RealAmplitudes block yields a near-identity unitary, so the resource profile (depth/2-qubit count) does not reflect any HHL-like cost shape.
- Discrepancy between decorator family ('hhl') and instance.json algorithm_family ('other-gate-based') will mislabel the cohort row in any per-family aggregation.

## Recommendations

- Either (a) reclassify ST1 as a generic-ansatz proxy (set decorator algorithm_family='other-gate-based' to match instance.json and document it as a non-faithful stretch), or (b) replace the bare/oracle builders with an HHL-shaped template (small QPE register + controlled e^{iAt} mock + inverse QFT + conditional rotation + uncompute) so the proxy matches the declared family.
- Reconcile algorithm_family between circuit.py @register and instance.json before Phase-8 aggregation to avoid silently inflating HHL coverage in the family roll-ups.
- If kept as ansatz proxy, drop the redundant compose(a.inverse()) so the circuit at least exercises a non-identity unitary that is informative for resource estimation.
