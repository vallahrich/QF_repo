"""
P4 QDK bridge — Qiskit circuit -> QDK Resource Estimator.

Uses ``qsharp.interop.qiskit.estimate`` (installed via the ``qsharp`` package
from the Microsoft Quantum Development Kit) to produce a resource estimate
for a Qiskit circuit under one of the 6 pre-registered hardware profiles
defined in ``p4_experiments/core/resource_profiles/``.

Returned dict conforms to the ``measured`` block of
``p4_experiments/core/schemas/result_record.schema.json``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from qiskit import QuantumCircuit
except ImportError:  # pragma: no cover
    QuantumCircuit = Any  # type: ignore[assignment,misc]


_PROFILES_DIR = Path(__file__).resolve().parent / "resource_profiles"
_VALID_EPSILONS = (1e-3, 1e-4, 1e-6)


@dataclass(frozen=True)
class REProfile:
    profile_id: str
    qubit_params: str
    qec_scheme: str
    description: str


def load_profile(profile_id: str) -> REProfile:
    path = _PROFILES_DIR / f"{profile_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Unknown RE profile: {profile_id} (looked in {path})")
    raw = json.loads(path.read_text(encoding="utf-8"))
    return REProfile(
        profile_id=raw["profile_id"],
        qubit_params=raw["qubit_params"],
        qec_scheme=raw["qec_scheme"],
        description=raw["description"],
    )


def list_profiles() -> List[str]:
    return sorted(p.stem for p in _PROFILES_DIR.glob("*.json"))


def _make_estimator_params(profile: REProfile, epsilon: float):
    """Construct a ``qsharp.estimator.EstimatorParams`` for one (profile, eps)."""
    if epsilon not in _VALID_EPSILONS:
        raise ValueError(
            f"epsilon must be one of {_VALID_EPSILONS}; got {epsilon}."
        )
    from qsharp.estimator import EstimatorParams

    ep = EstimatorParams()
    ep.qubit_params.name = profile.qubit_params
    ep.qec_scheme.name = profile.qec_scheme
    ep.error_budget = epsilon
    return ep


def _normalise_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the ``measured`` schema block from a QDK ``EstimatorResult`` dict."""
    def _dig(d: Dict[str, Any], *path: str) -> Any:
        cur: Any = d
        for key in path:
            if not isinstance(cur, dict) or key not in cur:
                return None
            cur = cur[key]
        return cur

    def _as_int(x: Any) -> Optional[int]:
        try:
            return int(x) if x is not None else None
        except (TypeError, ValueError):
            return None

    # Never coerce missing fields to 0 — that would mask genuine QDK data gaps
    # as legitimate Clifford-only circuits. Return None and let downstream code
    # (compare.py, stats.py) treat it as missing data explicitly.
    logical_qubits = (
        _dig(raw, "logicalCounts", "numQubits")
        or _dig(raw, "physicalCounts", "breakdown", "algorithmicLogicalQubits")
    )
    physical_qubits = _dig(raw, "physicalCounts", "physicalQubits")
    t_count = _dig(raw, "logicalCounts", "tCount")
    num_tstates = _dig(raw, "physicalCounts", "breakdown", "numTstates")
    # Prefer the explicit logicalCounts.tCount; fall back to breakdown.numTstates
    # (same underlying quantity in QDK, but only one is populated on some paths).
    if t_count is None:
        t_count = num_tstates
    # t_depth is approximated by rotationDepth: each rotation synthesises to a
    # serial T-sequence so rotationDepth is a conservative gate-level T-depth.
    # Flagged via t_depth_source so aggregators and figure captions can disclose it.
    rotation_depth = _dig(raw, "logicalCounts", "rotationDepth")
    logical_depth = _dig(raw, "physicalCounts", "breakdown", "logicalDepth")
    if rotation_depth is not None:
        t_depth: Optional[int] = _as_int(rotation_depth)
        t_depth_source = "rotationDepth"
    elif logical_depth is not None:
        t_depth = _as_int(logical_depth)
        t_depth_source = "logicalDepth-fallback"
    else:
        t_depth = None
        t_depth_source = "unavailable"
    runtime_ns = _dig(raw, "physicalCounts", "runtime")
    if isinstance(runtime_ns, (int, float)):
        runtime_seconds: Optional[float] = float(runtime_ns) * 1e-9
    else:
        runtime_seconds = None
    rqops = _dig(raw, "physicalCounts", "rqops")

    return {
        "logical_qubits": _as_int(logical_qubits),
        "physical_qubits": _as_int(physical_qubits),
        "t_count": _as_int(t_count),
        "t_depth": t_depth,
        "t_depth_source": t_depth_source,
        "runtime_seconds": runtime_seconds,
        "rqops": float(rqops) if isinstance(rqops, (int, float)) else None,
        "raw_estimate": raw,
    }


