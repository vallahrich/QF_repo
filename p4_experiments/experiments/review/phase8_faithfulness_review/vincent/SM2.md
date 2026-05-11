# Faithfulness Review: SM2

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Dividing quantum circuits for time evolution of stochastic processes by orthogonal series density estimation
- **Authors:** Koichi Miyamoto
- **Year:** 2025
- **Paper ID:** `623597ee0f9c` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/623597ee0f9c.md](p2_systematic_review/output/processed/623597ee0f9c.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/instance.json)

---

## Verdict summary

Circuit is a family- and structure-faithful QAE proxy for the OSDE/UBQAE paper, but the implementation file, registry label, and instance.json are all tagged 'SM3' instead of the cohort label 'SM2' under audit.

## Checks

### ✅ Family-faithful

Cohort family is amplitude-estimation; paper proposes OSDE+UBQAE/QMCI built on QAE; circuit uses canonical_qae(state_prep, num_eval_qubits) which is the right family. Modeling one OSDE inner block as state-prep + canonical QAE is a defensible proxy for the per-step UBQAE call that the paper iterates.

### ✅ Scale-faithful

Paper does not state a gate-level qubit count (numerical demo is classical emulation, v2 num_qubits=NOT_STATED). Circuit uses n_state=4 + num_eval_qubits=3 = 7 qubits, within the 12-qubit Phase-8 tractability cap and consistent with sibling SM-cohort sizing.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `7`

### ✅ Structurally non-trivial

Bare = continuous_func_state_prep (parameterized state preparation, 2 layers); full = canonical_qae composing state prep + Grover-operator powers + inverse QFT on 3 evaluation qubits. This is the canonical QAE structure the paper's UBQAE subroutine invokes per OSDE step.

### ❌ Metadata-consistent

Audit target is label_id SM2, but circuit.py @register(label='SM3', ...), accounting register_accounting(label='SM3', ...), instance.json label='SM3' / instance_id='SM3_MiyamotoOSDE_v1', and inline notes refer to 'SM3' and 'SM1 sizing'. paper_id (623597ee0f9c) and silo/family tags are correct, so this looks like a stale cohort-rename artifact rather than a wrong-paper implementation.

## Concerns

- Label/identifier drift: implementation, accounting registration, and instance.json are tagged SM3 while the cohort entry under audit is SM2 (same paper 623597ee0f9c).
- Proxy granularity: circuit models a single OSDE inner block (state-prep + one QAE), not the full N-step iterated UBQAE pipeline; tau accounting note acknowledges this is per-block, which is appropriate for a Phase-8 small-scale proxy but should not be confused with the paper's end-to-end O(sqrt(N))-depth claim.
- State preparation is a generic parameterized continuous_func_state_prep, not a Legendre-coefficient U_SP_{f_hat} oracle; this is the explicit template-proxy methodology and is acceptable, but the proxy does not exercise the OSDE-specific structure.

## Recommendations

- Reconcile the SM2 vs SM3 label across circuit_registry @register(label=...), register_accounting(label=...), instance.json (label / instance_id), and the cohort manifest so audit and execution use a single canonical id.
- Optional: in operator_notes / accounting notes, explicitly state that the per-block proxy under-represents the paper's iterated UBQAE depth, and that Phase-8 resource estimates from this circuit are per-OSDE-block, not per-end-to-end-run.
