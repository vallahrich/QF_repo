# Triage: ST2

**Reviewers (joint):** Vincent Wallerich + Aleix Telesforo  
**Triage date:** 2026-04-25  
**Vincent verdict (first pass):** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Quantitative Trading: High-Frequency Statistical Arbitrage Algorithm
- **Paper ID:** `3adb18321a79` · **Experiment:** `exp_2` · **Silo:** `trading-execution` · **Cohort algorithm family:** `hhl`

**Sources to consult:**
- Paper markdown: [p2_systematic_review/output/processed/3adb18321a79.md](p2_systematic_review/output/processed/3adb18321a79.md)
- Circuit: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py](p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py)
- Instance: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json](p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json)
- Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini, P3 s2_quantitative): [p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json](p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json) (experiment_id `exp_2`)
- Vincent's review: [../vincent/ST2.md](../vincent/ST2.md)

---

## Disagreement

Vincent's review (first pass) flagged this label as **DRIFT_MAJOR** —
i.e. the implemented circuit does not faithfully match what the
Phase 3 LLM extraction (GPT 5.3 / GPT 5.4-mini) recorded the paper's algorithm to be.

**Vincent's verdict summary:** Circuit is a generic RealAmplitudes ansatz proxy with no HHL/QPE/block-encoding structure, and is registered under label ST1 rather than ST2; family and structural checks both fail.

## Phase 3 (LLM) extraction — values for this label

**Source:** [p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json](p3_thematic_synthesis/s2_quantitative/output/extractions/3adb18321a79.json) (experiment_id `exp_2`)  
**Models used (per source `extraction_metadata.models_used`):** `gpt-5.3` (synthesis) + `gpt-5.4-mini` (extraction steps).

| Field | Phase 3 value |
|---|---|
| `algorithm_family` | `hhl` |
| `algorithm_variant` | `Quantum Cointegration Test Algorithm (QCT) with two-stage quantum linear regression` |
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
| Family-faithful | ❌ | Cohort and paper class the algorithm as HHL/QLR with block-encoded QSP and QPE measurement; circuit implements a generic RealAmplitudes variational ansatz (compute-uncompute pair), which is not in the HHL family. Explicit template-proxy methodology, but the proxy does not preserve the HHL family bucket. |
| Scale-faithful | ✅ | v2 reports ~35 data qubits (and ~>50 total); implemented n_qubits=6 is within the project's capped-at-12 tractability rule. |
| Structurally non-trivial | ❌ | An HHL/QLR-faithful proxy would require QPE-shaped structure (controlled-U powers, inverse QFT) and/or block-encoding/qubitization primitives. The circuit contains only a parametrised RealAmplitudes ansatz and its inverse plus measurement; no QPE, no QFT, no oracle/block-encoding structure. |
| Metadata-consistent | ❌ | circuit.py registers label='ST1' (not ST2) and algorithm_family='hhl', while instance.json carries instance_id='ST1_v3_proxy_v1', label='ST1', experiment_id='exp_1', and algorithm_family='other-gate-based'. ST2 (exp_2) reuses the same shared ST1 circuit with no ST2-specific registration; family tags also disagree between circuit (hhl) and instance (other-gate-based). |

### Concerns raised by Vincent

- Generic variational ansatz used as proxy for an HHL/QLR-class algorithm; no QPE or block-encoding structure present.
- circuit.py is registered under label 'ST1' (not 'ST2') and instance.json is the ST1 instance; ST2 has no distinct circuit/instance artefact in this triple.
- Family tag inconsistency between circuit registration ('hhl') and instance.json ('other-gate-based').
- v2 operator_notes flag ST1/ST2 as redundant (same Zhuang HFT paper); no exp_2-specific implementation differentiates ST2.

### Recommendations from Vincent

- If template-proxy is retained, upgrade ST2 proxy to an HHL-shaped skeleton (QPE block: state prep + controlled-e^{iAt} powers + inverse QFT + ancilla rotation) so the family bucket is preserved.
- Author a distinct ST2 circuit.py and instance.json (label='ST2', experiment_id='exp_2'), or explicitly document ST2 as an alias of ST1 in the cohort and skip auditing it as a separate circuit.
- Reconcile algorithm_family between circuit registration and instance.json (both should read 'hhl' for this cohort entry).

---

## DECISION (joint manual review)

