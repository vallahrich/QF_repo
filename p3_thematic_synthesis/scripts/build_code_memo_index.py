"""Build per-silo code↔memo index.

Mechanical assembly — NO LLM calls.

For each silo, for each paper in the silo's projection manifest:
  - Load A1 codes from papers/<paper_id>.jsonl (central, silo-blind)
  - Load A2 memo from papers/<paper_id>.json (central)
  - Load overlay (if multi-silo) from <silo>/memos/<paper_id>.json
    NB: for single-silo papers, <silo>/memos/<paper_id>.json is a COPY
        of the central memo (fan-out), not an overlay — skip in that case.

Output: p3_thematic_synthesis/s4_thematic_coding/<silo>/themes/code_memo_index.json

The index is used by:
  - L-B1 validator: check that every support_code_id in a B1 theme
    corresponds to a real A1 code for the cited paper.
  - Researcher review: one-click trace from theme → code → text span.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent  # p3_thematic_synthesis/
PAPERS_DIR = ROOT / "s4_thematic_coding" / "papers"
CODING_DIR = ROOT / "s4_thematic_coding"

SILOS = [
    "credit_lending",
    "derivative_pricing",
    "fraud_detection",
    "portfolio_optimization",
    "quantum_ml_finance",
    "risk_management",
    "simulation_monte_carlo",
    "trading_execution",
]


def _load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            out.append(json.loads(line))
    return out


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _detect_memo_type(silo_memo: dict) -> str:
    """central 9-dim memo vs silo overlay.

    Central has keys dimension_1_problem_framing..dimension_9_*.
    Overlay has silo_relevance + key_points.
    """
    if "silo_relevance" in silo_memo and "key_points" in silo_memo:
        return "overlay"
    if any(k.startswith("dimension_") for k in silo_memo.keys()):
        return "central"
    return "unknown"


def _collect_codes_from_memo(memo: dict) -> list[str]:
    """Union of support_codes across the memo (central or overlay)."""
    out: list[str] = []
    # Central memo: dimension_N_* -> {text, support_codes, ...}
    for key, val in memo.items():
        if isinstance(val, dict) and "support_codes" in val:
            for c in val.get("support_codes") or []:
                if c not in out:
                    out.append(c)
    # Overlay: key_points -> [{point, support_codes, ...}], primary_codes
    for kp in memo.get("key_points", []) or []:
        for c in kp.get("support_codes") or []:
            if c not in out:
                out.append(c)
    for c in memo.get("primary_codes", []) or []:
        if c not in out:
            out.append(c)
    return out


def build_silo_index(silo: str) -> dict:
    silo_dir = CODING_DIR / silo
    proj_path = silo_dir / "projection_manifest.json"
    if not proj_path.is_file():
        raise FileNotFoundError(f"Missing projection_manifest.json for {silo}")
    proj = _load_json(proj_path)

    papers_out: dict[str, dict] = {}
    missing_codes = 0
    missing_memos = 0
    papers_seen = 0

    for p in proj["papers"]:
        pid = p["paper_id"]
        papers_seen += 1

        # A1 codes (central, silo-blind)
        codes_path = PAPERS_DIR / f"{pid}.jsonl"
        codes: list[dict] = []
        if codes_path.is_file():
            for c in _load_jsonl(codes_path):
                codes.append({
                    "code_id": c.get("code_id"),
                    "code_label": c.get("code_label"),
                    "text_span": c.get("text_span"),
                    "locator": c.get("locator"),
                    "dimension_hint": c.get("dimension_hint"),
                    "l1_status": c.get("l1_status"),
                })
        else:
            missing_codes += 1

        # Central A2 memo (always load for provenance)
        central_memo_path = PAPERS_DIR / f"{pid}.json"
        central_memo = _load_json(central_memo_path) if central_memo_path.is_file() else None
        if central_memo is None:
            missing_memos += 1

        # Silo memo file (overlay for multi-silo, central-copy for single-silo)
        silo_memo_path = silo_dir / "memos" / f"{pid}.json"
        silo_memo = _load_json(silo_memo_path) if silo_memo_path.is_file() else None
        memo_type = _detect_memo_type(silo_memo) if silo_memo else "missing"

        is_multi_silo = len(p.get("all_silos", [])) > 1
        is_overlay = memo_type == "overlay"

        # Resolve evidence type for B1 per plan v4-2
        if is_multi_silo and is_overlay:
            evidence_type = "central+overlay"
        elif not is_multi_silo and memo_type == "central":
            evidence_type = "central"
        else:
            # Fall back — something inconsistent between projection manifest and file type
            evidence_type = f"inconsistent:{memo_type}"

        overlay_codes = _collect_codes_from_memo(silo_memo) if is_overlay else []

        papers_out[pid] = {
            "paper_id": pid,
            "all_silos": p.get("all_silos", []),
            "is_multi_silo": is_multi_silo,
            "evidence_type": evidence_type,
            "central_memo_path": str(central_memo_path.relative_to(ROOT.parent)) if central_memo else None,
            "silo_memo_path": str(silo_memo_path.relative_to(ROOT.parent)) if silo_memo else None,
            "codes_path": str(codes_path.relative_to(ROOT.parent)) if codes_path.is_file() else None,
            "codes": codes,
            "overlay_code_ids": overlay_codes,
            "code_count": len(codes),
        }

    index = {
        "silo": silo,
        "built_at": None,  # filled by caller if wanted
        "total_papers": papers_seen,
        "papers_with_codes": sum(1 for v in papers_out.values() if v["code_count"] > 0),
        "papers_with_central_memo": papers_seen - missing_memos,
        "papers_with_overlay": sum(1 for v in papers_out.values() if v["evidence_type"] == "central+overlay"),
        "missing_codes": missing_codes,
        "missing_memos": missing_memos,
        "papers": papers_out,
    }
    return index


def write_index(silo: str) -> Path:
    index = build_silo_index(silo)
    from datetime import datetime, timezone
    index["built_at"] = datetime.now(timezone.utc).isoformat()

    out_dir = CODING_DIR / silo / "themes"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "code_memo_index.json"

    tmp = out_path.with_suffix(".json.tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)
    tmp.replace(out_path)

    print(
        f"[{silo}] papers={index['total_papers']} "
        f"codes_ok={index['papers_with_codes']} "
        f"overlays={index['papers_with_overlay']} "
        f"missing_codes={index['missing_codes']} "
        f"missing_memos={index['missing_memos']}"
    )
    return out_path


def main(argv: list[str]) -> int:
    silos = SILOS if len(argv) <= 1 else argv[1:]
    for silo in silos:
        write_index(silo)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
