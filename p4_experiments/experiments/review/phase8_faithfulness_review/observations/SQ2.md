# Triage: SQ2

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Research on Financial Stock Market Prediction Based on the Hidden Quantum Markov Model
- **Paper ID:** `26d9ab80fc82` · **Experiment:** `exp_1` · **Silo:** `quantum-ml-finance` · **Cohort algorithm family:** `quantum-ml`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/26d9ab80fc82.md](p2_systematic_review/output/processed/26d9ab80fc82.md)
- Circuit: [p4_experiments/experiments/silos/quantum_ml_finance/26d9ab80fc82/circuit.py](p4_experiments/experiments/silos/quantum_ml_finance/26d9ab80fc82/circuit.py)
- Instance: [p4_experiments/experiments/silos/quantum_ml_finance/26d9ab80fc82/instance.json](p4_experiments/experiments/silos/quantum_ml_finance/26d9ab80fc82/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/26d9ab80fc82.json](p3_thematic_synthesis/s2_quantitative/output/extractions/26d9ab80fc82.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SQ2.md](../vincent/SQ2.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Paper is a quantum-inspired HQMM with no gate-level circuit (encoding/qubits NOT_STATED); the implementation is an explicitly-acknowledged generic RealAmplitudes ansatz template proxy in the quantum-ml family at small scale, which is a defensible proxy but with stale 'SQ8' labels and instance metadata mismatches.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/26d9ab80fc82.json](p3_thematic_synthesis/s2_quantitative/output/extractions/26d9ab80fc82.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `quantum-ml` |
| `algorithm_variant` | `Hidden Quantum Markov Model (HQMM) with Kraus-operator training; compared under even discretization and GMM+MVTF discretization` |
| `num_qubits` | `2` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Cohort and circuit register algorithm_family='quantum-ml'; instance.json declares 'other-gate-based' which is mildly inconsistent but the paper itself describes a quantum-inspired ML model (HQMM) so a quantum-ml ansatz proxy is family-appropriate. |
| Scale-faithful | ✅ | Paper does not state a circuit qubit count (NOT_STATED; quantum-inspired classical simulation with 6 hidden states and 2x2 Kraus operators implying density-matrix dim 2 ~ 1 qubit, stacked Z 12x2). Implementation uses 3 qubits, well within the factor-of-2 / cap-12 tractability allowance. |
| Structurally non-trivial | ✅ | Bare circuit is RealAmplitudes(reps=3, linear) with assigned random parameters; full variant adds an ansatz . ansatz^dagger compute-uncompute oracle proxy with measurement. Non-trivial gate structure for a generic variational template, consistent with the explicit template-proxy methodology. |
| Metadata-consistent | ❌ | Multiple stale labels: circuit.py @register and docstring use label='SQ8' (not 'SQ2'); instance.json instance_id='SQ8_v3_proxy_v1' and label='SQ8'; instance.algorithm_family='other-gate-based' contradicts the @register algorithm_family='quantum-ml'; instance.paper_claimed.num_qubits=2 vs v2 NOT_STATED. |

### Concerns raised by Vincent

- circuit.py register label is 'SQ8' but the cohort label_id is 'SQ2' (stale label leakage)
- instance.json instance_id and label are 'SQ8'/'SQ8_v3_proxy_v1', not aligned to SQ2
- instance.json algorithm_family='other-gate-based' inconsistent with @register algorithm_family='quantum-ml' and cohort.algorithm_family='quantum-ml'
- instance.paper_claimed.num_qubits=2 is asserted despite v2 extraction marking num_qubits as NOT_STATED (paper has no gate-level circuit)
- Implementation is acknowledged as not implementing the paper's HQMM/Kraus/Stiefel-manifold algorithm; it is a generic ansatz proxy, which is allowed by methodology but should remain transparently flagged

### Recommendations from Vincent

- Rename @register label and instance.json label/instance_id from 'SQ8' to 'SQ2' to eliminate stale-label drift
- Set instance.json algorithm_family to 'quantum-ml' to match the @register decorator and cohort
- Change instance.paper_claimed.num_qubits from 2 to null (or annotate NOT_STATED) to reflect the v2 ground truth
- Keep the explicit 'paper algorithm not implemented; generic RealAmplitudes ansatz at paper-scale' note in register_accounting; this transparency is correct

---

## DECISION (joint manual review)

```yaml
label_id: SQ2
paper_id: 26d9ab80fc82
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
