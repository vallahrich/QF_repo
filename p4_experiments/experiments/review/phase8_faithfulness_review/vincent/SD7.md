# Faithfulness Review: SD7

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum-inspired variational algorithms for partial differential equations: Application to financial derivative pricing
- **Authors:** Tianchen Zhao, Chuhao Sun, Asaf Cohen, James Stokes, Shravan Veerapaneni
- **Year:** 2022
- **Paper ID:** `439a750eda8c` · **Experiment:** `exp_2` · **Silo:** `derivative-pricing` · **Algorithm family:** `classical-simulation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/439a750eda8c.md](p2_systematic_review/output/processed/439a750eda8c.md)
- Circuit: [p4_experiments/experiments/silos/derivative_pricing/439a750eda8c__exp_2/circuit.py](p4_experiments/experiments/silos/derivative_pricing/439a750eda8c__exp_2/circuit.py)
- Instance: [p4_experiments/experiments/silos/derivative_pricing/439a750eda8c__exp_2/instance.json](p4_experiments/experiments/silos/derivative_pricing/439a750eda8c__exp_2/instance.json)

---

## Verdict summary

Paper is a quantum-inspired classical VMC/NQS PDE solver with no actual quantum circuit; the generic RealAmplitudes ansatz_stretch proxy is family-consistent (classical-simulation bucket) but runs at n=5 vs paper n=16, and the instance.json carries stale SD13 labeling.

## Checks

### ✅ Family-faithful

Paper is explicitly quantum-inspired classical (VMC + autoregressive NQS, no QPU). Cohort algorithm_family='classical-simulation' and circuit @register algorithm_family='classical-simulation' match. A generic variational template proxy is the documented methodology for this bucket since the paper has no quantum circuit to implement.

### ❌ Scale-faithful

Paper reports max_qubits_used_n=16 (mesh of 2^16=65536 points). Implemented circuit uses n_qubits=5, well below both the paper value and the 12-qubit tractability cap (16->cap 12 allowed; 5 is <half of 12 and ~1/3 of paper). Outside factor-of-2 scale-faithfulness band.

- `v2_n_qubits`: `16`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare circuit is a 3-layer linear-entanglement RealAmplitudes ansatz; full variant adds an ansatz . ansatz^dagger compute-uncompute pair plus measurement. Acceptable structural template for a 'classical-simulation / generic variational ansatz stretch' proxy where the paper itself prescribes no quantum circuit.

### ❌ Metadata-consistent

instance.json fields are inconsistent with the SD7 cohort: instance_id='SD13_v5_proxy_v1', label='SD13', algorithm_family='other-gate-based'. circuit.py @register also uses label='SD13' and description references SD13. Cohort/family for SD7 says algorithm_family='classical-simulation'. v2 operator_notes flags SD6/SD7 as potentially redundant rows of the same paper, consistent with a v5 stretch row carrying SD13 labeling that was later renamed/aliased to SD7.

## Concerns

- Scale gap: implemented n_qubits=5 vs paper n=16 (and vs 12-qubit tractability cap).
- Stale SD13 labeling in instance.json (instance_id, label) and circuit.py @register (label, description) for what is now SD7.
- algorithm_family='other-gate-based' in instance.json conflicts with cohort/register value 'classical-simulation'.
- Paper has no quantum circuit (quantum-inspired classical VMC/NQS); any Qiskit circuit is unavoidably a coarse template proxy and should not be over-interpreted as representing the paper's algorithm.

## Recommendations

- Bump n_qubits toward the 12-qubit tractability cap to bring scale within the factor-of-2 band of paper n=16.
- Rename label/instance_id/description from SD13 to SD7 in instance.json and circuit.py @register to align with the canonical cohort id.
- Set instance.json algorithm_family to 'classical-simulation' to match cohort and @register.
- Audit SD6 vs SD7 redundancy (same paper_id 439a750eda8c) and either disambiguate exp_1/exp_2 explicitly or collapse to a single row.
