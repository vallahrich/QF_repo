# Triage: ST1

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Quantitative Trading: High-Frequency Statistical Arbitrage Algorithm
- **Paper ID:** `3adb18321a79` · **Experiment:** `exp_1` · **Silo:** `trading-execution` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/3adb18321a79.md](p2_systematic_review/output/processed/3adb18321a79.md)
- Circuit: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py](p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py)
- Instance: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json](p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json](p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json) (experiment_id `exp_1`)
- Vincent's review: [../vincent/ST1.md](../vincent/ST1.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Paper proposes an HHL/QSP-based Quantum Cointegration Test with QPE measurement and qRAM amplitude encoding; the circuit is a generic 6-qubit RealAmplitudes ansatz (compute-uncompute) with no HHL/QPE/oracle structure, and metadata is internally inconsistent.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json](p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json) (experiment_id `exp_1`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `hhl` |
| `algorithm_variant` | `Variable Time Preselection Algorithm (VTPA) with Quantum Condition Number Comparison Algorithm (QCNCA)` |
| `num_qubits` | `35` |
| `ansatz` (free-text) | _(not extracted in P3 S2)_ |
| `num_layers` | _(not extracted in P3 S2)_ |
| `circuit_depth` | _(not extracted in P3 S2)_ |
| `oracle_structure` | _(not extracted in P3 S2)_ |
| `encoding` | _(not extracted in P3 S2)_ |

_Note: P3 s2_quantitative extracts paper-level algorithm and quantum-resource fields. Circuit-level details that are not in the S2 schema (e.g. `oracle_structure`, `encoding`) appear as _(not extracted in P3 S2)_ above. Vincent's per-check notes below adjudicate those fields from direct paper + circuit reading._

### Vincent's per-check notes

