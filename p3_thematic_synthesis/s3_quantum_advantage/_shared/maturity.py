"""L0-L5 experimental maturity ladder (lifted from assess_hoefler.py).

2026-04-20 audit fix M3: when hardware.type is missing or 'not_specified', the
ladder previously defaulted silently to L1_noiseless_sim — the most permissive
tier. This biases downstream Stilck-França and Beverland verdicts (no noise
penalty). The default behaviour is preserved for backward compatibility, but
``compute_maturity_with_source`` now exposes whether the level was inferred from
explicit data or from the permissive default, so assessors can flag it in their
reasoning strings.
"""

from __future__ import annotations


def _classify(experiment: dict) -> tuple[str, str]:
    """Return (level, source) where source ∈ {'explicit', 'default_unknown'}."""
    hw_type = str((experiment.get("hardware") or {}).get("type", "not_specified"))
    noise = experiment.get("noise_model") or {}
    is_noisy = noise.get("is_noisy")
    qr = experiment.get("quantum_resources") or {}
    n_qubits = qr.get("num_qubits")
    n_qubits_num = n_qubits if isinstance(n_qubits, (int, float)) else None

    if "real_qpu" in hw_type or hw_type == "quantum_annealer":
        if n_qubits_num and n_qubits_num > 20:
            return "L4_qpu_scale", "explicit"
        return "L3_qpu_small", "explicit"
    if hw_type == "simulator_noisy" or is_noisy:
        return "L2_noisy_sim", "explicit"
    if hw_type in ("simulator_statevector", "simulator_other"):
        return "L1_noiseless_sim", "explicit"
    # not_specified / unknown → assume noiseless simulator (PERMISSIVE DEFAULT)
    return "L1_noiseless_sim", "default_unknown"


def compute_maturity_level(experiment: dict) -> str:
    level, _src = _classify(experiment)
    return level


def compute_maturity_with_source(experiment: dict) -> tuple[str, str]:
    """Return (maturity_level, source). source='default_unknown' means the
    ladder fell back to L1 because no hardware.type was specified — verdicts
    using this maturity level should be treated with low confidence."""
    return _classify(experiment)
