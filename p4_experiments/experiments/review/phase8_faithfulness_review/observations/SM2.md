# Triage: SM2

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Dividing quantum circuits for time evolution of stochastic processes by orthogonal series density estimation
- **Paper ID:** `623597ee0f9c` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `amplitude-estimation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/623597ee0f9c.md](p2_systematic_review/output/processed/623597ee0f9c.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/623597ee0f9c/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/623597ee0f9c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/623597ee0f9c.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SM2.md](../vincent/SM2.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a family- and structure-faithful QAE proxy for the OSDE/UBQAE paper, but the implementation file, registry label, and instance.json are all tagged 'SM3' instead of the cohort label 'SM2' under audit.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/623597ee0f9c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/623597ee0f9c.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `amplitude-estimation` |
| `algorithm_variant` | `QMCI with orthogonal series density estimation; unbiased QAE in the theory, random-depth QAE in the numerical simulation` |
| `num_qubits` | _(not extracted in P3 S2)_ |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Cohort family is amplitude-estimation; paper proposes OSDE+UBQAE/QMCI built on QAE; circuit uses canonical_qae(state_prep, num_eval_qubits) which is the right family. Modeling one OSDE inner block as state-prep + canonical QAE is a defensible proxy for the per-step UBQAE call that the paper iterates. |
| Scale-faithful | ✅ | Paper does not state a gate-level qubit count (numerical demo is classical emulation, v2 num_qubits=NOT_STATED). Circuit uses n_state=4 + num_eval_qubits=3 = 7 qubits, within the 12-qubit Phase-8 tractability cap and consistent with sibling SM-cohort sizing. |
| Structurally non-trivial | ✅ | Bare = continuous_func_state_prep (parameterized state preparation, 2 layers); full = canonical_qae composing state prep + Grover-operator powers + inverse QFT on 3 evaluation qubits. This is the canonical QAE structure the paper's UBQAE subroutine invokes per OSDE step. |
| Metadata-consistent | ❌ | Audit target is label_id SM2, but circuit.py @register(label='SM3', ...), accounting register_accounting(label='SM3', ...), instance.json label='SM3' / instance_id='SM3_MiyamotoOSDE_v1', and inline notes refer to 'SM3' and 'SM1 sizing'. paper_id (623597ee0f9c) and silo/family tags are correct, so this looks like a stale cohort-rename artifact rather than a wrong-paper implementation. |

### Concerns raised by Vincent

- Label/identifier drift: implementation, accounting registration, and instance.json are tagged SM3 while the cohort entry under audit is SM2 (same paper 623597ee0f9c).
- Proxy granularity: circuit models a single OSDE inner block (state-prep + one QAE), not the full N-step iterated UBQAE pipeline; tau accounting note acknowledges this is per-block, which is appropriate for a Phase-8 small-scale proxy but should not be confused with the paper's end-to-end O(sqrt(N))-depth claim.
- State preparation is a generic parameterized continuous_func_state_prep, not a Legendre-coefficient U_SP_{f_hat} oracle; this is the explicit template-proxy methodology and is acceptable, but the proxy does not exercise the OSDE-specific structure.

### Recommendations from Vincent

- Reconcile the SM2 vs SM3 label across circuit_registry @register(label=...), register_accounting(label=...), instance.json (label / instance_id), and the cohort manifest so audit and execution use a single canonical id.
- Optional: in operator_notes / accounting notes, explicitly state that the per-block proxy under-represents the paper's iterated UBQAE depth, and that Phase-8 resource estimates from this circuit are per-OSDE-block, not per-end-to-end-run.

---

## DECISION (joint manual review)

```yaml
label_id: SM2
paper_id: 623597ee0f9c
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: 
  action: 
  rationale: |
    
  evidence_section: 
  remediation:
    template:           # e.g. hhl_proxy | qae_proxy | qaoa_proxy | qft_phase_proxy | ansatz_stretch
    n_qubits:
    notes: |
      
```
