"""
P4 algorithm-family templates.

Reusable circuit constructions used by the Phase 4-prime ``S*`` builders
(SD1, SQ1, SP1, SP2, SM1, SM2, SM3, SH1). Templates expose pure functions
that take parameter dicts and return Qiskit ``QuantumCircuit`` objects;
they do NOT register anything against the P4 ``circuit_registry`` — that
is the responsibility of the per-paper ``circuit.py`` files which import
these helpers.

Per-paper builders remain self-contained where needed to preserve the
bit-identical tau-table guarantee established in the pre-registration; they do
not consume this module unless they explicitly opt into a shared template.
"""
