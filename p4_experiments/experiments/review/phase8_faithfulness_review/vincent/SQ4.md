# Faithfulness Review: SQ4

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Improved Financial Forecasting via Quantum Machine Learning
- **Authors:** Sohum Thakkar, Skander Kazdaghli, Natansh Mathur, Iordanis Kerenidis, André J. Ferreira–Martins et al.
- **Year:** 2024
- **Paper ID:** `2a0770a1a995` · **Experiment:** `exp_2` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `quantum-ml`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/2a0770a1a995.md](p2_systematic_review/output/processed/2a0770a1a995.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz proxy is family-faithful (quantum-ml) and within scale, but the implementation file is registered as 'SQ5' / instance is exp_1 (DPP) — same paper but different sub-experiment than the v2 extraction's exp_2 (OrthoResNN/ExpFNN); structure does not capture the paper's RBS / Hamming-weight-preserving orthogonal-layer construction, which is acceptable under the explicit template-proxy methodology.

## Checks

### ✅ Family-faithful

Cohort algorithm_family='quantum-ml' matches @register(algorithm_family='quantum-ml'); paper exp_2 is a quantum-inspired variational orthogonal NN (RBS pyramid/X/butterfly) and the proxy is a generic variational ansatz — same broad bucket.

### ✅ Scale-faithful

v2 reports 8 qubits (ibm_hanoi QNN inference); circuit instance n_qubits=6 — within a factor of 2 and below the 12-qubit tractability cap.

- `v2_n_qubits`: `8`
- `circuit_n_qubits`: `6`

### ✅ Structurally non-trivial

RealAmplitudes(reps=3, linear entanglement) plus a compute-uncompute (ansatz · ansatz†) full-oracle variant with measurement is non-trivial and parametrised; however it does NOT implement RBS / Hamming-weight-preserving gates nor a unary-loader — the paper's distinguishing structural element is missing. Acceptable under explicit ansatz_stretch template-proxy methodology.

### ❌ Metadata-consistent

Significant metadata drift: circuit.py @register label='SQ5' (not 'SQ4'); instance.json label='SQ5', experiment_id='exp_1', algorithm_family='other-gate-based', algorithm_variant_paper='quantum DPP sampling for DPP-Random Forest', paper_claimed.num_qubits=16 — these all describe the paper's exp_1 (DPP) sub-experiment, while the v2 extraction for SQ4 is exp_2 (OrthoResNN, 8q, ibm_hanoi). The operator_notes explicitly flag SQ3/SQ4/SQ5 as redundant proxies of the same paper, so this appears to be intentional reuse of the SQ5 generic-ansatz proxy to cover SQ4, but the labels are not self-consistent.

## Concerns

- circuit.py is registered with label='SQ5', not 'SQ4'
- instance.json identifies as SQ5/exp_1 (DPP, 16q paper-claimed) but is being used as the SQ4 (exp_2, OrthoResNN, 8q) proxy
- instance algorithm_family='other-gate-based' in instance.json conflicts with cohort algorithm_family='quantum-ml' and @register algorithm_family='quantum-ml'
- Proxy uses RealAmplitudes/linear entanglement; paper exp_2 uses Hamming-weight-preserving RBS gates (pyramid/X/butterfly) with unary/RY/H data loaders — none of these structural elements are present
- v2 operator_notes already flags SQ3/SQ4/SQ5 as redundant — three cohort slots backed by one paper / one circuit may inflate Phase-8 cost estimates

## Recommendations

- Either (a) rename the registered label and instance metadata to match SQ4/exp_2 (8 qubits, quantum-ml) when used as the SQ4 proxy, or (b) document in canonical/REPRODUCE.md that SQ3/SQ4/SQ5 share a single SQ5-labeled proxy circuit by design.
- If a tighter family proxy is desired for exp_2, consider an RBS-pyramid template at n=6-8 qubits (Hamming-weight preserving, parameter-count consistent with OrthoResNN's 13 trainable params) instead of generic RealAmplitudes.
- Reconcile instance.json algorithm_family='other-gate-based' vs @register algorithm_family='quantum-ml' to avoid downstream classification errors in Phase-8 aggregation.
