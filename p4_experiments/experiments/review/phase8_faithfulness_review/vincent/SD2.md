# Faithfulness Review: SD2

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Algorithm for Local-Volatility Option Pricing via the Kolmogorov Equation
- **Authors:** Nikita Guseynov, Mikel Sanz, Ángel Rodríguez-Rozas, Nana Liu, Javier Gonzalez-Conde
- **Year:** 2025
- **Paper ID:** `081132e62980` · **Experiment:** `exp_1` · **Silo:** `derivative-pricing` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/081132e62980.md](p2_systematic_review/output/processed/081132e62980.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/081132e62980/circuit.py](p4_experiments/experiments/silos/derivative_pricing/081132e62980/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/081132e62980/instance.json](p4_experiments/experiments/silos/derivative_pricing/081132e62980/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz proxy at n=5 for a Schroedingerisation+sparse-HamSim+swap-test PDE algorithm; family bucket 'other-gate-based' is consistent and the template proxy is methodologically permitted, but the circuit shares no structural primitives with the paper and the label metadata is registered as 'SD6' rather than 'SD2'.

## Checks

### ✅ Family-faithful

Cohort and circuit both tag algorithm_family='other-gate-based', which is the catch-all bucket appropriate for this Schroedingerisation/QSP-based PDE solver; no narrower family (e.g., HHL, QAE, VQE) is claimed by the paper, so the generic ansatz does not violate family bucketing.

### ✅ Scale-faithful

Paper does not state a concrete qubit count (NOT_STATED); circuit uses n_qubits=5, which is well under the 12-qubit tractability cap and consistent with the v3 stretch methodology.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ❌ Structurally non-trivial

Circuit is a parametrised RealAmplitudes ansatz with a compute-uncompute pair as a proxy oracle; it contains none of the paper's defining primitives (amplitude encoding of p(x,0), Schroedingerisation auxiliary register, clock register, block-encoded sparse Hamiltonian via LCU, QSP-based Hamiltonian simulation, post-selection on momentum, payoff state preparation, swap test). This is a deliberate template proxy under the v3 stretch methodology, but it is not structurally representative of the paper's algorithm beyond providing a 2q-gate-bearing depth proxy.

### ❌ Metadata-consistent

circuit.py and instance.json both register/label this experiment as 'SD6' (label='SD6', instance_id='SD6_v3_proxy_v1', QuantumCircuit names 'SD6_bare'/'SD6_full', description references 'SD6'), while the cohort label_id under audit is 'SD2'. paper_id (081132e62980), silo (derivative-pricing) and algorithm_family (other-gate-based) are consistent across cohort, instance and circuit.

## Concerns

- Circuit/instance label metadata is 'SD6' but cohort label_id is 'SD2' (likely a relabel/rename that did not propagate into the implementation files).
- Implemented circuit shares no structural primitives with the paper's algorithm (no Hamiltonian simulation, no swap test, no block-encoding, no clock/Schroedingerisation register); it is a pure ansatz proxy.
- Paper reports no concrete n_qubits, so scale faithfulness cannot be quantitatively validated against a paper-claimed register size; n=5 is justified only by the stretch methodology and the 12-qubit cap.
- circuit.py docstring contains a truncated paper title ('Kolmogorov Equatio').

## Recommendations

- Reconcile the label_id in circuit.py / instance.json (SD6 -> SD2) or document the SD6<->SD2 mapping in the cohort registry so the audit trail is unambiguous.
- If a more faithful proxy is desired in a later phase, consider replacing the bare RealAmplitudes with a small QSP / block-encoded sparse-HamSim micro-circuit plus a swap-test ancilla so at least the dominant primitives (HamSim oracle + overlap measurement) are represented.
- Fix the truncated 'Kolmogorov Equatio' string in the circuit docstring/description for cleanliness.
