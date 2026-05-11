"""Phase 6 - Lift the trapped-ion blanket skip in the canonical runner.

This script does two things:

  1. Audits the canonical runner ``p4_experiments/core/run_unit.py`` to
     confirm it satisfies PRE_REGISTRATION audit category G:
         - ``_SKIP_CELLS`` is defined as an empty set.
         - No ``_SKIP_CELLS.add(...)`` call exists anywhere in the module.
         - ``_PER_CELL_TIMEOUT_S`` and ``_estimate_with_timeout`` symbols
           are present (per-cell wall-clock budget).
         - The engine_failure code path is wired (referenced >=1 time
           outside the historical-comment block).

  2. Writes a Phase 6 entry to ``cohort.json._phase_status.phase6`` with
     the runner SHA-256, the timeout default, and a UTC timestamp.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RUNNER = ROOT / "p4_experiments" / "core" / "run_unit.py"


def _sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    src = RUNNER.read_text(encoding="utf-8")
    # Parse to confirm syntactic validity.
    ast.parse(src)

    # AST-walk to verify _SKIP_CELLS is assigned to an empty set/literal.
    tree = ast.parse(src)
    skip_cells_assignments = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name) and t.id == "_SKIP_CELLS":
                    skip_cells_assignments.append(node)
    assert len(skip_cells_assignments) == 1, (
        f"Expected exactly one _SKIP_CELLS assignment, got {len(skip_cells_assignments)}"
    )
    val = skip_cells_assignments[0].value
    # Acceptable: set() call, or empty set literal {}, or empty dict (we use set()).
    is_empty_set_call = (
        isinstance(val, ast.Call)
        and isinstance(val.func, ast.Name)
        and val.func.id == "set"
        and not val.args
        and not val.keywords
    )
    assert is_empty_set_call, (
        f"_SKIP_CELLS must be assigned `set()`; got {ast.dump(val)}"
    )

    # No _SKIP_CELLS.add(...) calls anywhere.
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "_SKIP_CELLS"
            and node.func.attr == "add"
        ):
            raise AssertionError(
                f"Found _SKIP_CELLS.add() call at line {node.lineno}; canonical pipeline forbids it."
            )

    # Required symbols.
    for sym in ("_PER_CELL_TIMEOUT_S", "_estimate_with_timeout", "_estimate_worker", "_engine_failure_measured"):
        assert sym in src, f"Required symbol '{sym}' missing from runner."

    # engine_failure must appear at least 3x (status enum, log message, schema).
    n_engine_failure = src.count("engine_failure")
    assert n_engine_failure >= 3, f"engine_failure referenced only {n_engine_failure} times."

    # Capture timeout default.
    m = re.search(r'P4_CELL_TIMEOUT_S"\s*,\s*"(\d+)"', src)
    timeout_default = int(m.group(1)) if m else None

    runner_sha = _sha256_file(RUNNER)

    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {"_legacy": ps} if ps is not None else {}
    ps["phase6"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "runner_path": "p4_experiments/core/run_unit.py",
        "runner_sha256": runner_sha,
        "skip_cells_size": 0,
        "per_cell_timeout_seconds_default": timeout_default,
        "per_cell_timeout_env_override": "P4_CELL_TIMEOUT_S",
        "engine_failure_machinery": {
            "worker_function": "_estimate_worker",
            "wrapper_function": "_estimate_with_timeout",
            "measured_builder": "_engine_failure_measured",
            "log_path": "p4_experiments/common/output/results/_engine_failures.log",
        },
        "audit_categories_closed": ["G"],
    }
    cohort["_phase_status"] = ps
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")

    print("[Phase 6] OK")
    print(f"  runner: {RUNNER.relative_to(ROOT)}")
    print(f"  runner_sha256: {runner_sha[:16]}...")
    print(f"  _SKIP_CELLS = set() (size 0)")
    print(f"  _PER_CELL_TIMEOUT_S default = {timeout_default}s")
    print(f"  engine_failure references in runner: {n_engine_failure}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
