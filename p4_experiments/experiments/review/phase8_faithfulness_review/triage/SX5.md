# Triage: SX5

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Heavy-tailed Bandits
- **Paper ID:** `a2b747cae698` · **Experiment:** `exp_1` · **Silo:** `other` · **Cohort algorithm family:** `amplitude-estimation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/a2b747cae698.md](p2_systematic_review/output/processed/a2b747cae698.md)
- Circuit: [p4_experiments/experiments/silos/other/a2b747cae698/circuit.py](p4_experiments/experiments/silos/other/a2b747cae698/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/a2b747cae698/instance.json](p4_experiments/experiments/silos/other/a2b747cae698/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json](p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/SX5.md](../vincent/SX5.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Acknowledged template proxy (RealAmplitudes ansatz + inverse) for a purely theoretical heavy-tailed bandits paper with no implemented circuit; family tag aligns with cohort but circuit lacks AE structure, and metadata is internally inconsistent (registered label 'SX1' instead of SX5; instance.json algorithm_family='qaoa' contradicts cohort 'amplitude-estimation').

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json](p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `amplitude-estimation` |
| `algorithm_variant` | `Quantum Truncated Mean Estimator (QTME) built on Quantum Basic Mean Estimator (QBME) and Quantum Monte Carlo Mean Estimator` |
| `num_qubits` | _(not extracted in P3 S2)_ |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Cohort family is amplitude-estimation and the @register decorator tags the circuit as amplitude-estimation, but the implementation is a generic RealAmplitudes ansatz with a compute-uncompute pair, not an AE/QPE/Grover-style structure. The paper itself only simulates AE outputs classically (no implementable AE circuit is described), so a generic ansatz proxy is acceptable per methodology, but it is not family-faithful in a structural sense. |
| Scale-faithful | ✅ | v2 extraction reports num_qubits as NOT_STATED (paper has no implemented circuit, only theoretical / classically-simulated AE oracles), so no paper-side scale to drift from. Implemented n_qubits=5 is well within the <=12 tractability cap. |
| Structurally non-trivial | ✅ | Bare circuit is RealAmplitudes(n=5, reps=3, linear) and full circuit is ansatz . ansatz^dagger with measurement; non-trivial parameter count and entanglement, even though it does not encode AE-specific subcomponents (no QFT, no Grover oracle). |
| Metadata-consistent | ❌ | Multiple metadata defects: (1) the @register decorator and register_accounting both label this circuit 'SX1' rather than 'SX5', and the docstring/circuit names use 'SX1'; (2) instance.json sets instance_id='SX1_v3_proxy_v1', label='SX1', and algorithm_family='qaoa', which contradicts both the cohort algorithm_family='amplitude-estimation' and the @register algorithm_family='amplitude-estimation'; (3) algorithm_variant_paper in instance.json correctly names QTME/Heavy-QUCB but the family bucket disagrees. |

### Concerns raised by Vincent

- Circuit and instance files are tagged with label 'SX1' instead of 'SX5'; appears to be a copy-paste artifact across the SX cohort.
- instance.json algorithm_family='qaoa' is inconsistent with the cohort's 'amplitude-estimation' family and with the circuit registry tag.
- Implementation is a generic RealAmplitudes ansatz proxy and does not contain any amplitude-estimation structure (no QPE, no Grover oracle, no inverse QFT); resource estimates from this circuit will not reflect QTME/AE costs.
- Paper provides no concrete circuit (purely theoretical with classical simulation of AE output distribution), so any Phase-8 cost extrapolation from this proxy must be flagged as not paper-derived.

### Recommendations from Vincent

- Rename register/register_accounting label and instance_id/label fields from 'SX1' to 'SX5' to match the cohort identifier.
- Set instance.json algorithm_family to 'amplitude-estimation' to match the cohort and the @register tag.
- If a more faithful AE proxy is desired, replace the RealAmplitudes compute-uncompute with a Montanaro-style amplitude-estimation template (state prep + Grover operator + inverse QFT) at small qubit count; otherwise keep the explicit 'template_proxy' note in downstream Phase-8 reporting.

---

## DECISION (joint manual review)

```yaml
label_id: SX5
paper_id: a2b747cae698
experiment_id: exp_1
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: accept_vincent
  rationale: |
    Accept Vincent's DRIFT_MINOR assessment.

    Phase 3 is faithful to the paper at the algorithm level. The paper studies quantum multi-armed bandits and stochastic linear bandits with heavy-tailed rewards. Its key primitive is the Quantum Truncated Mean Estimator (QTME), built from the Quantum Basic Mean Estimator (QBME), which itself invokes a Quantum Monte Carlo Mean Estimator based on quantum reward oracles. The paper then uses QTME inside Heavy-QUCB and Heavy-QLinUCB to obtain improved regret bounds.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and measurement. This is not structurally faithful to the paper's amplitude-estimation / quantum-mean-estimation family. It has no quantum reward oracle, no amplitude-estimation or quantum Monte Carlo estimator structure, no Grover/amplitude-amplification iterate, no QPE/inverse-QFT-style estimation register, and no truncation-bin logic corresponding to QBME/QTME.

    However, the drift is minor rather than major because the paper is primarily theoretical and oracle-model based. It does not provide a concrete gate-level circuit, qubit count, depth, or implementation-ready amplitude-estimation circuit. Therefore, a small ansatz_stretch circuit can be retained as a disclosed template proxy, but it must not be interpreted as a family-faithful QTME/QAE implementation.

    The main non-negotiable issue is metadata consistency. The pasted review indicates that circuit.py and instance.json are labelled SX1 rather than SX5, and that instance.json sets algorithm_family='qaoa' while the cohort and circuit registry use amplitude-estimation. Those fields must be corrected before any downstream accounting.
  evidence_section: >
    PDF page 1, Abstract: the paper studies quantum multi-armed bandits and stochastic linear bandits with heavy-tailed rewards and proposes a new quantum mean estimator based on the Quantum Monte Carlo Mean Estimator.
    PDF pages 2-3, Contributions and Table 1: the paper states that QTME gives a quadratic improvement in estimation error and is used to obtain improved regret bounds for quantum heavy-tailed MAB and SLB.
    PDF page 3, Section 3.1: the paper defines the quantum oracle OY and reviews the Quantum Monte Carlo Mean Estimator, which queries OY and OY^\dagger and is the amplitude-estimation-like primitive underlying the later estimator.
    PDF pages 4-5, Section 4: Algorithm 1 defines QBME by dividing the interval [0,B] into segments and invoking QME on each segment; Algorithm 2 defines QTME by estimating positive and negative truncated parts separately.
    PDF page 5, Theorem 3 and Remark 1: the paper states that QTME achieves a quadratically improved heavy-tailed mean-estimation rate relative to the classical setting.
    PDF pages 5-7, Sections 5-6: Heavy-QUCB and Heavy-QLinUCB use QTME inside UCB-style bandit algorithms; the paper reports regret improvements for quantum heavy-tailed MAB and SLB.
    PDF page 7, Figure 1 and Experiments: the experiments compare Heavy-QUCB against robust UCB, but they simulate algorithmic regret behavior rather than providing a gate-level quantum circuit.
  remediation:
    template: ansatz_stretch
    n_qubits: 5
    notes: |
      Required immediate fixes:
      - Rename all SX1 references in circuit.py and instance.json to SX5.
      - Align @register(label=...), register_accounting(label=...), circuit names, function names, module docstring, instance_id, and instance label with SX5.
      - Set instance.json algorithm_family to amplitude-estimation, not qaoa.
      - Keep paper_id=a2b747cae698 and experiment_id=exp_1.

      Faithfulness status:
      - Keep SX5 as DRIFT_MINOR / template-proxy.
      - Do not treat the current RealAmplitudes circuit as a faithful QTME, QBME, QME, or amplitude-estimation implementation.
      - Mark the implementation as a resource-only ansatz_stretch proxy for a theoretical oracle-model paper.

      Optional stronger remediation:
      - Replace ansatz_stretch with a qae_proxy / quantum-mean-estimation proxy.
      - Include a reward-oracle placeholder O_i or O_Y.
      - Include an amplitude-estimation-like structure: state preparation, Grover/amplitude-amplification operator or controlled oracle calls, an estimation register, inverse QFT or iterative estimation surrogate, and measurement.
      - Add a small truncation-bin structure or accounting note to represent QBME/QTME's segmented estimation over [0,B].
      - Keep n_qubits=5 unless a later implementation source provides a concrete qubit count.

      Aggregation guidance:
      - Include SX5 only in template-proxy or weak-faithfulness aggregates unless reauthored with a QAE/QME structure.
      - Exclude the current RealAmplitudes proxy from headline claims about concrete amplitude-estimation resource costs.
      - Treat the paper as amplitude-estimation / quantum-mean-estimation at the paper level, but treat the current implementation as non-structural until reauthored.
```
