# Faithfulness Review: SX6

**Reviewer:** Vincent Wallerich  
**Review date:** 2026-04-24  
**Verdict:** **DRIFT_MINOR**

---

## Paper

- **Title:** Quantum Heavy-tailed Bandits
- **Authors:** Yulian Wu, Chaowen Guan, Vaneet Aggarwal, Di Wang
- **Year:** 2023
- **Paper ID:** `a2b747cae698` · **Experiment:** `exp_2` · **Silo:** `other` · **Algorithm family:** `amplitude-estimation`

**Sources consulted:**
- Paper markdown: [p2_systematic_review/output/processed/a2b747cae698.md](p2_systematic_review/output/processed/a2b747cae698.md)
- Circuit: [p4_experiments/experiments/silos/other/a2b747cae698__exp_2/circuit.py](p4_experiments/experiments/silos/other/a2b747cae698__exp_2/circuit.py)
- Instance: [p4_experiments/experiments/silos/other/a2b747cae698__exp_2/instance.json](p4_experiments/experiments/silos/other/a2b747cae698__exp_2/instance.json)

---

## Verdict summary

Generic RealAmplitudes ansatz proxy at n=5 is family-stale (paper uses amplitude-estimation-based QTME, not a variational ansatz), but registry tag and scale are defensible for a template-proxy stretch row.

## Checks

### ❌ Family-faithful

Registered algorithm_family='amplitude-estimation' matches cohort and paper (QTME via amplitude estimation per Brassard et al.), but the implementation is an ansatz-compute-uncompute proxy with no QPE/inverse-QFT structure. Acknowledged as template proxy in instance.notes (algorithm_family='other-gate-based').

### ✅ Scale-faithful

Paper does not state a circuit qubit count (NOT_STATED); n_qubits=5 is within the <=12 tractability cap and a reasonable default for a stretch row.

- `v2_n_qubits`: `None`
- `circuit_n_qubits`: `5`

### ✅ Structurally non-trivial

Bare = RealAmplitudes(n=5, reps=3, linear) with assigned parameters; full = ansatz . ansatz^dagger compute-uncompute pair plus measurement. Non-trivial gate content, but lacks AE-specific structure (no Grover oracle / inverse QFT).

### ✅ Metadata-consistent

Registry algorithm_family='amplitude-estimation' aligns with cohort and paper methodology tags; instance.json explicitly flags it as a template proxy and labels algorithm_family='other-gate-based' for the proxy run, with notes calling out that the paper algorithm is not implemented.

## Concerns

- Implementation is a generic variational ansatz, not an amplitude-estimation circuit; family-faithfulness is only nominal.
- Paper qubit count is NOT_STATED, so scale-faithfulness cannot be quantitatively verified.
- Mismatch between registry tag ('amplitude-estimation') and instance algorithm_family ('other-gate-based') could confuse downstream aggregation.

## Recommendations

- Either tag this row consistently as a template proxy in both registry and instance (e.g., algorithm_family='other-gate-based' with proxy_for='amplitude-estimation'), or upgrade the proxy to a minimal QAE skeleton (state-prep + Grover-like oracle + inverse QFT) to make the family tag literal.
- Document in operator notes that SX5/SX6/SX7 share paper a2b747cae698 and use proxies of differing fidelity.
