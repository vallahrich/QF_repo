# Triage: SM8

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum algorithm for solving McKean-Vlasov stochastic differential equations
- **Paper ID:** `e922f913e80b` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `amplitude-estimation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/e922f913e80b.md](p2_systematic_review/output/processed/e922f913e80b.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/e922f913e80b/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/e922f913e80b.json](p3_thematic_synthesis/s2_quantitative/output/extractions/e922f913e80b.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SM8.md](../vincent/SM8.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** QAE template proxy is family- and structure-faithful to the paper's QMCI/amplitude-estimation algorithm, but instance/circuit metadata is mislabeled as SM5 instead of SM8.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/e922f913e80b.json](p3_thematic_synthesis/s2_quantitative/output/extractions/e922f913e80b.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `amplitude-estimation` |
| `algorithm_variant` | `Quantum Monte Carlo integration (QMCI) with higher-order SDE discretization and linear extrapolation of mean-field terms` |
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
| Family-faithful | ✅ | Paper proposes QMCI (amplitude-estimation-based expectation estimation) for MVSDEs; cohort family is amplitude-estimation; circuit uses canonical_qae template wrapping a state-prep proxy. Family bucket matches. |
| Scale-faithful | ✅ | Paper reports no explicit qubit count (NOT_STATED — purely theoretical). Circuit uses n_state=4 + num_eval_qubits=3 (~8 qubits total via QAE), well within the <=12 tractability cap and a defensible small-scale proxy. |
| Structurally non-trivial | ✅ | Bare circuit performs continuous-function state prep (sim-MC style); full circuit invokes canonical_qae with state prep + num_eval_qubits=3 evaluation register, providing the QPE/inverse-QFT structure expected of a QAE proxy. |
| Metadata-consistent | ❌ | instance.json has instance_id 'SM5_v3_proxy_v1' and label 'SM5'; circuit.py @register/register_accounting use label='SM5' and the docstring/names reference SM5. paper_id e922f913e80b and algorithm_family amplitude-estimation are correct, but the SM5 vs SM8 label mismatch is a stale-tag bug. |

### Concerns raised by Vincent

- instance.json label='SM5' and instance_id='SM5_v3_proxy_v1' but cohort label_id is SM8.
- circuit.py registers under label='SM5' (both @register and register_accounting), so accounting/registry lookups by 'SM8' will not find this circuit.
- Paper-claimed qubit count is null/NOT_STATED, so scale-faithfulness is judged only against the <=12 tractability cap, not against an explicit paper figure.

### Recommendations from Vincent

- Rename label/instance_id from SM5 to SM8 in instance.json and update label='SM5' to label='SM8' in circuit.py (@register, register_accounting, docstring, circuit names) so registry keys match the cohort label_id.
- Optionally record in operator_notes that the paper provides no circuit-level qubit count and the proxy scale (n_state=4, num_eval_qubits=3) is a tractability choice, not a paper-derived figure.

---

## DECISION (joint manual review)

```yaml
label_id: SM8
paper_id: e922f913e80b
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
