# Triage: SM4

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Encoding of Probability Distributions for Quantum Monte Carlo Using Tensor Networks
- **Paper ID:** `75a7b04fa681` · **Experiment:** `exp_3` · **Silo:** `simulation-monte-carlo` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/75a7b04fa681.md](p2_systematic_review/output/processed/75a7b04fa681.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/75a7b04fa681.json](p3_thematic_synthesis/s2_quantitative/output/extractions/75a7b04fa681.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SM4.md](../vincent/SM4.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz_stretch template proxy at correct 5-qubit paper scale and matching 'other-gate-based' family bucket; defensible per methodology, but instance.json and circuit.py register the artifact under label 'SM12' rather than 'SM4', a metadata inconsistency.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/75a7b04fa681.json](p3_thematic_synthesis/s2_quantitative/output/extractions/75a7b04fa681.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `TT-cross tensor-network state preparation with interleaving quantization for multivariate distributions` |
| `num_qubits` | `10` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Cohort algorithm_family is 'other-gate-based' (catch-all bucket for the paper's TT-cross + per-core SVD UnitaryGate state-prep, which is non-variational and not in any standard family). Circuit registers under same 'other-gate-based' tag; using a generic ansatz as a template proxy is the explicit methodology for this bucket. |
| Scale-faithful | ✅ | v2 num_qubits=5 (IBM Eagle R3 5-qubit hardware run); circuit n_qubits=5 from instance.parameters. Exact scale match, well within factor-of-2 and below the 12-qubit cap. |
| Structurally non-trivial | ✅ | Bare circuit is a 5-qubit RealAmplitudes ansatz with 3 reps and linear entanglement (non-trivial parameterised entangling structure). Full circuit composes ansatz with its inverse (compute-uncompute proxy oracle) and measures all qubits. Acceptable as a template proxy; it does NOT implement TT-cross/SVD UnitaryGate state-prep, which is expected for a v5 stretch proxy. |
| Metadata-consistent | ❌ | instance.json 'instance_id'='SM12_v5_proxy_v1' and 'label'='SM12'; circuit.py @register(label='SM12', ...) and register_accounting(label='SM12', ...). Audit target label_id is SM4. The instance 'notes' field also explains this is a v5 extra-experiment proxy and that the covered v2/v3/v4 label for this paper_id is a different experiment row, which is consistent with SM4 being the v2-canonical label for paper 75a7b04fa681 exp_3 while the proxy artifact was authored under the SM12 v5 label. paper_id and experiment_id match correctly. |

### Concerns raised by Vincent

- Label mismatch: artifact registered as 'SM12' but audited as label_id 'SM4' (same paper_id/experiment_id, different label generation).
- Circuit is a generic RealAmplitudes ansatz proxy and does not implement the paper's TT-cross + per-core SVD UnitaryGate state-preparation algorithm; acceptable per template-proxy methodology but should not be interpreted as a re-implementation of the paper's algorithm.
- Compute-uncompute proxy oracle is a generic placeholder and bears no relation to QMC amplitude-estimation oracles or to the TT-mapped state-prep unitary; resource counts will reflect ansatz complexity, not the paper's TT-circuit depth claims.

### Recommendations from Vincent

- Document the SM4<->SM12 label aliasing in the cohort/label registry so resource-estimate roll-ups attribute the run to the canonical SM4 label.
- If higher fidelity to the paper is desired later, replace ansatz_stretch with a UnitaryGate-based state-prep proxy seeded from a TT-cross approximation of a log-normal PDF on 5 qubits; otherwise retain the generic proxy and flag in the Phase-8 readout that SM4 is a template-proxy row, not a paper-faithful row.

---

## DECISION (joint manual review)

```yaml
label_id: SM4
paper_id: 75a7b04fa681
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
