"""Phase 4 faithfulness-tier audit.

This audit separates the legacy F/P headline split from implementation
faithfulness. It does not mutate Phase 8 records; it verifies that any label
promoted to ``paper-faithful-strict`` satisfies paper-exact guardrails, and
that template/family-faithful labels are explicitly scoped as such.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"
AUDIT_REPORTS = CANON / "reports" / "audit"
VINCENT_DIR = ROOT / "p4_experiments" / "experiments" / "review" / "phase8_faithfulness_review" / "vincent"

STRICT_TIER = "paper-faithful-strict"
TEMPLATE_TIER = "paper-family-template"
PROXY_TIER = "proxy"
ALLOWED_TIERS = {STRICT_TIER, TEMPLATE_TIER, PROXY_TIER}


def _anchor_record(label: str) -> dict[str, Any]:
    path = RESULTS / f"{label}_maj_e6_floquet_eps1e-04_full.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _source_profile(label: str) -> dict[str, Any]:
    record = _anchor_record(label)
    source_path = (record.get("method_implementation") or {}).get("source_path")
    method_name = (record.get("method_implementation") or {}).get("name")
    source = ROOT / source_path if source_path else None
    text = source.read_text(encoding="utf-8", errors="replace") if source and source.exists() else ""
    registered_labels = re.findall(r"label\s*=\s*[\"']([^\"']+)[\"']", text)
    oracle_variants = re.findall(r"oracle_variant\s*=\s*[\"']([^\"']+)[\"']", text)
    return {
        "method_name": method_name,
        "source_path": source_path,
        "source_exists": bool(source and source.exists()),
        "registered_labels": sorted(set(registered_labels)),
        "oracle_variants": sorted(set(oracle_variants)),
        "label_registered_in_source": label in registered_labels,
        "source_disclaims_paper_algorithm": "does NOT implement" in text,
    }


def _review_profile(label: str, cohort_entry: dict[str, Any]) -> dict[str, Any]:
    path = VINCENT_DIR / f"{label}.md"
    payload = {
        "review_path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "review_exists": path.exists(),
        "verdict": cohort_entry.get("faithfulness_review_verdict"),
        "review_disclaims_paper_algorithm": False,
    }
    if path.exists():
        text = path.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"\*\*Verdict:\*\*\s*\*\*([^*]+)\*\*", text)
        if match:
            payload["verdict"] = match.group(1).strip()
        payload["review_disclaims_paper_algorithm"] = "does NOT implement" in text
    return payload


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = cohort.get("labels") or {}
    findings: list[dict[str, Any]] = []
    blockers_failed = 0

    def add(check_id: str, status: str, message: str, blocker: bool = True, **extra) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        findings.append({
            "check_id": check_id,
            "status": status,
            "blocker": blocker,
            "message": message,
            **extra,
        })

    f_labels = {label: entry for label, entry in labels.items() if entry.get("fidelity") == "F"}
    tier_counts: dict[str, int] = {}
    profiles: dict[str, dict[str, Any]] = {}
    missing_tier: list[str] = []
    bad_tier: list[tuple[str, str | None]] = []
    strict_violations: list[dict[str, Any]] = []
    honest_not_strict: list[str] = []
    missing_review_verdict: list[str] = []
    template_source_label_mismatches: list[str] = []
    template_source_missing_disclaimer: list[str] = []
    template_review_missing_disclaimer: list[str] = []

    for label, entry in sorted(f_labels.items()):
        tier = entry.get("faithfulness_tier")
        if not tier:
            missing_tier.append(label)
            tier = "<missing>"
        elif tier not in ALLOWED_TIERS:
            bad_tier.append((label, tier))
        tier_counts[tier] = tier_counts.get(tier, 0) + 1

        source = _source_profile(label)
        review = _review_profile(label, entry)
        profiles[label] = {
            "faithfulness_tier": tier,
            "paper_fidelity": entry.get("paper_fidelity"),
            "source": source,
            "review": review,
        }

        if entry.get("paper_fidelity") == "paper-faithful-honest" and tier != STRICT_TIER:
            honest_not_strict.append(label)
        if not review.get("verdict"):
            missing_review_verdict.append(label)
        if tier == STRICT_TIER:
            reasons = []
            if not source.get("source_exists"):
                reasons.append("source_missing")
            if not source.get("label_registered_in_source"):
                reasons.append("registered_label_mismatch")
            if source.get("source_disclaims_paper_algorithm"):
                reasons.append("source_disclaims_paper_algorithm")
            if review.get("review_disclaims_paper_algorithm"):
                reasons.append("review_disclaims_paper_algorithm")
            if review.get("verdict") not in {"CONFIRMED"}:
                reasons.append(f"review_verdict={review.get('verdict')}")
            if reasons:
                strict_violations.append({"label": label, "reasons": reasons})
        elif tier == TEMPLATE_TIER:
            if source.get("source_exists") and not source.get("label_registered_in_source"):
                template_source_label_mismatches.append(label)
            if source.get("source_exists") and not source.get("source_disclaims_paper_algorithm"):
                template_source_missing_disclaimer.append(label)
            if review.get("review_exists") and not review.get("review_disclaims_paper_algorithm"):
                template_review_missing_disclaimer.append(label)

    add(
        "P4F.A",
        "PASS" if not missing_tier and not bad_tier else "FAIL",
        "All F labels carry an allowed faithfulness_tier"
        if not missing_tier and not bad_tier
        else f"missing_tier={missing_tier}; bad_tier={bad_tier}",
        missing_tier=missing_tier,
        bad_tier=bad_tier,
    )
    add(
        "P4F.B",
        "PASS" if not strict_violations else "FAIL",
        f"Strict tier guardrails pass for {tier_counts.get(STRICT_TIER, 0)} labels"
        if not strict_violations
        else f"Strict tier violations: {strict_violations}",
        strict_violations=strict_violations,
    )
    add(
        "P4F.C",
        "PASS" if not honest_not_strict else "FAIL",
        "No legacy paper-faithful-honest label sits outside strict tier"
        if not honest_not_strict
        else f"paper-faithful-honest labels not strict: {honest_not_strict}",
        honest_not_strict=honest_not_strict,
    )
    add(
        "P4F.D",
        "PASS" if not missing_review_verdict else "FAIL",
        "All F labels have a Vincent review verdict"
        if not missing_review_verdict
        else f"missing review verdict: {missing_review_verdict}",
        missing_review_verdict=missing_review_verdict,
    )
    template_labels = sorted(label for label, profile in profiles.items() if profile.get("faithfulness_tier") == TEMPLATE_TIER)
    add(
        "P4F.E",
        "INFO",
        f"Template/family-faithful labels retained as scoped headline evidence: {len(template_labels)}",
        blocker=False,
        labels=template_labels,
    )
    add(
        "P4F.F",
        "INFO",
        "Template-tier implementation drift diagnostics recorded for source/review transparency",
        blocker=False,
        source_label_mismatches=template_source_label_mismatches,
        source_missing_disclaimer=template_source_missing_disclaimer,
        review_missing_disclaimer=template_review_missing_disclaimer,
    )

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "phase4_faithfulness",
        "tier_counts": dict(sorted(tier_counts.items())),
        "profiles": profiles,
        "results": findings,
        "totals": {
            "pass": sum(1 for item in findings if item["status"] == "PASS"),
            "fail": sum(1 for item in findings if item["status"] == "FAIL"),
            "info": sum(1 for item in findings if item["status"] == "INFO"),
            "blockers_failed": blockers_failed,
        },
    }
    out = AUDIT_REPORTS / "audit_phase4_faithfulness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"[Phase 4 faithfulness audit] {report['totals']['pass']} PASS / {report['totals']['fail']} FAIL / {report['totals']['info']} INFO; blockers_failed={blockers_failed}")
    for item in findings:
        marker = {"PASS": "[ok]", "FAIL": "[FAIL]", "INFO": "[info]"}.get(item["status"], "[??]")
        print(f"  {marker} {item['check_id']}: {item['message']}")
    print(f"[Phase 4 faithfulness audit] Report -> {out.relative_to(ROOT)}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())