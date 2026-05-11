"""Extract quantitative benchmark data from a single paper using LLM.

.. deprecated::
    This is the LEGACY single-step extractor. The canonical extraction
    pipeline is ``run_extraction.py`` (3-step cached-prefix architecture),
    which now includes the same validation and quality scoring that this
    module provides.  Use ``run_extraction.py --paper-id <ID>`` instead.

Reads a paper's extracted markdown text, sends it to Azure OpenAI with
the benchmark extraction prompt, parses and validates the JSON response,
and saves the result to output/extractions/{paper_id}.json.

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.extract_benchmarks \\
        shared/extracted_text/text/02db829631f9_quantum_optimization_for_portfolio.md
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_P3_ROOT = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Ensure project root is first on sys.path so our 'shared' package wins
# over any same-named package from other projects on PYTHONPATH.
_project_root_str = str(_PROJECT_ROOT)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
elif sys.path[0] != _project_root_str:
    sys.path.remove(_project_root_str)
    sys.path.insert(0, _project_root_str)

_p3_str = str(_P3_ROOT)
if _p3_str not in sys.path:
    sys.path.insert(1, _p3_str)

# Clear any cached 'shared' module that came from a different path
_shared_mod = sys.modules.get("shared")
if _shared_mod is not None:
    _shared_file = getattr(_shared_mod, "__file__", None) or ""
    if _PROJECT_ROOT.as_posix() not in Path(_shared_file).as_posix() if _shared_file else True:
        for _key in [k for k in sys.modules if k == "shared" or k.startswith("shared.")]:
            del sys.modules[_key]

from shared.tools.llm_client import LLMClient  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from shared.tools.text_chunker import truncate_tokens  # noqa: E402

from p3_thematic_synthesis.s2_quantitative.scripts.validate_benchmarks import (  # noqa: E402
    compute_quality_score,
    normalize_extraction_metrics,
    validate_extraction,
)

logger = get_logger("extract_benchmarks")

CONFIG_PATH = _QUANT_ROOT / "config" / "extraction_config.json"
PROMPT_PATH = _QUANT_ROOT / "prompts" / "benchmark_extraction.txt"
OUTPUT_DIR = _QUANT_ROOT / "output" / "extractions"


def _load_config() -> dict:
    """Load quantitative extraction configuration."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_prompt() -> str:
    """Load the benchmark extraction system prompt."""
    with open(PROMPT_PATH, encoding="utf-8") as f:
        return f.read()


def _derive_paper_id(filepath: str) -> str:
    """Extract paper_id (first 12 hex chars) from the filename.

    Filenames follow the pattern: {12-char-hex}_{slug}.md
    Falls back to the first 40 characters of the stem.
    """
    name = Path(filepath).stem
    match = re.match(r"^([0-9a-f]{12})", name)
    if match:
        return match.group(1)
    return name[:40]


def _parse_json_response(response: str) -> dict:
    """Parse JSON from the LLM response, handling code fences.

    Raises ValueError if parsing fails.
    """
    # Strip markdown code fences if present
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", response).strip()
    cleaned = cleaned.rstrip("`").strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try to find the outermost JSON object
    first = cleaned.find("{")
    last = cleaned.rfind("}")
    if first != -1 and last > first:
        try:
            return json.loads(cleaned[first : last + 1])
        except json.JSONDecodeError:
            pass

    raise ValueError(
        f"Could not parse JSON from LLM response (length={len(response)}). "
        f"First 200 chars: {response[:200]}"
    )


