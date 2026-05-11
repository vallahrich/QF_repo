"""Shared utilities for per-framework quantum advantage assessments.

Every framework module (hoefler_assessment, babbush_2021, dalzell_2023, ...)
imports from here so that extraction loading, derived-field lookup, maturity
computation, aggregation, and result emission stay consistent. The common
verdict schema in common_verdict_schema.json is the canonical cross-framework
contract; see triangulate.py in combined/ for the consumer.
"""

from .extraction_loader import iter_experiments, load_extraction
from .derived_fields_loader import load_derived_fields, get_derived
from .maturity import compute_maturity_level
from .aggregation import build_output_payload, save_payload, print_summary
from .verdict import COMMON_VERDICTS, CONFIDENCE_LEVELS, FRAMEWORKS, LAYERS, OPTIONAL_VETO_LAYER, make_verdict
from .speedup import infer_speedup_order, estimate_oracle_complexity

__all__ = [
    "iter_experiments",
    "load_extraction",
    "load_derived_fields",
    "get_derived",
    "compute_maturity_level",
    "build_output_payload",
    "save_payload",
    "print_summary",
    "COMMON_VERDICTS",
    "CONFIDENCE_LEVELS",
    "FRAMEWORKS",
    "LAYERS",
    "OPTIONAL_VETO_LAYER",
    "make_verdict",
    "infer_speedup_order",
    "estimate_oracle_complexity",
]
