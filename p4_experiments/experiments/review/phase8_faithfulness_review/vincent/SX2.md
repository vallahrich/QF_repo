# Faithfulness Review: SX2

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Demonstration of quantum linear equation solver on the IBM qiskit platform
- **Authors:** Wen Ji, Xiangdong Meng
- **Year:** 2020
- **Paper ID:** `7cfdb2957f6c` · **Experiment:** `exp_2` · **Silo:** `other` · **Algorithm family:** `hhl`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/7cfdb2957f6c.md](p2_systematic_review/output/processed/7cfdb2957f6c.md)
- Circuit: [p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/circuit.py](p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/instance.json](p4_experiments/experiments/silos/other/7cfdb2957f6c__exp_2/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz compute-uncompute template; the paper implements HHL (QPE + Lookup reciprocal + inverse QPE) on a 4x4 diagonal system, so the proxy does not represent the paper's algorithm class.

## Checks

### ❌ Family-faithful

Paper algorithm is HHL (QPE-based linear-systems solver). Circuit is a variational RealAmplitudes ansatz with an ansatz-inverse compute-uncompute pair; no QPE, no eigenvalue-reciprocal rotation, no inverse QPE. instance.json explicitly tags algorithm_family='other-gate-based' while the circuit register decorator and cohort tag say 'hhl' — internal inconsistency, and neither matches the paper's HHL structure structurally.

### ✅ Scale-faithful

Paper reports 7 qubits for this 4x4 instance (2 state + 3 clock + ancillae). Circuit uses 6 qubits, within a factor of 2 and below the 12-qubit tractability cap.

- `v2_n_qubits`: `7`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

Circuit is structurally a generic variational ansatz (RealAmplitudes, linear entanglement, 3 reps) followed by its inverse. It lacks every distinguishing HHL component: no Hamiltonian-simulation block, no QPE clock register, no controlled-reciprocal rotation on an ancilla, no inverse QPE. Compute-uncompute of a parametrised ansatz with measurement at the end yields a near-trivial bit-string distribution and is not HHL-shaped.

### ❌ Metadata-consistent

instance.json algorithm_family='other-gate-based' and label='SX5' / instance_id='SX5_v5_proxy_v1', but cohort label_id is SX2 and circuit register tag is algorithm_family='hhl' with label='SX5'. Notes also state 'covered v2/v3/v4 label corresponds to a DIFFERENT experiment row of the same paper', confirming this row was not authored as a faithful HHL implementation.

## Concerns

- Family drift: HHL paper proxied by a generic variational ansatz; no QPE / reciprocal / inverse-QPE structure.
- Label mismatch: cohort label_id=SX2 but instance.json label=SX5 and circuit register label='SX5' (paper-level reuse across SX1-SX4 noted in v2 operator_notes).
- Algorithm-family tag inconsistency between instance.json ('other-gate-based') and circuit @register decorator ('hhl').
- Compute-uncompute of an ansatz with measurement is a near-identity proxy that under-represents HHL's true gate cost (Hamiltonian simulation, controlled rotations) for Phase-8 resource estimation.

## Recommendations

- Either (a) replace circuit with a small HHL skeleton at n=6-7 qubits (mock QPE on a 2-qubit state register with 3 clock qubits + 1 reciprocal ancilla), or (b) explicitly down-classify this row as a non-faithful template stretch and exclude it from family-level HHL aggregates.
- Reconcile the SX2 vs SX5 labelling and the algorithm_family tag between instance.json and circuit.py before any Phase-8 reporting that groups by family.
