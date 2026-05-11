"""Approve or reject LLM-suggested tags and merge into the registry.

Usage examples:
    # List pending suggestions
    python scripts/approve_tags.py --list

    # List all suggestions regardless of status
    python scripts/approve_tags.py --list-all

    # Approve specific tags
    python scripts/approve_tags.py --approve quantum-error-correction,idea:barren-plateaus

    # Reject specific tags
    python scripts/approve_tags.py --reject some-bad-tag
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Ensure project root is on sys.path
_STEP2_ROOT = str(Path(__file__).resolve().parents[2])
_PROJECT_ROOT = str(Path(__file__).resolve().parents[3])
for p in (_STEP2_ROOT, _PROJECT_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from shared.tools.logger import get_logger  # noqa: E402

logger = get_logger("approve_tags")

SUGGESTIONS_PATH = os.path.join(_STEP2_ROOT, "output", "tag_suggestions.json")
REGISTRY_PATH = os.path.join(_PROJECT_ROOT, "shared", "config", "unified_taxonomy.json")
STEP6_PROMPT_PATH = os.path.join(_STEP2_ROOT, "s2_classification", "prompts", "step6_synthesis.txt")

# Map suggestion categories to registry keys
CATEGORY_TO_REGISTRY_KEY = {
    "topic": "topic_tags",
    "methodology": "methodology_tags",
    "idea": "synthesis_tags",
    "contradiction": "synthesis_tags",
    "limitation": "synthesis_tags",
}

# Map suggestion categories to step6 prompt section headers
CATEGORY_TO_PROMPT_SECTION = {
    "topic": "Topic tags (assign all that apply):",
    "methodology": "Methodology tags (assign all that apply):",
    "idea": "Synthesis tags (assign all that apply):",
    "contradiction": "Synthesis tags (assign all that apply):",
    "limitation": "Synthesis tags (assign all that apply):",
}


def _load_suggestions() -> dict:
    """Load tag suggestions file."""
    if not os.path.isfile(SUGGESTIONS_PATH):
        print("No suggestions file found. Run discover_tags.py first.")
        sys.exit(1)
    with open(SUGGESTIONS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_suggestions(data: dict) -> None:
    """Write updated suggestions file."""
    with open(SUGGESTIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _load_registry() -> dict:
    """Load the tag registry."""
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_registry(registry: dict) -> None:
    """Write the tag registry."""
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)
    f_name = os.path.relpath(REGISTRY_PATH, PROJECT_ROOT)
    print(f"Updated {f_name}")


def _tag_exists_in_registry(tag: str, registry: dict) -> bool:
    """Check if a tag already exists in any registry category."""
    for category_dict in registry.values():
        if isinstance(category_dict, dict) and tag in category_dict:
            return True
    return False


def _find_suggestion(tag: str, suggestions: list[dict]) -> dict | None:
    """Find a suggestion by tag name."""
    for s in suggestions:
        if s["tag"] == tag:
            return s
    return None


def _add_to_registry(registry: dict, tag: str, category: str, description: str) -> bool:
    """Add a tag to the registry under the right category. Returns True if added."""
    registry_key = CATEGORY_TO_REGISTRY_KEY.get(category)
    if not registry_key:
        logger.warning("Unknown category '%s' for tag '%s'", category, tag)
        return False
    if registry_key not in registry:
        registry[registry_key] = {}
    registry[registry_key][tag] = description
    return True


def _append_to_step6_prompt(tag: str, category: str, description: str) -> None:
    """Append a new tag entry to the appropriate section of the step6 prompt."""
    section_header = CATEGORY_TO_PROMPT_SECTION.get(category)
    if not section_header:
        logger.warning("No prompt section for category '%s'", category)
        return

    with open(STEP6_PROMPT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the section header and the block of "- tag: description" lines after it
    # We insert the new tag at the end of that block
    pattern = re.compile(
        rf"({re.escape(section_header)}\n(?:- .+\n)*)",
        re.MULTILINE,
    )
    match = pattern.search(content)
    if not match:
        logger.warning(
            "Could not find section '%s' in step6 prompt", section_header
        )
        return

    block = match.group(1)
    new_line = f"- {tag}: {description}\n"

    # Only append if not already present
    if new_line in block:
        return

    updated_block = block + new_line
    content = content[: match.start()] + updated_block + content[match.end() :]

    with open(STEP6_PROMPT_PATH, "w", encoding="utf-8") as f:
        f.write(content)


def do_list(show_all: bool = False) -> None:
    """Print suggestions, optionally filtered to pending only."""
    data = _load_suggestions()
    suggestions = data.get("suggestions", [])

    if not show_all:
        suggestions = [s for s in suggestions if s.get("status") == "pending"]

    if not suggestions:
        status = "any" if show_all else "pending"
        print(f"No {status} suggestions found.")
        return

    for s in suggestions:
        status_marker = f"[{s.get('status', 'pending')}]" if show_all else ""
        print(
            f"  {s['tag']} (freq: {s['frequency']}) {status_marker}\n"
            f"    {s.get('description', '')}"
        )
    print(f"\n{len(suggestions)} suggestion(s) shown.")


def do_approve(tags_str: str) -> None:
    """Approve the given comma-separated tags."""
    tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
    if not tag_names:
        print("No tags specified.")
        return

    data = _load_suggestions()
    suggestions = data.get("suggestions", [])
    registry = _load_registry()

    approved = []
    for tag in tag_names:
        suggestion = _find_suggestion(tag, suggestions)
        if suggestion is None:
            print(f"  WARNING: '{tag}' not found in suggestions file — skipped")
            continue

        if _tag_exists_in_registry(tag, registry):
            print(f"  WARNING: '{tag}' already exists in registry — skipped")
            suggestion["status"] = "already-exists"
            continue

        category = suggestion.get("category", "")
        description = suggestion.get("description", "")

        if _add_to_registry(registry, tag, category, description):
            suggestion["status"] = "approved"
            _append_to_step6_prompt(tag, category, description)
            approved.append(tag)
        else:
            print(f"  WARNING: Could not add '{tag}' (unknown category '{category}')")

    if approved:
        _save_registry(registry)
        _save_suggestions(data)
        prompt_rel = os.path.relpath(STEP6_PROMPT_PATH, PROJECT_ROOT)
        print(f"Approved {len(approved)} tags: {', '.join(approved)}")
        print(f"Updated {prompt_rel}")
        print(
            "To apply new tags, re-run step 6: "
            "python scripts/run_extraction_step.py --batch --step 6"
        )
    else:
        print("No tags were approved.")


def do_reject(tags_str: str) -> None:
    """Reject the given comma-separated tags."""
    tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
    if not tag_names:
        print("No tags specified.")
        return

    data = _load_suggestions()
    suggestions = data.get("suggestions", [])

    rejected = []
    for tag in tag_names:
        suggestion = _find_suggestion(tag, suggestions)
        if suggestion is None:
            print(f"  WARNING: '{tag}' not found in suggestions file — skipped")
            continue
        suggestion["status"] = "rejected"
        rejected.append(tag)

    if rejected:
        _save_suggestions(data)
        print(f"Rejected {len(rejected)} tags: {', '.join(rejected)}")
    else:
        print("No tags were rejected.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Approve or reject LLM-suggested tags and merge into the registry."
    )
    parser.add_argument(
        "--list",
        action="store_true",
        dest="list_pending",
        help="List all pending tag suggestions.",
    )
    parser.add_argument(
        "--list-all",
        action="store_true",
        help="List all suggestions regardless of status.",
    )
    parser.add_argument(
        "--approve",
        type=str,
        default=None,
        help="Comma-separated tag names to approve.",
    )
    parser.add_argument(
        "--reject",
        type=str,
        default=None,
        help="Comma-separated tag names to reject.",
    )
    args = parser.parse_args()

    if not any([args.list_pending, args.list_all, args.approve, args.reject]):
        parser.print_help()
        return

    if args.list_pending:
        do_list(show_all=False)
    elif args.list_all:
        do_list(show_all=True)

    if args.approve:
        do_approve(args.approve)

    if args.reject:
        do_reject(args.reject)


if __name__ == "__main__":
    main()
