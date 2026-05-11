# Triage: SD5

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Efficient Hamiltonian Simulation for Solving Option Price Dynamics
- **Paper ID:** `349c85ac46df` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Cohort algorithm family:** `quantum-simulation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/349c85ac46df.md](p2_systematic_review/output/processed/349c85ac46df.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/circuit.py](p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/instance.json](p4_experiments/experiments/silos/derivative_pricing/349c85ac46df/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/349c85ac46df.json](p3_thematic_synthesis/s2_quantitative/output/extractions/349c85ac46df.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SD5.md](../vincent/SD5.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz with compute-uncompute pair does not implement or structurally resemble the paper's QSP/QFT/unitary-dilation Hamiltonian-simulation algorithm; also under-scaled (6 vs 9 qubits) and metadata uses wrong label 'SD8'.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/349c85ac46df.json](p3_thematic_synthesis/s2_quantitative/output/extractions/349c85ac46df.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `quantum-simulation` |
| `algorithm_variant` | `Black-Scholes Hamiltonian simulation with unitary dilation and QFT-based diagonalization` |
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
| Family-faithful | ❌ | Cohort/registry tag is 'quantum-simulation' matching the paper's family, but the implemented circuit is a variational RealAmplitudes ansatz with compute-uncompute, which belongs to the variational-ansatz family rather than to gate-based Hamiltonian simulation (QSP/qubitization + QFT + unitary dilation). The instance.json itself flags algorithm_family as 'other-gate-based' and explicitly states 'does NOT implement the paper's algorithm'. This is a template-proxy mismatch in family terms. |
| Scale-faithful | ✅ | Paper reports 9 qubits (8 discretization + 1 dilation ancilla); circuit uses 6 qubits. 9/6 = 1.5, within the factor-of-2 tolerance, so scale is acceptable as a proxy. |
| Structurally non-trivial | ❌ | Circuit is structurally trivial as a Hamiltonian-simulation proxy: it is a RealAmplitudes ansatz composed with its inverse (U U^dagger), which collapses to the identity up to parameter assignment. There is no QFT, no diagonal momentum-phase rotation, no QSP/qubitization block, no block-encoding oracle, and no ancilla-based unitary dilation / post-selection — i.e., none of the structural components a QSP-based Black–Scholes Hamiltonian-simulation paper would use. |
| Metadata-consistent | ❌ | Identity drift: file is for label_id SD5 (paper 349c85ac46df) but the circuit's @register label, register_accounting label, function names ('SD8_bare', 'SD8_full'), docstring, description, and instance.json's instance_id ('SD8_v3_proxy_v1') and label ('SD8') all say SD8. instance.json algorithm_family ('other-gate-based') also disagrees with the registry tag ('quantum-simulation'). |

### Concerns raised by Vincent

- Label/identity mismatch throughout circuit.py and instance.json (says 'SD8', should be 'SD5').
- Algorithm_family disagreement between instance.json ('other-gate-based') and circuit registry ('quantum-simulation').
- Implemented circuit is U . U^dagger (RealAmplitudes compose inverse), which is functionally an identity proxy and carries no Hamiltonian-simulation structure.
- No QFT, no QSP/qubitization phase sequence, no block-encoding oracle, no dilation ancilla / post-selection step — all of which are central to the paper's algorithm.
- Instance is documented as a template proxy that 'does NOT implement the paper's algorithm', which is faithful documentation but means the proxy must be flagged as family/structural drift, not CONFIRMED.

### Recommendations from Vincent

- Rename all 'SD8' references in circuit.py and instance.json to 'SD5' (label, instance_id, function names, docstring, description).
- Reconcile algorithm_family: either keep 'quantum-simulation' in both registry and instance.json or downgrade both to 'other-gate-based' to match the proxy nature.
- If the cohort wants a structurally meaningful proxy, replace the RealAmplitudes-compose-inverse oracle with a small QFT + diagonal phase + inverse-QFT block on n discretization qubits plus one dilation ancilla (mirroring the paper's QFT/QSP/dilation skeleton at small scale), which is tractable at n<=8.

---

## DECISION (joint manual review)

```yaml
label_id: SD5
paper_id: 349c85ac46df
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper: the paper presents a Hamiltonian-simulation algorithm for Black-Scholes option-price dynamics. It maps the Black-Scholes PDE to a non-Hermitian Hamiltonian simulation problem, uses unitary dilation with one embedding ancilla to handle the non-unitary propagator, diagonalizes the discretized momentum operator through a Fourier/QFT transform, and identifies QSP/sparse Hamiltonian simulation as the efficient simulation primitive.

    The implemented circuit described in Vincent's review is not faithful to that algorithmic structure. A RealAmplitudes ansatz composed with its inverse is a variational/template-proxy construction, not a QSP/QFT/unitary-dilation Hamiltonian-simulation circuit. It lacks the paper's main structural components: QFT / inverse-QFT momentum-basis transformation, diagonal momentum-space phase or damping operator, QSP/qubitization oracle structure, unitary-dilation ancilla, and post-selection on the embedding qubit.

    The scale mismatch alone is not decisive because 6 qubits versus the paper's 9 qubits is within a factor-of-2 proxy tolerance. However, the family and structural mismatch is major. In addition, the metadata is internally inconsistent because the implementation is labelled as SD8 in several places although this triage item is SD5, and the instance-level algorithm_family reportedly says 'other-gate-based' while the cohort label says 'quantum-simulation'.

    Therefore the correct resolution is not to relabel the paper family. The paper remains quantum-simulation. The current circuit should either be reauthored into a structurally meaningful QFT-phase/unitary-dilation proxy or, if reauthoring is not performed, demoted to a non-family-faithful template proxy and excluded from family-faithful aggregates.
  evidence_section: >
    PDF page 1, Abstract: the paper states that it solves the Black-Scholes equation on a quantum computer by mapping it to the Schrödinger equation, embeds the non-Hermitian propagator into an enlarged Hilbert space using one additional ancillary qubit, uses efficient Hamiltonian simulation techniques such as Quantum Signal Processing, reports 9 qubits, and reports post-selection success probability above 60%.
    PDF page 2, Introduction: the paper explicitly frames the method as Hamiltonian simulation of the Black-Scholes PDE, not Monte Carlo sampling, and states that the method uses periodic boundary conditions, discrete Fourier transform diagonalization, unitary dilation, and post-selection.
    PDF page 3, Section II.A "Embedding Protocol": the non-Hermitian Black-Scholes Hamiltonian is embedded into a larger unitary operator using an ancillary qubit qE, followed by post-selection on the |0E> outcome.
    PDF pages 4-6, Sections II.B and III.B: the discretized momentum operator is diagonalized with the discrete Fourier transform / QFT, reducing the dynamics to diagonal Hamiltonian simulation; QSP is then presented as the efficient sparse-Hamiltonian simulation method.
    PDF page 6, Section III.C "Measurement and Post selection": recovery of the Black-Scholes dynamics requires measuring the embedding ancilla and discarding runs where the outcome is not |0E>.
  remediation:
    template: qft_phase_proxy
    n_qubits: 9
    notes: |
      Reauthor the circuit rather than keeping the current RealAmplitudes compute-uncompute implementation as SD5.

      Minimum metadata fixes:
      - Rename all SD8 references in circuit.py and instance.json to SD5.
      - Align instance_id, label, function names, docstring, and register_accounting labels with SD5.
      - Reconcile algorithm_family so the paper/cohort remains quantum-simulation, while the implementation is explicitly marked as a proxy if it remains approximate.

      Recommended circuit remediation:
      - Use 8 spatial/discretization qubits plus 1 embedding/dilation ancilla, matching the paper's reported 9-qubit setup.
      - Prepare or approximate the duplicated payoff state on the spatial register.
      - Apply QFT on the spatial register.
      - Apply a diagonal momentum-space phase/damping proxy for the Black-Scholes Hamiltonian.
      - Apply inverse QFT.
      - Include the embedding ancilla for unitary dilation and a post-selection/measurement path on that ancilla.

      If this reauthoring is not feasible, mark SD5 as a P-tier/template-proxy with DRIFT_MAJOR and exclude it from all family-faithful Hamiltonian-simulation headline aggregates.
```
