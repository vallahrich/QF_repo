# Faithfulness Review: SQ5

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Improved Financial Forecasting via Quantum Machine Learning
- **Authors:** Sohum Thakkar, Skander Kazdaghli, Natansh Mathur, Iordanis Kerenidis, André J. Ferreira–Martins et al.
- **Year:** 2024
- **Paper ID:** `2a0770a1a995` · **Experiment:** `exp_3` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `quantum-ml`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/2a0770a1a995.md](p2_systematic_review/output/processed/2a0770a1a995.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz is a defensible quantum-ml proxy at near-paper scale, but instance.json metadata is inconsistent with the v2 extraction and with the circuit registration.

## Checks

### ✅ Family-faithful

Paper uses RBS Pyramid/X/Butterfly variational layers (quantum-ml family); circuit registers as algorithm_family='quantum-ml' and uses a parametrised variational ansatz (RealAmplitudes). Same family bucket; specific RBS Pyramid structure is not reproduced but proxy is permitted.

### ✅ Scale-faithful

Circuit uses 6 qubits; v2 reports 8 qubits for exp_3 (ibm_hanoi QNN inference). 6 vs 8 is within factor of 2 and below the 12-qubit cap.

- `v2_n_qubits`: `8`
- `circuit_n_qubits`: `6`

### ✅ Structurally non-trivial

Bare circuit is a 3-layer RealAmplitudes ansatz with linear entanglement and assigned parameters; full variant adds compute-uncompute pair and measurement. Non-trivial variational structure consistent with a QML inference proxy.

### ❌ Metadata-consistent

instance.json declares algorithm_family='other-gate-based' and algorithm_variant_paper='quantum DPP sampling for DPP-Random Forest' (the churn-side experiment), while the @register decorator and the SQ5 task here target exp_3 (the QNN inference experiment, RBS Pyramid). instance.json also gives experiment_id='exp_1' (not exp_3) and paper_claimed.num_qubits=16 (matches ibmq_guadelupe DPP work, not the 8-qubit ibm_hanoi QNN run that v2 documents).

## Concerns

- instance.json experiment_id is 'exp_1' but task and v2 target exp_3.
- instance.json algorithm_family ('other-gate-based') and algorithm_variant_paper ('quantum DPP sampling for DPP-Random Forest') describe a different experiment in the paper than the one v2 extracted (RBS Pyramid QNN inference on ibm_hanoi, 8 qubits).
- paper_claimed.num_qubits=16 in instance.json conflicts with v2 (8 qubits for exp_3); 16 corresponds to ibmq_guadelupe used for the DPP sampling experiments, not the QNN inference.
- Specific RBS Pyramid structure (28 two-qubit RBS gates, Hamming-weight preserving) is not reproduced by the generic RealAmplitudes proxy; this is acknowledged as a template-proxy stretch.

## Recommendations

- Reconcile instance.json: set experiment_id='exp_3', algorithm_family='quantum-ml', algorithm_variant_paper to the RBS Pyramid QNN inference, paper_claimed.num_qubits=8.
- Optionally bump n_qubits to 8 to match v2 exactly (still within 12-qubit cap).
- If feasible, swap RealAmplitudes for an RBS-Pyramid template to better preserve structure; otherwise keep the proxy and document the family_drift on the RBS-specific structural axis.
