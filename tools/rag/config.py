"""Configuration for the offline RAG tool.

Edit include/exclude rules here. After editing, rerun:
    python -m tools.rag.index --rebuild
"""
from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
RAG_DIR = REPO_ROOT / "tools" / "rag"
CHROMA_DIR = RAG_DIR / ".chroma"
STATE_FILE = CHROMA_DIR / "_state.json"
MANIFEST_PATH = RAG_DIR / "INDEX_MANIFEST.md"
COLLECTION_NAME = "quantum_finance"

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
OLLAMA_BASE_URL = "http://localhost:11434"
EMBED_MODEL = "nomic-embed-text"
LLM_DEFAULT = "qwen2.5:14b-instruct-q4_K_M"
LLM_DEEP = "qwen2.5:32b-instruct-q4_K_M"

# Generation context window (Ollama default is too small for RAG).
LLM_NUM_CTX = 16384

# ---------------------------------------------------------------------------
# Retrieval defaults
# ---------------------------------------------------------------------------
DEFAULT_TOP_K = 8

# ---------------------------------------------------------------------------
# Chunking (per tier)
# ---------------------------------------------------------------------------
# Token sizes are approximate (1 token ≈ 4 chars in English).
CHUNK_SIZES = {
    1: (800, 100),    # Documentation: dense prose, smaller chunks for precision
    2: (800, 100),    # Pipeline outputs
    3: (1200, 0),     # Per-paper extraction JSONs: one record per chunk, no overlap
    4: (1024, 128),   # Raw paper texts: larger chunks for context
}
BIB_CHUNK_TOKENS = 600  # one entry per chunk, capped

# Skip files larger than this (likely data dumps, not prose).
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MB

# ---------------------------------------------------------------------------
# Tier definitions
# ---------------------------------------------------------------------------
# Each tier is a list of (root_relative_path, glob_pattern, kind) tuples.
# `kind` controls which reader is used: tex, md, json_records, json_single,
# yaml, raw_paper, bib, frontmatter_md.
TIERS: dict[int, list[tuple[str, str, str]]] = {
    1: [
        # Manuscript chapters & appendix (LaTeX)
        ("manuscript/03_Chapters", "**/*.tex", "tex"),
        ("manuscript/04_Appendix", "**/*.tex", "tex"),
        # In-progress drafts (will be tagged status=draft)
        ("manuscript/working", "**/*.md", "md"),
        # Project documentation
        ("docs", "**/*.md", "md"),
        ("docs", "PROJECT_STATE.yaml", "yaml"),
        # Per-phase READMEs and high-level docs
        ("p1_framework_synthesis", "*.md", "md"),
        ("p2_systematic_review", "*.md", "md"),
        ("p3_thematic_synthesis", "*.md", "md"),
        ("p3_thematic_synthesis/docs", "**/*.md", "md"),
        ("p4_experiments", "*.md", "md"),
        # Root project files
        (".", "README.md", "md"),
        (".", "CONTRIBUTING.md", "md"),
        # Bibliography abstracts
        ("manuscript/07_Bibliography", "*.bib", "bib"),
    ],
    2: [
        # P1 outputs
        ("p1_framework_synthesis/s4_outputs", "**/*.md", "md"),
        ("p1_framework_synthesis", "audit-trail.md", "md"),
        ("p1_framework_synthesis", "REVIEW_CHECKLIST.md", "md"),
        # P2 outputs
        ("p2_systematic_review/s1_slr", "**/*.md", "md"),
        ("p2_systematic_review/s2_classification", "**/*.md", "md"),
        # P3 synthesized findings (s4 thematic coding, s5 cross-silo, s6 silo framing)
        ("p3_thematic_synthesis/s1_silo_scoping", "**/*.md", "md"),
        ("p3_thematic_synthesis/s4_thematic_coding", "**/*.md", "frontmatter_md"),
        ("p3_thematic_synthesis/s5_cross_silo", "**/*.md", "frontmatter_md"),
        ("p3_thematic_synthesis/s6_silo_framing", "**/*.md", "frontmatter_md"),
        # P4 results
        ("p4_experiments", "**/RESULTS*.md", "md"),
        ("p4_experiments", "**/README.md", "md"),
        ("p4_experiments/common", "*.json", "json_single"),
        # Shared config (taxonomy etc.)
        ("shared/config", "*.json", "json_single"),
        ("shared/config", "*.yaml", "yaml"),
    ],
    3: [
        # P1 per-paper extractions (~30 high-priority surveys)
        ("p1_framework_synthesis/s1_extractions", "*.json", "json_records"),
        # P2 per-paper extractions (~777 files)
        ("p2_systematic_review/output/processed", "*_extraction.json", "json_records"),
        # P3 quantitative extractions (per-paper structured)
        ("p3_thematic_synthesis/s2_quantitative/output", "**/*.json", "json_records"),
        # P3 thematic coding per-paper memos & codes
        ("p3_thematic_synthesis/s4_thematic_coding/papers", "*.json", "json_records"),
        # P3 silo framing extractions
        ("p3_thematic_synthesis/s6_silo_framing/extractions", "**/*.json", "json_records"),
        # _v2_phase3_rextract canonical experiment-level extractions
        ("_v2_phase3_rextract/canonical", "*.json", "json_records"),
        ("_v2_phase3_rextract/extractions", "*.json", "json_records"),
    ],
    4: [
        # Raw paper full-texts (~777 markdowns)
        ("shared/extracted_text/text", "*.md", "raw_paper"),
    ],
}

