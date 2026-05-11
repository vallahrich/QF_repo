# Triage: SD9

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Noise-Robust Quantum Generative Models for Distribution Learning and Efficient Data Loading
- **Paper ID:** `872cedb13e27` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/872cedb13e27.md](p2_systematic_review/output/processed/872cedb13e27.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/circuit.py](p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/instance.json](p4_experiments/experiments/silos/derivative_pricing/872cedb13e27__exp_1/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/872cedb13e27.json](p3_thematic_synthesis/s2_quantitative/output/extractions/872cedb13e27.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SD9.md](../vincent/SD9.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz at the paper's 6-qubit qGAN loader scale is a defensible template proxy for the EfficientSU2 generator, but it omits the QAE oracle/QFT structure used for the pricing experiment.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/872cedb13e27.json](p3_thematic_synthesis/s2_quantitative/output/extractions/872cedb13e27.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `hybrid qGAN with WGAN-GP and MMD losses; QCNN and EfficientSU2 generator ansätze` |
| `num_qubits` | `6` |
| `ansatz` (free-text) | `QCNN; EfficientSU2` |
| `num_layers` | `8` |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Paper uses a variational qGAN loader (EfficientSU2 reps=8) plus QAE for pricing. RealAmplitudes is a reasonable variational-ansatz proxy for the EfficientSU2 generator, and the cohort family 'other-gate-based' is consistent with a hybrid qGAN+QAE workload. |
| Scale-faithful | ✅ | Circuit n_qubits=6 matches v2 num_qubits=6 (qGAN loader scale; the separate QAE pricing experiment used 10 qubits but the canonical v2 field winner is 6). |
| Structurally non-trivial | ❌ | Circuit is a parametrised RealAmplitudes(reps=3) plus an ansatz-inverse compute/uncompute pair. It is non-trivial as a variational ansatz, but it lacks the amplitude-estimation structure (Grover-style oracle + inverse QFT / QPE) that v2 lists as oracle_structure='amplitude_estimation' and measurement='QPE'. Acknowledged as a template proxy. |
| Metadata-consistent | ✅ | Cohort/instance algorithm_family='other-gate-based' matches the registered circuit; instance.notes and circuit docstring openly disclose this is an ansatz_stretch template proxy authored 2026-04-23 and does NOT implement the paper's qGAN+QAE algorithm. Random seed and parameter counts are coherent. |

### Concerns raised by Vincent

- Implementation does not reflect the paper's QAE oracle/QPE measurement structure; only the variational loader half of the pipeline is proxied.
- ansatz_layers in the circuit (reps=3) is much smaller than the paper's EfficientSU2 reps=8, so depth/parameter scaling is not representative for resource estimation.
- RealAmplitudes (RY+CX linear) differs in two-qubit-gate structure from EfficientSU2 (RY/RZ + CX full/linear), which will under-estimate 2q gate count for Phase-8 cost projection.

### Recommendations from Vincent

- If a tighter proxy is desired later, swap RealAmplitudes for EfficientSU2(reps=8) to match the paper's loader, and optionally append a small QAE block (e.g., 2-3 eval qubits + inverse QFT) to capture the measurement-side cost.
- Document in the cohort that SD9's resource estimate covers the qGAN loader only, not the QAE pricing oracle, so downstream Phase-8 totals are not misread.

---

## DECISION (joint manual review)

```yaml
label_id: SD9
paper_id: 872cedb13e27
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
