#!/usr/bin/env python3
"""Phase 1 extraction — run the exploratory extraction prompt on a document.

Reads a PDF or text file, sends it through the extraction prompt, and saves
the structured JSON output to p1_framework_synthesis/s1_extractions/.

Usage:
    python -m p1_framework_synthesis.scripts.extract_document --pdf path/to/paper.pdf --name Author_2024_Title
    python -m p1_framework_synthesis.scripts.extract_document --text path/to/paper.txt --name Author_2024_Title
    python -m p1_framework_synthesis.scripts.extract_document --pdf paper.pdf --name Author_2024_Title --model gpt-5.1
"""

import argparse
import json
import os
import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.llm_client import LLMClient
from shared.tools.logger import get_logger
from shared.tools.text_chunker import chunk_by_sections

logger = get_logger("phase1_extraction")

PHASE1_ROOT = str(Path(__file__).resolve().parents[1])
EXTRACTIONS_DIR = os.path.join(PHASE1_ROOT, "s1_extractions")
PROMPT_PATH = os.path.join(PHASE1_ROOT, "prompts", "extraction.txt")

# Default LLM settings
DEFAULT_MODEL = "gpt-5.1"
DEFAULT_TEMPERATURE = 0.2
# max_completion_tokens must cover both reasoning and visible output.
# gpt-5.1 uses ~8K reasoning tokens on large chunks, so 16K gives 8K for JSON output.
DEFAULT_MAX_TOKENS = 16000
# Max input tokens per chunk (leave room for the prompt template)
MAX_INPUT_TOKENS = 12000
# Smaller chunk size for retry attempts
RETRY_INPUT_TOKENS = 6000
# Minimum thresholds for a "good" extraction
MIN_PROBLEMS = 1
MIN_SOLUTIONS = 1
# Maximum fraction of chunks allowed to fail JSON parsing
MAX_FAILED_CHUNK_RATIO = 0.5


def load_prompt() -> str:
    """Load the extraction prompt template."""
    with open(PROMPT_PATH, encoding="utf-8") as f:
        return f.read()


def read_pdf(pdf_path: str) -> str:
    """Extract text from a PDF using pypdf."""
    try:
        from pypdf import PdfReader  # noqa: WPS433
    except ImportError:
        logger.error(
            "pypdf is required for PDF extraction. "
            "Install with: pip install pypdf"
        )
        sys.exit(1)

    reader = PdfReader(pdf_path)
    pages = []
    for i, page in enumerate(reader.pages, 1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {i}]\n{text}")
    return "\n\n".join(pages)


def read_text(text_path: str) -> str:
    """Read a plain text or markdown file."""
    with open(text_path, encoding="utf-8") as f:
        return f.read()


def merge_extractions(results: list[dict]) -> dict:
    """Merge extraction results from multiple chunks into one.

    For metadata, use the first chunk's metadata.
    For list fields, concatenate and deduplicate by quote.
    """
    if len(results) == 1:
        return results[0]

    merged = {
        "metadata": results[0].get("metadata", {}),
        "problem_domains": [],
        "solution_approaches": [],
        "problem_solution_mappings": [],
        "key_claims": [],
        "maturity_indicators": [],
        "open_questions": [],
    }

    seen_quotes: set[str] = set()

    for result in results:
        for field in [
            "problem_domains",
            "solution_approaches",
            "problem_solution_mappings",
            "key_claims",
            "maturity_indicators",
            "open_questions",
        ]:
            for item in result.get(field, []):
                quote = item.get("quote", "")
                if quote and quote in seen_quotes:
                    continue
                if quote:
                    seen_quotes.add(quote)
                merged[field].append(item)

    return merged


