# Faithfulness Review: SQ9

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum machine learning for quantum anomaly detection
- **Authors:** Nana Liu, Patrick Rebentrost
- **Year:** 2017
- **Paper ID:** `53a718c11ea8` · **Experiment:** `exp_2` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/53a718c11ea8.md](p2_systematic_review/output/processed/53a718c11ea8.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz template proxy with no HHL/QPE structure, while the paper's exp_2 is explicitly the HHL-based quantum one-class SVM variant; additionally the circuit/instance carry SQ10 labels and a 'quantum-svm' family tag rather than SQ9.

## Checks

### ❌ Family-faithful

Paper exp_2 is HHL-based quantum one-class SVM (block-encoded QSP / QPE / density-matrix exponentiation per v2 extraction). Circuit is a generic linear RealAmplitudes ansatz with no linear-system-solving structure. Cohort tag 'other-gate-based' and circuit registry tag 'quantum-svm' both fail to match the HHL/quantum-linear-systems family the paper claims for this experiment.

### ✅ Scale-faithful

Paper does not state qubit count (NOT_STATED). Implemented n_qubits=5 is within the <=12 tractability cap and is a reasonable small-scale proxy.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ❌ Structurally non-trivial

An HHL-shaped circuit would require QPE on a controlled e^{-iKt} block plus controlled rotations and uncomputation. The implementation is only RealAmplitudes . RealAmplitudes^dagger (compute-uncompute), which has no QPE register, no controlled Hamiltonian-evolution block, and no eigenvalue-inversion rotation. It is non-trivial as a generic ansatz but not structurally representative of the HHL-class algorithm.

### ❌ Metadata-consistent

instance.json reports label='SQ10', experiment_id='exp_1', and algorithm_variant_paper='quantum kernel PCA for anomaly detection (pure states)'; circuit.py registers label='SQ10' with algorithm_family='quantum-svm'. None of these match the SQ9 / exp_2 (HHL one-class SVM) target. Note explicitly says 'does NOT implement the paper's algorithm'.

## Concerns

- Wrong experiment binding: SQ9 targets exp_2 (HHL variant) but the implementation files are labeled SQ10 / exp_1 (kernel PCA pure-states variant).
- Family drift: HHL/quantum-linear-systems paper algorithm represented by a generic RealAmplitudes ansatz with no QPE or matrix-inversion structure.
- Cohort algorithm_family tag 'other-gate-based' inconsistent with both paper (HHL) and circuit registry tag 'quantum-svm'.
- Self-declared in instance notes: 'The implemented circuit ... does NOT implement the paper's algorithm.'

## Recommendations

- If a structural proxy is required, switch to an HHL-shaped template (QPE register + controlled-U evolution block + ancilla rotation + inverse QPE) sized to the n_qubits cap.
- Otherwise reclassify SQ9 as an explicit ansatz_stretch resource-only proxy and update cohort algorithm_family to a generic-ansatz bucket so the family tag, circuit registry tag, and v2 extraction all agree.
- Re-author SQ9-specific instance.json and circuit.py (or alias to SQ10's files intentionally) so label_id/experiment_id metadata match the SQ9/exp_2 target instead of SQ10/exp_1.
