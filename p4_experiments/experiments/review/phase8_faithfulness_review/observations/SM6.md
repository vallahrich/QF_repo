# Triage: SM6

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** A quantum spectral method for simulating stochastic processes, with applications to Monte Carlo
- **Paper ID:** `8f553bfb1077` · **Experiment:** `exp_2` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/8f553bfb1077.md](p2_systematic_review/output/processed/8f553bfb1077.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json) (experiment_id `exp_2`)
- Vincent's review: [../vincent/SM6.md](../vincent/SM6.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a defensible spectral-state-prep + canonical-QAE proxy for the paper's Algorithm 6.1, but the instance.json metadata is mislabelled (identifies as SM2/exp_5 instead of SM6/exp_2) and the cohort family tag 'other-gate-based' is stale relative to the v2 oracle_structure 'amplitude_estimation'.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json) (experiment_id `exp_2`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Fractional Brownian motion spectral simulator` |
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
| Family-faithful | ✅ | Paper combines spectral fBM state prep with quantum amplitude/mean estimation (Algorithm 6.1). Circuit uses continuous_func_state_prep + canonical_qae, which matches the spectral-prep + QAE family. Cohort tag 'other-gate-based' is loose but defensible since the paper is a custom spectral pipeline rather than a textbook QAE; v2 oracle_structure='amplitude_estimation' aligns with the QAE downstream. |
| Scale-faithful | ✅ | Paper's qubit count is symbolic (O(polylog(T) + O(eps^{-1/(2H)}))), v2 num_qubits NOT_STATED. Circuit instantiates n_state=5 with 3 state-prep layers and num_eval_qubits=3 (full QAE ~ 8 qubits), well within the small-scale Phase-8 budget and consistent with the spectral encoding's claimed compactness. |
| Structurally non-trivial | ✅ | Bare circuit performs a multi-layer spectral-style state preparation and measures all qubits. Full circuit (via accounting) wraps the same state prep in canonical QAE, providing the QPE/inverse-QFT structure the paper requires for amplitude estimation. Not an empty/trivial template. |
| Metadata-consistent | ❌ | instance.json identifies itself as instance_id 'SM2_BoulandQspectral_v1', label 'SM2', experiment_id 'exp_5', and algorithm_family 'amplitude-estimation', whereas this triple is SM6 / exp_2 / cohort family 'other-gate-based'. circuit.py @register also uses label='SM2'. Same paper as SM5/SM7 (operator_notes flags redundancy), so this looks like reuse of a single SM2 artifact across SM5/SM6/SM7 rather than a logic error, but the label/experiment/family fields are not consistent with the SM6 cohort entry. |

### Concerns raised by Vincent

- instance.json label/experiment_id/instance_id refer to SM2/exp_5, not SM6/exp_2.
- circuit.py @register label is 'SM2', not 'SM6'; one circuit artifact is being shared across SM5/SM6/SM7 (operator_notes confirms redundancy).
- Cohort algorithm_family 'other-gate-based' is inconsistent with instance.json algorithm_family 'amplitude-estimation' and with v2 oracle_structure 'amplitude_estimation'.
- v2 num_qubits is NOT_STATED, so scale-faithfulness cannot be checked against a paper-reported qubit count; only consistency with the symbolic O(polylog(T)+poly(eps^{-1/(2H)})) bound is asserted.
- Bare circuit measures only the state-prep register and does not exercise QAE; QAE is only realized via the registered 'full' oracle accounting path.

### Recommendations from Vincent

- Either author distinct circuit/instance files per label (SM5/SM6/SM7) or document explicitly that one canonical SM2-family artifact is reused for all three, and align the cohort algorithm_family tag accordingly.
- Update instance.json label/experiment_id/instance_id to match the cohort entry actually being executed, or add an explicit alias map so SM6 -> SM2_BoulandQspectral_v1 is auditable.
- Reconcile cohort algorithm_family ('other-gate-based') with v2 oracle_structure ('amplitude_estimation') and instance.json ('amplitude-estimation') — pick one canonical bucket.

---

## DECISION (joint manual review)

```yaml
label_id: SM6
paper_id: 8f553bfb1077
experiment_id: exp_2
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
