"""Step dispatch engine — the heart of the extraction pipeline.

Loads step config, prepares prompts, calls the LLM, parses JSON responses,
and writes results to paper markdown files.
"""

import json
import os
import re
from datetime import datetime

import sys
from pathlib import Path

# Ensure project root is on sys.path for shared imports
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from shared.tools.llm_client import LLMClient
from shared.tools.logger import get_logger
from shared.tools.text_chunker import truncate_tokens
from .frontmatter import read_frontmatter, write_frontmatter, update_frontmatter
from .processing_log import mark_step_complete

logger = get_logger("step_runner")

_llm_client = LLMClient()

# p2_systematic_review root (contains s2_classification/, output/)
STEP2_ROOT = str(Path(__file__).resolve().parents[2])


def _find_project_root() -> str:
    """Return the p2_systematic_review root directory."""
    return STEP2_ROOT


def load_config() -> dict:
    """Load extraction_config.json from shared/config/."""
    config_path = os.path.join(_PROJECT_ROOT, "shared", "config", "extraction_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompt(prompt_file: str) -> str:
    """Load a prompt template from the extraction prompts/ directory.

    Args:
        prompt_file: Relative path like 'prompts/step1_classify.txt'.
    """
    # Try s2_classification/prompts/ first, then fallback
    prompt_path = os.path.join(STEP2_ROOT, "s2_classification", prompt_file)
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def run_step(paper_path: str, step_num: int, pdf_text: str = None) -> dict:
    """Run a single extraction step on a paper.

    Args:
        paper_path: Path to the paper's .md file in papers/processed/
        step_num: Which step to run (1-6)
        pdf_text: Full PDF text (required for steps 1-5, not needed for step 6)

    Returns:
        dict with the step's extracted data

    Raises:
        ValueError: If step_num is invalid or pdf_text is missing for steps 1-5.
        FileNotFoundError: If paper_path doesn't exist (for steps 2-6).
    """
    if step_num < 1 or step_num > 6:
        raise ValueError(f"Invalid step number: {step_num}. Must be 1-6.")

    if step_num <= 5 and not pdf_text:
        raise ValueError(f"pdf_text is required for step {step_num}")

    config = load_config()
    step_key = f"step{step_num}"
    step_config = config["steps"][step_key]

    model = step_config["model"]
    temperature = step_config["temperature"]
    max_tokens = step_config["max_tokens"]
    prompt_file = step_config["prompt_file"]
    input_tokens = step_config["input_tokens"]

    prompt_template = load_prompt(prompt_file)

    # Prepare the prompt with appropriate variables
    prompt = _prepare_prompt(
        paper_path, step_num, prompt_template, pdf_text, input_tokens
    )

    paper_name = os.path.basename(paper_path)
    logger.info(
        "Running step %d on %s",
        step_num,
        paper_name,
        extra={"step": step_num, "paper": paper_name, "model": model},
    )

    # Call the LLM
    response = _llm_client.call(model, prompt, temperature, max_tokens)

    # Parse the JSON response
    data = _parse_llm_json(response)
    if not data:
        logger.error(
            "Failed to parse LLM response for step %d on %s",
            step_num,
            paper_name,
        )
        return {}

    # Write results to the paper file
    _write_results(paper_path, step_num, data, model)

    # Update processing log
    mark_step_complete(paper_name, step_num, model)

    logger.info(
        "Step %d completed for %s",
        step_num,
        paper_name,
        extra={"step": step_num, "paper": paper_name},
    )

    return data


def _prepare_prompt(
    paper_path: str,
    step_num: int,
    template: str,
    pdf_text: str | None,
    input_tokens: int,
) -> str:
    """Format the prompt template with the appropriate variables."""
    if step_num == 1:
        truncated = truncate_tokens(pdf_text, input_tokens)
        return template.format(paper_text=truncated)

    if step_num in (2, 3, 4, 5):
        truncated = truncate_tokens(pdf_text, input_tokens)
        meta, _ = read_frontmatter(paper_path)
        source_type = meta.get("source_type", "unknown")
        return template.format(paper_text=truncated, source_type=source_type)

    # Step 6: read all existing sections from the markdown
    meta, body = read_frontmatter(paper_path)
    return template.format(extracted_content=body)


def _write_results(paper_path: str, step_num: int, data: dict, model: str) -> None:
    """Dispatch writing results to the appropriate step handler."""
    now = datetime.now().isoformat()

    if step_num == 1:
        _write_step1_results(paper_path, data, model, now)
    elif step_num == 2:
        _write_step2_results(paper_path, data, model, now)
    elif step_num == 3:
        _write_step3_results(paper_path, data, model, now)
    elif step_num == 4:
        _write_step4_results(paper_path, data, model, now)
    elif step_num == 5:
        _write_step5_results(paper_path, data, model, now)
    elif step_num == 6:
        _write_step6_results(paper_path, data, model, now)


def _write_step1_results(paper_path: str, data: dict, model: str, now: str) -> None:
    """Write step 1 results to frontmatter."""
    updates = {
        "source_type": data.get("source_type", ""),
        "source_type_confidence": data.get("source_type_confidence", ""),
        "auto_detected": True,
        f"step1_model": model,
        f"step1_date": now,
    }

    meta, _ = read_frontmatter(paper_path)
    steps = meta.get("steps_completed", [])
    if 1 not in steps:
        steps.append(1)
        steps.sort()
    updates["steps_completed"] = steps

    update_frontmatter(paper_path, updates)


def _write_step2_results(paper_path: str, data: dict, model: str, now: str) -> None:
    """Write step 2 results to frontmatter + Abstract summary section."""
    updates = {
        "title": data.get("title", ""),
        "authors": data.get("authors", []),
        "year": data.get("year"),
        "journal_or_venue": data.get("journal_or_venue", ""),
        "doi": data.get("doi", ""),
        "step2_model": model,
        "step2_date": now,
    }

    # Add Obsidian aliases for searchability
    title = data.get("title", "")
    if title:
        words = re.findall(r'[A-Za-z]+', title)
        stop_words = {'a', 'an', 'the', 'of', 'in', 'on', 'for', 'and', 'or', 'to', 'with', 'by', 'from', 'is', 'are', 'was', 'were'}
        significant = [w for w in words if w.lower() not in stop_words][:4]
        short_alias = ' '.join(significant)
        updates["aliases"] = [title, short_alias]

    meta, _ = read_frontmatter(paper_path)
    steps = meta.get("steps_completed", [])
    if 2 not in steps:
        steps.append(2)
        steps.sort()
    updates["steps_completed"] = steps

    update_frontmatter(paper_path, updates)

    # Write abstract summary section
    abstract = data.get("abstract_summary", "")
    if abstract:
        _write_body_section(paper_path, "Abstract summary", abstract)


def _write_step3_results(paper_path: str, data: dict, model: str, now: str) -> None:
    """Write step 3 results to Methodology section."""
    updates = {
        "step3_model": model,
        "step3_date": now,
    }

    meta, _ = read_frontmatter(paper_path)
    steps = meta.get("steps_completed", [])
    if 3 not in steps:
        steps.append(3)
        steps.sort()
    updates["steps_completed"] = steps

    update_frontmatter(paper_path, updates)

    # Build methodology section content
    parts = []
    if data.get("methodology_description"):
        parts.append(data["methodology_description"])
    if data.get("algorithms_used"):
        algos = data["algorithms_used"]
        if isinstance(algos, list):
            parts.append("\n**Algorithms used:** " + ", ".join(algos))
        else:
            parts.append(f"\n**Algorithms used:** {algos}")
    if data.get("frameworks"):
        fw = data["frameworks"]
        if isinstance(fw, list):
            parts.append("**Frameworks:** " + ", ".join(fw))
        else:
            parts.append(f"**Frameworks:** {fw}")
    if data.get("experimental_setup"):
        parts.append(f"\n**Experimental setup:** {data['experimental_setup']}")
    if data.get("dataset_used"):
        parts.append(f"\n**Dataset:** {data['dataset_used']}")

    if parts:
        _write_body_section(paper_path, "Methodology", "\n".join(parts))

    # Build experiment details section
    exp_fields = [
        ("experiment_input", "Input"),
        ("experiment_process", "Process"),
        ("experiment_output", "Output"),
        ("experiment_parameters", "Parameters"),
        ("hardware_details", "Hardware"),
        ("reproducibility_notes", "Reproducibility"),
    ]

    has_experiment_data = any(
        data.get(key) is not None and data.get(key) != ""
        for key, _ in exp_fields
    )

    if has_experiment_data:
        exp_parts = []
        for key, heading in exp_fields:
            value = data.get(key)
            exp_parts.append(f"### {heading}")
            if value is None or value == "":
                exp_parts.append("N/A")
            elif key == "experiment_parameters" and isinstance(value, dict):
                for pk, pv in value.items():
                    exp_parts.append(f"- {pk}: {pv}")
            else:
                exp_parts.append(str(value))
            exp_parts.append("")  # blank line after each subsection

        _write_body_section(
            paper_path, "Experiment details", "\n".join(exp_parts).rstrip()
        )


def _write_step4_results(paper_path: str, data: dict, model: str, now: str) -> None:
    """Write step 4 results to Findings and Quantum advantage claim sections."""
    updates = {
        "quantum_advantage_claim": data.get("quantum_advantage_claim", ""),
        "step4_model": model,
        "step4_date": now,
    }

    meta, _ = read_frontmatter(paper_path)
    steps = meta.get("steps_completed", [])
    if 4 not in steps:
        steps.append(4)
        steps.sort()
    updates["steps_completed"] = steps

    update_frontmatter(paper_path, updates)

    # Write findings section
    parts = []
    if data.get("key_findings"):
        findings = data["key_findings"]
        if isinstance(findings, list):
            for f in findings:
                parts.append(f"- {f}")
        else:
            parts.append(str(findings))
    if data.get("results_summary"):
        parts.append(f"\n**Results summary:** {data['results_summary']}")
    if data.get("performance_claims"):
        claims = data["performance_claims"]
        if isinstance(claims, list):
            parts.append("\n**Performance claims:**")
            for c in claims:
                parts.append(f"- {c}")
        else:
            parts.append(f"\n**Performance claims:** {claims}")

    if parts:
        _write_body_section(paper_path, "Findings", "\n".join(parts))

    # Write quantum advantage claim section
    qa_claim = data.get("quantum_advantage_claim", "")
    qa_detail = data.get("quantum_advantage_detail", "")
    if qa_claim:
        qa_text = f"**Classification:** {qa_claim}"
        if qa_detail:
            qa_text += f"\n\n{qa_detail}"
        _write_body_section(paper_path, "Quantum advantage claim", qa_text)


def _write_step5_results(paper_path: str, data: dict, model: str, now: str) -> None:
    """Write step 5 results to Limitations and Open questions sections."""
    updates = {
        "step5_model": model,
        "step5_date": now,
    }

    meta, _ = read_frontmatter(paper_path)
    steps = meta.get("steps_completed", [])
    if 5 not in steps:
        steps.append(5)
        steps.sort()
    updates["steps_completed"] = steps

    update_frontmatter(paper_path, updates)

    # Write limitations section
    limitations = data.get("limitations", [])
    if isinstance(limitations, list) and limitations:
        content = "\n".join(f"- {lim}" for lim in limitations)
        _write_body_section(paper_path, "Limitations", content)
    elif isinstance(limitations, str) and limitations:
        _write_body_section(paper_path, "Limitations", limitations)

    # Write open questions section
    parts = []
    if data.get("open_questions"):
        oq = data["open_questions"]
        if isinstance(oq, list):
            parts = [f"- {q}" for q in oq]
        else:
            parts = [str(oq)]
    if data.get("future_work"):
        fw = data["future_work"]
        if isinstance(fw, list):
            parts.append("\n**Future work:**")
            parts.extend(f"- {w}" for w in fw)
        elif fw:
            parts.append(f"\n**Future work:** {fw}")

    if parts:
        _write_body_section(paper_path, "Open questions", "\n".join(parts))


def _write_step6_results(paper_path: str, data: dict, model: str, now: str) -> None:
    """Write step 6 results to frontmatter tags + Key ideas and Contradictions."""
    updates = {
        "topic_tags": data.get("topic_tags", []),
        "methodology_tags": data.get("methodology_tags", []),
        "idea_tags": data.get("idea_tags", []),
        "contradiction_flags": data.get("contradiction_flags", []),
        "has_quantitative_results": data.get("has_quantitative_results", False),
        "evaluation_type": data.get("evaluation_type", ""),
        "related_papers": data.get("related_papers", []),
        "relevance_phase1": data.get("relevance_phase1", ""),
        "relevance_phase3": data.get("relevance_phase3", "not-yet-assessed"),
        "step6_model": model,
        "step6_date": now,
    }

    # Build unified Obsidian tags field (Obsidian reads "tags:" for its tag pane)
    all_tags = []
    for t in data.get("topic_tags", []):
        all_tags.append(f"topic/{t}")
    for t in data.get("methodology_tags", []):
        all_tags.append(f"method/{t}")
    for t in data.get("idea_tags", []):
        all_tags.append(t.replace(":", "/"))
    for t in data.get("contradiction_flags", []):
        all_tags.append(t.replace(":", "/"))
    updates["tags"] = all_tags

    meta, _ = read_frontmatter(paper_path)
    steps = meta.get("steps_completed", [])
    if 6 not in steps:
        steps.append(6)
        steps.sort()
    updates["steps_completed"] = steps

    update_frontmatter(paper_path, updates)

    # Write Key ideas section
    ideas = data.get("key_ideas", [])
    if isinstance(ideas, list) and ideas:
        content = "\n".join(f"- {idea}" for idea in ideas)
        _write_body_section(paper_path, "Key ideas", content)
    elif isinstance(ideas, str) and ideas:
        _write_body_section(paper_path, "Key ideas", ideas)

    # Write Contradictions section
    contradictions = data.get("contradictions", [])
    if isinstance(contradictions, list) and contradictions:
        content = "\n".join(f"- {c}" for c in contradictions)
        _write_body_section(paper_path, "Contradictions", content)
    elif isinstance(contradictions, str) and contradictions:
        _write_body_section(paper_path, "Contradictions", contradictions)


def _write_body_section(paper_path: str, section_name: str, content: str) -> None:
    """Replace a specific ## section in the paper body with new content.

    Finds the section by '## Section Name', replaces everything between that
    header and the next '## ' header (or end of file). Preserves all other
    sections. If the section doesn't exist, appends it.
    """
    meta, body = read_frontmatter(paper_path)

    # Pattern: match from '## Section Name' to just before the next '## ' or end
    pattern = re.compile(
        r"(## " + re.escape(section_name) + r")\s*\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )

    header = f"## {section_name}"
    replacement = f"{header}\n{content}"

    if pattern.search(body):
        new_body = pattern.sub(replacement, body, count=1)
    else:
        # Section doesn't exist — append it
        new_body = body.rstrip() + f"\n\n{replacement}\n"

    write_frontmatter(paper_path, meta, new_body)


def _parse_llm_json(response: str) -> dict:
    """Parse JSON from an LLM response.

    Handles common issues: markdown code fences, trailing text.
    Extracts the first valid JSON object from the response.
    Returns empty dict if parsing fails.
    """
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*\n?", "", response)
    cleaned = cleaned.strip()

    # Try direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Try extracting from first { to last }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        substring = cleaned[first_brace : last_brace + 1]
        try:
            return json.loads(substring)
        except json.JSONDecodeError:
            pass

    logger.warning(
        "Failed to parse JSON from LLM response",
        extra={"response_preview": response[:200]},
    )
    return {}
