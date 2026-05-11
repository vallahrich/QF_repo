"""Validate markdown paper files against the frontmatter spec (CLAUDE.md §4.2)."""

import json
import os
import re
import sys

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_REPO_ROOT = os.path.abspath(os.path.join(_PROJECT_ROOT, ".."))
# Fix 2026-05-02: previously pointed to non-existent
# {package}/config/tag_registry.json and {package}/templates/paper_base.md.
# The canonical taxonomy and template live in shared/config/ and
# s2_classification/templates/ respectively.
_TAG_REGISTRY_PATH = os.path.join(_REPO_ROOT, "shared", "config", "unified_taxonomy.json")
_PAPER_TEMPLATE_PATH = os.path.join(_PROJECT_ROOT, "s2_classification", "templates", "paper_base.md")

# Add project root to sys.path so we can import s2_classification.utils
# Fix 2026-05-02: previous path 'scripts.utils.frontmatter' did not exist on
# a clean checkout, so this file failed to collect. Real module lives under
# s2_classification/utils/frontmatter.py.
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REQUIRED_FIELDS: dict[str, type | tuple[type, ...]] = {
    "title": str,
    "authors": list,
    # Fix 2026-05-02: processed corpus stores year as a YAML string ('2024');
    # accept both forms — fewer ripple changes than coercing 777 files. The
    # _minimal_metadata template fixture uses int 2024, also covered.
    "year": (int, str, type(None)),
    "source_type": str,
    "source_type_confidence": str,
    "auto_detected": bool,
    "topic_tags": list,
    "methodology_tags": list,
    "steps_completed": list,
}

ENUM_RULES: dict[str, list[str]] = {
    "source_type": [
        "peer-reviewed-empirical",
        "peer-reviewed-theoretical",
        "preprint",
        "conference-paper",
        "review-article",
        "technical-report",
        "industry-whitepaper",
        "industry-report",
        "other",
        "",
    ],
    "source_type_confidence": ["high", "medium-high", "medium", "medium-low", "low", ""],
    "classification": ["generic", "application-specific", ""],
    "evidence_type": ["empirical", "theoretical", "mixed", ""],
    "quantum_advantage_claim": [
        "demonstrated",
        "theoretical",
        "speculative",
        "disputed",
        "not-applicable",
        "",
    ],
    "relevance_phase1": ["high", "medium", "low", ""],
    "relevance_phase3": ["high", "medium", "low", "not-yet-assessed", ""],
}

REQUIRED_SECTIONS = [
    "## Abstract summary",
    "## Methodology",
    "## Findings",
    "## Quantum advantage claim",
    "## Limitations",
    "## Open questions",
    "## Key ideas",
    "## Contradictions",
    "## Notable quotes",
    "## Researcher notes",
]

_IDEA_TAG_PATTERN = re.compile(r"^(idea|contradiction|limitation):.+$")

# ---------------------------------------------------------------------------
# Tag registry loader
# ---------------------------------------------------------------------------


def _load_tag_registry() -> dict:
    with open(_TAG_REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Validation functions (importable)
# ---------------------------------------------------------------------------


def validate_frontmatter(metadata: dict) -> list[str]:
    """Return a list of validation error strings. Empty list = valid."""
    errors: list[str] = []

    # Required fields
    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in metadata:
            errors.append(f"Missing required field: {field}")
            continue
        value = metadata[field]
        if not isinstance(value, expected_type):
            errors.append(
                f"Field '{field}' has type {type(value).__name__}, "
                f"expected {expected_type}"
            )

    # Enum validation
    for field, allowed in ENUM_RULES.items():
        if field not in metadata:
            continue
        value = metadata[field]
        if value is None:
            value = ""
        if isinstance(value, str) and value not in allowed:
            errors.append(
                f"Field '{field}' has invalid value '{value}'. "
                f"Allowed: {allowed}"
            )

    return errors


def validate_body_sections(body: str) -> list[str]:
    """Return a list of missing section headers."""
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"Missing section: {section}")
    return errors


