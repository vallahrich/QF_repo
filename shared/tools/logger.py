"""Structured JSON-lines logging for all pipeline steps.

Provides a shared logger factory that writes JSON-lines to a logs/ directory
and human-readable output to stderr.
"""

import json
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from ._paths import find_project_root as _find_project_root


@lru_cache(maxsize=1)
def _git_sha() -> str:
    """Return the short git SHA of the working tree, or 'unknown'.

    Cached for the process lifetime; harmless if git is missing.
    """
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(_find_project_root()),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=2,
        )
        return out.strip() or "unknown"
    except Exception:
        return "unknown"


class _JsonFormatter(logging.Formatter):
    """Format log records as JSON-lines."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            # Reproducibility (added 2026-05-02 freeze): pin every line to a
            # process + git revision so logs from concurrent runs can be
            # disambiguated and cross-referenced against the repo state.
            "pid": os.getpid(),
            "git_sha": _git_sha(),
        }
        # Include any extra fields passed via the `extra` kwarg
        _base_keys = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__)
        for key in record.__dict__:
            if key not in _base_keys and key not in ("message", "msg"):
                entry[key] = record.__dict__[key]
        return json.dumps(entry)


class _ConsoleFormatter(logging.Formatter):
    """Human-readable console format: LEVEL: message."""

    def format(self, record: logging.LogRecord) -> str:
        return f"{record.levelname}: {record.getMessage()}"


def get_logger(name: str) -> logging.Logger:
    """Return a logger that writes JSON-lines to logs/ and outputs to stderr.

    File handler: logs/{YYYY-MM-DD}_{name}.jsonl at DEBUG level.
    Console handler: stderr at INFO level in human-readable format.
    Avoids adding duplicate handlers on repeated calls.
    """
    logger = logging.getLogger(f"qfin.{name}")

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Ensure logs/ directory exists at project root
    root = _find_project_root()
    logs_dir = root / "logs"
    logs_dir.mkdir(exist_ok=True)

    # File handler — JSON-lines
    date_str = datetime.now().strftime("%Y-%m-%d")
    log_file = logs_dir / f"{date_str}_{name}.jsonl"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_JsonFormatter())
    logger.addHandler(file_handler)

    # Console handler — human-readable on stderr
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(_ConsoleFormatter())
    logger.addHandler(console_handler)

    return logger
