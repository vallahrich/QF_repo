"""Single .env resolver for the quantum-finance project.

Finds and loads the project root .env file, normalizing credential names
so both SLR and analysis code can use the same environment variables.

Usage:
    from shared.tools.env_loader import load_env
    load_env()  # call once at entry points
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from ._paths import find_project_root as _find_project_root

_logger = logging.getLogger("qfin.env_loader")


PROJECT_ROOT = _find_project_root()


def load_env() -> None:
    """Load .env from the project root and normalize credential names.

    Ensures both naming conventions work:
    - AZURE_API_KEY / AZURE_ENDPOINT (analysis convention)
    - AZURE_OPENAI_API_KEY / AZURE_OPENAI_ENDPOINT (SLR convention)
    """
    env_path = PROJECT_ROOT / ".env"
    if env_path.is_file():
        load_dotenv(env_path)

    # Normalize: ensure both naming conventions are populated
    _sync_env("AZURE_API_KEY", "AZURE_OPENAI_API_KEY")
    _sync_env("AZURE_ENDPOINT", "AZURE_OPENAI_ENDPOINT")
    _sync_env("AZURE_DEPLOYMENT", "AZURE_OPENAI_DEPLOYMENT")


def _sync_env(name_a: str, name_b: str) -> None:
    """Ensure both env var names point to the same value.

    If both are set with different values, emit a warning and leave both as-is
    (added 2026-05-02 for reproducibility — silent divergence was an under-
    specified failure mode).
    """
    val_a = os.getenv(name_a)
    val_b = os.getenv(name_b)
    if val_a and not val_b:
        os.environ[name_b] = val_a
    elif val_b and not val_a:
        os.environ[name_a] = val_b
    elif val_a and val_b and val_a != val_b:
        _logger.warning(
            "env var divergence: %s and %s are both set with different values; "
            "preserving each as-is. Reconcile your .env to avoid silent drift.",
            name_a,
            name_b,
        )