# ---------------------------------------------------------------------------
# Hard exclude rules (any path containing these segments is dropped).
# ---------------------------------------------------------------------------
EXCLUDE_SUBSTRINGS = (
    "/_archive/",
    "/archive/",
    "/__pycache__/",
    "/.git/",
    "/.venv/",
    "/node_modules/",
    "/excluded_non_english/",
    "/manuscript/01_Preamble/",
    "/manuscript/02_Front/",
    "/manuscript/05_Figures/",
    "/manuscript/07_Bibliography/raw/",
    "/_v2_phase3_rextract/triage/",
    "/_v2_phase3_rextract/prompts/",
    "/p3_thematic_synthesis/_archive/",
)
EXCLUDE_SUFFIXES = (
    ".aux", ".bbl", ".bcf", ".blg", ".fdb_latexmk", ".fls",
    ".lof", ".lot", ".log", ".out", ".run.xml", ".synctex.gz",
    ".toc", ".nav", ".snm", ".vrb", ".pdf",
)

# ---------------------------------------------------------------------------
# Known silos (used to tag chunks via path inspection)
# ---------------------------------------------------------------------------
SILOS = (
    "credit_lending",
    "derivative_pricing",
    "fraud_detection",
    "insurance_actuarial",
    "portfolio_optimization",
    "quantum_ml_finance",
    "risk_management",
    "simulation_monte_carlo",
    "trading_execution",
    "cross_silo_other",
    "cross_silo",
)


def detect_silo(path_str: str) -> str | None:
    """Return the first known silo name found in the path, or None."""
    parts = {p.lower() for p in path_str.replace("\\", "/").split("/")}
    for silo in SILOS:
        if silo in parts:
            return silo
    return None


def detect_phase(path_str: str) -> str:
    """Map a workspace-relative path to a coarse phase tag."""
    p = path_str.replace("\\", "/")
    if p.startswith("manuscript/"):
        return "manuscript"
    if p.startswith("docs/"):
        return "docs"
    if p.startswith("shared/"):
        return "shared"
    if p.startswith("p1_"):
        return "p1"
    if p.startswith("p2_"):
        return "p2"
    if p.startswith("p3_") or p.startswith("_v2_phase3"):
        return "p3"
    if p.startswith("p4_"):
        return "p4"
    return "root"


def is_excluded(path: Path) -> bool:
    """Return True if this path should be skipped."""
    s = "/" + str(path).replace("\\", "/").lstrip("/")
    if any(sub in s for sub in EXCLUDE_SUBSTRINGS):
        return True
    if path.suffix.lower() in EXCLUDE_SUFFIXES:
        return True
    try:
        if path.is_file() and path.stat().st_size > MAX_FILE_BYTES:
            return True
    except OSError:
        return True
    return False
