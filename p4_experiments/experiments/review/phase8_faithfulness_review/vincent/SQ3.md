# Faithfulness Review: SQ3

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Improved Financial Forecasting via Quantum Machine Learning
- **Authors:** Sohum Thakkar, Skander Kazdaghli, Natansh Mathur, Iordanis Kerenidis, André J. Ferreira–Martins et al.
- **Year:** 2024
- **Paper ID:** `2a0770a1a995` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Algorithm family:** `quantum-ml`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/2a0770a1a995.md](p2_systematic_review/output/processed/2a0770a1a995.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz_stretch proxy is a defensible quantum-ml template at near-paper scale, but the circuit file is registered under label SQ5 (shared across SQ3/SQ4/SQ5 from the same paper) rather than SQ3, and the proxy does not reproduce the paper's RBS-Pyramid structure.

## Checks

### ✅ Family-faithful

Paper algorithm family is quantum-ml (QNN with RBS Pyramid orthogonal/compound layers); circuit is registered with algorithm_family='quantum-ml'. Family bucket matches.

### ✅ Scale-faithful

v2 num_qubits=4 (canonical reconciliation; paper hardware used 8q on ibm_hanoi); circuit n_qubits=6. Ratio 1.5x, within factor-of-2 tolerance and under the 12-qubit cap.

- `v2_n_qubits`: `4`
- `circuit_n_qubits`: `6`

### ✅ Structurally non-trivial

Bare circuit is a parametrised RealAmplitudes ansatz with linear entanglement and 3 layers; full variant adds compute-uncompute (a . a^dagger) plus measurement. This is a non-trivial parametrised proxy, but it does NOT reproduce the paper's hamming-weight-preserving RBS Pyramid (n(n-1)/2 RBS gates, depth 2n-3, unary loader). Acceptable as a generic template_proxy under the cohort methodology, but structurally a stand-in rather than a faithful reimplementation.

### ❌ Metadata-consistent

circuit.py @register(label='SQ5', ...) and instance.json label='SQ5'/instance_id='SQ5_v3_proxy_v1' with algorithm_family='other-gate-based', while this audit target is SQ3. The directory is shared across SQ3/SQ4/SQ5 (all from paper 2a0770a1a995, flagged in v2 operator_notes), but the registered label and family tag do not match SQ3 (cohort.algorithm_family='quantum-ml').

## Concerns

- Circuit file registers label='SQ5' and algorithm_family='other-gate-based' in instance.json, while the SQ3 cohort entry expects label='SQ3' and family='quantum-ml'.
- Single shared circuit at p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/ is reused for SQ3, SQ4, and SQ5 (three distinct cohort entries from the same paper); resource cost will be triple-counted unless deduplicated downstream.
- Generic RealAmplitudes ansatz does not preserve hamming weight and is not an RBS pyramid; depth and 2-qubit gate counts will not track paper formulas (Pyramid_depth=2n-3, gates=n(n-1)/2).
- instance.json paper_claimed.num_qubits=16 conflicts with v2 canonical num_qubits=4 and v2 instance_parameters.num_qubits=8 (ibm_hanoi hardware); scale baseline used by the proxy is ambiguous.

## Recommendations

- Either (a) add a label='SQ3' alias registration pointing at the same build function, or (b) author SQ3-specific instance.json/circuit.py so per-label resource accounting is unambiguous.
- Reconcile algorithm_family in instance.json ('other-gate-based') with the SQ3 cohort tag ('quantum-ml').
- Reconcile paper_claimed.num_qubits across instance.json (16), v2 canonical (4), and v2 instance_parameters (8); cite which value the proxy is targeting.
- If feasible at this scale, swap the RealAmplitudes ansatz for an RBS-pyramid template (n(n-1)/2 RBS gates) so structural faithfulness improves without leaving the template-proxy methodology.
