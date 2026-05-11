# Faithfulness Review: ST2

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Quantum Quantitative Trading: High-Frequency Statistical Arbitrage Algorithm
- **Authors:** Xi-Ning Zhuang, Zhao-Yun Chen, Yu-Chun Wu, Guo-Ping Guo
- **Year:** 2021
- **Paper ID:** `3adb18321a79` · **Experiment:** `exp_2` · **Silo:** `trading-execution` · **Algorithm family:** `hhl`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/3adb18321a79.md](p2_systematic_review/output/processed/3adb18321a79.md)
- Circuit: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py](p4_experiments/experiments/silos/trading_execution/3adb18321a79/circuit.py)
- Instance: [p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json](p4_experiments/experiments/silos/trading_execution/3adb18321a79/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz proxy with no HHL/QPE/block-encoding structure, and is registered under label ST1 rather than ST2; family and structural checks both fail.

## Checks

### ❌ Family-faithful

Cohort and paper class the algorithm as HHL/QLR with block-encoded QSP and QPE measurement; circuit implements a generic RealAmplitudes variational ansatz (compute-uncompute pair), which is not in the HHL family. Explicit template-proxy methodology, but the proxy does not preserve the HHL family bucket.

### ✅ Scale-faithful

v2 reports ~35 data qubits (and ~>50 total); implemented n_qubits=6 is within the project's capped-at-12 tractability rule.

- `v2_n_qubits`: `35`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

An HHL/QLR-faithful proxy would require QPE-shaped structure (controlled-U powers, inverse QFT) and/or block-encoding/qubitization primitives. The circuit contains only a parametrised RealAmplitudes ansatz and its inverse plus measurement; no QPE, no QFT, no oracle/block-encoding structure.

### ❌ Metadata-consistent

circuit.py registers label='ST1' (not ST2) and algorithm_family='hhl', while instance.json carries instance_id='ST1_v3_proxy_v1', label='ST1', experiment_id='exp_1', and algorithm_family='other-gate-based'. ST2 (exp_2) reuses the same shared ST1 circuit with no ST2-specific registration; family tags also disagree between circuit (hhl) and instance (other-gate-based).

## Concerns

- Generic variational ansatz used as proxy for an HHL/QLR-class algorithm; no QPE or block-encoding structure present.
- circuit.py is registered under label 'ST1' (not 'ST2') and instance.json is the ST1 instance; ST2 has no distinct circuit/instance artefact in this triple.
- Family tag inconsistency between circuit registration ('hhl') and instance.json ('other-gate-based').
- v2 operator_notes flag ST1/ST2 as redundant (same Zhuang HFT paper); no exp_2-specific implementation differentiates ST2.

## Recommendations

- If template-proxy is retained, upgrade ST2 proxy to an HHL-shaped skeleton (QPE block: state prep + controlled-e^{iAt} powers + inverse QFT + ancilla rotation) so the family bucket is preserved.
- Author a distinct ST2 circuit.py and instance.json (label='ST2', experiment_id='exp_2'), or explicitly document ST2 as an alias of ST1 in the cohort and skip auditing it as a separate circuit.
- Reconcile algorithm_family between circuit registration and instance.json (both should read 'hhl' for this cohort entry).
