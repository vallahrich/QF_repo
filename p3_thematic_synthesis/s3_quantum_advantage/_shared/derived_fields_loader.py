"""Load the derived-fields enrichment produced by derived_fields/compute_derived_fields.py."""

from __future__ import annotations

import json
from pathlib import Path

_MODULE_ROOT = Path(__file__).resolve().parent
DERIVED_PATH = (
    _MODULE_ROOT.parent / "derived_fields" / "enriched" / "derived_fields.json"
)


def load_derived_fields() -> dict[str, dict]:
    """Return a lookup keyed by f"{paper_id}_{experiment_id}"."""
    if not DERIVED_PATH.exists():
        return {}
    data = json.loads(DERIVED_PATH.read_text(encoding="utf-8"))
    lookup: dict[str, dict] = {}
    for e in data.get("enriched_experiments", []):
        key = f"{e.get('paper_id', '')}_{e.get('experiment_id', '')}"
        lookup[key] = e
    return lookup


def get_derived(lookup: dict[str, dict], paper_id: str, experiment_id: str) -> dict | None:
    return lookup.get(f"{paper_id}_{experiment_id}")
