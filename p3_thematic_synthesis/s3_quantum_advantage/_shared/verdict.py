"""Common verdict vocabulary shared by every framework assessor."""

from __future__ import annotations

from typing import Any

COMMON_VERDICTS = (
    "viable",
    "likely_viable",
    "potentially_viable",
    "conditional",
    "fails",
    "not_applicable",
    "insufficient_data",
)

CONFIDENCE_LEVELS = ("high", "medium", "low")

FRAMEWORKS = (
    "ronnow_2014",
    "hoefler_2023",
    "babbush_2021",
    "beverland_inspired_2022",  # honest relabel (2026-05-02): assessor sweeps Babbush Eq. (5)
                                # across Beverland's 6 hardware-scenario names rather than
                                # implementing Beverland's full QEC stack. See BEVERLAND_CAVEAT.md.
    "beverland_2022",           # legacy ID kept for backward compatibility with frozen result files.
    "chakrabarti_2021",
    "dalzell_2023",
    "stilck_franca_2021",
)

# 4 core + 1 optional-veto layered design
LAYERS = (
    "benchmark_validity",       # Rønnow 2014
    "practicality_crossover",   # Hoefler 2023 + Babbush 2021 (merged, single score)
    "fullstack_resource",       # Beverland 2022
    "finance_domain_realism",   # Chakrabarti 2021 (pricing/risk/MC) OR Dalzell 2023 (optimization)
)
OPTIONAL_VETO_LAYER = "nisq_veto"  # Stilck França 2021


def make_verdict(
    *,
    paper_id: str,
    experiment_id: str,
    silo: str,
    algorithm_family: str,
    framework: str,
    verdict: str,
    confidence: str,
    reasoning: str,
    assumptions: dict[str, Any] | None = None,
    quantitative_margin: float | None = None,
    framework_specific: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Construct a verdict record conforming to common_verdict_schema.json.

    Raises ValueError if verdict/confidence/framework are outside the allowed sets.
    """
    if verdict not in COMMON_VERDICTS:
        raise ValueError(f"verdict '{verdict}' not in {COMMON_VERDICTS}")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError(f"confidence '{confidence}' not in {CONFIDENCE_LEVELS}")
    if framework not in FRAMEWORKS:
        raise ValueError(f"framework '{framework}' not in {FRAMEWORKS}")

    return {
        "paper_id": paper_id,
        "experiment_id": experiment_id,
        "silo": silo,
        "algorithm_family": algorithm_family,
        "framework": framework,
        "verdict": verdict,
        "confidence": confidence,
        "assumptions": assumptions or {},
        "quantitative_margin": quantitative_margin,
        "reasoning": reasoning,
        "framework_specific": framework_specific or {},
    }
