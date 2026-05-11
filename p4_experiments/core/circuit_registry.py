"""
P4 circuit registry — experiment_id -> Qiskit circuit builder.

A builder is a callable that takes an instance-parameter dict and returns a
Qiskit QuantumCircuit. The registry maps active P4 cohort labels and paper_ids
to builder callables.

Implementations live under p4_experiments/experiments/silos/<silo>/<paper_id>/circuit.py and
register themselves via the @register decorator at import time. This module
provides the registry plus a loader that imports all known builder modules.

Usage:
    from p4_experiments.core.circuit_registry import REGISTRY, get_builder

    builder = get_builder("B3")
    circuit = builder({"n_features": 4, "n_samples": 20, "seed": 0})
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any, Optional

try:
    from qiskit import QuantumCircuit
except ImportError:  # pragma: no cover
    QuantumCircuit = Any  # type: ignore[assignment,misc]

BuilderFn = Callable[[Dict[str, Any]], "QuantumCircuit"]


@dataclass(frozen=True)
class BuilderEntry:
    label: str
    paper_id: str
    silo: str
    algorithm_family: str
    description: str
    builder: BuilderFn


REGISTRY: Dict[str, BuilderEntry] = {}


def register(
    label: str,
    paper_id: str,
    silo: str,
    algorithm_family: str,
    description: str = "",
) -> Callable[[BuilderFn], BuilderFn]:
    """Decorator to register a circuit builder under a P4 label.

    Labels must match the active canonical cohort label set.
    """

    def decorate(fn: BuilderFn) -> BuilderFn:
        if label in REGISTRY:
            existing = REGISTRY[label]
            if (
                existing.paper_id == paper_id
                and existing.silo == silo
                and existing.algorithm_family == algorithm_family
            ):
                return fn
            raise ValueError(f"Duplicate P4 registry label: {label}")
        REGISTRY[label] = BuilderEntry(
            label=label,
            paper_id=paper_id,
            silo=silo,
            algorithm_family=algorithm_family,
            description=description,
            builder=fn,
        )
        return fn

    return decorate


def get_builder(label: str) -> BuilderEntry:
    if label not in REGISTRY:
        raise KeyError(
            f"P4 label {label!r} is not registered. Known labels: {sorted(REGISTRY)}"
        )
    return REGISTRY[label]


def load_all_builders() -> None:
    """Import every builder module so that @register side-effects populate REGISTRY.

    Iterates p4_experiments/experiments/silos/<silo>/<paper_id>/circuit.py and imports each.
    Silent on import errors so that partial scaffolding does not block other
    builders; failures are logged to stderr.
    """
    import importlib
    import sys
    from pathlib import Path

    p4_root = Path(__file__).resolve().parents[1]
    search_roots = [p4_root / "experiments" / "silos"]
    legacy_roots = [
        p for p in p4_root.iterdir()
        if p.is_dir() and p.name not in {"canonical", "common", "core", "docs", "experiments", "infra", "prompts"}
    ]
    for circuit_py in [path for root in search_roots + legacy_roots for path in root.glob("*/*/circuit.py")]:
        rel = circuit_py.relative_to(p4_root.parent)
        mod_name = ".".join(rel.with_suffix("").parts)
        try:
            importlib.import_module(mod_name)
        except Exception as exc:  # pragma: no cover
            print(f"[circuit_registry] failed to import {mod_name}: {exc}", file=sys.stderr)


def list_registered() -> list[str]:
    return sorted(REGISTRY.keys())
