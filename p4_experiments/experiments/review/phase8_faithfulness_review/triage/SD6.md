# Triage: SD6

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum-inspired variational algorithms for partial differential equations: Application to financial derivative pricing
- **Paper ID:** `439a750eda8c` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Cohort algorithm family:** `classical-simulation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/439a750eda8c.md](p2_systematic_review/output/processed/439a750eda8c.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/circuit.py](p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/instance.json](p4_experiments/experiments/silos/derivative_pricing/439a750eda8c/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/439a750eda8c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/439a750eda8c.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SD6.md](../vincent/SD6.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Paper is a purely classical quantum-inspired VMC/NQS PDE solver with no quantum circuit; the implemented generic RealAmplitudes ansatz proxy cannot represent that algorithm, and the circuit/instance are mislabeled SD9.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/439a750eda8c.json](p3_thematic_synthesis/s2_quantitative/output/extractions/439a750eda8c.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `classical-simulation` |
| `algorithm_variant` | `Variational Monte Carlo with autoregressive neural-network quantum states; McLachlan variational principle; mesh-based PDE solver` |
| `num_qubits` | _(not extracted in P3 S2)_ |
| `ansatz` (free-text) | `autoregressive neural-network quantum state (MADE-style masked fully connected network)` |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Cohort tag and @register both say 'classical-simulation', which matches the paper's category, but the implementation is an actual quantum RealAmplitudes ansatz. The paper constructs NO quantum circuit (autoregressive MADE NQS + classical VMC + Euler TDVP step). A generic variational ansatz is not a faithful proxy for a classical NQS PDE solver; the v2 operator_notes explicitly flag this and question Tier-1 inclusion. |
| Scale-faithful | ✅ | Paper reports up to n=16 mesh-qubit-equivalents; circuit uses n_qubits=6, well within the 12-qubit tractability cap and within ~factor 2.7 of the paper value (acceptable under the cap rule). |
| Structurally non-trivial | ✅ | RealAmplitudes(reps=3, entanglement='linear') with seeded parameters and a compute-uncompute oracle variant; non-empty and gate-rich, but structurally generic (no NQS, no autoregressive sampling, no TDVP linear-system step, no Euler update — none of which are quantum-circuit constructs anyway). |
| Metadata-consistent | ❌ | instance.json uses instance_id 'SD9_v3_proxy_v1' and label 'SD9'; circuit.py docstring, @register(label='SD9'), build_bare name 'SD9_bare', full circuit name 'SD9_full', and register_accounting(label='SD9') all say SD9, but the task/cohort label is SD6 (paper_id 439a750eda8c). Also instance.json algorithm_family='other-gate-based' disagrees with cohort/circuit 'classical-simulation'. |

### Concerns raised by Vincent

- Label mismatch: every artifact (instance.json, circuit.py registrations, oracle name) is tagged SD9 while the cohort row and v2 extraction are SD6.
- instance.json algorithm_family='other-gate-based' contradicts cohort and circuit registration ('classical-simulation').
- Paper has no quantum circuit at all (quantum-inspired classical VMC with MADE NQS); a RealAmplitudes proxy is not an algorithmically meaningful representation of the paper's method.
- v2 operator_notes itself flags this paper for Tier-1 review ('should this even be in tier-1?').

### Recommendations from Vincent

- Either drop SD6 from the Tier-1 quantum-circuit cohort (recommended, consistent with v2 extractor's flag) or relabel/rebuild as an explicit classical-simulation placeholder with zero quantum gates rather than a misleading variational ansatz.
- If retained, fix the SD9->SD6 label mismatch across instance.json and circuit.py (label, registration, oracle name, instance_id) and reconcile algorithm_family in instance.json with the cohort ('classical-simulation').

---

## DECISION (joint manual review)

```yaml
label_id: SD6
paper_id: 439a750eda8c
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: demote_label
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper: the paper presents a quantum-inspired classical variational Monte Carlo method for PDEs, using neural-network quantum states, McLachlan's variational principle, autoregressive sampling, stochastic estimation of the M and V matrices, and Euler-style parameter evolution. The method is inspired by VMC/NQS and VQA literature, but the actual algorithm is a classical simulation / stochastic neural-network PDE solver, not a gate-based quantum circuit.

    The paper does use an n-qubit state-vector notation to encode a discretized mesh, but this is a representation of a classical mesh-indexed state variable, not a quantum circuit construction. The numerical implementation is based on autoregressive MADE-style neural-network quantum states, Monte Carlo sampling, per-sample gradients, local-energy estimation, and solving a classical linear system for the parameter update.

    Therefore, a generic RealAmplitudes quantum circuit with a compute-uncompute structure cannot faithfully represent the paper's algorithm. It introduces an actual quantum ansatz where the paper has none, and it lacks the paper's central components: autoregressive NQS architecture, VMC sampling from |psi_beta|^2, McLachlan/TDVP matrix construction, stochastic estimation of M and V, and Euler update of neural-network parameters.

    The metadata drift is also material. The pasted review indicates that the circuit and instance are labeled SD9 rather than SD6, and that instance.json uses algorithm_family='other-gate-based' while the cohort and paper-level extraction identify the paper as classical-simulation. This makes the current artifact unsuitable as a faithful Tier-1 quantum-circuit instance.

    The correct resolution is to demote SD6 from the quantum-circuit cohort or retain it only as an explicit classical-simulation placeholder. The paper family should remain classical-simulation. It should not be relabeled as a quantum-circuit or variational-circuit algorithm.
  evidence_section: >
    PDF page 1, Abstract: the paper describes VMC combined with neural-network quantum states for PDEs and applies it to multi-asset Black-Scholes derivative pricing.
    PDF pages 2-3, Introduction and Theory: the authors explicitly position the method as a generalization of McLachlan's variational principle for time-dependent PDEs, applicable in classical or quantum settings, and propose a VMC stochastic approximate solution method using autoregressive neural-network quantum states.
    PDF pages 4-6, Sections 2.3 and 3: the algorithm is implemented through a mesh-based encoding, autoregressive neural-network quantum state u_theta = alpha psi_beta, MADE-style conditional probabilities, pre-training, Monte Carlo estimation, per-sample gradients, and stochastic construction of M and V.
    PDF page 7, Section 3.4: parameter updates are obtained by solving the classical linear system M delta_theta = V delta_t and applying an Euler update, confirming that the operative algorithm is a classical variational simulation pipeline rather than a quantum circuit.
    PDF pages 8 and 12-13, Tables 1-4 and conclusions: the paper evaluates runtime/error of the proposed classical VMC method against forward Euler baselines and frames the contribution as a quantum-inspired training algorithm based on neural-network quantum states.
  remediation:
    template: classical_nqs_placeholder
    n_qubits: NOT_APPLICABLE
    notes: |
      Recommended resolution:
      - Remove SD6 from any Tier-1 quantum-circuit or gate-count aggregate.
      - Keep the paper-level algorithm_family as classical-simulation.
      - Do not represent this paper with a RealAmplitudes ansatz or any other gate-based proxy unless the proxy is explicitly marked as non-faithful and excluded from family-faithful results.

      If the label must remain in the registry:
      - Replace the quantum circuit with an explicit zero-gate classical-simulation placeholder.
      - Record the relevant scale as mesh-qubit-equivalent n, not physical/logical circuit qubits.
      - Use n_qubits = NOT_APPLICABLE for circuit resources, with notes that the paper reports mesh encodings up to n=16 in the numerical experiments.
      - Fix all SD9 references in circuit.py and instance.json to SD6.
      - Align instance_id, label, function names, docstring, and register_accounting labels with SD6.
      - Reconcile algorithm_family so it consistently says classical-simulation rather than other-gate-based.

      If a separate classical benchmark implementation is desired, the faithful proxy should implement the paper's NQS/VMC pipeline: MADE-style autoregressive network, sampling from |psi_beta|^2, stochastic estimation of M and V, local-energy evaluation for the PDE operator, and Euler/TDVP parameter updates.
```