def _parse_llm_response(response: str) -> dict | None:
    """Parse LLM response into a JSON dict. Returns None on failure."""
    text = response.strip()
    # Strip markdown code fences if present
    if text.startswith("```"):
        first_nl = text.index("\n") if "\n" in text else 3
        text = text[first_nl + 1:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    # Try to find JSON object if response has extra text
    if not text.startswith("{"):
        start = text.find("{")
        if start != -1:
            text = text[start:]
    if not text.endswith("}"):
        end = text.rfind("}")
        if end != -1:
            text = text[:end + 1]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def validate_extraction(result: dict, total_chunks: int, failed_chunks: int) -> tuple[bool, str]:
    """Check whether an extraction result is acceptable.

    Returns (is_valid, reason).
    """
    n_problems = len(result.get("problem_domains", []))
    n_solutions = len(result.get("solution_approaches", []))

    # Check minimum content thresholds
    if n_problems < MIN_PROBLEMS and n_solutions < MIN_SOLUTIONS:
        return False, f"Too few extractions: {n_problems} problems, {n_solutions} solutions"

    # Check chunk failure ratio
    if total_chunks > 0 and failed_chunks / total_chunks > MAX_FAILED_CHUNK_RATIO:
        return False, f"Too many chunk failures: {failed_chunks}/{total_chunks} chunks failed"

    # Check if metadata was captured (indicates the LLM processed actual content)
    metadata = result.get("metadata", {})
    if not metadata.get("title") and n_problems + n_solutions < 3:
        return False, "No metadata and sparse content — likely processed references only"

    return True, "OK"


def _run_chunks(
    chunks: list[str],
    prompt_template: str,
    client: LLMClient,
    model: str,
    temperature: float,
    max_tokens: int,
) -> tuple[list[dict], int]:
    """Process chunks through the LLM. Returns (results, failed_count)."""
    results = []
    failed = 0
    for i, chunk in enumerate(chunks, 1):
        logger.info("Processing chunk %d/%d (%d chars)", i, len(chunks), len(chunk))
        prompt = prompt_template.replace("{document_text}", chunk)

        response = client.call(
            model=model,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        parsed = _parse_llm_response(response)
        if parsed is not None:
            results.append(parsed)
        else:
            logger.error("Failed to parse LLM response for chunk %d", i)
            logger.debug("Raw response (first 500 chars):\n%s", response.strip()[:500])
            failed += 1

    return results, failed


def extract_document(
    document_text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    max_input_tokens: int = MAX_INPUT_TOKENS,
) -> dict:
    """Run extraction on a document, chunking if necessary.

    If the initial extraction fails validation, retries with smaller chunks.
    """
    prompt_template = load_prompt()
    client = LLMClient()

    chunks = chunk_by_sections(document_text, max_input_tokens)
    logger.info("Document split into %d chunk(s) (max_input=%d tokens)", len(chunks), max_input_tokens)

    results, failed = _run_chunks(chunks, prompt_template, client, model, temperature, max_tokens)

    if not results:
        logger.warning("All %d chunks failed — no usable results", len(chunks))
        merged = merge_extractions([{"metadata": {}}])
    else:
        merged = merge_extractions(results)

    # Validate
    is_valid, reason = validate_extraction(merged, total_chunks=len(chunks), failed_chunks=failed)

    if not is_valid and max_input_tokens > RETRY_INPUT_TOKENS:
        logger.warning(
            "Extraction failed validation (%s). Retrying with smaller chunks (%d tokens)...",
            reason, RETRY_INPUT_TOKENS,
        )
        # Retry with smaller chunks
        smaller_chunks = chunk_by_sections(document_text, RETRY_INPUT_TOKENS)
        logger.info("Retry: document split into %d chunk(s)", len(smaller_chunks))

        retry_results, retry_failed = _run_chunks(
            smaller_chunks, prompt_template, client, model, temperature, max_tokens,
        )

        if retry_results:
            retry_merged = merge_extractions(retry_results)
            retry_valid, retry_reason = validate_extraction(
                retry_merged, total_chunks=len(smaller_chunks), failed_chunks=retry_failed,
            )

            # Use retry result if it's better (more content or passes validation)
            retry_content = (
                len(retry_merged.get("problem_domains", []))
                + len(retry_merged.get("solution_approaches", []))
            )
            orig_content = (
                len(merged.get("problem_domains", []))
                + len(merged.get("solution_approaches", []))
            )

            if retry_valid or retry_content > orig_content:
                logger.info(
                    "Retry produced better results: %d items vs %d (valid=%s, reason=%s)",
                    retry_content, orig_content, retry_valid, retry_reason,
                )
                merged = retry_merged
                is_valid = retry_valid
                reason = retry_reason
            else:
                logger.warning("Retry did not improve results; keeping original")

    # Tag the result with extraction quality metadata
    merged["_extraction_quality"] = {
        "valid": is_valid,
        "reason": reason,
        "total_chunks": len(chunks),
        "failed_chunks": failed,
    }

    if not is_valid:
        logger.warning("Final extraction still below quality threshold: %s", reason)

    return merged


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Phase 1 exploratory extraction on a document.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--pdf", help="Path to a PDF file")
    source.add_argument("--text", help="Path to a text/markdown file")
    parser.add_argument(
        "--name",
        required=True,
        help="Output name (e.g. Author_2024_Title). .json is appended automatically.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"LLM model to use (default: {DEFAULT_MODEL})",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"LLM temperature (default: {DEFAULT_TEMPERATURE})",
    )
    args = parser.parse_args()

    # Read document
    if args.pdf:
        if not os.path.isfile(args.pdf):
            logger.error("PDF not found: %s", args.pdf)
            sys.exit(1)
        logger.info("Reading PDF: %s", args.pdf)
        document_text = read_pdf(args.pdf)
    else:
        if not os.path.isfile(args.text):
            logger.error("Text file not found: %s", args.text)
            sys.exit(1)
        logger.info("Reading text: %s", args.text)
        document_text = read_text(args.text)

    if not document_text.strip():
        logger.error("Document is empty")
        sys.exit(1)

    logger.info("Document loaded: %d characters", len(document_text))

    # Run extraction
    result = extract_document(
        document_text,
        model=args.model,
        temperature=args.temperature,
    )

    # Save output
    os.makedirs(EXTRACTIONS_DIR, exist_ok=True)
    output_name = args.name.removesuffix(".json") + ".json"
    output_path = os.path.join(EXTRACTIONS_DIR, output_name)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    logger.info("Extraction saved to: %s", output_path)

    # Print summary
    n_problems = len(result.get("problem_domains", []))
    n_solutions = len(result.get("solution_approaches", []))
    n_claims = len(result.get("key_claims", []))
    n_mappings = len(result.get("problem_solution_mappings", []))
    print(
        f"\nExtraction complete: {n_problems} problems, {n_solutions} solutions, "
        f"{n_mappings} mappings, {n_claims} claims"
    )
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
