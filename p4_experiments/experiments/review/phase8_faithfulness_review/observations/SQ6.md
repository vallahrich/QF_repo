# Triage: SQ6

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum support vector data description for anomaly detection
- **Paper ID:** `2a9cd8a96604` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `quantum-ml`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/2a9cd8a96604.md](p2_systematic_review/output/processed/2a9cd8a96604.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/2a9cd8a96604/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/2a9cd8a96604.json](p3_thematic_synthesis/s2_quantitative/output/extractions/2a9cd8a96604.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SQ6.md](../vincent/SQ6.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz proxy at 6 qubits is a defensible quantum-ml stand-in for the paper's 8-qubit QCNN-based QSVDD, but does not implement QCNN convolution+pooling structure and carries stale 'SQ9' labels plus an instance-level family tag mismatch.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/2a9cd8a96604.json](p3_thematic_synthesis/s2_quantitative/output/extractions/2a9cd8a96604.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `quantum-ml` |
| `algorithm_variant` | `Quantum Support Vector Data Description (QSVDD) with QCNN ansatz` |
| `num_qubits` | `8` |
| `ansatz` (free-text) | `Quantum convolutional neural network (QCNN)` |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Cohort algorithm_family is 'quantum-ml' and the circuit is a generic variational ansatz registered under algorithm_family='quantum-ml', matching the paper's variational quantum ML (QSVDD) class. Instance.json tags algorithm_family='other-gate-based', which is a metadata inconsistency rather than a family-faithfulness failure. |
| Scale-faithful | ✅ | Paper uses 8 qubits (amplitude encoding of 16x16 = 256 amplitudes); circuit uses 6 qubits. 6 is within a factor of 2 of 8 and below the 12-qubit tractability cap. |
| Structurally non-trivial | ❌ | Circuit is RealAmplitudes(reps=3, entanglement='linear') with a compute-uncompute pair plus measurement; it is non-trivial as a generic VQC template proxy but does not exhibit the QCNN structure (hierarchical convolution + pooling, shared SU(4)-type two-qubit gates, partial-trace reduction to 2 qubits, expectation-value latent vector) that the paper's QSVDD algorithm requires. This is explicitly disclosed in the instance notes as 'template proxy' and is consistent with the cohort's preregistered template-proxy methodology. |
| Metadata-consistent | ❌ | Multiple stale identifiers: instance.json instance_id='SQ9_v3_proxy_v1' and label='SQ9'; circuit.py @register(label='SQ9'), build_bare description and accounting register all under label 'SQ9'; instance.json algorithm_family='other-gate-based' contradicts cohort algorithm_family='quantum-ml' and the registry tag. paper_id and paper_title remain consistent with SQ6's paper (2a9cd8a96604, QSVDD). |

### Concerns raised by Vincent

- Circuit/instance are registered under label 'SQ9', not 'SQ6'; a downstream lookup by 'SQ6' may miss this circuit unless a label-remap is applied.
- instance.json algorithm_family='other-gate-based' disagrees with cohort and circuit registry which use 'quantum-ml'.
- Implemented circuit (generic RealAmplitudes + compute-uncompute) does not realize the paper's QCNN convolution+pooling structure or its expectation-value latent measurement, so it cannot be used to estimate QSVDD-specific resource scaling beyond a generic VQC proxy.
- Qubit count slightly under-scaled (6 vs paper 8); within tolerance but loses the exact amplitude-encoding scale of 256 input amplitudes.

### Recommendations from Vincent

- Reconcile label_id: either rename circuit/instance from 'SQ9' to 'SQ6' or add an explicit alias so the label registry resolves SQ6 -> this artifact.
- Update instance.json algorithm_family from 'other-gate-based' to 'quantum-ml' to match the cohort and circuit registry.
- If a more faithful proxy is desired, raise n_qubits to 8 to match the paper's amplitude encoding scale (still well under the 12-qubit cap).
- Optionally swap RealAmplitudes for a minimal QCNN-shaped template (alternating two-qubit conv blocks + pooling) to preserve structural family fidelity for QSVDD-class resource estimates.

---

## DECISION (joint manual review)

```yaml
label_id: SQ6
paper_id: 2a9cd8a96604
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
