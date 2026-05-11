# Faithfulness Review: SP3

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MAJOR**

---

## Paper

- **Title:** Qudit-based scalable quantum algorithm for solving the integer programming problem
- **Authors:** Kapil Goswami, Peter Schmelcher, Rick Mukherjee
- **Year:** 2025
- **Paper ID:** `de580e8c085e` · **Experiment:** `exp_1` · **Silo:** `portfolio-optimization` · **Algorithm family:** `other-gate-based`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/de580e8c085e.md](p2_systematic_review/output/processed/de580e8c085e.md)
- Circuit: [p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/circuit.py](p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/circuit.py)
- Instance: [p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/instance.json](p4_experiments/experiments/silos/portfolio_optimization/de580e8c085e/instance.json)

---

## Verdict summary

Circuit is a generic RealAmplitudes ansatz-compute-uncompute proxy that does not reproduce the paper's distinctive Grover-AA + QPE + controlled-rotation qudit IP structure; instance/circuit are also mislabelled as SP7.

## Checks

### ✅ Family-faithful

Cohort algorithm_family is the catchall 'other-gate-based' and circuit registers under the same tag, so the family bucket is technically consistent; however the paper's actual family is Grover-AA + QPE qudit, which the proxy does not reflect.

### ✅ Scale-faithful

Paper reports 9 qubit-equivalents (5 qudits dim 3 + 4 constraint + 4 QPE + 1 ancilla); circuit runs at 6 qubits, well within the factor-2 / cap-12 tolerance.

- `v2_n_qubits`: `9`
- `circuit_n_qubits`: `6`

### ❌ Structurally non-trivial

Implementation is a parametrised RealAmplitudes ansatz composed with its inverse (compute-uncompute) plus measurement. There is no QPE register, no inverse QFT, no Grover/amplitude-amplification operator, no constraint-distillation 1-sparse unitary, and no controlled rotation on an ancilla — i.e., none of the structural primitives a faithful proxy for this paper would require. The accompanying notes ('paper algorithm not implemented; generic RealAmplitudes ansatz at paper-scale') confirm this.

### ❌ Metadata-consistent

instance.json and circuit.py are labelled 'SP7' (instance_id 'SP7_v3_proxy_v1', register label='SP7', docstring/name 'SP7_bare'/'SP7_full') while the cohort entry under audit is SP3. paper_id de580e8c085e matches, but the SP3/SP7 label mismatch is a real metadata inconsistency.

## Concerns

- Structural mismatch: ansatz-compute-uncompute proxy shares no primitives with the paper's qudit Grover-AA + QPE + controlled-rotation pipeline.
- Label mismatch: circuit and instance are tagged 'SP7' across registry label, instance_id, and circuit names, but this audit row is SP3.
- Stretch-template self-disclosure: notes explicitly state 'paper algorithm not implemented', so the proxy cannot stand in for resource estimation of the actual algorithm.
- Qudit nature of the paper (d=3 qudits) is wholly lost in the qubit ansatz proxy.

## Recommendations

- Reconcile label_id: either rename registry/instance to SP3 or correct the cohort mapping so SP3 and SP7 do not both point at this proxy.
- If a faithful proxy is required, replace the ansatz with at least a small QPE block (Hadamards + controlled phase + inverse QFT) on a few-qubit register, optionally preceded by a toy Grover oracle, to mirror the paper's algorithm class.
- If the stretch-template proxy is intentional for resource estimation only, document this explicitly in the cohort manifest so downstream analyses do not treat the resource estimate as algorithm-faithful.
