"""Generate chapter-supporting-literature reading notes.

Drafting assistance for Chapters 1 and 2. NOT analytical extraction.

Workflow:
    python -m shared.chapter_supporting_literature.scripts.make_notes <paper_id> [<paper_id> ...]
    python -m shared.chapter_supporting_literature.scripts.make_notes --all

Output:
    shared/chapter_supporting_literature/_pending/<paper_id>__<slug>.md
    Researcher reviews + moves to parent folder to accept (audit trail).

Audit:
    Every call logged via shared.tools.logger to logs/<date>_chapter_lit_notes.jsonl
    Prompt is versioned in scripts/prompt_v1.txt (PROMPT_VERSION below).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from shared.tools.llm_client import LLMClient
from shared.tools.logger import get_logger

# --- pinned configuration (bump together when prompt changes) ---
PROMPT_VERSION = "1.0"
PROMPT_DATE = "2026-05-03"
MODEL = "gpt-5-mini"
TEMPERATURE = 0.2  # dropped silently for reasoning models; logged by LLMClient
MAX_TOKENS = 16000  # reasoning models consume tokens internally; budget for both

# --- paths ---
ROOT = Path(__file__).resolve().parents[3]  # quantum-finance/
EXTRACTED_TEXT_DIR = ROOT / "shared" / "extracted_text" / "text"
P2_PROCESSED_DIR = ROOT / "p2_systematic_review" / "output" / "processed"
PENDING_DIR = ROOT / "shared" / "chapter_supporting_literature" / "_pending"
PROMPT_PATH = Path(__file__).parent / "prompt_v1.txt"

# --- selection (mirror of _selection.md) ---
SELECTION = {
    "78cc9d5068f3": "C-03",
    "3f4c5ad6749d": "C-04",
    "e6ece474516c": "C-05",
    "1961129130d1": "C-06",
    "d0568e395fbf": "C-10",
    "ea3050e19cb2": "C-11",
    "ca17c4baa8d1": "C-12",
    "04326473e1bb": "C-18",
    "246963801530": "C-19",
    "7f0f52d2eab9": "C-22",
}

logger = get_logger("chapter_lit_notes")


def _find_extracted_text(paper_id: str) -> Path:
    matches = list(EXTRACTED_TEXT_DIR.glob(f"{paper_id}_*.md"))
    if not matches:
        raise FileNotFoundError(f"No extracted text for paper_id {paper_id}")
    return matches[0]


def _short_title_slug(filename: str) -> str:
    # filename: 78cc9d5068f3_quantum_algorithms_for_portfolio_optimization.md
    stem = Path(filename).stem
    parts = stem.split("_", 1)
    if len(parts) < 2:
        return "untitled"
    title_part = parts[1]
    title_part = re.sub(r"[^a-z0-9_]", "_", title_part.lower())
    title_part = re.sub(r"_+", "_", title_part).strip("_")
    return title_part[:60]


def _render_prompt(template: str, filename_hint: str, document_text: str) -> str:
    return template.replace("{filename_hint}", filename_hint).replace(
        "{document_text}", document_text
    )


def make_note(paper_id: str, client: LLMClient, prompt_template: str) -> Path:
    if paper_id not in SELECTION:
        logger.warning("paper_id %s not in SELECTION; proceeding anyway", paper_id)

    text_path = _find_extracted_text(paper_id)
    document_text = text_path.read_text(encoding="utf-8")
    filename_hint = text_path.name

    rendered = _render_prompt(prompt_template, filename_hint, document_text)
    prompt_sha = hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()[:12]
    rendered_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:12]

    logger.info(
        "calling LLM",
        extra={
            "paper_id": paper_id,
            "model": MODEL,
            "prompt_version": PROMPT_VERSION,
            "prompt_sha": prompt_sha,
            "rendered_sha": rendered_sha,
            "doc_chars": len(document_text),
        },
    )

    response = client.simple_completion(
        model=MODEL,
        system="You are a careful research assistant producing reading notes for a thesis.",
        user=rendered,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        timeout=300,
    )

    # strip accidental ```markdown fences
    cleaned = response.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:markdown)?\s*\n", "", cleaned)
        cleaned = re.sub(r"\n```\s*$", "", cleaned)

    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    slug = _short_title_slug(text_path.name)
    out_path = PENDING_DIR / f"{paper_id}__{slug}.md"

    header = (
        f"<!-- chapter-supporting-literature reading note\n"
        f"     paper_id:        {paper_id}\n"
        f"     selection_id:    {SELECTION.get(paper_id, '(unlisted)')}\n"
        f"     source_text:     {text_path.relative_to(ROOT).as_posix()}\n"
        f"     generated_at:    {datetime.now(timezone.utc).isoformat()}\n"
        f"     model:           {MODEL}\n"
        f"     temperature:     {TEMPERATURE}\n"
        f"     prompt_version:  {PROMPT_VERSION} ({PROMPT_DATE})\n"
        f"     prompt_sha:      {prompt_sha}\n"
        f"     rendered_sha:    {rendered_sha}\n"
        f"     status:          PENDING researcher review\n"
        f"     accept by:       moving this file to ../<paper_id>__<slug>.md -->\n\n"
    )

    out_path.write_text(header + cleaned + "\n", encoding="utf-8")
    logger.info("wrote note", extra={"path": str(out_path), "paper_id": paper_id})
    return out_path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paper_ids", nargs="*", help="paper_id(s) to process")
    parser.add_argument("--all", action="store_true", help="process the full SELECTION")
    parser.add_argument(
        "--skip-existing", action="store_true",
        help="skip if a note already exists in _pending/ or parent folder",
    )
    args = parser.parse_args(argv)

    if args.all:
        targets = list(SELECTION.keys())
    elif args.paper_ids:
        targets = args.paper_ids
    else:
        parser.error("provide paper_id(s) or --all")
        return 2

    prompt_template = PROMPT_PATH.read_text(encoding="utf-8")
    client = LLMClient()

    written = []
    skipped = []
    failed = []
    parent = PENDING_DIR.parent
    for pid in targets:
        try:
            slug_glob = f"{pid}__*.md"
            if args.skip_existing and (
                list(PENDING_DIR.glob(slug_glob)) or list(parent.glob(slug_glob))
            ):
                logger.info("skipping existing note for %s", pid)
                skipped.append(pid)
                continue
            out = make_note(pid, client, prompt_template)
            written.append(out)
        except Exception as exc:  # noqa: BLE001
            logger.error("failed for %s: %s", pid, exc)
            failed.append((pid, str(exc)))

    print(json.dumps({
        "written": [str(p.relative_to(ROOT)) for p in written],
        "skipped": skipped,
        "failed": failed,
    }, indent=2))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
