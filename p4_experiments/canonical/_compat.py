"""Compatibility helpers for the staged canonical namespace migration."""

from __future__ import annotations

import sys
from importlib import import_module
from inspect import signature
from typing import Sequence


def run_legacy_main(module_name: str, argv: Sequence[str] | None = None) -> int:
    """Run a legacy module's ``main`` function from a new namespace wrapper."""
    module = import_module(module_name)
    entrypoint = getattr(module, "main")
    if signature(entrypoint).parameters:
        result = entrypoint(list(sys.argv[1:] if argv is None else argv))
    else:
        result = entrypoint()
    return int(result or 0)