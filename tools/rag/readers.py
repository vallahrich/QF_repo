"""File readers that turn workspace paths into LlamaIndex Document objects.

Each reader returns a list of `Document` instances with rich metadata
(`tier`, `phase`, `silo`, `paper_id`, `paper_title`, `kind`, `section_path`,
`taxonomy_codes`, `mtime`, `status`).

The indexer (`tools.rag.index`) dispatches paths to readers by `kind`
(see `config.TIERS`).
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import yaml
from llama_index.core import Document

from tools.rag import config

# ---------------------------------------------------------------------------
# paper_id_bridge enrichment
# ---------------------------------------------------------------------------
_BRIDGE_CACHE: dict[str, dict[str, str]] | None = None


def _load_bridge() -> dict[str, dict[str, str]]:
    """Load shared/bridge/paper_id_bridge.csv into {paper_id: {doi, title, ...}}."""
    global _BRIDGE_CACHE
    if _BRIDGE_CACHE is not None:
        return _BRIDGE_CACHE
    bridge_path = config.REPO_ROOT / "shared" / "bridge" / "paper_id_bridge.csv"
    out: dict[str, dict[str, str]] = {}
    if bridge_path.exists():
        with bridge_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                pid = (row.get("slr_paper_id") or "").strip()
                if pid:
                    out[pid] = {
                        "doi": (row.get("doi") or "").strip(),
                        "title": (row.get("title") or "").strip(),
                        "zotero_item_key": (row.get("zotero_item_key") or "").strip(),
                    }
    _BRIDGE_CACHE = out
    return out


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
PAPER_ID_RE = re.compile(r"^([0-9a-f]{12})(?:[_.]|$)")
TAXONOMY_CODE_RE = re.compile(r"\b((?:PD|SA)-\d{2,3})\b")


def _rel_path(path: Path) -> str:
    """Return path relative to repo root, with forward slashes."""
    try:
        return str(path.resolve().relative_to(config.REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def _mtime_iso(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def _extract_paper_id(path: Path) -> str | None:
    """Find a 12-hex paper_id in the filename (most P2/P3/raw paper files)."""
    m = PAPER_ID_RE.match(path.stem)
    return m.group(1) if m else None


def _slug_to_title(stem: str) -> str:
    """Turn '001f5dbe487a_applications_of_vedic_computing' into a readable title."""
    parts = stem.split("_")
    if parts and PAPER_ID_RE.fullmatch(parts[0]):
        parts = parts[1:]
    return " ".join(parts).strip().title()


def _base_metadata(path: Path, tier: int, kind: str) -> dict:
    rel = _rel_path(path)
    md = {
        "path": rel,
        "tier": tier,
        "phase": config.detect_phase(rel),
        "kind": kind,
        "mtime": _mtime_iso(path),
    }
    silo = config.detect_silo(rel)
    if silo:
        md["silo"] = silo
    if rel.startswith("manuscript/working/"):
        md["status"] = "draft"
    return md


def _enrich_with_paper_id(meta: dict, paper_id: str | None) -> None:
    if not paper_id:
        return
    meta["paper_id"] = paper_id
    bridge = _load_bridge().get(paper_id)
    if bridge:
        if bridge.get("title"):
            meta["paper_title"] = bridge["title"]
        if bridge.get("doi"):
            meta["doi"] = bridge["doi"]


# ---------------------------------------------------------------------------
# LaTeX reader
# ---------------------------------------------------------------------------
LATEX_COMMENT_RE = re.compile(r"(?<!\\)%.*?$", re.MULTILINE)
LATEX_SECTION_RE = re.compile(
    r"\\(chapter|section|subsection|subsubsection)\*?\{([^}]*)\}"
)


def read_tex(path: Path, tier: int) -> list[Document]:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = LATEX_COMMENT_RE.sub("", text)

    # Split on section boundaries; first chunk before the first section is preface.
    matches = list(LATEX_SECTION_RE.finditer(text))
    docs: list[Document] = []
    base = _base_metadata(path, tier, "tex")

    if not matches:
        return [Document(text=text.strip(), metadata={**base, "section_path": ""})]

    # Track section heading hierarchy
    hierarchy: list[str] = []
    last_end = 0
    spans: list[tuple[int, int, str]] = []  # (start, end, section_path)

    sections: list[tuple[int, int, str]] = []
    for i, m in enumerate(matches):
        kind = m.group(1)
        title = m.group(2).strip()
        level = {"chapter": 0, "section": 1, "subsection": 2, "subsubsection": 3}[kind]
        hierarchy = hierarchy[:level] + [title]
        section_path = " > ".join(hierarchy)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((m.end(), end, section_path))

    # Optional preface
    if matches[0].start() > 0:
        preface = text[: matches[0].start()].strip()
        if preface:
            docs.append(Document(text=preface, metadata={**base, "section_path": "<preface>"}))

    for start, end, section_path in sections:
        body = text[start:end].strip()
        if not body:
            continue
        meta = {**base, "section_path": section_path}
        # Surface taxonomy codes if present in body
        codes = sorted(set(TAXONOMY_CODE_RE.findall(body)))
        if codes:
            meta["taxonomy_codes"] = ",".join(codes)
        docs.append(Document(text=f"# {section_path}\n\n{body}", metadata=meta))
    return docs


# ---------------------------------------------------------------------------
# Markdown readers
# ---------------------------------------------------------------------------
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
MD_HEADING_RE = re.compile(r"^(#{1,4})\s+(.+?)\s*$", re.MULTILINE)


def _split_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        data = yaml.safe_load(m.group(1)) or {}
        if not isinstance(data, dict):
            data = {}
    except yaml.YAMLError:
        data = {}
    return data, text[m.end():]


def _split_markdown_by_headings(text: str, base_meta: dict) -> list[Document]:
    """Split a markdown body into one Document per section under H1/H2/H3."""
    matches = list(MD_HEADING_RE.finditer(text))
    if not matches:
        return [Document(text=text.strip(), metadata={**base_meta, "section_path": ""})]

    docs = []
    hierarchy: list[str] = []
    # Optional preface
    if matches[0].start() > 0:
        pre = text[: matches[0].start()].strip()
        if pre:
            docs.append(Document(text=pre, metadata={**base_meta, "section_path": "<preface>"}))

    for i, m in enumerate(matches):
        level = len(m.group(1))  # 1..4
        title = m.group(2).strip()
        hierarchy = hierarchy[: level - 1] + [title]
        section_path = " > ".join(hierarchy)
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[m.start():end].strip()
        if body:
            docs.append(Document(text=body, metadata={**base_meta, "section_path": section_path}))
    return docs


def read_md(path: Path, tier: int) -> list[Document]:
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = _split_frontmatter(text)
    base = _base_metadata(path, tier, "md")
    if fm:
        codes = fm.get("taxonomy_codes") or fm.get("codes")
        if isinstance(codes, list):
            base["taxonomy_codes"] = ",".join(str(c) for c in codes)
        elif isinstance(codes, str):
            base["taxonomy_codes"] = codes
        if "silo" in fm and "silo" not in base:
            base["silo"] = str(fm["silo"]).strip()
        if "paper_id" in fm:
            _enrich_with_paper_id(base, str(fm["paper_id"]).strip())
    return _split_markdown_by_headings(body, base)


def read_frontmatter_md(path: Path, tier: int) -> list[Document]:
    """Same as read_md but explicit (used for P3 thematic outputs)."""
    return read_md(path, tier)


# ---------------------------------------------------------------------------
# Raw paper reader (Tier 4)
# ---------------------------------------------------------------------------
def read_raw_paper(path: Path, tier: int) -> list[Document]:
    """One markdown per paper, ~10–80 KB, no reliable headings.

    Strategy: chunk by paragraph blocks rather than headings. Keep ~1024 tokens
    per chunk. paper_id and title go into metadata.
    """
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if not text:
        return []
    base = _base_metadata(path, tier, "raw_paper")
    pid = _extract_paper_id(path)
    if pid:
        _enrich_with_paper_id(base, pid)
        if "paper_title" not in base:
            base["paper_title"] = _slug_to_title(path.stem)

    # Paragraph-based chunking, target ~4000 chars (~1024 tokens) with ~500 char overlap.
    target = config.CHUNK_SIZES[4][0] * 4
    overlap = config.CHUNK_SIZES[4][1] * 4
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: list[str] = []
    buf: list[str] = []
    buf_len = 0
    for para in paragraphs:
        p = para.strip()
        if not p:
            continue
        if buf_len + len(p) > target and buf:
            chunks.append("\n\n".join(buf))
            # carry overlap (last paragraph or two)
            tail = buf[-1:] if len(buf[-1]) <= overlap else [buf[-1][-overlap:]]
            buf = list(tail)
            buf_len = sum(len(x) for x in buf)
        buf.append(p)
        buf_len += len(p)
    if buf:
        chunks.append("\n\n".join(buf))

    docs = []
    for i, chunk in enumerate(chunks):
        meta = {**base, "section_path": f"chunk {i+1}/{len(chunks)}"}
        docs.append(Document(text=chunk, metadata=meta))
    return docs


# ---------------------------------------------------------------------------
# JSON readers
# ---------------------------------------------------------------------------
def _stringify_record(record, *, max_chars: int = 4000) -> str:
    """Render a JSON value as readable text for embedding."""
    s = json.dumps(record, indent=2, ensure_ascii=False, default=str)
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "\n... (truncated)"


def read_json_records(path: Path, tier: int) -> list[Document]:
    """Per-record JSON: each top-level dict key OR list item becomes a chunk.

    Common shapes handled:
    - dict with metadata + lists of records (e.g., problem_domains, solution_approaches)
    - flat dict: emitted as one Document
    - list of records: each item becomes one Document
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []

    base = _base_metadata(path, tier, "json")
    pid = _extract_paper_id(path)
    if pid:
        _enrich_with_paper_id(base, pid)

    # Check for an embedded paper_id in the JSON itself
    if isinstance(data, dict) and "paper_id" in data and "paper_id" not in base:
        _enrich_with_paper_id(base, str(data["paper_id"]).strip())

    docs: list[Document] = []

    if isinstance(data, list):
        for i, item in enumerate(data):
            text = _stringify_record(item)
            meta = {**base, "section_path": f"record[{i}]"}
            codes = sorted(set(TAXONOMY_CODE_RE.findall(text)))
            if codes:
                meta["taxonomy_codes"] = ",".join(codes)
            docs.append(Document(text=text, metadata=meta))
        return docs

    if isinstance(data, dict):
        # Special-case: list-valued sections become per-item chunks; scalar sections lumped into one.
        scalar_block: dict = {}
        for key, value in data.items():
            if isinstance(value, list) and value and isinstance(value[0], (dict, list)):
                for i, item in enumerate(value):
                    text = _stringify_record({key: item})
                    meta = {**base, "section_path": f"{key}[{i}]"}
                    codes = sorted(set(TAXONOMY_CODE_RE.findall(text)))
                    if codes:
                        meta["taxonomy_codes"] = ",".join(codes)
                    docs.append(Document(text=text, metadata=meta))
            else:
                scalar_block[key] = value
        if scalar_block:
            text = _stringify_record(scalar_block)
            meta = {**base, "section_path": "metadata"}
            docs.insert(0, Document(text=text, metadata=meta))
        return docs

    # Anything else: dump as single chunk
    return [Document(text=_stringify_record(data), metadata={**base, "section_path": ""})]