| Check | Result | Note |
|---|---|---|
| Family-faithful | ❌ | Cohort/decorator tag the circuit as algorithm_family='hhl' (matching the paper's HHL+qubitization+QSP/QLR pipeline), but the actual implementation is a generic variational RealAmplitudes ansatz with no HHL components (no QPE, no controlled-A, no eigenvalue inversion, no qRAM proxy). This is the explicit family_drift case called out in the rubric. |
| Scale-faithful | ✅ | Paper claims '>50 qubits' (~35 data + extras); circuit uses 6 qubits, which is within the documented 12-qubit tractability cap for the small-scale Phase-8 cohort, so scale is acceptable per methodology. |
| Structurally non-trivial | ❌ | An HHL/QLR-family proxy should exhibit QPE-shaped structure (clock register, controlled time-evolution of A, inverse QFT, conditional rotation, uncomputation). The circuit only stacks RealAmplitudes . RealAmplitudes^dagger on a single 6-qubit register and measures — a trivial compute-uncompute pair that approximates the identity and carries none of the HHL/QSP signature gates. |
| Metadata-consistent | ❌ | Internal metadata conflict: instance.json sets algorithm_family='other-gate-based' and explicitly says 'does NOT implement the paper's algorithm', while the @register decorator in circuit.py declares algorithm_family='hhl'. Cohort downstream code keys on the decorator, so the registered family overstates faithfulness. |

### Concerns raised by Vincent

- Implementation is a template proxy that is explicitly disclaimed in instance.json as not implementing the paper's algorithm, yet is registered under algorithm_family='hhl'.
- No QPE, qubitization, QSP, or qRAM-style oracle structure — none of the HHL/QLR signature components are present even at proxy scale.
- Compute-uncompute of the same RealAmplitudes block yields a near-identity unitary, so the resource profile (depth/2-qubit count) does not reflect any HHL-like cost shape.
- Discrepancy between decorator family ('hhl') and instance.json algorithm_family ('other-gate-based') will mislabel the cohort row in any per-family aggregation.

### Recommendations from Vincent

- Either (a) reclassify ST1 as a generic-ansatz proxy (set decorator algorithm_family='other-gate-based' to match instance.json and document it as a non-faithful stretch), or (b) replace the bare/oracle builders with an HHL-shaped template (small QPE register + controlled e^{iAt} mock + inverse QFT + conditional rotation + uncompute) so the proxy matches the declared family.
- Reconcile algorithm_family between circuit.py @register and instance.json before Phase-8 aggregation to avoid silently inflating HHL coverage in the family roll-ups.
- If kept as ansatz proxy, drop the redundant compose(a.inverse()) so the circuit at least exercises a non-identity unitary that is informative for resource estimation.

---

## DECISION (joint manual review)

```yaml
label_id: ST1
paper_id: 3adb18321a79
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

    Phase 3 is faithful to the paper for exp_1. The relevant paper-side algorithm is the Variable Time Preselection Algorithm (VTPA) with the Quantum Condition Number Comparison Algorithm (QCNCA). This is the preselection branch of the quantum statistical-arbitrage pipeline: it screens stock portfolios by detecting large condition numbers / small eigenvalues before the cointegration-test stage.

    The paper-side structure is not a variational ansatz. It assumes qRAM-style data loading of historical stock-price matrices, Hermitian embedding of the data matrix following the HHL strategy, simplified phase-estimation subroutines to detect eigenvalues below a threshold, clock registers C1,...,M, a stop/flag register F, and repeated QCNCA calls inside the variable-time preselection routine.

    The implemented circuit described in Vincent's review is a generic RealAmplitudes ansatz followed by its inverse and then measurement. That compute-uncompute template has none of the defining ST1 structures: no qRAM/data-loading proxy, no Hermitian matrix embedding, no phase-estimation register, no controlled exp(iAt) or block-encoding oracle, no eigenvalue-threshold comparator, no QCNCA subroutine, no clock-register sequence, and no VTPA stop/flag logic.

    The mismatch is major because the cohort family is hhl and the paper's exp_1 algorithm is explicitly a quantum-linear-systems / phase-estimation / condition-number-comparison pipeline. Registering a generic ansatz-stretch identity-like circuit as hhl would misstate family-faithful HHL coverage in downstream aggregation.

    Scale alone does not repair the drift. The paper estimates about 35 qubits for initial-state preparation and more than 50 qubits for the full VTPA/QCNC setting, while the proxy uses 6 qubits. A 6-qubit toy proxy can be acceptable under the tractability cap only if it preserves the QPE/QCNCA/VTPA skeleton. The current ansatz proxy does not.

    Metadata consistency is also broken. The pasted review indicates that instance.json records algorithm_family='other-gate-based' and explicitly says the circuit does not implement the paper algorithm, while circuit.py registers algorithm_family='hhl'. This inconsistency must be corrected before resource accounting.
  evidence_section: >
    PDF page 1, Abstract and Introduction: the paper proposes quantum algorithms for high-frequency statistical arbitrage using variable-time condition-number estimation and quantum linear regression; it identifies VTPA as the first subroutine and QCNCA as the tool for condition-number comparison.
    PDF pages 2-3, Section II.C and Section III: the paper grounds the pipeline in quantum linear regression, HHL-style Hermitian embedding, qPCA/SVD, qubitization, QSP, and qRAM-style access to historical stock-price matrices.
    PDF pages 3-4, Algorithms 1 and 2: the global statistical-arbitrage algorithms call VTPA for preselection before applying QCT to remaining portfolios.
    PDF pages 4-6, Section IV: the paper defines QCNCA and VTPA using simplified phase-estimation subroutines, eigenvalue-threshold testing, clock registers C1,...,M, and a stop/flag register F.
    PDF pages 6-7, Complexity Analysis: the paper derives the VTPA average query complexity and shows its dependence on sqrt(d), kappa_0, and log(1/epsilon).
    PDF page 9, Realistic Case Analysis: the paper estimates about log(1.2e7) + log(8000) ≈ 35 qubits for initial-state preparation and more than 50 qubits for VTPA/QCNC circuits.
  remediation:
    template: hhl_proxy
    n_qubits: 6
    notes: |
      Required immediate handling:
      - Mark the current ST1 artifact as DRIFT_MAJOR.
      - Do not treat the current RealAmplitudes compute-uncompute circuit as an HHL, QCNCA, VTPA, or condition-number-estimation implementation.
      - Exclude the current circuit from family-faithful HHL / quantum-linear-systems / trading-execution resource aggregates.

      Metadata fixes:
      - Reconcile algorithm_family between circuit.py and instance.json.
      - If the current ansatz_stretch proxy is retained temporarily, set the registered family to other-gate-based or generic-ansatz and mark proxy_faithfulness=template_only.
      - If the family remains hhl, the circuit body must be reauthored with a QPE/QCNCA/VTPA-shaped structure.

      Recommended ST1-specific remediation:
      - Use a small Hermitian matrix proxy for the portfolio/design matrix A.
      - Include a data-loading or amplitude-encoding placeholder for historical price data.
      - Add a QPE/eigenvalue register and controlled exp(iAt) or mocked controlled-U powers.
      - Add inverse-QFT / QPE uncomputation structure.
      - Add a comparator or flag ancilla representing the eigenvalue threshold test lambda < 1/kappa_0.
      - Include clock-register or sequential-threshold logic to represent the VTPA/QCNCA variable-time structure.
      - Keep n_qubits=6 only as a tractable toy skeleton; otherwise consider increasing toward the 12-qubit cap for better QPE/VTPA structural coverage.

      Aggregation guidance:
      - Treat the paper and ST1 label as hhl / quantum-linear-systems at the paper level.
      - Treat the current implementation as non-family-faithful until reauthored.
      - Deduplicate ST1/ST2 in per-paper aggregates unless they are implemented as genuinely distinct proxies for VTPA/QCNCA and QCT respectively.
```
