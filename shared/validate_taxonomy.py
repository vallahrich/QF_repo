"""DEPRECATED — delegates to `tools.verify.v2_consistency`.

The original implementation only verified that PD/SA `slr_id` substrings
appeared in a single Phase-2 markdown file (a near no-op). The real
cross-file consistency surface — taxonomy ↔ silo_inclusion ↔ folder
structure ↔ retraction markers — now lives in
`tools.verify.v2_consistency`.

This shim is kept so that any legacy command lines or scripts pointing
at `python shared/validate_taxonomy.py` continue to work.

Run (preferred):
    python -m tools.verify.v2_consistency

Run (legacy, equivalent):
    python shared/validate_taxonomy.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the repo root importable so `tools.verify.v2_consistency` resolves.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.verify.v2_consistency import main as _v2_main  # noqa: E402


if __name__ == "__main__":
    print("[shared/validate_taxonomy.py] delegating to tools.verify.v2_consistency")
    sys.exit(_v2_main())
