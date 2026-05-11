# Faithfulness Review: SM8

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum algorithm for solving McKean-Vlasov stochastic differential equations
- **Authors:** Koichi Miyamoto
- **Year:** 2025
- **Paper ID:** `e922f913e80b` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/e922f913e80b.md](p2_systematic_review/output/processed/e922f913e80b.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/instance.json)

---

## Verdict summary

QAE template proxy is family- and structure-faithful to the paper's QMCI/amplitude-estimation algorithm, but instance/circuit metadata is mislabeled as SM5 instead of SM8.

## Checks

### ✅ Family-faithful

Paper proposes QMCI (amplitude-estimation-based expectation estimation) for MVSDEs; cohort family is amplitude-estimation; circuit uses canonical_qae template wrapping a state-prep proxy. Family bucket matches.

### ✅ Scale-faithful

Paper reports no explicit qubit count (NOT_STATED — purely theoretical). Circuit uses n_state=4 + num_eval_qubits=3 (~8 qubits total via QAE), well within the <=12 tractability cap and a defensible small-scale proxy.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `8`

### ✅ Structurally non-trivial

Bare circuit performs continuous-function state prep (sim-MC style); full circuit invokes canonical_qae with state prep + num_eval_qubits=3 evaluation register, providing the QPE/inverse-QFT structure expected of a QAE proxy.

### ❌ Metadata-consistent

instance.json has instance_id 'SM5_v3_proxy_v1' and label 'SM5'; circuit.py @register/register_accounting use label='SM5' and the docstring/names reference SM5. paper_id e922f913e80b and algorithm_family amplitude-estimation are correct, but the SM5 vs SM8 label mismatch is a stale-tag bug.

## Concerns

- instance.json label='SM5' and instance_id='SM5_v3_proxy_v1' but cohort label_id is SM8.
- circuit.py registers under label='SM5' (both @register and register_accounting), so accounting/registry lookups by 'SM8' will not find this circuit.
- Paper-claimed qubit count is null/NOT_STATED, so scale-faithfulness is judged only against the <=12 tractability cap, not against an explicit paper figure.

## Recommendations

- Rename label/instance_id from SM5 to SM8 in instance.json and update label='SM5' to label='SM8' in circuit.py (@register, register_accounting, docstring, circuit names) so registry keys match the cohort label_id.
- Optionally record in operator_notes that the paper provides no circuit-level qubit count and the proxy scale (n_state=4, num_eval_qubits=3) is a tractability choice, not a paper-derived figure.
