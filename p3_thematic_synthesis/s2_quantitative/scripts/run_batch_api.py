"""Submit benchmark extractions as an Azure OpenAI Batch job.

The Batch API processes all papers asynchronously at 50% cost.
Flow: prepare JSONL → upload file → create batch → poll → download results.

Usage:
    # Prepare and submit all papers
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch_api --submit

    # Check status of a running batch
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch_api --status <batch_id>

    # Download results when complete
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch_api --download <batch_id>

    # Submit only specific papers
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch_api --submit --limit 10

    # Re-submit even if output exists
    python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch_api --submit --no-skip
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_project_root_str = str(_PROJECT_ROOT)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
elif sys.path[0] != _project_root_str:
    sys.path.remove(_project_root_str)
    sys.path.insert(0, _project_root_str)

_shared_mod = sys.modules.get("shared")
if _shared_mod is not None:
    _shared_file = getattr(_shared_mod, "__file__", None) or ""
    if _PROJECT_ROOT.as_posix() not in Path(_shared_file).as_posix() if _shared_file else True:
        for _key in [k for k in sys.modules if k == "shared" or k.startswith("shared.")]:
            del sys.modules[_key]

from shared.tools.llm_client import LLMClient  # noqa: E402
from shared.tools.logger import get_logger  # noqa: E402
from shared.tools.text_chunker import truncate_tokens  # noqa: E402

from p3_thematic_synthesis.s2_quantitative.scripts.extract_benchmarks import (  # noqa: E402
    _derive_paper_id,
    _load_config,
    _load_prompt,
    _parse_json_response,
)
from p3_thematic_synthesis.s2_quantitative.scripts.validate_benchmarks import (  # noqa: E402
    compute_quality_score,
    normalize_extraction_metrics,
    validate_extraction,
)

logger = get_logger("batch_api")

DEFAULT_INPUT = _PROJECT_ROOT / "shared" / "extracted_text" / "text"
OUTPUT_DIR = _QUANT_ROOT / "output" / "extractions"
BATCH_DIR = _QUANT_ROOT / "output" / "batch"


def prepare_batch_jsonl(
    input_dir: Path | None = None,
    limit: int | None = None,
    skip_existing: bool = True,
) -> Path:
    """Create a JSONL file with all extraction requests for the Batch API.

    Each line is a JSON object with custom_id, method, url, and body.
    Returns the path to the JSONL file.
    """
    in_dir = input_dir or DEFAULT_INPUT
    config = _load_config()
    system_prompt = _load_prompt()
    max_input = config.get("input_token_limit", 60000)

    papers = sorted(in_dir.glob("*.md"))
    if limit:
        papers = papers[:limit]

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    jsonl_path = BATCH_DIR / f"batch_input_{date.today().isoformat()}.jsonl"

    count = 0
    skipped = 0
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for paper_path in papers:
            paper_id = _derive_paper_id(str(paper_path))

            if skip_existing and (OUTPUT_DIR / f"{paper_id}.json").is_file():
                skipped += 1
                continue

            text = paper_path.read_text(encoding="utf-8", errors="replace")
            text = truncate_tokens(text, max_input)

            user_message = (
                f"## Paper Text\n\n{text}\n\n"
                "## Response\n\nReturn ONLY the JSON object."
            )

            request = {
                "custom_id": paper_id,
                "method": "POST",
                "url": "/chat/completions",
                "body": {
                    "model": config["model"],
                    "temperature": config.get("temperature", 0),
                    "max_completion_tokens": config.get("max_tokens", 16000),
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                },
            }

            f.write(json.dumps(request, ensure_ascii=False) + "\n")
            count += 1

    logger.info(f"Prepared {count} requests ({skipped} skipped) → {jsonl_path}")
    print(f"Prepared {count} requests ({skipped} skipped) → {jsonl_path.name}")
    return jsonl_path


def submit_batch(jsonl_path: Path) -> str:
    """Upload the JSONL file and create a batch job.

    Returns the batch ID.
    """
    client = LLMClient()

    # Upload the file
    logger.info(f"Uploading {jsonl_path.name}...")
    with open(jsonl_path, "rb") as f:
        file_response = client.azure_client.files.create(
            file=f,
            purpose="batch",
        )
    file_id = file_response.id
    logger.info(f"File uploaded: {file_id}")

    # Create batch
    batch = client.azure_client.batches.create(
        input_file_id=file_id,
        endpoint="/chat/completions",
        completion_window="24h",
    )
    batch_id = batch.id
    logger.info(f"Batch created: {batch_id}")

    # Save batch metadata
    meta = {
        "batch_id": batch_id,
        "file_id": file_id,
        "input_file": jsonl_path.name,
        "created": date.today().isoformat(),
        "status": "submitted",
    }
    meta_path = BATCH_DIR / f"batch_{batch_id}.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Batch submitted: {batch_id}")
    print(f"Check status: python -m p3_thematic_synthesis.s2_quantitative.scripts.run_batch_api --status {batch_id}")
    return batch_id


def check_status(batch_id: str) -> dict:
    """Check the status of a batch job."""
    client = LLMClient()
    batch = client.azure_client.batches.retrieve(batch_id)

    info = {
        "id": batch.id,
        "status": batch.status,
        "created_at": str(batch.created_at),
        "completed_at": str(batch.completed_at) if batch.completed_at else None,
        "total": batch.request_counts.total if batch.request_counts else 0,
        "completed": batch.request_counts.completed if batch.request_counts else 0,
        "failed": batch.request_counts.failed if batch.request_counts else 0,
        "output_file_id": batch.output_file_id,
        "error_file_id": batch.error_file_id,
    }

    print(f"Batch {batch_id}:")
    print(f"  Status: {info['status']}")
    if info["total"]:
        print(f"  Progress: {info['completed']}/{info['total']} ({info['failed']} failed)")
    if info["completed_at"]:
        print(f"  Completed: {info['completed_at']}")
    if info["output_file_id"]:
        print(f"  Output file: {info['output_file_id']}")
    return info


def download_results(batch_id: str) -> dict:
    """Download batch results and process them into individual extraction JSONs.

    Returns summary dict with counts.
    """
    client = LLMClient()
    batch = client.azure_client.batches.retrieve(batch_id)

    if batch.status != "completed":
        print(f"Batch {batch_id} is '{batch.status}', not 'completed'. Wait or check errors.")
        if batch.error_file_id:
            print(f"Error file: {batch.error_file_id}")
        return {"status": batch.status}

    if not batch.output_file_id:
        print("No output file available.")
        return {"status": "no_output"}

    # Download output JSONL
    output_content = client.azure_client.files.content(batch.output_file_id)
    output_path = BATCH_DIR / f"batch_output_{batch_id}.jsonl"
    output_path.write_bytes(output_content.read())

    config = _load_config()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    succeeded = 0
    failed = 0
    errors_list = []

    with open(output_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            result = json.loads(line)
            paper_id = result.get("custom_id", "unknown")
            response_body = result.get("response", {}).get("body", {})
            error = result.get("error")

            if error:
                failed += 1
                errors_list.append({"paper_id": paper_id, "error": str(error)})
                logger.warning(f"Batch error for {paper_id}: {error}")
                continue

            # Extract the content from the response
            choices = response_body.get("choices", [])
            if not choices:
                failed += 1
                errors_list.append({"paper_id": paper_id, "error": "no choices in response"})
                continue

            content = choices[0].get("message", {}).get("content", "")
            if not content:
                failed += 1
                errors_list.append({"paper_id": paper_id, "error": "empty content"})
                continue

            # Parse and validate
            try:
                data = _parse_json_response(content)
            except ValueError as exc:
                failed += 1
                errors_list.append({"paper_id": paper_id, "error": str(exc)})
                continue

            # Post-processing (same as extract_benchmarks.py)
            data["paper_id"] = paper_id
            data.setdefault("extraction_metadata", {})
            data["extraction_metadata"]["extraction_date"] = date.today().isoformat()
            data["extraction_metadata"]["model_used"] = config["model"]
            data["extraction_metadata"]["batch_id"] = batch_id
            data.setdefault("has_quantitative_results", len(data.get("experiments", [])) > 0)

            # Fix silo names
            fd = data.get("finance_domain") or {}
            if fd.get("primary_silo"):
                fd["primary_silo"] = fd["primary_silo"].replace("_", "-")
            if fd.get("secondary_silos"):
                fd["secondary_silos"] = [s.replace("_", "-") for s in fd["secondary_silos"]]

            # Normalize and validate
            normalize_extraction_metrics(data)
            errs, warns = validate_extraction(data)
            data["extraction_metadata"]["validation_errors"] = len(errs)
            data["extraction_metadata"]["validation_warnings"] = len(warns)

            # Quality score
            quality = compute_quality_score(data)
            data["extraction_metadata"]["quality_score"] = quality["score"]
            data["extraction_metadata"]["quality_details"] = quality

            # Save
            out_path = OUTPUT_DIR / f"{paper_id}.json"
            with open(out_path, "w", encoding="utf-8") as out_f:
                json.dump(data, out_f, indent=2, ensure_ascii=False)

            succeeded += 1

    summary = {
        "batch_id": batch_id,
        "succeeded": succeeded,
        "failed": failed,
        "errors": errors_list,
    }

    # Save summary
    summary_path = BATCH_DIR / f"batch_summary_{batch_id}.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"\nResults: {succeeded} succeeded, {failed} failed")
    if errors_list:
        print(f"Errors saved to {summary_path.name}")
        for e in errors_list[:5]:
            print(f"  {e['paper_id']}: {str(e['error'])[:80]}")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Submit benchmark extractions via Azure Batch API."
    )
    parser.add_argument(
        "--submit", action="store_true",
        help="Prepare JSONL and submit batch job.",
    )
    parser.add_argument(
        "--status", metavar="BATCH_ID",
        help="Check status of a batch job.",
    )
    parser.add_argument(
        "--download", metavar="BATCH_ID",
        help="Download results from a completed batch job.",
    )
    parser.add_argument(
        "--input-dir", default=None,
        help="Directory with paper markdown files.",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Maximum number of papers to include.",
    )
    parser.add_argument(
        "--no-skip", action="store_true",
        help="Include papers that already have extraction JSONs.",
    )
    args = parser.parse_args()

    if args.status:
        check_status(args.status)
    elif args.download:
        download_results(args.download)
    elif args.submit:
        in_dir = Path(args.input_dir) if args.input_dir else None
        jsonl_path = prepare_batch_jsonl(
            input_dir=in_dir,
            limit=args.limit,
            skip_existing=not args.no_skip,
        )
        submit_batch(jsonl_path)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