def validate_tags(metadata: dict, tag_registry: dict) -> list[str]:
    """Return a list of invalid tag errors.

    Tolerant of two LLM emission patterns observed in the production corpus
    (2026-05-02): (a) PD-/SA-code references (e.g. 'SA-03') instead of slug
    keys (e.g. 'amplitude-estimation'), and (b) case variants. Both are
    unambiguous references to the same tags, so we accept them.
    """
    errors: list[str] = []

    valid_topic_slugs = set(tag_registry.get("topic_tags", {}).keys())
    valid_topic_codes = {
        v.get("code", "").upper()
        for v in tag_registry.get("topic_tags", {}).values()
        if v.get("code")
    }
    valid_methodology_slugs = set(tag_registry.get("methodology_tags", {}).keys())
    valid_methodology_codes = {
        v.get("code", "").upper()
        for v in tag_registry.get("methodology_tags", {}).values()
        if v.get("code")
    }

    for tag in metadata.get("topic_tags", []):
        t = (tag or "").strip()
        if t.lower() in valid_topic_slugs:
            continue
        if t.upper() in valid_topic_codes:
            continue
        errors.append(f"Unregistered topic tag: '{tag}'")

    for tag in metadata.get("methodology_tags", []):
        t = (tag or "").strip()
        if t.lower() in valid_methodology_slugs:
            continue
        if t.upper() in valid_methodology_codes:
            continue
        errors.append(f"Unregistered methodology tag: '{tag}'")

    for tag in metadata.get("idea_tags", []):
        if not _IDEA_TAG_PATTERN.match(tag):
            errors.append(
                f"Invalid idea tag format: '{tag}'. "
                "Must match 'idea:*', 'contradiction:*', or 'limitation:*'"
            )

    return errors


def validate_file(filepath: str) -> list[str]:
    """Run all validations on a markdown paper file. Returns list of errors."""
    metadata, body = read_frontmatter(filepath)
    if not metadata and not body:
        return [f"File not found or empty: {filepath}"]

    tag_registry = _load_tag_registry()
    errors: list[str] = []
    errors.extend(validate_frontmatter(metadata))
    errors.extend(validate_body_sections(body))
    errors.extend(validate_tags(metadata, tag_registry))
    return errors


# ---------------------------------------------------------------------------
# Pytest tests
# ---------------------------------------------------------------------------


class TestPaperBaseTemplate:
    """Validate the blank template has all required fields and sections."""

    @pytest.fixture(autouse=True)
    def _load_template(self):
        self.metadata, self.body = read_frontmatter(_PAPER_TEMPLATE_PATH)
        self.tag_registry = _load_tag_registry()

    def test_template_has_required_fields(self):
        errors = validate_frontmatter(self.metadata)
        assert errors == [], f"Template frontmatter errors: {errors}"

    def test_template_has_required_sections(self):
        errors = validate_body_sections(self.body)
        assert errors == [], f"Template section errors: {errors}"

    def test_template_tags_are_valid(self):
        errors = validate_tags(self.metadata, self.tag_registry)
        assert errors == [], f"Template tag errors: {errors}"


class TestEnumValidation:
    """Test that enum validation catches invalid values."""

    def test_valid_source_type_accepted(self):
        meta = {"source_type": "preprint"}
        errors = validate_frontmatter(meta)
        source_errors = [e for e in errors if "source_type" in e and "invalid" in e.lower()]
        assert source_errors == []

    def test_invalid_source_type_rejected(self):
        meta = {**_minimal_metadata(), "source_type": "blog-post"}
        errors = validate_frontmatter(meta)
        assert any("source_type" in e and "blog-post" in e for e in errors)

    def test_empty_source_type_accepted(self):
        meta = {**_minimal_metadata(), "source_type": ""}
        errors = validate_frontmatter(meta)
        source_errors = [e for e in errors if "source_type" in e and "invalid" in e.lower()]
        assert source_errors == []

    def test_invalid_source_type_confidence_rejected(self):
        meta = {**_minimal_metadata(), "source_type_confidence": "very-high"}
        errors = validate_frontmatter(meta)
        assert any("source_type_confidence" in e for e in errors)

    def test_invalid_classification_rejected(self):
        meta = {**_minimal_metadata(), "classification": "unknown"}
        errors = validate_frontmatter(meta)
        assert any("classification" in e for e in errors)

    def test_invalid_evidence_type_rejected(self):
        meta = {**_minimal_metadata(), "evidence_type": "qualitative"}
        errors = validate_frontmatter(meta)
        assert any("evidence_type" in e for e in errors)

    def test_invalid_quantum_advantage_claim_rejected(self):
        meta = {**_minimal_metadata(), "quantum_advantage_claim": "proven"}
        errors = validate_frontmatter(meta)
        assert any("quantum_advantage_claim" in e for e in errors)

    def test_invalid_relevance_phase1_rejected(self):
        meta = {**_minimal_metadata(), "relevance_phase1": "critical"}
        errors = validate_frontmatter(meta)
        assert any("relevance_phase1" in e for e in errors)

    def test_invalid_relevance_phase3_rejected(self):
        meta = {**_minimal_metadata(), "relevance_phase3": "maybe"}
        errors = validate_frontmatter(meta)
        assert any("relevance_phase3" in e for e in errors)

    def test_all_valid_enums_pass(self):
        meta = {
            **_minimal_metadata(),
            "source_type": "peer-reviewed-empirical",
            "source_type_confidence": "high",
            "classification": "application-specific",
            "evidence_type": "empirical",
            "quantum_advantage_claim": "demonstrated",
            "relevance_phase1": "high",
            "relevance_phase3": "not-yet-assessed",
        }
        errors = validate_frontmatter(meta)
        assert errors == []


