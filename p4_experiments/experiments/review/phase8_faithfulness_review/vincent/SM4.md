# Faithfulness Review: SM4

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Encoding of Probability Distributions for Quantum Monte Carlo Using Tensor Networks
- **Authors:** António Pereira, Alba Villarino, Aser Cortines, Samuel Mugel, Román Orús et al.
- **Year:** 2024
- **Paper ID:** `75a7b04fa681` · **Experiment:** `exp_3` · **Silo:** `simulation-monte-carlo` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/75a7b04fa681.md](p2_systematic_review/output/processed/75a7b04fa681.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/75a7b04fa681__exp_3/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz_stretch template proxy at correct 5-qubit paper scale and matching 'other-gate-based' family bucket; defensible per methodology, but instance.json and circuit.py register the artifact under label 'SM12' rather than 'SM4', a metadata inconsistency.

## Checks

### ✅ Family-faithful

Cohort algorithm_family is 'other-gate-based' (catch-all bucket for the paper's TT-cross + per-core SVD UnitaryGate state-prep, which is non-variational and not in any standard family). Circuit registers under same 'other-gate-based' tag; using a generic ansatz as a template proxy is the explicit methodology for this bucket.

### ✅ Scale-faithful

v2 num_qubits=5 (IBM Eagle R3 5-qubit hardware run); circuit n_qubits=5 from instance.parameters. Exact scale match, well within factor-of-2 and below the 12-qubit cap.

- `v2_n_qubits`: `5`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit is a 5-qubit RealAmplitudes ansatz with 3 reps and linear entanglement (non-trivial parameterised entangling structure). Full circuit composes ansatz with its inverse (compute-uncompute proxy oracle) and measures all qubits. Acceptable as a template proxy; it does NOT implement TT-cross/SVD UnitaryGate state-prep, which is expected for a v5 stretch proxy.

### ❌ Metadata-consistent

instance.json 'instance_id'='SM12_v5_proxy_v1' and 'label'='SM12'; circuit.py @register(label='SM12', ...) and register_accounting(label='SM12', ...). Audit target label_id is SM4. The instance 'notes' field also explains this is a v5 extra-experiment proxy and that the covered v2/v3/v4 label for this paper_id is a different experiment row, which is consistent with SM4 being the v2-canonical label for paper 75a7b04fa681 exp_3 while the proxy artifact was authored under the SM12 v5 label. paper_id and experiment_id match correctly.

## Concerns

- Label mismatch: artifact registered as 'SM12' but audited as label_id 'SM4' (same paper_id/experiment_id, different label generation).
- Circuit is a generic RealAmplitudes ansatz proxy and does not implement the paper's TT-cross + per-core SVD UnitaryGate state-preparation algorithm; acceptable per template-proxy methodology but should not be interpreted as a re-implementation of the paper's algorithm.
- Compute-uncompute proxy oracle is a generic placeholder and bears no relation to QMC amplitude-estimation oracles or to the TT-mapped state-prep unitary; resource counts will reflect ansatz complexity, not the paper's TT-circuit depth claims.

## Recommendations

- Document the SM4<->SM12 label aliasing in the cohort/label registry so resource-estimate roll-ups attribute the run to the canonical SM4 label.
- If higher fidelity to the paper is desired later, replace ansatz_stretch with a UnitaryGate-based state-prep proxy seeded from a TT-cross approximation of a log-normal PDF on 5 qubits; otherwise retain the generic proxy and flag in the Phase-8 readout that SM4 is a template-proxy row, not a paper-faithful row.
