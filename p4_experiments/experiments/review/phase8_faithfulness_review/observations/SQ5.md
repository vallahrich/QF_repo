# Triage: SQ5

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Improved Financial Forecasting via Quantum Machine Learning
- **Paper ID:** `2a0770a1a995` · **Experiment:** `exp_3` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `quantum-ml`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/2a0770a1a995.md](p2_systematic_review/output/processed/2a0770a1a995.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a0770a1a995/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json](p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SQ5.md](../vincent/SQ5.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz is a defensible quantum-ml proxy at near-paper scale, but instance.json metadata is inconsistent with the v2 extraction and with the circuit registration.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json](p3_thematic_synthesis/s2_quantitative/output/extractions/2a0770a1a995.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `quantum-ml` |
| `algorithm_variant` | `Hardware inference of OrthoResNN and ExpFNN using semi-diagonal/H loaders with X circuit` |
| `num_qubits` | `8` |
| `ansatz` (free-text) | `semi-diagonal loader + X circuit; Hadamard loader + X circuit` |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Paper uses RBS Pyramid/X/Butterfly variational layers (quantum-ml family); circuit registers as algorithm_family='quantum-ml' and uses a parametrised variational ansatz (RealAmplitudes). Same family bucket; specific RBS Pyramid structure is not reproduced but proxy is permitted. |
| Scale-faithful | ✅ | Circuit uses 6 qubits; v2 reports 8 qubits for exp_3 (ibm_hanoi QNN inference). 6 vs 8 is within factor of 2 and below the 12-qubit cap. |
| Structurally non-trivial | ✅ | Bare circuit is a 3-layer RealAmplitudes ansatz with linear entanglement and assigned parameters; full variant adds compute-uncompute pair and measurement. Non-trivial variational structure consistent with a QML inference proxy. |
| Metadata-consistent | ❌ | instance.json declares algorithm_family='other-gate-based' and algorithm_variant_paper='quantum DPP sampling for DPP-Random Forest' (the churn-side experiment), while the @register decorator and the SQ5 task here target exp_3 (the QNN inference experiment, RBS Pyramid). instance.json also gives experiment_id='exp_1' (not exp_3) and paper_claimed.num_qubits=16 (matches ibmq_guadelupe DPP work, not the 8-qubit ibm_hanoi QNN run that v2 documents). |

### Concerns raised by Vincent

- instance.json experiment_id is 'exp_1' but task and v2 target exp_3.
- instance.json algorithm_family ('other-gate-based') and algorithm_variant_paper ('quantum DPP sampling for DPP-Random Forest') describe a different experiment in the paper than the one v2 extracted (RBS Pyramid QNN inference on ibm_hanoi, 8 qubits).
- paper_claimed.num_qubits=16 in instance.json conflicts with v2 (8 qubits for exp_3); 16 corresponds to ibmq_guadelupe used for the DPP sampling experiments, not the QNN inference.
- Specific RBS Pyramid structure (28 two-qubit RBS gates, Hamming-weight preserving) is not reproduced by the generic RealAmplitudes proxy; this is acknowledged as a template-proxy stretch.

### Recommendations from Vincent

- Reconcile instance.json: set experiment_id='exp_3', algorithm_family='quantum-ml', algorithm_variant_paper to the RBS Pyramid QNN inference, paper_claimed.num_qubits=8.
- Optionally bump n_qubits to 8 to match v2 exactly (still within 12-qubit cap).
- If feasible, swap RealAmplitudes for an RBS-Pyramid template to better preserve structure; otherwise keep the proxy and document the family_drift on the RBS-specific structural axis.

---

## DECISION (joint manual review)

```yaml
label_id: SQ5
paper_id: 2a0770a1a995
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