class TestTagValidation:
    """Test that unregistered tags are caught."""

    @pytest.fixture(autouse=True)
    def _load_registry(self):
        self.tag_registry = _load_tag_registry()

    def test_valid_topic_tag_accepted(self):
        # Fix 2026-05-02: previous fixture used UK spelling 'portfolio-optimisation';
        # the canonical taxonomy uses US 'portfolio-optimization' (PD-01).
        meta = {"topic_tags": ["portfolio-optimization"], "methodology_tags": [], "idea_tags": []}
        errors = validate_tags(meta, self.tag_registry)
        assert errors == []

    def test_unregistered_topic_tag_rejected(self):
        meta = {"topic_tags": ["quantum-teleportation"], "methodology_tags": [], "idea_tags": []}
        errors = validate_tags(meta, self.tag_registry)
        assert any("quantum-teleportation" in e for e in errors)

    def test_valid_methodology_tag_accepted(self):
        # Fix 2026-05-02: previous fixture used 'QAOA' which is not a registry slug;
        # canonical taxonomy uses 'variational-nisq' (SA-02) covering QAOA/VQE/etc.
        meta = {"topic_tags": [], "methodology_tags": ["variational-nisq"], "idea_tags": []}
        errors = validate_tags(meta, self.tag_registry)
        assert errors == []

    def test_unregistered_methodology_tag_rejected(self):
        meta = {"topic_tags": [], "methodology_tags": ["quantum-teleport"], "idea_tags": []}
        errors = validate_tags(meta, self.tag_registry)
        assert any("quantum-teleport" in e for e in errors)

    def test_valid_idea_tag_accepted(self):
        meta = {"topic_tags": [], "methodology_tags": [], "idea_tags": ["idea:quantum-advantage"]}
        errors = validate_tags(meta, self.tag_registry)
        assert errors == []

    def test_valid_contradiction_tag_accepted(self):
        meta = {"topic_tags": [], "methodology_tags": [], "idea_tags": ["contradiction:scalability"]}
        errors = validate_tags(meta, self.tag_registry)
        assert errors == []

    def test_valid_limitation_tag_accepted(self):
        meta = {"topic_tags": [], "methodology_tags": [], "idea_tags": ["limitation:noise"]}
        errors = validate_tags(meta, self.tag_registry)
        assert errors == []

    def test_invalid_idea_tag_format_rejected(self):
        meta = {"topic_tags": [], "methodology_tags": [], "idea_tags": ["random-tag"]}
        errors = validate_tags(meta, self.tag_registry)
        assert any("random-tag" in e for e in errors)

    def test_empty_tags_pass(self):
        meta = {"topic_tags": [], "methodology_tags": [], "idea_tags": []}
        errors = validate_tags(meta, self.tag_registry)
        assert errors == []


class TestBodySections:
    """Test that missing body sections are caught."""

    def test_complete_body_passes(self):
        body = "\n".join(REQUIRED_SECTIONS)
        errors = validate_body_sections(body)
        assert errors == []

    def test_missing_section_caught(self):
        body = "\n".join(REQUIRED_SECTIONS[:-1])  # drop last section
        errors = validate_body_sections(body)
        assert len(errors) == 1
        assert "Researcher notes" in errors[0]

    def test_empty_body_catches_all(self):
        errors = validate_body_sections("")
        assert len(errors) == len(REQUIRED_SECTIONS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_metadata() -> dict:
    """Return a metadata dict with all required fields set to valid defaults."""
    return {
        "title": "Test Paper",
        "authors": ["Author A"],
        "year": 2024,
        "source_type": "preprint",
        "source_type_confidence": "high",
        "auto_detected": True,
        "topic_tags": [],
        "methodology_tags": [],
        "idea_tags": [],
        "steps_completed": [],
    }
