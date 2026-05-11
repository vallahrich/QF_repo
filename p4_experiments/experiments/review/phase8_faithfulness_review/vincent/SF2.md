# Faithfulness Review: SF2

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Q-DTN: A Quantum-Enhanced Framework for Secure Financial Risk Management
- **Authors:** Akshay Mittal, Krishna Kandi, Anusha Nagineni, Vamsi Alla
- **Year:** 2025
- **Paper ID:** `8fec8d839e47` · **Experiment:** `exp_1` · **Silo:** `fraud-detection` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/8fec8d839e47.md](p2_systematic_review/output/processed/8fec8d839e47.md)
- Circuit: [p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/circuit.py](p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/circuit.py)
- Instance: [p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/instance.json](p4_experiments/experiments/silos/fraud_detection/8fec8d839e47/instance.json)

---

## Verdict summary

RealAmplitudes proxy at correct 5-qubit scale faithfully represents the paper's variational Ry/Rz+CNOT ansatz family, with minor deviations (Ry-only vs Ry/Rz, 3 vs 4 layers, stale 'other-gate-based' family tag).

## Checks

### ✅ Family-faithful

Paper describes a hybrid QSVM+VQC (QERC) with a parameterised variational circuit using alternating Ry/Rz single-qubit rotations and CNOT entanglers. RealAmplitudes(reps, entanglement='linear') is a standard variational ansatz with Ry rotations + CNOT entanglement — same family (variational-nisq / VQC). The cohort tag 'other-gate-based' is loose but not contradictory.

### ✅ Scale-faithful

Paper reports n_qubits_used=5; circuit instantiates n_qubits=5. Exact match (well within factor of 2 and below 12-qubit cap).

- `v2_n_qubits`: `5`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

build_bare uses ansatz_stretch (RealAmplitudes-style parameterised ansatz with random angles); _full_oracle composes ansatz . ansatz^dagger (compute-uncompute) followed by computational-basis measurement. Non-trivial parameterised entangling structure consistent with a VQC proxy.

### ❌ Metadata-consistent

Two minor inconsistencies: (1) instance.parameters.ansatz_layers=3 but paper-reported optimal depth is 4 layers (also recorded in instance.paper_claimed.circuit_depth=4 and v2 ansatz_layers=4); (2) algorithm_family tag is 'other-gate-based' whereas the paper is clearly variational-nisq / VQC. Both are documented as a template-proxy stretch and do not invalidate the proxy.

## Concerns

- ansatz_layers mismatch: instance uses 3 layers, paper reports optimal 4 layers (v2 extraction also says 4)
- RealAmplitudes uses Ry rotations only; paper specifies alternating Ry/Rz rotations (proxy approximation)
- algorithm_family tag 'other-gate-based' understates that this is a VQC/variational-nisq cohort entry
- Paper algorithm (hybrid QSVM+VQC with hinge loss, COBYLA, parameter-shift training) is not implemented — only the variational ansatz at paper scale is exercised, as openly disclosed in instance.notes

## Recommendations

- Bump instance.parameters.ansatz_layers from 3 to 4 to match paper's reported optimal circuit_depth_layers=4
- Consider re-tagging algorithm_family as 'variational-nisq' (or adding a sub-tag) for downstream Phase-8 cohort analysis
- Optionally extend the proxy to interleave Rz layers between Ry layers to better mirror the paper's alternating Ry/Rz structure
