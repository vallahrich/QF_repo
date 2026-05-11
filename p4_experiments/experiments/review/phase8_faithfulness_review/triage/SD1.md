# Triage: SD1

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Efficient Hamiltonian Simulation for Solving Option Price Dynamics
- **Paper ID:** `0608ad48d5b8` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Cohort algorithm family:** `quantum-simulation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/0608ad48d5b8.md](p2_systematic_review/output/processed/0608ad48d5b8.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/circuit.py](p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/instance.json](p4_experiments/experiments/silos/derivative_pricing/0608ad48d5b8__exp_1/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/0608ad48d5b8.json](p3_thematic_synthesis/s2_quantitative/output/extractions/0608ad48d5b8.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SD1.md](../vincent/SD1.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes compute-uncompute ansatz at the paper's 9-qubit scale, which does not represent the paper's QSP/qubitization Hamiltonian-simulation algorithm class.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/0608ad48d5b8.json](p3_thematic_synthesis/s2_quantitative/output/extractions/0608ad48d5b8.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `quantum-simulation` |
| `algorithm_variant` | `Hamiltonian simulation of Black-Scholes dynamics with quantum signal processing and unitary dilation` |
| `num_qubits` | `9` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Paper algorithm family is Hamiltonian simulation via Quantum Signal Processing / qubitization with unitary dilation, QFT diagonalization of the momentum operator, and post-selection on an embedding ancilla. The implemented circuit is a generic linear-entanglement RealAmplitudes variational ansatz followed by its inverse (compute-uncompute) — a variational-ansatz family, not a Hamiltonian-simulation primitive. Cohort/registry tag 'quantum-simulation' matches the paper, but the actual circuit body does not. |
| Scale-faithful | ✅ | Implemented n_qubits=9 matches v2_extraction.circuit.num_qubits=9 (8 spatial + 1 embedding ancilla + 1 duplication qubit collapsed into the same 9-qubit register). Exact match, well within the factor-of-2 tolerance. |
| Structurally non-trivial | ❌ | A faithful Hamiltonian-simulation/QSP circuit would contain QFT (and inverse QFT) blocks for momentum diagonalization, block-encoding/qubitization or QSP-style controlled rotations, an embedding ancilla actually used for unitary dilation, and post-selection/measurement on that ancilla. The circuit contains none of these structural markers — only RealAmplitudes Ry layers with linear CX entanglement, then its inverse, then a full-register computational measurement. The compute-uncompute pair makes the bare oracle action approximately identity on the seeded parameters, providing no algorithmic content beyond the ansatz template. |
| Metadata-consistent | ✅ | instance.json and circuit.py both explicitly and consistently disclose the proxy status (instance notes 'does NOT implement the paper's algorithm'; circuit docstring repeats 'template-proxy methodology'; oracle_variant='ansatz-compute-uncompute-template-proxy'). n_qubits, paper_id, label, silo, and algorithm_family tags are internally consistent across cohort/instance/circuit registry. |

### Concerns raised by Vincent

- family_drift: paper is QSP/qubitization Hamiltonian simulation; proxy is a variational RealAmplitudes ansatz — different algorithmic families despite sharing the 'quantum-simulation' silo tag.
- No QFT, no block-encoding, no QSP rotation structure, and no embedding-ancilla post-selection are present, so the proxy carries none of the structural cost drivers (QSP query repetitions, controlled phase oracles) that would dominate the paper's resource profile.
- Compute-uncompute of a randomly-seeded ansatz approximates identity, so the 'full' oracle path contributes essentially no additional gate-cost-relevant structure beyond the bare ansatz.

### Recommendations from Vincent

- Ensure downstream Phase-8 reporting flags SD1 as P-tier/template-proxy and excludes it from any family-faithful headline aggregate.
- If a stronger proxy is desired without re-implementing full QSP, swap the ansatz_stretch template for a QFT-based template (QFT + diagonal phase + inverse QFT on 8 spatial qubits with a single embedding ancilla) to at least preserve the paper's structural cost drivers.

---

## DECISION (joint manual review)

```yaml
label_id: SD1
paper_id: 0608ad48d5b8
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: demote_label
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment. Phase 3 correctly identifies the paper-level algorithm family as quantum-simulation and the specific variant as Hamiltonian simulation of Black-Scholes dynamics using quantum signal processing / sparse Hamiltonian simulation, unitary dilation, QFT-based momentum diagonalization, and post-selection on an embedding ancilla.

    The paper-side extraction is well supported: the PDF explicitly maps the Black-Scholes PDE to a non-Hermitian Hamiltonian simulation problem, solves the non-Hermitian propagator through unitary dilation with one additional ancillary qubit, uses Fourier/QFT structure to diagonalize the momentum operator, and discusses QSP as the efficient Hamiltonian-simulation method. The paper also reports a 9-qubit fault-tolerant simulation with post-selection success probability above 60%.

    However, the implemented circuit described in Vincent's review is a generic RealAmplitudes variational ansatz followed by its inverse, i.e. a compute-uncompute template. That circuit does not contain the structural markers of the paper algorithm: no QFT / inverse-QFT momentum diagonalization, no QSP/qubitization oracle structure, no diagonal phase simulation of the Black-Scholes Hamiltonian, no unitary-dilation block, and no embedding-ancilla post-selection workflow. Therefore, the implementation is scale-faithful on n_qubits=9 but not family-faithful or structurally faithful.

    The correct resolution is not to relabel the paper family, because the paper is genuinely a quantum-simulation / Hamiltonian-simulation paper. The issue is that the circuit is only a template proxy. SD1 should therefore be demoted from any family-faithful headline aggregate and retained only as a P-tier/template-proxy implementation unless reauthored.
  evidence_section: >
    PDF pages 1-2, Abstract and Introduction: algorithm described as Hamiltonian simulation for Black-Scholes dynamics, using unitary dilation, QSP-compatible Hamiltonian simulation, one additional ancillary qubit, 9 total qubits, and post-selection success above 60%.
    PDF page 3, Section II.A "Embedding Protocol": non-Hermitian Black-Scholes Hamiltonian is embedded into a larger unitary operator using an ancillary qubit, with post-selection on |0E>.
    PDF pages 4-6, Sections II.B and III.B: discretized momentum operator is diagonalized through the discrete Fourier transform / QFT; the dynamics reduce to diagonal Hamiltonian simulation; QSP is presented as the efficient sparse-Hamiltonian simulation method.
    PDF page 6, Section III.C "Measurement and Post selection": measurement/post-selection on the embedding ancilla is required to recover the non-Hermitian Black-Scholes dynamics.
  remediation:
    template: qft_phase_proxy
    n_qubits: 9
    notes: |
      Keep paper_id, experiment_id, silo, and algorithm_family as quantum-simulation. Do not relabel the paper itself as variational.

      Mark the current circuit as a template/proxy with DRIFT_MAJOR. Exclude it from family-faithful Hamiltonian-simulation aggregates.

      If reauthoring is feasible, replace the RealAmplitudes compute-uncompute proxy with a minimal QFT-phase proxy: prepare/load the duplicated payoff state on the spatial register, apply QFT on the spatial qubits, apply a diagonal phase/damping proxy corresponding to the Black-Scholes momentum-space Hamiltonian, apply inverse QFT, include one embedding ancilla for unitary dilation, and post-select or measure that ancilla. This would still be a proxy, but it would preserve the paper's main structural cost drivers better than the current ansatz_stretch template.
```
