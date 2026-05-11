# Faithfulness Review: SQ6

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum support vector data description for anomaly detection
- **Authors:** Hyeondo Oh, Daniel K. Park
- **Year:** 2023
- **Paper ID:** `2a9cd8a96604` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `quantum-ml`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/2a9cd8a96604.md](p2_systematic_review/output/processed/2a9cd8a96604.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz proxy at 6 qubits is a defensible quantum-ml stand-in for the paper's 8-qubit QCNN-based QSVDD, but does not implement QCNN convolution+pooling structure and carries stale 'SQ9' labels plus an instance-level family tag mismatch.

## Checks

### ✅ Family-faithful

Cohort algorithm_family is 'quantum-ml' and the circuit is a generic variational ansatz registered under algorithm_family='quantum-ml', matching the paper's variational quantum ML (QSVDD) class. Instance.json tags algorithm_family='other-gate-based', which is a metadata inconsistency rather than a family-faithfulness failure.

### ✅ Scale-faithful

Paper uses 8 qubits (amplitude encoding of 16x16 = 256 amplitudes); circuit uses 6 qubits. 6 is within a factor of 2 of 8 and below the 12-qubit tractability cap.

- `v2_n_qubits`: `8`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

Circuit is RealAmplitudes(reps=3, entanglement='linear') with a compute-uncompute pair plus measurement; it is non-trivial as a generic VQC template proxy but does not exhibit the QCNN structure (hierarchical convolution + pooling, shared SU(4)-type two-qubit gates, partial-trace reduction to 2 qubits, expectation-value latent vector) that the paper's QSVDD algorithm requires. This is explicitly disclosed in the instance notes as 'template proxy' and is consistent with the cohort's preregistered template-proxy methodology.

### ❌ Metadata-consistent

Multiple stale identifiers: instance.json instance_id='SQ9_v3_proxy_v1' and label='SQ9'; circuit.py @register(label='SQ9'), build_bare description and accounting register all under label 'SQ9'; instance.json algorithm_family='other-gate-based' contradicts cohort algorithm_family='quantum-ml' and the registry tag. paper_id and paper_title remain consistent with SQ6's paper (2a9cd8a96604, QSVDD).

## Concerns

- Circuit/instance are registered under label 'SQ9', not 'SQ6'; a downstream lookup by 'SQ6' may miss this circuit unless a label-remap is applied.
- instance.json algorithm_family='other-gate-based' disagrees with cohort and circuit registry which use 'quantum-ml'.
- Implemented circuit (generic RealAmplitudes + compute-uncompute) does not realize the paper's QCNN convolution+pooling structure or its expectation-value latent measurement, so it cannot be used to estimate QSVDD-specific resource scaling beyond a generic VQC proxy.
- Qubit count slightly under-scaled (6 vs paper 8); within tolerance but loses the exact amplitude-encoding scale of 256 input amplitudes.

## Recommendations

- Reconcile label_id: either rename circuit/instance from 'SQ9' to 'SQ6' or add an explicit alias so the label registry resolves SQ6 -> this artifact.
- Update instance.json algorithm_family from 'other-gate-based' to 'quantum-ml' to match the cohort and circuit registry.
- If a more faithful proxy is desired, raise n_qubits to 8 to match the paper's amplitude encoding scale (still well under the 12-qubit cap).
- Optionally swap RealAmplitudes for a minimal QCNN-shaped template (alternating two-qubit conv blocks + pooling) to preserve structural family fidelity for QSVDD-class resource estimates.
