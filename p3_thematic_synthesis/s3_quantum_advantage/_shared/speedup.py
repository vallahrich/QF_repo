"""Speedup-order inference & oracle-complexity estimation shared across frameworks.

Ported from assess_hoefler.py so Babbush/Dalzell/Beverland/Montanaro can reuse
the same priority hierarchy (paper-reported > derived-from-theory > family mapping).
"""

from __future__ import annotations

from typing import Optional

_K_MAP = {
    "quadratic": 2,
    "cubic": 3,
    "quartic": 4,
    "polynomial_other": 4,
    "exponential": None,
    "logarithmic": None,
}


def infer_speedup_order(
    algorithm_family: str,
    complexity: dict | None,
    algorithm_speedup_mapping: dict,
    derived: dict | None = None,
) -> tuple[str, Optional[int], str]:
    """Return (speedup_order, k, reasoning).

    Priority: paper-reported > derived-from-theory > family fallback.
    """
    # 1. paper-reported
    if complexity:
        so = complexity.get("speedup_order")
        if so and so not in ("none", "unknown", None):
            return so, _K_MAP.get(so), f"Speedup '{so}' from paper complexity analysis"

    # 2. derived-from-theory
    if derived:
        cd = derived.get("complexity_derived") or {}
        so = cd.get("speedup_order")
        if so and so not in ("none", "unknown", None):
            citation = cd.get("quantum_complexity_citation", "")
            return so, _K_MAP.get(so), f"Speedup '{so}' derived from theory [{citation}]"
        if so == "none_proven":
            citation = cd.get("quantum_complexity_citation", "")
            return "none_proven", None, f"No proven speedup per theory [{citation}]"

    # 3. family mapping
    entry = algorithm_speedup_mapping.get(algorithm_family, {})
    so = entry.get("speedup_order", "unknown")
    k = entry.get("k")
    caveat = entry.get("caveat", "")
    reasoning = f"Algorithm '{algorithm_family}': {so}"
    if caveat:
        reasoning += f" — {caveat}"
    return so, k, reasoning


def estimate_oracle_complexity(
    experiment: dict, derived: dict | None = None
) -> tuple[Optional[int], str]:
    """Return (M, operation_type). Priority: T-count > gate_count > derived > depth*qubits.

    NOTE: Hoefler's 'binary ops' in Table 2 refers to logical T/Toffoli operations
    under fault tolerance; Clifford gates are effectively free. Consumers that need
    the stricter T-count-only number should prefer t_count and treat gate_count_total
    as an upper bound on M_binary.
    """
    qr = experiment.get("quantum_resources") or {}
    complexity = experiment.get("complexity_analysis") or {}

    t_count = qr.get("t_count")
    if isinstance(t_count, (int, float)) and t_count > 0:
        return int(t_count), "t_count"

    gate_count = qr.get("gate_count_total")
    if isinstance(gate_count, (int, float)) and gate_count > 0:
        return int(gate_count), "binary"

    total_q = complexity.get("total_operations_quantum")
    if isinstance(total_q, (int, float)) and total_q > 0:
        return int(total_q), "binary"

    if derived:
        rd = derived.get("resources_derived") or {}
        m = rd.get("oracle_complexity_M")
        if isinstance(m, (int, float)) and m > 0:
            return int(m), "binary_derived"

    depth = qr.get("circuit_depth")
    qubits = qr.get("num_qubits")
    if (
        isinstance(depth, (int, float))
        and isinstance(qubits, (int, float))
        and depth > 0
        and qubits > 0
    ):
        return int(depth * qubits), "depth_times_qubits"

    return None, "unknown"
