# Faithfulness Review: SX3

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Authors:** Wen Ji, Xiangdong Meng
- **Year:** 2020
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_3` · **Silo:** `other` · **Algorithm family:** `hhl`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz compute-uncompute proxy with no QPE/controlled-reciprocal/inverse-QPE structure, so it does not represent the paper's HHL algorithm class; instance.json metadata is also for a different label (SX4/exp_1).

## Checks

### ❌ Family-faithful

Paper algorithm family is HHL (QPE + Lookup reciprocal + inverse QPE). The circuit uses a generic variational RealAmplitudes ansatz (template proxy) with no HHL-specific structure; @register tag says 'hhl' but the implementation is not in the HHL family.

### ✅ Scale-faithful

Paper reports 7 qubits for the full HHL register (2 state-prep + 3 clock + 3 ancilla per v2; 4 system-side for the 4x4 instance). Circuit uses 4 qubits, within a factor of 2 of the paper's 7-qubit count and matching the 4x4 system size.

- `v2_n_qubits`: `7`
- `circuit_n_qubits`: `4`

### ❌ Structurally non-trivial

Full circuit is just RealAmplitudes . RealAmplitudes^dagger (compute-uncompute), which approximates the identity and contains none of the HHL building blocks (no QPE/Hamiltonian simulation, no controlled rotation implementing 1/lambda, no inverse QPE). Not structurally representative of HHL.

### ❌ Metadata-consistent

instance.json has label='SX4', experiment_id='exp_1', algorithm_family='other-gate-based', and notes='paper algorithm not implemented'. Task is SX3/exp_3 with cohort algorithm_family='hhl'. The @register decorator tags the circuit as label='SX4' algorithm_family='hhl', so label_id, experiment_id, and family tags disagree across cohort, instance, and circuit.

## Concerns

- Generic ansatz proxy does not implement HHL (no QPE, no controlled reciprocal, no inverse QPE).
- instance.json is labelled SX4/exp_1 but is being used for SX3/exp_3.
- circuit.py @register uses label='SX4' while the cohort entry is SX3.
- instance.json algorithm_family='other-gate-based' contradicts cohort/registry algorithm_family='hhl'.
- Compute-uncompute pair approximates the identity, providing no algorithmically meaningful proxy oracle for HHL cost estimation.

## Recommendations

- Re-author the SX3 instance.json and circuit.py with correct label_id='SX3' and experiment_id='exp_3'.
- Either implement an HHL-shaped proxy (QPE + controlled rotation + inverse QPE) at small scale, or downgrade cohort algorithm_family to reflect that the implementation is a generic ansatz.
- Reconcile algorithm_family tags across cohort, instance.json, and the @register decorator.