_SAFE_BASIS_GATES = (
    # Exactly the set supported by the QDK QirTarget; decomposing to this
    # basis ensures the QDK QASM3 importer never sees an unsupported gate
    # (like ``p``, ``u``, ``u3``) that its rotation synthesizer then has
    # to handle — and on ``ti_e3_surface`` at ε=1e-4/1e-6 that path can
    # stall indefinitely for small ansatz circuits.
    "rx", "ry", "rz",
    "rxx", "ryy", "rzz",
    "crx", "cry", "crz",
    "cx", "cy", "cz", "ch",
    "h", "x", "y", "z",
    "s", "sdg", "t", "tdg",
    "sx",
    "swap", "ccx",
    "id",
)


def _decompose_for_qdk(circuit: "QuantumCircuit") -> "QuantumCircuit":
    """Decompose to a QDK-QASM3-friendly basis without applying a layout.

    ``qsharp.interop.qiskit.estimate`` transpiles against its own backend
    target, which re-lays-out the circuit and emits physical-qubit operands
    (``$n``) that the QDK QASM importer rejects. We therefore pass
    ``skip_transpilation=True`` to the QDK backend and do our own pre-pass
    here: a plain ``transpile`` call with a fixed basis and no coupling
    map, which decomposes composite Qiskit gates (e.g. ``mcphase``,
    ``Grover operator``, multiplexers) into primitives the QDK compiler
    recognises, while keeping virtual-qubit operands.

    Uses ``optimization_level=0`` to avoid Qiskit's rotation-merge pass,
    which can produce ``p``/``u3`` gates with arbitrary angles that cause
    the QDK trapped-ion (``ti_e3/ti_e4_surface``) rotation-synthesis stage
    to blow up on certain small circuits (observed on B4: 3-qubit
    RealAmplitudes+ZZFeatureMap, hangs >45min on ``ti_e3`` full-mode
    estimates after ``optimization_level=1``).
    """
    from qiskit import transpile

    return transpile(
        circuit,
        basis_gates=list(_SAFE_BASIS_GATES),
        optimization_level=0,
    )


def estimate(
    circuit: "QuantumCircuit",
    profile_id: str,
    epsilon: float,
) -> Dict[str, Any]:
    """Run the QDK Resource Estimator on a Qiskit circuit under one profile.

    The caller is responsible for decomposing the circuit into a QDK-safe
    basis via ``_decompose_for_qdk`` before reaching this entry point
    (done once per mode in ``run_unit.py`` to avoid redundant transpile
    passes across the profile x epsilon grid).
    """
    profile = load_profile(profile_id)
    params = _make_estimator_params(profile, epsilon)

    from qsharp.interop.qiskit import estimate as qdk_estimate

    result = qdk_estimate(circuit, params=params, skip_transpilation=True)
    raw_json = result.json if hasattr(result, "json") else None
    if isinstance(raw_json, str):
        raw = json.loads(raw_json)
    elif isinstance(result, dict):
        raw = dict(result)
    else:
        raw = {k: result[k] for k in result.keys()}
    return _normalise_result(raw)


def estimate_matrix(
    circuit: "QuantumCircuit",
    profile_ids: Optional[Iterable[str]] = None,
    epsilons: Iterable[float] = _VALID_EPSILONS,
) -> List[Dict[str, Any]]:
    """Estimate the circuit across every (profile, epsilon) combination."""
    if profile_ids is None:
        profile_ids = list_profiles()
    out: List[Dict[str, Any]] = []
    for pid in profile_ids:
        for eps in epsilons:
            measured = estimate(circuit, pid, eps)
            out.append({"profile_id": pid, "epsilon": eps, "measured": measured})
    return out
