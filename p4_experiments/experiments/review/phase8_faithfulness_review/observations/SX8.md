# Triage: SX8

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Attacks on Bitcoin, and How to Protect Against Them
- **Paper ID:** `cd9329dc38ef` · **Experiment:** `exp_3` · **Silo:** `cryptography-security` · **Cohort algorithm family:** `other-gate-based`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/cd9329dc38ef.md](p2_systematic_review/output/processed/cd9329dc38ef.md)
- Circuit: [p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/circuit.py](p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/instance.json](p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/cd9329dc38ef.json](p3_thematic_synthesis/s2_quantitative/output/extractions/cd9329dc38ef.json) (experiment_id `exp_3`)
- Vincent's review: [../vincent/SX8.md](../vincent/SX8.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz_stretch template proxy stands in for a Shor-ECDLP resource-estimation paper; under the explicit template-proxy methodology this is acceptable but the circuit does not implement Shor/QPE structure.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/cd9329dc38ef.json](p3_thematic_synthesis/s2_quantitative/output/extractions/cd9329dc38ef.json) (experiment_id `exp_3`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `other-gate-based` |
| `algorithm_variant` | `Shor algorithm for elliptic-curve discrete logarithm problem` |
| `num_qubits` | `2330` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ✅ | Paper algorithm is Shor-ECDLP (QFT/QPE-based). Cohort tags algorithm_family='other-gate-based' and the circuit is an explicit ansatz_stretch template proxy. Per the methodology, generic-ansatz proxies for resource-estimation-only papers are allowed, but family is not Shor-specific - flagged as borderline. |
| Scale-faithful | ✅ | Paper claims 2334 logical qubits; circuit uses 12 qubits, which is the explicit Phase-8 tractability cap. |
| Structurally non-trivial | ✅ | RealAmplitudes(reps=3, linear entanglement) plus compute-uncompute pair with measurement; well-formed parametrised ansatz, not empty or trivial. |
| Metadata-consistent | ✅ | instance.json, circuit.py decorator, v2 extraction, and authoring metadata all agree on label_id=SX8, paper_id=cd9329dc38ef, exp_3, n_qubits=12, ansatz_layers=3, template=ansatz_stretch, and explicitly note the proxy does NOT implement the paper's algorithm. |

### Concerns raised by Vincent

- Paper is a Shor-ECDLP / Grover-SHA256 resource estimation; circuit family tag 'other-gate-based' obscures that the paper's actual algorithms are Shor (QFT/QPE) and Grover.
- Circuit contains no QPE-shaped structure, modular-arithmetic oracle, or Grover oracle - it cannot inform a Shor-ECDLP resource estimate beyond a generic small-ansatz baseline.
- Paper-claimed scale (2334 logical qubits, 1.28e11 Toffoli) is ~194x larger in qubits than the proxy; extrapolation from 12-qubit ansatz to paper-scale will be model-driven rather than circuit-driven.

### Recommendations from Vincent

- Document explicitly in the cohort that SX8 is a resource-estimation paper with no implementable circuit; the proxy is a placeholder for slot-counting only.
- Consider tagging algorithm_family as 'shor-ecdlp' or 'resource-estimation-proxy' so downstream Phase-8 analysis can group it correctly rather than mixing it into 'other-gate-based'.

---

## DECISION (joint manual review)

```yaml
label_id: SX8
paper_id: cd9329dc38ef
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
