"""Render and dispatch Stage C (C1) cross-silo synthesis prompt."""
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SILOS = [
    "trading_execution", "credit_lending", "fraud_detection",
    "derivative_pricing", "risk_management", "simulation_monte_carlo",
    "portfolio_optimization", "quantum_ml_finance",
]
SILO_CODES = {
    "trading_execution": "TE", "credit_lending": "CL", "fraud_detection": "FD",
    "derivative_pricing": "DP", "risk_management": "RM",
    "simulation_monte_carlo": "SMC", "portfolio_optimization": "PO",
    "quantum_ml_finance": "QML",
}


def trim_theme(t: dict) -> dict:
    """Remove verbose fields; keep identity + interpretive payload."""
    keep = {
        "theme_id": t.get("theme_id"),
        "theme_label": t.get("theme_label"),
        "interpretation": t.get("interpretation"),
        "grounded_in": t.get("grounded_in", []),
        "counter_evidence": [
            {"paper_id": ce.get("paper_id"), "reason": ce.get("reason"),
             "evidence_type": ce.get("evidence_type")}
            for ce in t.get("counter_evidence", [])
        ],
        "no_counter_evidence_reason": t.get("no_counter_evidence_reason"),
        "implication": t.get("implication"),
        "supporting_paper_count": len(t.get("supporting_papers", [])),
    }
    return {k: v for k, v in keep.items() if v not in (None, [], "")}


def main():
    analytical_by_silo = {}
    descriptive_headers_by_silo = {}
    for silo in SILOS:
        p = ROOT / "s4_thematic_coding" / silo / "themes" / "b2_silo_themes.json"
        obj = json.loads(p.read_text(encoding="utf-8"))
        out = obj["output"]
        code = SILO_CODES[silo]
        analytical_by_silo[code] = [trim_theme(t) for t in out.get("analytical_themes", [])]
        descriptive_headers_by_silo[code] = [
            [dt["theme_id"], dt["theme_label"]] for dt in out.get("descriptive_themes", [])
        ]

    prompt_template = (ROOT / "prompts" / "c1_cross_silo_synthesis_v1.txt").read_text(encoding="utf-8")
    prompt_sha = hashlib.sha256(prompt_template.encode("utf-8")).hexdigest()

    rendered = prompt_template.format(
        all_analytical_themes=json.dumps(analytical_by_silo, indent=2, ensure_ascii=False),
        all_descriptive_headers=json.dumps(descriptive_headers_by_silo, indent=2, ensure_ascii=False),
    )
    rendered_sha = hashlib.sha256(rendered.encode("utf-8")).hexdigest()

    out_dir = ROOT / "s5_cross_silo"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "c1.prompt.txt").write_text(rendered, encoding="utf-8")

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_file": "c1_cross_silo_synthesis_v1.txt",
        "prompt_sha256": prompt_sha,
        "rendered_sha256": rendered_sha,
        "prompt_chars": len(rendered),
        "approx_tokens_k": round(len(rendered) / 4000, 1),
        "silos": SILOS,
        "analytical_theme_count_by_silo": {k: len(v) for k, v in analytical_by_silo.items()},
        "total_analytical_themes": sum(len(v) for v in analytical_by_silo.values()),
        "model_intended": "claude-opus-4.6-1m",
    }
    (out_dir / "c1.meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
