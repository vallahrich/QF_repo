# Triage: SX6

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Heavy-tailed Bandits
- **Paper ID:** `a2b747cae698` · **Experiment:** `exp_2` · **Silo:** `other` · **Cohort algorithm family:** `amplitude-estimation`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/a2b747cae698.md](p2_systematic_review/output/processed/a2b747cae698.md)
- Circuit: [p4_experiments/experiments/silos/other/a2b747cae698__exp_2/circuit.py](p4_experiments/experiments/silos/other/a2b747cae698__exp_2/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/a2b747cae698__exp_2/instance.json](p4_experiments/experiments/silos/other/a2b747cae698__exp_2/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json](p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json) (experiment_id `exp_2`)
- Vincent's review: [../vincent/SX6.md](../vincent/SX6.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MINOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Generic RealAmplitudes ansatz proxy at n=5 is family-stale (paper uses amplitude-estimation-based QTME, not a variational ansatz), but registry tag and scale are defensible for a template-proxy stretch row.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json](p3_thematic_synthesis/s2_quantitative/output/extractions/a2b747cae698.json) (experiment_id `exp_2`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `amplitude-estimation` |
| `algorithm_variant` | `Heavy-QUCB (quantum UCB for heavy-tailed MAB)` |
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
| Family-faithful | ❌ | Registered algorithm_family='amplitude-estimation' matches cohort and paper (QTME via amplitude estimation per Brassard et al.), but the implementation is an ansatz-compute-uncompute proxy with no QPE/inverse-QFT structure. Acknowledged as template proxy in instance.notes (algorithm_family='other-gate-based'). |
| Scale-faithful | ✅ | Paper does not state a circuit qubit count (NOT_STATED); n_qubits=5 is within the <=12 tractability cap and a reasonable default for a stretch row. |
| Structurally non-trivial | ✅ | Bare = RealAmplitudes(n=5, reps=3, linear) with assigned parameters; full = ansatz . ansatz^dagger compute-uncompute pair plus measurement. Non-trivial gate content, but lacks AE-specific structure (no Grover oracle / inverse QFT). |
| Metadata-consistent | ✅ | Registry algorithm_family='amplitude-estimation' aligns with cohort and paper methodology tags; instance.json explicitly flags it as a template proxy and labels algorithm_family='other-gate-based' for the proxy run, with notes calling out that the paper algorithm is not implemented. |

### Concerns raised by Vincent

- Implementation is a generic variational ansatz, not an amplitude-estimation circuit; family-faithfulness is only nominal.
- Paper qubit count is NOT_STATED, so scale-faithfulness cannot be quantitatively verified.
- Mismatch between registry tag ('amplitude-estimation') and instance algorithm_family ('other-gate-based') could confuse downstream aggregation.

### Recommendations from Vincent

- Either tag this row consistently as a template proxy in both registry and instance (e.g., algorithm_family='other-gate-based' with proxy_for='amplitude-estimation'), or upgrade the proxy to a minimal QAE skeleton (state-prep + Grover-like oracle + inverse QFT) to make the family tag literal.
- Document in operator notes that SX5/SX6/SX7 share paper a2b747cae698 and use proxies of differing fidelity.

---

## DECISION (joint manual review)