def read_json_single(path: Path, tier: int) -> list[Document]:
    """Render the entire JSON file as a single chunk (small config files)."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []
    base = _base_metadata(path, tier, "json")
    text = _stringify_record(data, max_chars=12000)
    return [Document(text=text, metadata={**base, "section_path": ""})]


# ---------------------------------------------------------------------------
# YAML reader
# ---------------------------------------------------------------------------
def read_yaml(path: Path, tier: int) -> list[Document]:
    text = path.read_text(encoding="utf-8", errors="replace")
    base = _base_metadata(path, tier, "yaml")
    # If the file is small, ship as one chunk; otherwise split on top-level keys.
    if len(text) < 8000:
        return [Document(text=text, metadata={**base, "section_path": ""})]
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return [Document(text=text[:12000], metadata={**base, "section_path": ""})]
    if not isinstance(data, dict):
        return [Document(text=text[:12000], metadata={**base, "section_path": ""})]
    docs = []
    for key, value in data.items():
        body = yaml.safe_dump({key: value}, sort_keys=False, allow_unicode=True)
        meta = {**base, "section_path": str(key)}
        docs.append(Document(text=body, metadata=meta))
    return docs


# ---------------------------------------------------------------------------
# BibTeX reader (abstract-only)
# ---------------------------------------------------------------------------
BIB_ENTRY_RE = re.compile(r"@\w+\s*\{([^,]+),(.*?)\n\}\s*", re.DOTALL)
BIB_FIELD_RE = re.compile(r"(\w+)\s*=\s*[{\"]\s*(.*?)\s*[}\"]\s*[,]?", re.DOTALL)


def read_bib(path: Path, tier: int) -> list[Document]:
    text = path.read_text(encoding="utf-8", errors="replace")
    docs = []
    base = _base_metadata(path, tier, "bib")
    for match in BIB_ENTRY_RE.finditer(text):
        cite_key = match.group(1).strip()
        body = match.group(2)
        fields = {k.lower(): v.strip() for k, v in BIB_FIELD_RE.findall(body)}
        title = fields.get("title", "").replace("\n", " ").strip()
        authors = fields.get("author", "").replace("\n", " ").strip()
        year = fields.get("year", "").strip()
        abstract = fields.get("abstract", "").replace("\n", " ").strip()
        if not (title or abstract):
            continue
        text_block = f"@{cite_key}\nTitle: {title}\nAuthors: {authors}\nYear: {year}\n\nAbstract:\n{abstract}"
        meta = {
            **base,
            "section_path": cite_key,
            "cite_key": cite_key,
            "year": year,
        }
        docs.append(Document(text=text_block, metadata=meta))
    return docs


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------
READERS = {
    "tex": read_tex,
    "md": read_md,
    "frontmatter_md": read_frontmatter_md,
    "raw_paper": read_raw_paper,
    "json_records": read_json_records,
    "json_single": read_json_single,
    "yaml": read_yaml,
    "bib": read_bib,
}


def read(path: Path, kind: str, tier: int) -> list[Document]:
    """Dispatch a path to the appropriate reader."""
    reader = READERS.get(kind)
    if reader is None:
        raise ValueError(f"unknown reader kind: {kind}")
    try:
        return reader(path, tier)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"  ! reader failed for {path}: {exc}")
        return []


def discover(tier: int) -> Iterable[tuple[Path, str]]:
    """Yield (path, kind) for every file in `tier` after applying excludes."""
    for root_rel, glob, kind in config.TIERS[tier]:
        root = (config.REPO_ROOT / root_rel).resolve()
        if not root.exists():
            continue
        for path in root.glob(glob):
            if not path.is_file():
                continue
            if config.is_excluded(path):
                continue
            yield path, kind
