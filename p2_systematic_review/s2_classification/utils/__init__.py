"""Extraction utilities — frontmatter, step_runner, processing_log.

These utilities import shared tools (LLM client, logger, text_chunker)
from shared/tools/ via sys.path insertion at the project root.
"""

import sys
from pathlib import Path

# Ensure quantum-finance project root is on sys.path so 'shared.tools' resolves
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # p2_systematic_review/s2_classification/utils -> root
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from .frontmatter import read_frontmatter, update_frontmatter, write_frontmatter
from .processing_log import load_log, save_log, get_paper_status, mark_step_complete
from .step_runner import run_step, load_config

from shared.tools.llm_client import LLMClient
from shared.tools.logger import get_logger
from shared.tools.text_chunker import truncate_tokens, chunk_by_sections

__all__ = [
    "LLMClient",
    "chunk_by_sections",
    "get_logger",
    "get_paper_status",
    "load_config",
    "load_log",
    "mark_step_complete",
    "read_frontmatter",
    "run_step",
    "save_log",
    "truncate_tokens",
    "update_frontmatter",
    "write_frontmatter",
]
