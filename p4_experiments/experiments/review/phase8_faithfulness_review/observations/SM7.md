# Triage: SM7

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** A quantum spectral method for simulating stochastic processes, with applications to Monte Carlo
- **Paper ID:** `8f553bfb1077` · **Experiment:** `exp_3` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `amplitude-estimation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/8f553bfb1077.md](p2_systematic_review/output/processed/8f553bfb1077.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/8f553bfb1077/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SM7.md](../vincent/SM7.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a faithful canonical-QAE proxy of the paper's spectral+amplitude-estimation algorithm, but the registered algorithm_family tag is 'other-gate-based' instead of 'amplitude-estimation', and the circuit/instance are reused from sibling label SM2 because SM7 (exp_3) has no dedicated numerical instance.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json](p3_thematic_synthesis/s2_quantitative/output/extractions/8f553bfb1077.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `amplitude-estimation` |
| `algorithm_variant` | `Quantum Monte Carlo with coherent analog encodings` |
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
| Family-faithful | ✅ | Paper Algorithm 6.1 is QAE applied to a spectral/analog state preparation; circuit composes continuous_func_state_prep (analog amplitude encoding proxy) with canonical_qae template, matching the cohort's amplitude-estimation family and v2 oracle_structure='amplitude_estimation' / measurement='QPE'. |
| Scale-faithful | ✅ | Paper qubit count is NOT_STATED (theoretical, scales as O(polylog(T)+eps^{-1/2H})). Implementation uses n_state=5 + num_eval_qubits=3 = 8 qubits for the full QAE variant, well within the documented 12-qubit tractability cap. |
| Structurally non-trivial | ✅ | Bare circuit = spectral fBM-style state prep with 3 layers; full circuit = canonical_qae template (Grover-like operator + inverse QFT on 3 eval qubits), which is the expected QAE structure for this family. |
| Metadata-consistent | ❌ | circuit.py @register declares algorithm_family='other-gate-based' and label='SM2', but the cohort entry under audit is label_id='SM7' / paper experiment_id='exp_3' with cohort.algorithm_family='amplitude-estimation'. v2 operator_notes explicitly flags SM7 as redundant with SM5/SM6 and notes exp_3 has no corresponding numerical instance, so reusing the SM2 instance is the documented methodology — but the family tag in the registry is stale. |

### Concerns raised by Vincent

- Registered algorithm_family='other-gate-based' contradicts cohort tag 'amplitude-estimation' and the circuit's actual canonical_qae structure.
- Circuit/instance are physically the SM2 artefact (instance_id='SM2_BoulandQspectral_v1', exp_5); SM7's exp_3 has no dedicated instance because v2 marks it redundant with SM5/SM6.
- Paper claims (qubits/depth) are all NOT_STATED, so scale faithfulness is unfalsifiable beyond the 12-qubit tractability cap.

### Recommendations from Vincent

- Update @register algorithm_family for the SM2/SM5/SM6/SM7 family from 'other-gate-based' to 'amplitude-estimation' to match cohort and v2 oracle_structure.
- Document in cohort metadata that SM7 intentionally aliases the SM2 circuit/instance per v2 redundancy note, so the SM2 label on the registered circuit is not flagged as drift in future audits.

---

## DECISION (joint manual review)

```yaml
label_id: SM7
paper_id: 8f553bfb1077
experiment_id: exp_3
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
