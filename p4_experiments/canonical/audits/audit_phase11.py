"""Phase 11 audit - Zenodo bundle verification."""

from __future__ import annotations

import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RELEASE = CANON / "release"
BUNDLE = RELEASE / "zenodo_bundle"
TARBALL = RELEASE / "zenodo_bundle.tar.gz"
SHA = RELEASE / "zenodo_bundle.tar.gz.sha256"
REPORT = CANON / "reports" / "audit" / "audit_phase11.json"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    results: list[dict] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": check_id, "status": status, "blocker": blocker, "message": msg})

    p11 = (cohort.get("_phase_status") or {}).get("phase11") or {}
    add("P11.A", "PASS" if p11.get("status") == "complete" else "FAIL",
        f"cohort._phase_status.phase11.status='{p11.get('status')}'")

    add("P11.B", "PASS" if BUNDLE.exists() else "FAIL",
        f"bundle dir exists: {BUNDLE.relative_to(ROOT)}")

    if not TARBALL.exists():
        add("P11.C", "FAIL", "tarball missing")
    else:
        actual = _sha256(TARBALL)
        recorded = p11.get("tarball_sha256")
        add("P11.C", "PASS" if actual == recorded else "FAIL",
            f"tarball sha256 matches cohort"
            if actual == recorded else f"sha mismatch: actual={actual[:8]}, cohort={(recorded or '')[:8]}")

    if BUNDLE.exists():
        manifest_path = BUNDLE / "MANIFEST.json"
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                files = manifest.get("files") or {}
                bad = []
                for rel, meta in files.items():
                    p = BUNDLE / rel
                    if not p.exists():
                        bad.append((rel, "missing"))
                        continue
                    if _sha256(p) != meta["sha256"]:
                        bad.append((rel, "sha_mismatch"))
                add("P11.D", "PASS" if not bad else "FAIL",
                    f"All {len(files)} bundle files match MANIFEST sha256"
                    if not bad else f"{len(bad)} bad files; first: {bad[:3]}")
            except Exception as exc:
                add("P11.D", "FAIL", f"MANIFEST.json parse error: {exc}")
        else:
            add("P11.D", "FAIL", "MANIFEST.json missing")

    if SHA.exists() and TARBALL.exists():
        recorded = SHA.read_text(encoding="utf-8").split()[0]
        actual = _sha256(TARBALL)
        add("P11.E", "PASS" if recorded == actual else "FAIL",
            f"sidecar .sha256 matches tarball"
            if recorded == actual else f"mismatch")
    else:
        add("P11.E", "FAIL", "sidecar .sha256 missing")

    # P11.F - rendered figures are intentionally excluded from P4 because
    # final figures live in the thesis and appendix. Keep the source CSVs.
    expected_figure_sources = [
        "manuscript_artifacts/figure_h1_heatmap.csv",
        "manuscript_artifacts/figure_h4_criterion_heatmap.csv",
        "manuscript_artifacts/figure_h4_funnel.csv",
        "manuscript_artifacts/figure_h4_qdk_nontriviality.csv",
        "manuscript_artifacts/figure_h4_sensitivity.csv",
        "manuscript_artifacts/figure_oracle_tax_box.csv",
        "manuscript_artifacts/figure_phase8d_scaling.csv",
        "manuscript_artifacts/figure_regime_map.csv",
    ]
    if BUNDLE.exists():
        bundled_rendered_figures = sorted((BUNDLE / "figures").glob("*")) if (BUNDLE / "figures").exists() else []
        missing_sources = [f for f in expected_figure_sources if not (BUNDLE / f).exists()]
        ok = not bundled_rendered_figures and not missing_sources
        add("P11.F", "PASS" if ok else "FAIL",
            "Rendered figures excluded; figure source CSVs present"
            if ok else f"rendered_figures={[p.name for p in bundled_rendered_figures]}, missing_sources={missing_sources}")
    else:
        add("P11.F", "FAIL", "bundle dir missing; cannot check figure source policy")

    # P11.G - engine_failure forensic artifact present in bundle (IV-10
    # appendix source). Produced by audit_phase8.py P8.G.
    fa = BUNDLE / "reports" / "surviving_engine_failures.json"
    if BUNDLE.exists():
        add("P11.G", "PASS" if fa.exists() else "FAIL",
            "surviving_engine_failures.json present in bundle"
            if fa.exists() else "surviving_engine_failures.json missing from bundle")
    else:
        add("P11.G", "FAIL", "bundle dir missing; cannot check forensic artifact")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "totals": {"pass": n_pass, "fail": n_fail, "blockers_failed": blockers_failed},
    }, indent=2), encoding="utf-8")
    print(f"[Phase 11 audit] {n_pass} PASS / {n_fail} FAIL; blockers_failed={blockers_failed}")
    for r in results:
        tag = "[ok]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {tag} {r['id']}: {r['message']}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
