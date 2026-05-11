# Triage: SP3

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Qudit-based scalable quantum algorithm for solving the integer programming problem
- **Paper ID:** `de580e8c085e` · **Experiment:** `exp_1` · **Silo:** `portfolio-optimization` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/de580e8c085e.md](p2_systematic_review/output/processed/de580e8c085e.md)
- Circuit: [p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/circuit.py](p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/circuit.py)
- Instance: [p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/instance.json](p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/de580e8c085e.json](p3_thematic_synthesis/s2_quantitative/output/extractions/de580e8c085e.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SP3.md](../vincent/SP3.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz-compute-uncompute proxy that does not reproduce the paper's distinctive Grover-AA + QPE + controlled-rotation qudit IP structure; instance/circuit are also mislabelled as SP7.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/de580e8c085e.json](p3_thematic_synthesis/s2_quantitative/output/extractions/de580e8c085e.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Qudit-based scalable integer programming algorithm with constraint distillation, Grover amplitude amplification, and QPE-based cost maximization` |
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
| Family-faithful | ✅ | Cohort algorithm_family is the catchall 'other-gate-based' and circuit registers under the same tag, so the family bucket is technically consistent; however the paper's actual family is Grover-AA + QPE qudit, which the proxy does not reflect. |
| Scale-faithful | ✅ | Paper reports 9 qubit-equivalents (5 qudits dim 3 + 4 constraint + 4 QPE + 1 ancilla); circuit runs at 6 qubits, well within the factor-2 / cap-12 tolerance. |
| Structurally non-trivial | ❌ | Implementation is a parametrised RealAmplitudes ansatz composed with its inverse (compute-uncompute) plus measurement. There is no QPE register, no inverse QFT, no Grover/amplitude-amplification operator, no constraint-distillation 1-sparse unitary, and no controlled rotation on an ancilla — i.e., none of the structural primitives a faithful proxy for this paper would require. The accompanying notes ('paper algorithm not implemented; generic RealAmplitudes ansatz at paper-scale') confirm this. |
| Metadata-consistent | ❌ | instance.json and circuit.py are labelled 'SP7' (instance_id 'SP7_v3_proxy_v1', register label='SP7', docstring/name 'SP7_bare'/'SP7_full') while the cohort entry under audit is SP3. paper_id de580e8c085e matches, but the SP3/SP7 label mismatch is a real metadata inconsistency. |

### Concerns raised by Vincent

- Structural mismatch: ansatz-compute-uncompute proxy shares no primitives with the paper's qudit Grover-AA + QPE + controlled-rotation pipeline.
- Label mismatch: circuit and instance are tagged 'SP7' across registry label, instance_id, and circuit names, but this audit row is SP3.
- Stretch-template self-disclosure: notes explicitly state 'paper algorithm not implemented', so the proxy cannot stand in for resource estimation of the actual algorithm.
- Qudit nature of the paper (d=3 qudits) is wholly lost in the qubit ansatz proxy.

### Recommendations from Vincent

- Reconcile label_id: either rename registry/instance to SP3 or correct the cohort mapping so SP3 and SP7 do not both point at this proxy.
- If a faithful proxy is required, replace the ansatz with at least a small QPE block (Hadamards + controlled phase + inverse QFT) on a few-qubit register, optionally preceded by a toy Grover oracle, to mirror the paper's algorithm class.
- If the stretch-template proxy is intentional for resource estimation only, document this explicitly in the cohort manifest so downstream analyses do not treat the resource estimate as algorithm-faithful.

---

## DECISION (joint manual review)

```yaml
label_id: SP3
paper_id: de580e8c085e
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
