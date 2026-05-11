# Faithfulness Review: SP1

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Impacting Financial Predictions & Security through Quantum Support Vector Machines, Quantum Approximate Optimization, and Quantum-Resistant Lattice Cryptography
- **Authors:** Dr Hansaraj Wankhede, Dr Vrushali Nasre, Dr Aniruddha Kailuke, Dr Kapil Gupta, Priti Kakde et al.
- **Year:** 2025
- **Paper ID:** `378c2a73ea46` · **Experiment:** `exp_1` · **Silo:** `portfolio-optimization` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/378c2a73ea46.md](p2_systematic_review/output/processed/378c2a73ea46.md)
- Circuit: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/circuit.py](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/circuit.py)
- Instance: [p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/instance.json](p4_experiments/experiments/silos/portfolio_optimization/378c2a73ea46/instance.json)

---

## Verdict summary

v2 ground truth identifies exp_1 as QAOA on a 50-asset portfolio with an Ising cost Hamiltonian, but the implemented circuit is a QSVM-style amplitude-encoding paired-inverse template proxy and is also mislabeled as SP4 with algorithm_family quantum-svm.

## Checks

### ❌ Family-faithful

Paper exp_1 (per v2) = QAOA portfolio optimization with Ising H = sum_ij J_ij Z_i Z_j + sum_i h_i Z_i and parameterized (gamma, beta) layers. Circuit implements an amplitude-encoding ansatz with an encoder . encoder^dagger paired-inverse oracle (a QSVM-kernel-style template), which is a different algorithm family. Cohort tag 'other-gate-based' is broad enough to nominally cover both, but the proxy does not represent QAOA.

### ✅ Scale-faithful

Paper does not state qubit count (NOT_STATED). Circuit uses n_qubits=5, well within the 12-qubit tractability cap; no contradictory paper number to violate the factor-of-2 rule.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit composes a parameterized amplitude encoder with computational-basis measurement; full accounting registers a paired-inverse oracle (encoder . encoder^dagger). Non-trivial as a QSVM-kernel proxy, but lacks any QAOA structure (no cost-unitary exp(-i gamma H_C) and no mixer exp(-i beta H_M) layers, no Z_iZ_j couplings).

### ❌ Metadata-consistent

instance.json and circuit.py are labeled 'SP4' (label/instance_id/name/description), and instance algorithm_family='quantum-svm' / algorithm_variant_paper='QSVM for financial classification and regression'. Cohort entry for SP1 declares algorithm_family='other-gate-based', and v2 extraction targets QAOA portfolio optimization (exp_1). Label, family tag, and variant string all disagree with the cohort/v2 record.

## Concerns

- Algorithm-family mismatch: implemented proxy is QSVM-kernel amplitude-encoding paired-inverse, but v2 ground truth for exp_1 is QAOA portfolio optimization on the Ising Hamiltonian.
- Cross-label contamination: circuit.py and instance.json are stamped 'SP4' (label, instance_id 'SP4_v3_proxy_v1', register label='SP4', circuit name 'SP4_bare', algorithm_variant_paper QSVM), suggesting this artifact was authored for a different cohort entry and reused for SP1.
- v2 operator_notes explicitly flags substantive drift from the old SP1 (old=QSVM, v2=QAOA) and asks for manual canonical-experiment selection; the implemented proxy still tracks the old QSVM reading, not the v2-selected QAOA exp_1.
- No QAOA-specific structure present: no Z_iZ_j cost layer, no transverse-field mixer, no (gamma, beta) parameter pair, so Phase-8 resource extrapolation from this circuit will not represent QAOA cost.
- Paper does not specify qubit count, p-depth, mixer, shots, or optimizer; even a faithful QAOA proxy here would have to assume defaults, but the current proxy is the wrong family entirely.

## Recommendations

- Replace the SP1 circuit with a QAOA template proxy (e.g., portfolio_optimization/qaoa_ising) using a 50-node Ising-style cost Hamiltonian truncated/mapped to <=12 qubits and a default p (e.g., p=1 or p=2) with a transverse-field mixer.
- Fix metadata: set label='SP1', algorithm_family='quantum-optimization' (or repository's QAOA bucket) and algorithm_variant_paper='QAOA on 50-asset Ising portfolio Hamiltonian'; rename instance_id and remove SP4 stamps.
- If the canonical-experiment decision is to keep the QSVM reading instead of v2's QAOA, record that decision explicitly in DECISIONS_LOG.md and re-run the v2 extraction so the cohort ground truth and the implemented proxy agree.
