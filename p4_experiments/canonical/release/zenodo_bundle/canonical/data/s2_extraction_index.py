"""Helpers for resolving P3 S2 quantitative extractions for P4 labels."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
S2_EXTRACTIONS = ROOT / "p3_thematic_synthesis" / "s2_quantitative" / "output" / "extractions"
S2_EXTRACTIONS_REL = "p3_thematic_synthesis/s2_quantitative/output/extractions"


def s2_extraction_path(entry: dict[str, Any]) -> Path:
    return S2_EXTRACTIONS / f"{entry['paper_id']}.json"


def s2_extraction_relpath(entry: dict[str, Any]) -> str:
    return f"{S2_EXTRACTIONS_REL}/{entry['paper_id']}.json"


def s2_extraction_sha256(entry: dict[str, Any]) -> str:
    path = s2_extraction_path(entry)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def s2_experiment(entry: dict[str, Any]) -> dict[str, Any] | None:
    path = s2_extraction_path(entry)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    experiment_id = entry.get("experiment_id")
    for experiment in data.get("experiments", []):
        if experiment.get("experiment_id") == experiment_id:
            return experiment
    return None


def has_s2_experiment(entry: dict[str, Any]) -> bool:
    return s2_experiment(entry) is not None