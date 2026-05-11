# Faithfulness Review: SD4

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Pricing multi-asset derivatives by variational quantum algorithms
- **Authors:** Kenji Kubo, Koichi Miyamoto, Kosuke Mitarai, Keisuke Fujii
- **Year:** 2022
- **Paper ID:** `1d44742c9e15` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/1d44742c9e15.md](p2_systematic_review/output/processed/1d44742c9e15.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/circuit.py](p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/instance.json](p4_experiments/experiments/silos/derivative_pricing/1d44742c9e15/instance.json)

---

## Verdict summary

RealAmplitudes (RY+CZ-style, linear entanglement) compute-uncompute proxy is a defensible variational stand-in for the paper's RY+CZ VQS ansatz at near-paper scale, but cohort family tag 'other-gate-based' and instance 'vqe' are both stale relative to the paper's actual VQS algorithm.

## Checks

### ✅ Family-faithful

Paper uses a parameterized RY+CZ ansatz inside a VQS loop; RealAmplitudes (RY rotations + CZ-like entanglers) is the canonical hardware-efficient ansatz proxy and is family-faithful as a variational template. The VQS time evolution and SWAP/Hadamard tests are not implemented, but the methodology explicitly permits a template proxy.

### ✅ Scale-faithful

Paper reports up to 6 qubits in VQS runs (ngr=64); circuit uses 5 qubits, well within factor 2 and below the 12-qubit cap.

- `v2_n_qubits`: `6`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit is RealAmplitudes(reps=3, linear entanglement) with assigned parameters; full circuit composes ansatz . ansatz_dagger compute-uncompute and measures. Non-trivial parameterized two-qubit-entangling structure consistent with a variational ansatz.

### ❌ Metadata-consistent

Cohort/registry tags algorithm_family='other-gate-based' while instance.json sets algorithm_family='vqe'; the paper is VQS (variational, hybrid), so the cohort 'other-gate-based' label is a stale/incorrect family tag. Also, ansatz_layers in instance (3) differs from paper's reported 4 (within proxy tolerance) and instance n_qubits=5 vs paper-claimed 6.

## Concerns

- Cohort algorithm_family='other-gate-based' contradicts instance algorithm_family='vqe' and the paper's VQS classification.
- Implementation is explicitly a generic ansatz_stretch template proxy and does not implement VQS time evolution, LCU decomposition of F/C, SWAP test, or Hadamard test.
- n_qubits=5 and ansatz_layers=3 instead of paper's 6 qubits / 4 layers, though within proxy tolerance.

## Recommendations

- Update cohort algorithm_family for SD4 from 'other-gate-based' to 'vqe' (or 'variational') to align with the paper and instance.json.
- Optionally bump n_qubits to 6 and ansatz_layers to 4 to exactly match the paper's reported configuration since both are well under the 12-qubit cap.
