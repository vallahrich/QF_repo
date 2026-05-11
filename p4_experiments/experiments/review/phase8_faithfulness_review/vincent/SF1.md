# Faithfulness Review: SF1

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **CONFIRMED**

---

## Paper

- **Title:** Quantum Principal Component Analysis for Financial Fraud Detection
- **Authors:** Giacomo Lancellotti, Alberto Guerrini, Giacomo Ranieri, Valeria Zaffaroni, Paolo Cremonesi
- **Year:** 2025
- **Paper ID:** `76a87207ec32` · **Experiment:** `exp_1` · **Silo:** `fraud-detection` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/76a87207ec32.md](p2_systematic_review/output/processed/76a87207ec32.md)
- Circuit: [p4_experiments/experiments/silos/fraud_detection/76a87207ec32/circuit.py](p4_experiments/experiments/silos/fraud_detection/76a87207ec32/circuit.py)
- Instance: [p4_experiments/experiments/silos/fraud_detection/76a87207ec32/instance.json](p4_experiments/experiments/silos/fraud_detection/76a87207ec32/instance.json)

---

## Verdict summary

Circuit is a faithful QAE template proxy in the amplitude-estimation family matching the paper's AD-QPCA algorithm class, scaled down under the explicit 12-qubit tractability cap.

## Checks

### ✅ Family-faithful

Paper algorithm is QAE-based AD-QPCA (oracle_structure=amplitude_estimation, measurement=QPE on Grover operator). Circuit uses canonical_qae template with state_prep + num_eval_qubits register, same family bucket as cohort tag amplitude-estimation.

### ✅ Scale-faithful

Paper reports ~1.41e10 logical qubits (dominated by Bucket-Brigade QRAM); intractable to simulate. Methodology explicitly permits capping at <=12 qubits. Implemented bare circuit uses n_state=3; full QAE adds num_eval_qubits=3 (~7 qubits total), within the cap.

- `v2_n_qubits`: `14100000000`
- `circuit_n_qubits`: `7`

### ✅ Structurally non-trivial

Bare uses continuous_func_state_prep (n_state=3, 2 layers). Full wraps it with canonical_qae which provides the QAE structure (controlled-Q Grover-style oracle applications + inverse QFT on the eval register), the structural shape a QAE/QPE paper requires.

### ✅ Metadata-consistent

register decorator declares algorithm_family=amplitude-estimation matching cohort and v2 oracle_structure=amplitude_estimation; instance.notes correctly flags this is a template proxy and not a literal implementation of AD-QPCA.

## Concerns

- Circuit is an intentional template proxy: it does NOT implement BtA conversion, Bucket-Brigade QRAM, ripple-carry/multiplier arithmetic, or the Step 1-5 AD-PCA pipeline. Aggregate Phase-8 resource estimates derived from this proxy will not reflect the paper's QRAM-dominated 1.41e10-qubit footprint.
- instance.json paper_claimed values (num_qubits=1, depth=1, t_count=1) are placeholders rather than the v2-reported 1.41e10 / 5.80e6 / 1.99e13; downstream cost extrapolation must read from v2 extraction, not instance.paper_claimed.

## Recommendations

- When extrapolating SF1 to Phase-8 resource cost, use v2 num_qubits=1.41e10, depth=5.8e6, T-count=1.99e13, T-depth=2.26e6 directly; do not derive from the proxy circuit.
- Optionally backfill instance.paper_claimed with v2 numerics so any cost-rollup script that reads instance.json yields paper-faithful figures.
