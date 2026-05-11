"""
P4 oracle accounting — bare vs full resource accounting.

Per P4_PLAN §3.1, the oracle tax tau(u) is defined against two accounting modes:

    bare : the circuit as submitted by the paper (no state-prep, no oracle body)
    full : state-preparation sub-circuit + explicit oracle implementation prepended

This module provides a thin façade. The actual state-prep and oracle circuits
are authored per-experiment and registered via `register_accounting()`. This
keeps oracle-construction choices auditable and disclosed in source.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any, Literal, Optional

try:
    from qiskit import QuantumCircuit
except ImportError:  # pragma: no cover
    QuantumCircuit = Any  # type: ignore[assignment,misc]

Mode = Literal["bare", "full"]

AccountingFn = Callable[[Dict[str, Any], "QuantumCircuit"], "QuantumCircuit"]


@dataclass(frozen=True)
class AccountingEntry:
    label: str
    state_prep: Optional[AccountingFn]
    oracle: Optional[AccountingFn]
    oracle_variant: str  # e.g. "grover-standard" | "lks-optimised"
    notes: str


ACCOUNTING: Dict[str, AccountingEntry] = {}


def register_accounting(
    label: str,
    *,
    state_prep: Optional[AccountingFn] = None,
    oracle: Optional[AccountingFn] = None,
    oracle_variant: str = "grover-standard",
    notes: str = "",
) -> None:
    if label in ACCOUNTING:
        existing = ACCOUNTING[label]
        if existing.oracle_variant == oracle_variant and existing.notes == notes:
            return
        raise ValueError(f"Duplicate accounting registration for label: {label}")
    ACCOUNTING[label] = AccountingEntry(
        label=label,
        state_prep=state_prep,
        oracle=oracle,
        oracle_variant=oracle_variant,
        notes=notes,
    )


def apply_accounting(
    label: str,
    mode: Mode,
    instance: Dict[str, Any],
    bare_circuit: "QuantumCircuit",
) -> "QuantumCircuit":
    """Return the circuit to hand to the RE under the requested accounting mode.

    For `bare`, returns the circuit unchanged.
    For `full`, prepends state preparation and oracle implementation if registered.
    If neither state_prep nor oracle is registered for a label, `full` == `bare`
    and the caller must document this in notes.md (we do not silently pretend
    that oracle overhead is zero).
    """
    if mode == "bare":
        return bare_circuit.copy()

    if mode != "full":
        raise ValueError(f"Unknown accounting mode: {mode!r}")

    entry = ACCOUNTING.get(label)
    if entry is None:
        raise KeyError(
            f"No accounting registered for label {label!r}. "
            f"Register state_prep / oracle or explicitly document that full == bare."
        )

    qc = bare_circuit.copy()
    # Order matters: state prep first, then oracle body.
    if entry.state_prep is not None:
        qc = entry.state_prep(instance, qc)
    if entry.oracle is not None:
        qc = entry.oracle(instance, qc)
    return qc


def oracle_variant(label: str) -> str:
    entry = ACCOUNTING.get(label)
    return entry.oracle_variant if entry is not None else "none"
