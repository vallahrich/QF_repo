# Faithfulness Review: SQ7

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Variational Quantum Eigensolver for Classification in Credit Sales Risk
- **Authors:** Joanna Wiśniewska, Marek Sawerwain
- **Year:** 2024
- **Paper ID:** `2fe0d0f15604` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `vqe`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/2fe0d0f15604.md](p2_systematic_review/output/processed/2fe0d0f15604.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2fe0d0f15604/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2fe0d0f15604/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2fe0d0f15604/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2fe0d0f15604/instance.json)

---

## Verdict summary

RealAmplitudes/ZZFeatureMap proxy is family-faithful (VQE) and structurally reasonable at the paper's compact 3-qubit scale, but omits the SWAP-Test classifier head and instance metadata tags algorithm_family as 'other-gate-based' instead of 'vqe'.

## Checks

### ✅ Family-faithful

Paper is a VQE-trained classifier (Wisniewska & Sawerwain 2024); circuit registers algorithm_family='vqe' and uses a parameterized variational ansatz (RealAmplitudes), which is a standard generic VQE-family proxy.

### ✅ Scale-faithful

Circuit uses 3 qubits matching the paper's primary compact variant (q=3 to encode 2^3=8 amplitudes for 7 features + 1 pad). v2 canonical lists num_qubits=9 (P3 override that appears to count SWAP-Test ancilla + two 3-qubit registers ~ 2*3+1=7..9); 3 vs 9 is within the factor-2/cap-at-12 tractability allowance.

- `v2_n_qubits`: `9`
- `circuit_n_qubits`: `3`

### ✅ Structurally non-trivial

Bare = RealAmplitudes (Ry + CX entanglers), matching the paper's tailored 'Ry + CNOT' ansatz family. Full = ZZFeatureMap data encoding + ansatz + Hadamard basis change + measurement. Non-trivial parameterized circuit appropriate for a VQE proxy.

### ❌ Metadata-consistent

instance.json sets parameters.algorithm_family='other-gate-based' while the @register decorator and cohort declare algorithm_family='vqe'. Also paper_claimed.circuit_depth=1 in instance.json contradicts paper's depth=NOT_STATED and the al=2 best-config note in the v2 extraction.

## Concerns

- Circuit omits the SWAP-Test similarity head, which is the paper's actual classification primitive — proxy captures only the VQE state-preparation half of the pipeline.
- instance.parameters.algorithm_family ('other-gate-based') is inconsistent with the cohort/register tag ('vqe').
- ansatz_reps=1 in instance.json vs paper's best-config al=2 (v2 extraction) — minor depth under-estimate for the proxy.
- ZZFeatureMap data encoding does not match the paper's sqrt-amplitude encoding (state-preparation method drift in the 'full' mode).
- v2 num_qubits=9 (P3-override winner) vs paper-text q=3 (compact) / q=8 (alt) is itself a canonical-extraction discrepancy worth noting.

## Recommendations

- Fix instance.json: set parameters.algorithm_family='vqe' and ansatz_reps=2 to match paper Table 4 No. 11 best config.
- Document explicitly that the proxy intentionally excludes the SWAP-Test classifier head (or add an optional SWAP-Test variant for resource-cost completeness).
- Reconcile v2 num_qubits=9 with paper text (3 or 8) — the P3 override note suggests it counts SWAP-Test ancillas; surface this in the canonical_metadata field_changes rationale.
- Consider replacing ZZFeatureMap with an Initialize/amplitude-encoding stage in 'full' mode to better match the paper's sqrt-amplitude state preparation.
