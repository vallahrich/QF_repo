# Faithfulness Review: SP2

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Impacting Financial Predictions & Security through Quantum Support Vector Machines, Quantum Approximate Optimization, and Quantum-Resistant Lattice Cryptography
- **Authors:** Dr Hansaraj Wankhede, Dr Vrushali Nasre, Dr Aniruddha Kailuke, Dr Kapil Gupta, Priti Kakde et al.
- **Year:** 2025
- **Paper ID:** `378c2a73ea46` · **Experiment:** `exp_3` · **Silo:** `portfolio-optimization` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/378c2a73ea46.md](p2_systematic_review/output/processed/378c2a73ea46.md)
- Circuit: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/circuit.py](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/circuit.py)
- Instance: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/instance.json](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46__exp_3/instance.json)

---

## Verdict summary

Acknowledged template-proxy stretch: paper exp_3 is QAOA portfolio optimization but circuit is a generic RealAmplitudes ansatz with compute-uncompute oracle; cohort family bucket is 'other-gate-based' so the proxy is methodologically permitted, but it is not algorithmically QAOA and internal labels say SP9.

## Checks

### ❌ Family-faithful

Paper exp_3 is QAOA over an Ising portfolio Hamiltonian (H = sum J_ij sigma_z sigma_z + sum h_i sigma_z) with mixer/cost alternation. Circuit implements a generic RealAmplitudes variational ansatz (linear entanglement) with no problem-Hamiltonian evolution and no QAOA mixer. Cohort tags this as 'other-gate-based' and instance.json explicitly declares 'generic variational ansatz stretch (template proxy)' / 'ansatz_stretch' / 'does NOT implement the paper's algorithm', so the family drift is preregistered and methodology-permitted, but it is genuine drift from the paper's QAOA.

### ✅ Scale-faithful

Paper does not state a qubit count for exp_3 (v2 num_qubits=NOT_STATED; paper itself flags qubits/p/mixer/shots as unspecified). Reported portfolio sizes are 50/100/200 assets, which would imply 50-200 qubits for a one-qubit-per-asset QAOA encoding, far above the 12-qubit tractability cap. Circuit uses n_qubits=5, ansatz_layers=3, which is within the agreed cap and is a legitimate small-scale proxy.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit is RealAmplitudes(n=5, reps=3, entanglement='linear') with random fixed-seed parameters; full circuit composes the ansatz with its inverse (compute-uncompute proxy oracle) and measures all 5 qubits. Non-empty, non-trivial gate content with parameterised single-qubit rotations and CX entanglement, consistent with the 'ansatz_stretch' template proxy contract — though it has none of QAOA's cost/mixer structure.

### ❌ Metadata-consistent

Internal labels in circuit.py and instance.json identify this artefact as 'SP9' (register(label='SP9'), instance_id='SP9_v5_proxy_v1', label='SP9'), while the cohort and audit task identify it as label_id='SP2'. Paper_id (378c2a73ea46) and experiment_id (exp_3) match. Per the v2 operator_notes, SP1/SP2/SP3 are three label rows that all map to this single multi-experiment paper, so the SP9 label appears to be a v5 stretch artefact label that has not been reconciled with the SP2 cohort identifier.

## Concerns

- Paper exp_3 algorithm (QAOA over Ising portfolio Hamiltonian) is not implemented; a generic RealAmplitudes ansatz with compute-uncompute is used as the proxy.
- Internal label mismatch: circuit/instance use label 'SP9' while the audit cohort row is 'SP2' (same paper_id and experiment_id).
- Paper does not specify qubit count, p-depth, mixer, shots, optimizer, iter, or seed for exp_3 (v2 extraction marks all as NOT_STATED), so scale-faithfulness can only be checked against the 12-qubit tractability cap.
- v2 fidelity_assessment is 'P' and operator_notes flag SP1/SP2/SP3 as three redundant labels from the same paper requiring manual triage.

## Recommendations

- Reconcile the SP9 label inside circuit.py / instance.json with the canonical SP2 label_id (or document the SP9->SP2 mapping in cohort metadata) so register() and the audit row agree.
- If exp_3 is meant to be representative of QAOA portfolio optimization, consider replacing the RealAmplitudes proxy with a small QAOA template (problem-Hamiltonian Ising layer + transverse-field mixer, p=1-2) at n_qubits<=12 to make family_faithful=true.
- Resolve the SP1/SP2/SP3 multi-label issue from the same paper as flagged in v2 operator_notes before final Phase-8 resource estimation.
