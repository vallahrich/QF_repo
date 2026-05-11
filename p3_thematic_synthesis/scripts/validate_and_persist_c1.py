"""L-C1 structural validator + persist Stage C output."""
import json
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
VALID_SILOS = {"TE", "CL", "FD", "DP", "RM", "SMC", "PO", "QML"}

def validate_c1(obj: dict) -> tuple[bool, list]:
    errs = []
    mts = obj.get("meta_themes", [])
    if not (5 <= len(mts) <= 8):
        errs.append(f"SC2: meta_theme count {len(mts)} not in [5,8]")

    # Load all valid AT IDs from B2 outputs
    valid_ats = {}
    for s in ["trading_execution","credit_lending","fraud_detection","derivative_pricing",
              "risk_management","simulation_monte_carlo","portfolio_optimization","quantum_ml_finance"]:
        b2 = json.loads((ROOT / "s4_thematic_coding" / s / "themes" / "b2_silo_themes.json").read_text(encoding="utf-8"))
        for at in b2["output"].get("analytical_themes", []):
            valid_ats[at["theme_id"]] = True

    for i, mt in enumerate(mts):
        sid = mt.get("meta_theme_id", f"idx{i}")
        silos = mt.get("silos_grounded_in", [])
        if len(silos) < 3:
            errs.append(f"SC3: {sid} silos_grounded_in={len(silos)} < 3")
        for s in silos:
            if s not in VALID_SILOS:
                errs.append(f"SC3: {sid} invalid silo code '{s}'")
        gt = mt.get("grounded_in_themes", {})
        for silo, ids in gt.items():
            for at_id in ids:
                if at_id not in valid_ats:
                    errs.append(f"SC4: {sid} references non-existent theme {at_id}")
        label = mt.get("meta_theme_label", "")
        if re.search(r"\b(PD|SA)-\d{2}\b", label):
            errs.append(f"SC5: {sid} label contains Phase-1 taxonomy code")
        for field in ("divergence_notes", "implication_for_field"):
            if len(mt.get(field, "")) < 20:
                errs.append(f"SC6: {sid} {field} < 20 chars")
    if len(obj.get("meta_synthesis_note", "")) < 20:
        errs.append("SC6: meta_synthesis_note < 20 chars")
    return (len(errs) == 0, errs)


def main():
    out_dir = ROOT / "s5_cross_silo"
    raw = (out_dir / "c1.raw_response.txt").read_text(encoding="utf-8").strip()
    obj = json.loads(raw)
    ok, errs = validate_c1(obj)
    print(f"L-C1 validation: {'PASS' if ok else 'FAIL'}")
    for e in errs:
        print(f"  - {e}")
    if not ok:
        raise SystemExit(1)

    # Persist
    out = {
        "stage": "C1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "prompt_file": "c1_cross_silo_synthesis_v1.txt",
        "model": "claude-opus-4.6",
        "output": obj,
        "meta_theme_count": len(obj["meta_themes"]),
        "silos_coverage": {mt["meta_theme_id"]: mt["silos_grounded_in"] for mt in obj["meta_themes"]},
    }
    (out_dir / "c1_meta_themes.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    # Manifest
    manifest = {
        "stage": "C1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "meta_theme_count": len(obj["meta_themes"]),
        "total_silo_coverage": sum(len(mt["silos_grounded_in"]) for mt in obj["meta_themes"]),
    }
    (out_dir / "c1_manifest.jsonl").write_text(json.dumps(manifest) + "\n", encoding="utf-8")

    print(f"\nMeta-themes: {len(obj['meta_themes'])}")
    for mt in obj["meta_themes"]:
        print(f"  {mt['meta_theme_id']}: {len(mt['silos_grounded_in'])} silos -> {','.join(mt['silos_grounded_in'])}")
    print(f"\nmeta_synthesis_note ({len(obj['meta_synthesis_note'])} chars):")
    print(obj["meta_synthesis_note"][:500] + "...")


if __name__ == "__main__":
    main()
