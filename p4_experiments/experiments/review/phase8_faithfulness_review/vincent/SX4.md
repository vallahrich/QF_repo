# Faithfulness Review: SX4

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Authors:** Wen Ji, Xiangdong Meng
- **Year:** 2020
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_4` · **Silo:** `other` · **Algorithm family:** `hhl`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz compute-uncompute proxy with no QPE/controlled-rotation/inverse-QPE structure, so it does not represent the HHL algorithm class the paper implements.

## Checks

### ❌ Family-faithful

Cohort/registry tag is hhl, but the implementation is a variational ansatz stretch (instance.json algorithm_family='other-gate-based', task='generic variational ansatz stretch (template proxy)'). Variational ansatz is not in the HHL family.

### ✅ Scale-faithful

Paper system register is 4 qubits for the 4x4 dense symmetric case (plus 3 clock + 3 ancillae); circuit uses n_qubits=4, matching the system-register scale within the factor-of-2 / cap-12 rule.

- `v2_n_qubits`: `4`
- `circuit_n_qubits`: `4`

### ❌ Structurally non-trivial

HHL requires QPE (Suzuki Hamiltonian simulation) + controlled reciprocal rotation (Lookup) + inverse QPE. The circuit contains only a RealAmplitudes ansatz and its inverse with measurement; no QPE shape, no controlled rotations on an ancilla register, no inverse-QPE uncomputation.

### ❌ Metadata-consistent

Inconsistencies: instance.json experiment_id='exp_1' but cohort/prompt experiment_id='exp_4'; instance.json algorithm_family='other-gate-based' while @register declares algorithm_family='hhl'; description string says 'generic variational ansatz stretch' which contradicts the hhl family tag.

## Concerns

- Implementation is explicitly a template proxy that does not implement HHL (state_prep, QPE, controlled rotation, inverse QPE all absent).
- algorithm_family mismatch between registry decorator ('hhl') and instance.json ('other-gate-based').
- experiment_id mismatch: instance.json says exp_1 but this cohort entry is exp_4 (4x4 dense symmetric matrix).
- Resource estimates from this circuit will reflect a RealAmplitudes ansatz, not an HHL circuit, so Phase-8 cost extrapolation for the HHL family will be biased downward.

## Recommendations

- Either (a) replace circuit with an HHL-shaped proxy (QPE block + controlled rotation on ancilla + inverse QPE) sized to 4 system + 3 clock + 1 ancilla qubits, or (b) reclassify SX4 cohort algorithm_family to 'other-gate-based / variational-proxy' and document that HHL family resource estimates are not derived from SX1-SX4.
- Fix instance.json experiment_id from 'exp_1' to 'exp_4' and align algorithm_family with the registry decorator.
- Note in cohort that SX1-SX4 are flagged redundant in v2 extraction; consolidate or explicitly differentiate the four matrix instances.
