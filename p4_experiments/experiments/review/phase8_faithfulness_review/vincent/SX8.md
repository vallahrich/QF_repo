# Faithfulness Review: SX8

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Attacks on Bitcoin, and How to Protect Against Them
- **Authors:** Divesh Aggarwal, Gavin Brennen, Troy Lee, Miklos Santha, Marco Tomamichel
- **Year:** 2018
- **Paper ID:** `cd9329dc38ef` · **Experiment:** `exp_3` · **Silo:** `cryptography-security` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/cd9329dc38ef.md](p2_systematic_review/output/processed/cd9329dc38ef.md)
- Circuit: [p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/circuit.py](p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/instance.json](p4_experiments/experiments/silos/other/cd9329dc38ef__exp_3/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz_stretch template proxy stands in for a Shor-ECDLP resource-estimation paper; under the explicit template-proxy methodology this is acceptable but the circuit does not implement Shor/QPE structure.

## Checks

### ✅ Family-faithful

Paper algorithm is Shor-ECDLP (QFT/QPE-based). Cohort tags algorithm_family='other-gate-based' and the circuit is an explicit ansatz_stretch template proxy. Per the methodology, generic-ansatz proxies for resource-estimation-only papers are allowed, but family is not Shor-specific - flagged as borderline.

### ✅ Scale-faithful

Paper claims 2334 logical qubits; circuit uses 12 qubits, which is the explicit Phase-8 tractability cap.

- `v2_n_qubits`: `2334`
- `circuit_n_qubits`: `12`

### ✅ Structurally non-trivial

RealAmplitudes(reps=3, linear entanglement) plus compute-uncompute pair with measurement; well-formed parametrised ansatz, not empty or trivial.

### ✅ Metadata-consistent

instance.json, circuit.py decorator, v2 extraction, and authoring metadata all agree on label_id=SX8, paper_id=cd9329dc38ef, exp_3, n_qubits=12, ansatz_layers=3, template=ansatz_stretch, and explicitly note the proxy does NOT implement the paper's algorithm.

## Concerns

- Paper is a Shor-ECDLP / Grover-SHA256 resource estimation; circuit family tag 'other-gate-based' obscures that the paper's actual algorithms are Shor (QFT/QPE) and Grover.
- Circuit contains no QPE-shaped structure, modular-arithmetic oracle, or Grover oracle - it cannot inform a Shor-ECDLP resource estimate beyond a generic small-ansatz baseline.
- Paper-claimed scale (2334 logical qubits, 1.28e11 Toffoli) is ~194x larger in qubits than the proxy; extrapolation from 12-qubit ansatz to paper-scale will be model-driven rather than circuit-driven.

## Recommendations

- Document explicitly in the cohort that SX8 is a resource-estimation paper with no implementable circuit; the proxy is a placeholder for slot-counting only.
- Consider tagging algorithm_family as 'shor-ecdlp' or 'resource-estimation-proxy' so downstream Phase-8 analysis can group it correctly rather than mixing it into 'other-gate-based'.
