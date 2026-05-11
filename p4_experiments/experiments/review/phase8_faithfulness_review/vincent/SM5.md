# Faithfulness Review: SM5

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** A quantum spectral method for simulating stochastic processes, with applications to Monte Carlo
- **Authors:** Adam Bouland, Aditi Dandapani, Anupam Prakash
- **Year:** 2023
- **Paper ID:** `8f553bfb1077` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/8f553bfb1077.md](p2_systematic_review/output/processed/8f553bfb1077.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077__exp_1/instance.json)

---

## Verdict summary

Acknowledged generic RealAmplitudes template proxy for a theoretical spectral-MC paper; family bucket and scale defensible, but circuit/instance carry the SM15 label rather than SM5 and structure does not reflect QFT/QAE spectral pipeline.

## Checks

### ✅ Family-faithful

Cohort algorithm_family is 'other-gate-based' and the circuit registers under the same family. Paper itself is a QFT+QAE spectral method, but template proxy under the 'other-gate-based' bucket is permitted by methodology.

### ✅ Scale-faithful

Paper reports only asymptotic qubit bounds (NOT_STATED concretely); proxy uses n_qubits=5, well within the 12-qubit tractability cap and consistent with v5 paper_claimed=null for this experiment row.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit is a 5-qubit RealAmplitudes ansatz with linear entanglement and 3 reps; full variant adds an inverse compute-uncompute oracle pair plus measurement, so it is not empty/trivial. It does NOT implement QFT/Wiener-loader/QAE structure of the paper, but that is the explicit template-proxy methodology.

### ❌ Metadata-consistent

Task label_id is SM5 but circuit.py registers label='SM15', instance.json instance_id='SM15_v5_proxy_v1' and label='SM15'. Notes field also references SM15. This is a v5 stretch-label mismatch with the SM5 cohort entry.

## Concerns

- Circuit and instance use label 'SM15' while this audit task is label_id 'SM5' (same paper_id 8f553bfb1077, same exp_1) - label registry / cohort mapping should be reconciled.
- v2 extraction notes SM5/SM6/SM7 are 3 redundant labels for one theoretical paper; combined with SM15 stretch label, the SM-family labeling for this paper is overloaded.
- Circuit is an explicit generic ansatz proxy and does not exercise QFT, recursive RBS data loader, or QAE oracle structure that the paper's algorithm requires; resource estimates from this proxy will not reflect the paper's claimed polylog(T) + poly(eps^{-1/2H}) scaling.

## Recommendations

- Reconcile label naming: either rename the registered circuit/instance from SM15 to SM5 (or whichever canonical label the cohort uses) or document the SM5<->SM15 mapping in the cohort registry.
- If Phase-8 needs a more faithful proxy for this paper, consider a QFT-based template (e.g., QFT + amplitude-estimation skeleton) rather than a bare RealAmplitudes ansatz, while keeping qubit count <=12.
