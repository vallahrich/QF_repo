# Faithfulness Review: SM7

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** A quantum spectral method for simulating stochastic processes, with applications to Monte Carlo
- **Authors:** Adam Bouland, Aditi Dandapani, Anupam Prakash
- **Year:** 2023
- **Paper ID:** `8f553bfb1077` · **Experiment:** `exp_3` · **Silo:** `simulation-monte-carlo` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/8f553bfb1077.md](p2_systematic_review/output/processed/8f553bfb1077.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/instance.json)

---

## Verdict summary

Circuit is a faithful canonical-QAE proxy of the paper's spectral+amplitude-estimation algorithm, but the registered algorithm_family tag is 'other-gate-based' instead of 'amplitude-estimation', and the circuit/instance are reused from sibling label SM2 because SM7 (exp_3) has no dedicated numerical instance.

## Checks

### ✅ Family-faithful

Paper Algorithm 6.1 is QAE applied to a spectral/analog state preparation; circuit composes continuous_func_state_prep (analog amplitude encoding proxy) with canonical_qae template, matching the cohort's amplitude-estimation family and v2 oracle_structure='amplitude_estimation' / measurement='QPE'.

### ✅ Scale-faithful

Paper qubit count is NOT_STATED (theoretical, scales as O(polylog(T)+eps^{-1/2H})). Implementation uses n_state=5 + num_eval_qubits=3 = 8 qubits for the full QAE variant, well within the documented 12-qubit tractability cap.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `8`

### ✅ Structurally non-trivial

Bare circuit = spectral fBM-style state prep with 3 layers; full circuit = canonical_qae template (Grover-like operator + inverse QFT on 3 eval qubits), which is the expected QAE structure for this family.

### ❌ Metadata-consistent

circuit.py @register declares algorithm_family='other-gate-based' and label='SM2', but the cohort entry under audit is label_id='SM7' / paper experiment_id='exp_3' with cohort.algorithm_family='amplitude-estimation'. v2 operator_notes explicitly flags SM7 as redundant with SM5/SM6 and notes exp_3 has no corresponding numerical instance, so reusing the SM2 instance is the documented methodology — but the family tag in the registry is stale.

## Concerns

- Registered algorithm_family='other-gate-based' contradicts cohort tag 'amplitude-estimation' and the circuit's actual canonical_qae structure.
- Circuit/instance are physically the SM2 artefact (instance_id='SM2_BoulandQspectral_v1', exp_5); SM7's exp_3 has no dedicated instance because v2 marks it redundant with SM5/SM6.
- Paper claims (qubits/depth) are all NOT_STATED, so scale faithfulness is unfalsifiable beyond the 12-qubit tractability cap.

## Recommendations

- Update @register algorithm_family for the SM2/SM5/SM6/SM7 family from 'other-gate-based' to 'amplitude-estimation' to match cohort and v2 oracle_structure.
- Document in cohort metadata that SM7 intentionally aliases the SM2 circuit/instance per v2 redundancy note, so the SM2 label on the registered circuit is not flagged as drift in future audits.
