"""Build the canonical per-framework results payload and save it to disk.

Every assess_<framework>.py calls build_output_payload(framework, verdicts, out_path).
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Iterable


def _count(items: Iterable[str]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for i in items:
        counts[i] += 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def build_output_payload(framework: str, verdicts: list[dict]) -> dict:
    """Aggregate a list of per-experiment verdict dicts into the output payload."""
    verdict_counts = _count(v["verdict"] for v in verdicts)

    by_silo: dict[str, dict[str, int]] = {}
    by_algo: dict[str, dict[str, int]] = {}
    for v in verdicts:
        silo = v.get("silo", "other")
        algo = v.get("algorithm_family", "unknown")
        by_silo.setdefault(silo, defaultdict(int))[v["verdict"]] += 1
        by_algo.setdefault(algo, defaultdict(int))[v["verdict"]] += 1

    return {
        "framework": framework,
        "total_experiments": len(verdicts),
        "verdict_summary": verdict_counts,
        "by_silo": {
            s: dict(sorted(d.items(), key=lambda x: -x[1]))
            for s, d in sorted(by_silo.items())
        },
        "by_algorithm": {
            a: dict(sorted(d.items(), key=lambda x: -x[1]))
            for a, d in sorted(by_algo.items())
        },
        "experiments": verdicts,
    }


def save_payload(payload: dict, out_path: Path) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )


def print_summary(payload: dict) -> None:
    total = payload["total_experiments"]
    print(f"\n{'=' * 60}")
    print(f"  {payload['framework'].upper()} — {total} experiments")
    print("=" * 60)
    for v, c in payload["verdict_summary"].items():
        pct = round(c / max(total, 1) * 100, 1)
        print(f"  {v}: {c} ({pct}%)")
