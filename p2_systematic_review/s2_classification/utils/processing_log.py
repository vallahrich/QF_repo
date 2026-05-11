"""Manage the processing_log.json file that tracks extraction step completion."""

import json
import os
import threading
from datetime import datetime

import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.logger import get_logger

logger = get_logger("processing_log")

# Module-level lock for thread-safe read-modify-write cycles on processing_log.json
_lock = threading.Lock()

# p2_systematic_review root
STEP2_ROOT = str(Path(__file__).resolve().parents[2])


def _log_path() -> str:
    """Return the absolute path to processing_log.json."""
    return os.path.join(STEP2_ROOT, "processing_log.json")


def load_log() -> dict:
    """Load the processing log from processing_log.json. Returns the full dict."""
    path = _log_path()
    if not os.path.isfile(path):
        logger.warning("processing_log.json not found, returning empty log")
        return {"papers": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_log(log: dict) -> None:
    """Write the processing log back to processing_log.json."""
    path = _log_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
        f.write("\n")
    logger.debug("Saved processing log to %s", path)


def get_paper_status(paper_name: str) -> dict:
    """Get the status dict for a specific paper. Returns {} if not found."""
    log = load_log()
    return log.get("papers", {}).get(paper_name, {})


def mark_step_complete(paper_name: str, step: int, model: str) -> None:
    """Mark a step as completed for a paper.

    - Adds step number to steps_completed list (no duplicates, sorted)
    - Records step{N}_date as current ISO timestamp
    - Records step{N}_model
    - Updates last_updated timestamp

    Thread-safe: uses module-level lock around full read-modify-write cycle.
    """
    with _lock:
        log = load_log()
        papers = log.setdefault("papers", {})
        entry = papers.setdefault(paper_name, {})

        steps = entry.get("steps_completed", [])
        if step not in steps:
            steps.append(step)
            steps.sort()
        entry["steps_completed"] = steps

        now = datetime.now().isoformat()
        entry[f"step{step}_date"] = now
        entry[f"step{step}_model"] = model
        entry["last_updated"] = now

        save_log(log)
    logger.info(
        "Marked step %d complete for %s (model=%s)", step, paper_name, model
    )


def get_incomplete_papers(step: int) -> list[str]:
    """Return paper names that have NOT completed the given step."""
    log = load_log()
    result = []
    for name, entry in log.get("papers", {}).items():
        if step not in entry.get("steps_completed", []):
            result.append(name)
    return result


def get_papers_by_filter(key: str, value) -> list[str]:
    """Return paper names where log[paper][key] == value."""
    log = load_log()
    return [
        name
        for name, entry in log.get("papers", {}).items()
        if entry.get(key) == value
    ]


def update_paper_field(paper_name: str, key: str, value) -> None:
    """Update an arbitrary field in a paper's log entry.

    Thread-safe: uses module-level lock around full read-modify-write cycle.
    """
    with _lock:
        log = load_log()
        papers = log.setdefault("papers", {})
        entry = papers.setdefault(paper_name, {})
        entry[key] = value
        save_log(log)
    logger.debug("Updated %s.%s = %s", paper_name, key, value)
