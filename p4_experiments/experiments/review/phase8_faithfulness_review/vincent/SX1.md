# Faithfulness Review: SX1

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Authors:** Wen Ji, Xiangdong Meng
- **Year:** 2020
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_1` · **Silo:** `other` · **Algorithm family:** `hhl`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json)

---

## Verdict summary

Paper implements HHL (QPE + controlled reciprocal rotation + inverse QPE on Qiskit Aqua), but circuit.py is a generic RealAmplitudes ansatz compute-uncompute template proxy with no QPE structure; explicitly self-flagged as not implementing the paper's algorithm.

## Checks

### ❌ Family-faithful

Cohort/@register tag declares algorithm_family='hhl' matching the paper, but the actual gates are a generic variational ansatz, not an HHL circuit. Family tag is aspirational rather than realised.

### ✅ Scale-faithful

Paper 2x2 case uses 1 system + 3 clock + 3 ancillae ~= 7 qubits; circuit uses 4 qubits. Within factor of 2 and under the 12-qubit cap.

- `v2_n_qubits`: `7`
- `circuit_n_qubits`: `4`

### ❌ Structurally non-trivial

An HHL proxy must exhibit QPE-shaped structure (Hamiltonian simulation of e^{-iAt}, QFT/inverse-QFT on a clock register, controlled reciprocal rotation on an ancilla). The circuit contains only RealAmplitudes followed by its inverse and a measurement; no QPE, no controlled rotation, no clock register.

### ❌ Metadata-consistent

@register declares algorithm_family='hhl' but instance.json declares algorithm_family='other-gate-based' and notes 'does NOT implement the paper's algorithm'. Inconsistent family labels across registry and instance.

## Concerns

- Circuit is a generic variational ansatz proxy, not an HHL implementation; no QPE / controlled-rotation / inverse-QPE structure.
- Metadata mismatch: registry algorithm_family='hhl' vs instance.json algorithm_family='other-gate-based'.
- Instance label inside instance.json is 'SX4' (instance_id 'SX4_v3_proxy_v1', label 'SX4') even though this triple is SX1; SX1-SX4 share one paper but the instance file appears to have been authored against the SX4 slot and reused.
- Resource estimates derived from this circuit will reflect ansatz cost, not HHL cost; using them as a Phase-8 proxy for HHL resource scaling will systematically understate true HHL gate counts (no Trotterised Hamiltonian simulation, no QFT).

## Recommendations

- Either (a) replace circuit with an HHL skeleton (state-prep on system + QPE with Trotterised e^{-iAt} on a clock register + controlled-Y reciprocal on ancilla + inverse QPE) sized at paper scale, or (b) downgrade registry algorithm_family to 'other-gate-based' / 'ansatz-proxy' so the proxy classification is honest and Phase-8 aggregation does not attribute these costs to the HHL family.
- Reconcile instance.json metadata for SX1: set label/instance_id to SX1 and align algorithm_family with the registry choice made above.
- If the proxy is retained, document in the cohort that SX1-SX4 contribute ansatz-proxy resource estimates, not HHL estimates, and exclude them from any HHL-family scaling claim.