```yaml
label_id: ST2
paper_id: 3adb18321a79
experiment_id: exp_2
reviewers: [Vincent Wallerich, Aleix Telesforo]
reviewed_utc: 2026-04-25

# winner: 'phase3' | 'vincent' | 'merge' | 'other'
# action:  'accept_vincent' | 'reauthor_circuit' | 'demote_label' | 'relabel_family' | 'no_change'
decision:
  winner: vincent
  action: reauthor_circuit
  rationale: |
    Accept Vincent's DRIFT_MAJOR assessment.

    Phase 3 is faithful to the paper for exp_2. The paper's second main subroutine is the Quantum Cointegration Test Algorithm (QCT), which verifies whether preselected portfolios are cointegrated. QCT is built around quantum linear regression: first, QLR is used to estimate regression coefficients and construct residuals; then a second QLR is used on lagged residuals for the Augmented Dickey-Fuller-style regression. The final Dickey-Fuller statistic and critical-value comparison are classical post-processing steps.

    The paper-side algorithm is therefore an HHL / quantum-linear-regression / QSP-qubitization-derived linear-systems pipeline. It assumes qRAM-style amplitude encoding of historical price data, access to data-loading procedures, matrix inversion / pseudo-inverse machinery, and repeated regression modules. This is not a generic variational circuit.

    The implemented circuit described in Vincent's review is a RealAmplitudes ansatz followed by its inverse and then measurement. That compute-uncompute template has none of the defining ST2 structures: no amplitude-encoded price-data register, no Hermitian matrix or design-matrix embedding, no QPE register, no controlled matrix evolution, no inverse-QFT / phase-estimation uncomputation, no conditional eigenvalue-inversion rotation, no QLR block, no residual-construction path, and no second QLR block for the ADF regression.

    The mismatch is major because the cohort family is hhl and the paper's exp_2 algorithm is explicitly quantum linear regression / HHL-family. Registering an ansatz-stretch identity-like circuit as an HHL implementation would misstate family-faithful HHL coverage in downstream aggregation.

    Metadata drift is also material. The pasted review indicates that ST2 reuses a circuit and instance registered as ST1 / exp_1, while this audit item is ST2 / exp_2. The instance also reportedly says algorithm_family='other-gate-based' while the circuit decorator says 'hhl'. This must be resolved before resource accounting.
  evidence_section: >
    PDF page 1, Abstract and Introduction: the paper proposes quantum algorithms for high-frequency statistical arbitrage using variable-time condition-number estimation and quantum linear regression; it identifies QCT as the second subroutine for verifying cointegrated pairs.
    PDF pages 2-3, Section II.C and Section III: the paper introduces quantum linear regression as the primary tool, grounded in HHL, qPCA/SVD, qubitization, QSP, and CKS-style matrix inversion, then defines the statistical-arbitrage pipeline using qRAM-style data loading and HHL-style Hermitian embedding.
    PDF pages 3-4, Algorithms 1 and 2: the global trading algorithms call QCT(p) after VTPA preselection to output a cointegration flag and coefficients.
    PDF page 7, Section V "Quantum Cointegration Test" and Theorem 3: the paper defines QCT and gives the two-stage complexity expression for cointegration testing with lag-length augmented Dickey-Fuller regression.
    PDF page 7, Algorithm 3: QCT performs amplitude encoding of price data, QLR(d, delta, kappa) to derive beta, classical residual construction, lagged residual computation, a second QLR(L+1, delta', kappa') to derive gamma, and classical comparison with a critical-value table.
    PDF pages 8-9, Complexity Analysis and Realistic Case Analysis: the paper analyzes residual-generation complexity, second-regression complexity, and estimates about 35 qubits for initial-state preparation and more than 50 qubits for the full VTPA/QCNC setting.
  remediation:
    template: hhl_proxy
    n_qubits: 6
    notes: |
      Required immediate handling:
      - Mark the current ST2 artifact as DRIFT_MAJOR.
      - Do not treat the current RealAmplitudes compute-uncompute circuit as an HHL, QLR, QCT, or cointegration-test implementation.
      - Exclude the current circuit from family-faithful HHL / quantum-linear-regression / trading-execution resource aggregates.

      Metadata fixes:
      - Author a distinct ST2 circuit.py and instance.json, or explicitly document ST2 as an alias of ST1 and avoid counting both as independent circuit implementations.
      - Replace ST1 labels with ST2 in any ST2-specific artifact.
      - Set experiment_id=exp_2 consistently.
      - Reconcile algorithm_family between circuit.py and instance.json.
      - If the current ansatz_stretch proxy is retained temporarily, set the registered family to other-gate-based or generic-ansatz and mark proxy_faithfulness=template_only.
      - If the family remains hhl, the circuit body must be reauthored with an HHL/QLR-shaped structure.

      Recommended ST2-specific HHL/QLR remediation:
      - Use a small Hermitian design-matrix proxy for the first regression.
      - Include a data-loading or amplitude-encoding placeholder for historical price data.
      - Add a QPE/eigenvalue register and controlled exp(iAt) or mocked controlled-U powers.
      - Add inverse-QFT / QPE uncomputation structure.
      - Add a conditional rotation representing pseudo-inverse / eigenvalue inversion.
      - Include a first QLR block for beta estimation.
      - Add an explicit residual-construction accounting note or small classical-postprocessing boundary.
      - Include a second small QLR block for the lagged-residual ADF regression.
      - Keep n_qubits=6 only as a tractable toy skeleton; otherwise consider increasing toward the 12-qubit cap for better HHL/QPE structural coverage.

      Aggregation guidance:
      - Treat the paper and ST2 label as hhl / quantum-linear-regression at the paper level.
      - Treat the current implementation as non-family-faithful until reauthored.
      - Deduplicate ST1/ST2 in per-paper aggregates unless they are implemented as genuinely distinct proxies for VTPA/QCNCA and QCT respectively.
```
