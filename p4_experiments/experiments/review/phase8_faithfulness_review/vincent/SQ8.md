# Faithfulness Review: SQ8

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum machine learning for quantum anomaly detection
- **Authors:** Nana Liu, Patrick Rebentrost
- **Year:** 2017
- **Paper ID:** `53a718c11ea8` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/53a718c11ea8.md](p2_systematic_review/output/processed/53a718c11ea8.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/53a718c11ea8/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz compute-uncompute proxy does not represent the paper's HHL/QPE/density-matrix-exponentiation algorithm class for quantum kernel PCA / one-class SVM anomaly detection.

## Checks

### ❌ Family-faithful

Paper's algorithm is HHL-style quantum linear-system inversion with density-matrix exponentiation of a quantum kernel and swap-test proximity estimation (oracle_structure=block_encoded_QSP, measurement=QPE in v2). Cohort bucket 'other-gate-based' is a catch-all, but the implemented circuit is a variational RealAmplitudes ansatz, which belongs to the VQE/ansatz family, not the QPE/HHL/quantum-kernel family the paper specifies. Circuit metadata further labels algorithm_family='quantum-svm', which is yet a third bucket and inconsistent with cohort and v2.

### ✅ Scale-faithful

Paper does not state a qubit count (NOT_STATED in v2 — pure-theory paper). Implemented n_qubits=5 is within the standard 12-qubit tractability cap and is a defensible default scale.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ❌ Structurally non-trivial

Paper-class structure would include density-matrix exponentiation of the kernel, QPE-shaped HHL inversion, and modified swap tests. Implemented circuit is RealAmplitudes(reps=3, linear entanglement) followed by its inverse and a computational-basis measurement — no QPE register, no controlled-rotation/inverse-QPE HHL skeleton, no swap test, no ancilla-based overlap test. The compute-uncompute pair is structurally trivial (returns to |0..0> up to noise) and bears no resemblance to the paper's algorithm structure.

### ❌ Metadata-consistent

circuit.py module docstring, register(label=...), register_accounting(label=...), instance.label, and instance.instance_id all say 'SQ10', but this audit target is SQ8. The four labels SQ8/SQ9/SQ10/SQ11 share paper 53a718c11ea8 (per v2 operator_notes), so reuse of one proxy across labels appears intentional, but the SQ8 cohort entry points at a circuit whose own metadata identifies it as SQ10. Additionally, register(algorithm_family='quantum-svm') disagrees with cohort.algorithm_family='other-gate-based'.

## Concerns

- Circuit implements a generic variational ansatz, not the paper's HHL + density-matrix-exponentiation + swap-test pipeline; resource estimates derived from this proxy will not reflect the paper's claimed costs.
- Compute-uncompute (U then U^dagger) on |0..0> with no intervening operation is structurally trivial and produces no algorithmic content; it is not a meaningful proxy oracle for a kernel-PCA / one-class-SVM anomaly detector.
- Single shared proxy used across SQ8/SQ9/SQ10/SQ11 (all from arXiv:1710.07405) — fine in principle, but circuit/instance metadata is hard-coded to 'SQ10', not parameterised per label.
- register(algorithm_family='quantum-svm') is inconsistent with cohort.algorithm_family='other-gate-based' for SQ8.
- Paper is pure theory with no stated qubit count, depth, or gate counts (v2 fidelity_assessment='P'); any small-scale proxy is necessarily a stretch, which strengthens (not weakens) the need to flag the family/structural mismatch.

## Recommendations

- Flag SQ8 (and the SQ9/SQ10/SQ11 siblings sharing this paper) as theoretical-paper proxies in the cohort, so downstream Phase-8 resource projections are not interpreted as faithful to the paper's HHL claims.
- If a more faithful proxy is desired, replace compute-uncompute with at minimum a QPE-shaped skeleton (QPE register + controlled-U powers + inverse QFT) over a small synthetic Hermitian K to mimic the HHL inversion stage, plus a final swap-test-style ancilla measurement.
- Reconcile circuit/instance metadata: either parameterise label/instance_id per cohort entry, or document explicitly in the cohort that SQ8/SQ9/SQ10/SQ11 share one circuit file labelled 'SQ10'.
- Reconcile algorithm_family tags: cohort says 'other-gate-based', register decorator says 'quantum-svm'; pick one and apply consistently.
