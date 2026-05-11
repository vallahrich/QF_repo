# Faithfulness Review: SM1

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Entanglement scaling in matrix product state representation of smooth functions and their shallow quantum circuit approximations
- **Authors:** Vladyslav Bohun, Illia Lukin, Mykola Luhanko, Georgios Korpas, Philippe J.S. De Brouwer et al.
- **Year:** 2025
- **Paper ID:** `48cd8220e3b2` · **Experiment:** `exp_1` · **Silo:** `simulation-monte-carlo` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/48cd8220e3b2.md](p2_systematic_review/output/processed/48cd8220e3b2.md)
- Circuit: [p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/circuit.py](p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/circuit.py)
- Instance: [p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/instance.json](p4_experiments/experiments/silos/simulation_monte_carlo/48cd8220e3b2/instance.json)

---

## Verdict summary

Generic RealAmplitudes template proxy at N=6 is a defensible scale/family-faithful stand-in for the paper's MPS V-layer state-prep algorithm, but circuit.py and instance.json carry a stale 'SM8' label instead of 'SM1'.

## Checks

### ✅ Family-faithful

Paper algorithm (MPS-to-circuit V-layer isometry state preparation) and the RealAmplitudes proxy both fall within the cohort 'other-gate-based' bucket; v2 ansatz_type='custom' and the proxy is explicitly acknowledged as a template stretch.

### ✅ Scale-faithful

Paper sweeps N in {6,10,15,18,20,25,27,40,50,64}; circuit uses n_qubits=6, exactly the smallest paper-tested value and within the 12-qubit tractability cap.

- `v2_n_qubits`: `6`
- `circuit_n_qubits`: `6`

### ✅ Structurally non-trivial

Bare circuit is RealAmplitudes(reps=3, linear entanglement) with assigned random parameters; full variant adds compute-uncompute and measurement. Uses RY+CNOT (subset of paper's RX/RY/RZ/CNOT gate set). It is not a V-layer double-staircase nor isometry-synthesised, so it does not implement the paper's specific construction — but it is a non-trivial parametrised state-prep proxy as the cohort methodology permits.

### ❌ Metadata-consistent

circuit.py @register(label='SM8'), register_accounting(label='SM8'), and instance.json {instance_id:'SM8_v3_proxy_v1', label:'SM8'} all tag this artifact as SM8, but the cohort task and paper_id 48cd8220e3b2 are assigned to label_id SM1. Paper_id and silo are correct; only the label string is stale.

## Concerns

- Label mismatch: artifact files self-identify as 'SM8' while the cohort entry is 'SM1' (paper_id 48cd8220e3b2 is correct in both).
- Proxy does not reproduce the paper's V-layer (double-staircase) isometry-synthesised structure; it is a generic RealAmplitudes ansatz.
- instance_parameters.algorithm_variant_paper mentions 'TCI + isometry compilation' which is not what the proxy implements; flagged as expected for a stretch template proxy.

## Recommendations

- Rename the @register/register_accounting label from 'SM8' to 'SM1' and update instance.json instance_id/label fields to match the canonical label_id.
- If a tighter proxy is wanted, replace the linear-entanglement RealAmplitudes with a brick-wall / staircase 2-qubit-block ansatz to better mimic the V-layer pattern; otherwise document explicitly that the cohort accepts ansatz_stretch for this paper.