```yaml
label_id: SX6
paper_id: a2b747cae698
experiment_id: exp_2
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: accept_vincent
  rationale: |
    Accept Vincent's DRIFT_MINOR assessment.

    Phase 3 is faithful to the paper for exp_2. The relevant paper-side algorithm is Heavy-QUCB, a quantum UCB algorithm for heavy-tailed multi-armed bandits. Heavy-QUCB is built on the Quantum Truncated Mean Estimator (QTME), which itself is built from the Quantum Basic Mean Estimator (QBME) and Quantum Monte Carlo Mean Estimator (QME). The method assumes quantum reward oracles and uses QTME to estimate arm means inside a phased/doubling UCB framework.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and measurement. This is not structurally faithful to Heavy-QUCB or to the amplitude-estimation / quantum-mean-estimation primitive behind it. It has no quantum reward oracle, no QME/QTME structure, no Grover/amplitude-amplification iterate, no QPE or inverse-QFT-style estimation register, and no truncation-bin logic corresponding to QBME/QTME.

    However, the drift is minor rather than major because the paper is primarily theoretical and oracle-model based. It does not provide a concrete gate-level Heavy-QUCB or QTME circuit, qubit count, depth, oracle decomposition, or implementation-ready QAE circuit. Therefore, the current circuit may be retained as an explicitly disclosed ansatz_stretch template proxy, but it must not be interpreted as a family-faithful amplitude-estimation implementation.

    Metadata is acceptable at the cohort level if the registry remains amplitude-estimation and the instance clearly flags the circuit as a proxy. However, the registry/instance distinction should be documented carefully: the paper family is amplitude-estimation / quantum-mean-estimation, while the implemented proxy body is generic ansatz_stretch.
  evidence_section: >
    PDF page 1, Abstract: the paper studies quantum multi-armed bandits and stochastic linear bandits with heavy-tailed rewards and proposes a new quantum mean estimator based on the Quantum Monte Carlo Mean Estimator.
    PDF pages 2-3, Contributions and Table 1: the paper states that QTME gives a quadratic improvement in estimation error and is used to obtain improved regret bounds for quantum heavy-tailed MAB and SLB.
    PDF page 3, Section 3.1: the paper defines the quantum oracle OY and reviews the Quantum Monte Carlo Mean Estimator, which queries OY and OY^\dagger and is the amplitude-estimation-like primitive underlying the later estimator.
    PDF pages 4-5, Section 4: Algorithm 1 defines QBME by dividing the interval [0,B] into segments and invoking QME on each segment; Algorithm 2 defines QTME by estimating positive and negative truncated parts separately.
    PDF page 5, Section 5 and Algorithm 3: the paper defines Heavy-QUCB, which selects arms through a UCB rule and updates arm means by running QTME on the selected arm's quantum reward oracle.
    PDF page 6, Theorem 4: the paper proves the Heavy-QUCB regret bound O(u^{1/(1+v)} K T^{(1-v)/(1+v)} log T), showing that exp_2 is the quantum heavy-tailed MAB/UCB algorithm rather than a gate-level ansatz experiment.
    PDF page 7, Figure 1 and Experiments: the experiments compare Heavy-QUCB against robust UCB using simulated regret curves, but they do not provide a concrete quantum circuit implementation.
  remediation:
    template: ansatz_stretch
    n_qubits: 5
    notes: |
      Recommended immediate handling:
      - Keep SX6 as DRIFT_MINOR / template-proxy.
      - Do not treat the current RealAmplitudes circuit as a faithful Heavy-QUCB, QTME, QBME, QME, or amplitude-estimation implementation.
      - Keep paper_id=a2b747cae698 and experiment_id=exp_2.

      Metadata:
      - Keep the paper/cohort family as amplitude-estimation, because Heavy-QUCB depends on QTME/QME and quantum reward oracles.
      - If instance.json uses algorithm_family='other-gate-based' for the implementation body, document this as proxy_family rather than paper_family.
      - Add an explicit proxy_for='amplitude-estimation / quantum-mean-estimation / Heavy-QUCB' note if the schema supports it.
      - Avoid counting this artifact as a family-faithful QAE implementation unless reauthored.

      Optional stronger remediation:
      - Replace ansatz_stretch with a qae_proxy / quantum-mean-estimation proxy.
      - Include a reward-oracle placeholder O_i for a selected arm.
      - Include amplitude-estimation-like structure: state preparation, controlled oracle calls or Grover/amplitude-amplification iterate, an estimation register, inverse QFT or iterative estimation surrogate, and measurement.
      - Add a small truncation-bin or segmented-estimation accounting path to represent QBME/QTME.
      - Add a UCB-level wrapper note indicating that Heavy-QUCB repeatedly invokes QTME across arms and epochs, rather than being a single standalone circuit.
      - Keep n_qubits=5 unless a later implementation source provides a concrete qubit count.

      Aggregation guidance:
      - Include SX6 only in template-proxy or weak-faithfulness aggregates.
      - Exclude the current RealAmplitudes proxy from headline claims about concrete amplitude-estimation or QTME resource costs.
      - Deduplicate SX5/SX6/SX7 in per-paper aggregation unless each label is implemented as a distinct proxy for QTME, Heavy-QUCB, and Heavy-QLinUCB respectively.
```
