"""Phase 8e audit: 10 blockers (P8e.A-J)."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
OUT_DIR = CANON / "outputs" / "phase08e_per_silo"
ROLLUP = OUT_DIR / "per_silo_synthesis.json"
ARTI = CANON / "outputs" / "manuscript_artifacts"
COHORT = CANON / "cohort.json"
REPORTS = CANON / "reports"
STATS = REPORTS / "stats_report.json"
REPORT = REPORTS / "audit" / "audit_phase8e.json"

SCHEMA_TAG = "phase8e.1.1"


def main() -> int:
    results, blockers_failed = [], 0

    def add(cid, status, msg, blocker=True):
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": cid, "status": status,
                        "blocker": blocker, "message": msg})

    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    expected_silos = sorted({e["silo"] for e in cohort["labels"].values()})
    f_labels_expected = sorted(L for L, e in cohort["labels"].items()
                               if e.get("paper_fidelity", "")
                               .startswith("paper-faithful"))
    expected_totals = {
        "n_F": len(f_labels_expected),
        "n_P": sum(1 for e in cohort["labels"].values()
                   if e.get("paper_fidelity") == "proxy"),
        "n_labels": len(cohort["labels"]),
    }

    # ---- P8e.A
    missing = [s for s in expected_silos if not (OUT_DIR / f"{s}.json").exists()]
    add("P8e.A", "PASS" if not missing else "FAIL",
        f"missing cards: {missing}" if missing
        else f"{len(expected_silos)}/{len(expected_silos)} cards present")

    cards: dict[str, dict] = {}
    for s in expected_silos:
        p = OUT_DIR / f"{s}.json"
        if p.exists():
            try:
                cards[s] = json.loads(p.read_text(encoding="utf-8"))
            except Exception as ex:
                add("P8e.A", "FAIL", f"{s}.json parse error: {ex}")

    # ---- P8e.B
    bad_schema = [s for s, c in cards.items() if c.get("schema") != SCHEMA_TAG]
    add("P8e.B", "PASS" if not bad_schema else "FAIL",
        f"bad schema in: {bad_schema}" if bad_schema
        else f"all {len(cards)} cards have schema={SCHEMA_TAG}")

    # ---- P8e.C
    sum_F = sum(c["n_F"] for c in cards.values())
    sum_P = sum(c["n_P"] for c in cards.values())
    sum_L = sum_F + sum_P
    ok_C = (sum_F == expected_totals["n_F"]
            and sum_P == expected_totals["n_P"]
            and sum_L == expected_totals["n_labels"])
    add("P8e.C", "PASS" if ok_C else "FAIL",
        f"sumF={sum_F} sumP={sum_P} sumL={sum_L} (expected {expected_totals})")

    # ---- P8e.D
    seen = []
    for c in cards.values():
        seen.extend(c.get("label_list_F", []))
    dup = sorted({L for L in seen if seen.count(L) > 1})
    miss = sorted(set(f_labels_expected) - set(seen))
    extra = sorted(set(seen) - set(f_labels_expected))
    ok_D = not dup and not miss and not extra
    add("P8e.D", "PASS" if ok_D else "FAIL",
        f"dup={dup} miss={miss} extra={extra}")

    # ---- P8e.E
    fz_violations = []
    for s, c in cards.items():
        if c.get("card_kind") == "f-zero":
            if (c.get("label_list_F") or c.get("h4_scoreboard")
                    or c.get("phase8d_per_label_n_star")
                    or c.get("data_completeness_flag") != "f_zero"):
                fz_violations.append(s)
    add("P8e.E", "PASS" if not fz_violations else "FAIL",
        f"f-zero silos with stray data: {fz_violations}" if fz_violations
        else "f-zero invariants OK")

    # ---- P8e.F
    h4_bad = []
    sum_passes_all_5 = 0
    required_keys = ("C1_tau_runtime_lt_10", "C2_full_runtime_lt_baseline",
                     "C3_full_t_count_gt_0", "C4_tau_tdepth_ge_10",
                     "C5_baseline_ge_0_01s",
                     "passes_all_5", "values")
    for s, c in cards.items():
        for L, row in (c.get("h4_scoreboard") or {}).items():
            for k in required_keys:
                if k not in row:
                    h4_bad.append(f"{s}/{L} missing {k}")
            if row.get("passes_all_5"):
                sum_passes_all_5 += 1
    h4_winners = -1
    if STATS.exists():
        try:
            sd = json.loads(STATS.read_text(encoding="utf-8"))
            h4_winners = ((sd.get("H4") or {})
                          .get("canonical_winners_count", -1))
        except Exception:
            pass
    cross_ok = (h4_winners != 0) or (sum_passes_all_5 == 0)
    add("P8e.F",
        "PASS" if (not h4_bad and cross_ok) else "FAIL",
        f"h4 structural defects={len(h4_bad)} | "
        f"sum_passes_all_5={sum_passes_all_5} vs canonical_winners={h4_winners}"
        + (f"; sample={h4_bad[:3]}" if h4_bad else ""))

    # ---- P8e.G
    empties = [s for s, c in cards.items()
               if not (c.get("bottom_line_paragraph") or "").strip()]
    add("P8e.G", "PASS" if not empties else "FAIL",
        f"empty bottom_line in: {empties}" if empties
        else "all bottom_line paragraphs present")

    # ---- P8e.H
    if not ROLLUP.exists():
        add("P8e.H", "FAIL", "per_silo_synthesis.json missing")
    else:
        r = json.loads(ROLLUP.read_text(encoding="utf-8"))
        roll_silos = sorted(r.get("silos") or [])
        ok = (roll_silos == expected_silos
              and r.get("totals", {}).get("n_F") == expected_totals["n_F"]
              and r.get("totals", {}).get("n_P") == expected_totals["n_P"]
              and r.get("totals", {}).get("n_labels")
              == expected_totals["n_labels"])
        add("P8e.H", "PASS" if ok else "FAIL",
            "rollup OK" if ok else
            f"rollup mismatch: silos={roll_silos} totals={r.get('totals')}")

    # ---- P8e.I
    bad_tex = []
    for s, c in cards.items():
        if c.get("n_F", 0) >= 1:
            for kind in ("h4", "phase8d"):
                p = ARTI / f"table_silo_{s}_{kind}.tex"
                if not p.exists():
                    bad_tex.append(f"{p.name} missing")
                    continue
                txt = p.read_text(encoding="utf-8").strip()
                if not (txt.startswith(r"\begin{tabular}")
                        and txt.endswith(r"\end{tabular}")):
                    bad_tex.append(f"{p.name} malformed")
    add("P8e.I", "PASS" if not bad_tex else "FAIL",
        f"{len(bad_tex)} table issues"
        + (f": {bad_tex[:5]}" if bad_tex else ""))

    # ---- P8e.J
    scoping_bad = []
    banned_fragments = (
        "cross C5 (advantage",
        "C5 (advantage",
        "C5 advantage",
        "Median oracle anchor runtime",
    )
    for silo, card in cards.items():
        bottom = card.get("bottom_line_paragraph") or ""
        scope = card.get("claim_scope") or {}
        tier_hist = card.get("faithfulness_tier_histogram") or {}
        strict_count = scope.get("paper_exact_strict_count")
        template_count = scope.get("template_family_count")
        if not scope:
            scoping_bad.append(f"{silo}: missing claim_scope")
        if strict_count != tier_hist.get("paper-faithful-strict", 0):
            scoping_bad.append(f"{silo}: strict count mismatch")
        if template_count != tier_hist.get("paper-family-template", 0):
            scoping_bad.append(f"{silo}: template count mismatch")
        if any(fragment in bottom for fragment in banned_fragments):
            scoping_bad.append(f"{silo}: banned overclaim text")
        if card.get("n_F", 0) == 0 and "No quantitative" not in bottom:
            scoping_bad.append(f"{silo}: f-zero bottom line lacks no-claim caveat")
        if 0 < card.get("n_F", 0) <= 2 and "No silo-level statistical claim" not in bottom:
            scoping_bad.append(f"{silo}: small-sample bottom line lacks no-test caveat")
        if card.get("n_F", 0) > 0 and strict_count == 0 and "template/family" not in bottom:
            scoping_bad.append(f"{silo}: legacy F scope does not mention template/family tier")
    add("P8e.J", "PASS" if not scoping_bad else "FAIL",
        "per-silo claim scoping OK" if not scoping_bad
        else f"claim-scoping issues: {scoping_bad[:8]}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "phase": "8e",
        "results": results,
        "totals": {
            "blockers_failed": blockers_failed,
            "n_pass": sum(1 for r in results if r["status"] == "PASS"),
            "n_fail": sum(1 for r in results if r["status"] == "FAIL"),
        },
    }, indent=2), encoding="utf-8")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    print(f"[Phase 8e audit] {n_pass} PASS / {n_fail} FAIL; "
          f"blockers_failed={blockers_failed}")
    for r in results:
        marker = "[ok]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {marker} {r['id']}: {r['message']}")
    print(f"[Phase 8e audit] Report -> {REPORT}")
    return 1 if blockers_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