def extract_paper(
    paper_path: str,
    output_dir: str | None = None,
) -> dict:
    """Extract benchmark data from a single paper.

    Args:
        paper_path: Path to the paper markdown file.
        output_dir: Directory to save the output JSON.
                    Defaults to output/extractions/ within the quantitative folder.

    Returns:
        The extracted and validated benchmark data dict.

    Raises:
        FileNotFoundError: If paper_path does not exist.
        RuntimeError: If LLM call fails after retries.
        ValueError: If JSON parsing fails.
    """
    paper_path = Path(paper_path)
    if not paper_path.is_file():
        raise FileNotFoundError(f"Paper not found: {paper_path}")

    config = _load_config()
    system_prompt = _load_prompt()
    paper_id = _derive_paper_id(str(paper_path))

    # Read and truncate paper text to fit context window
    text = paper_path.read_text(encoding="utf-8", errors="replace")
    max_input = config.get("input_token_limit", 60000)
    text = truncate_tokens(text, max_input)

    logger.info(
        "Starting extraction",
        extra={"paper_id": paper_id, "text_chars": len(text)},
    )

    # Call LLM with system/user message pattern
    client = LLMClient()
    user_message = (
        f"## Paper Text\n\n{text}\n\n"
        "## Response\n\nReturn ONLY the JSON object."
    )

    response = client.simple_completion(
        model=config["model"],
        system=system_prompt,
        user=user_message,
        temperature=config.get("temperature", 1),
        max_tokens=config.get("max_tokens", 16000),
    )

    # Retry with truncated input if response is empty
    if not response.strip() and config.get("retry_with_truncation"):
        retry_limit = config.get("retry_input_token_limit", 30000)
        truncated = truncate_tokens(
            paper_path.read_text(encoding="utf-8", errors="replace"),
            retry_limit,
        )
        logger.info(
            "Empty response — retrying with truncated input",
            extra={"paper_id": paper_id, "retry_tokens": retry_limit},
        )
        user_message = (
            f"## Paper Text\n\n{truncated}\n\n"
            "## Response\n\nReturn ONLY the JSON object."
        )
        response = client.simple_completion(
            model=config["model"],
            system=system_prompt,
            user=user_message,
            temperature=config.get("temperature", 1),
            max_tokens=config.get("max_tokens", 16000),
        )

    # Parse the JSON response
    data = _parse_json_response(response)

    # Ensure required top-level fields
    data["paper_id"] = paper_id
    data.setdefault("extraction_metadata", {})
    data["extraction_metadata"]["extraction_date"] = date.today().isoformat()
    data["extraction_metadata"]["model_used"] = config["model"]
    data["extraction_metadata"]["source_file"] = paper_path.name
    data.setdefault("has_quantitative_results", len(data.get("experiments", [])) > 0)

    # Fix common silo name issues (underscore vs hyphen)
    fd = data.get("finance_domain") or {}
    if fd.get("primary_silo"):
        fd["primary_silo"] = fd["primary_silo"].replace("_", "-")
    if fd.get("secondary_silos"):
        fd["secondary_silos"] = [s.replace("_", "-") for s in fd["secondary_silos"]]

    # Normalize metric names to canonical forms
    normalize_extraction_metrics(data)

    # Validate
    errors, warnings = validate_extraction(data)
    data["extraction_metadata"]["validation_errors"] = len(errors)
    data["extraction_metadata"]["validation_warnings"] = len(warnings)

    # Compute quality score
    quality = compute_quality_score(data)
    data["extraction_metadata"]["quality_score"] = quality["score"]
    data["extraction_metadata"]["quality_details"] = quality

    if errors:
        logger.warning(
            "Validation errors in extraction",
            extra={"paper_id": paper_id, "error_count": len(errors), "errors": errors},
        )
    if warnings:
        logger.info(
            "Validation warnings",
            extra={"paper_id": paper_id, "warning_count": len(warnings)},
        )

    # Save output
    out_dir = Path(output_dir) if output_dir else OUTPUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{paper_id}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    n_exp = len(data.get("experiments", []))
    logger.info(
        "Extraction complete",
        extra={
            "paper_id": paper_id,
            "experiments": n_exp,
            "has_quantitative": data.get("has_quantitative_results", False),
            "validation_errors": len(errors),
            "output": str(out_path),
        },
    )

    return data


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract benchmark data from a single paper."
    )
    parser.add_argument("paper_path", help="Path to the paper markdown file.")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for the JSON file.",
    )
    args = parser.parse_args()

    data = extract_paper(args.paper_path, args.output_dir)

    n_exp = len(data.get("experiments", []))
    has_q = data.get("has_quantitative_results", False)
    errs = data.get("extraction_metadata", {}).get("validation_errors", 0)
    print(
        f"Extracted: {data['paper_id']} | "
        f"{n_exp} experiments | "
        f"quantitative={has_q} | "
        f"validation_errors={errs}"
    )


if __name__ == "__main__":
    main()
