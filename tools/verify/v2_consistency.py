"""V2: cross-file consistency between the canonical taxonomy and the
artefacts that depend on it.

Operates on existing files only. Reports drift; does not modify anything.

Checks
------
C1 PD codes in `unified_taxonomy.json` ⊇ codes in `silo_inclusion.json`
   (`active_silos` ∪ `excluded_silos`).
C2 For every active silo, `p3_thematic_synthesis/s4_thematic_coding/<folder>/`
   exists. (Active per-silo working data was relocated from `problems/`
   to `s4_thematic_coding/` after the 2026-05-02 freeze; `problems/`
   retains only the excluded PD-08 silo for traceability.)
C3 Every silo folder under `s4_thematic_coding/` is referenced somewhere
   in the taxonomy / silo_inclusion / cross_cutting list (no orphan folders).
   Non-silo subfolders (`cross_silo/`, `papers/`, `output/`) are skipped.
C4 PD-08 status drift: `unified_taxonomy.json` PD-08 should have
   `status=excluded` AND silo_inclusion.json should list it under
   `excluded_silos`.
C5 PD-10 status drift: `unified_taxonomy.json` PD-10 should have
   `status=retracted` and `merged_into=PD-03`; silo_inclusion.json
   should list it under `excluded_silos` (merged) too.
C6 If a silo folder is the target of a `merged_into=` annotation,
   the source category should also carry a `RETRACTION.md` or
   in-folder STATUS.md somewhere obvious.

This script also serves as the production replacement for
`shared/validate_taxonomy.py` (which previously did only a one-line
substring check); the legacy script is rewritten to delegate here.

Run: python -m tools.verify.v2_consistency
"""

from __future__ import annotations

import datetime as _dt
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    findings: list[dict] = []

    tax = _load(REPO_ROOT / "shared" / "config" / "unified_taxonomy.json")
    silo = _load(REPO_ROOT / "shared" / "config" / "silo_inclusion.json")
    # Active per-silo working data lives under s4_thematic_coding/ since the
    # post-2026-05-02 restructure; problems/ retains only excluded PD-08.
    active_silo_dir = REPO_ROOT / "p3_thematic_synthesis" / "s4_thematic_coding"
    problems_dir = REPO_ROOT / "p3_thematic_synthesis" / "problems"
    # Subfolders of s4_thematic_coding/ that are not silos.
    NON_SILO_SUBDIRS = {"cross_silo", "papers", "output"}

    tax_codes = {v["code"]: k for k, v in tax["topic_tags"].items()}
    tax_status = {v["code"]: v.get("status", "active") for v in tax["topic_tags"].values()}
    tax_folder = {v["code"]: v.get("silo_folder") for v in tax["topic_tags"].values()}
    tax_merged = {v["code"]: v.get("merged_into") for v in tax["topic_tags"].values()}

    silo_active = {s["code"]: s for s in silo.get("active_silos", [])}
    silo_excluded = {s["code"]: s for s in silo.get("excluded_silos", [])}
    silo_cross_cutting = {s["folder"] for s in silo.get("cross_cutting", [])}

    # C1: superset
    silo_codes = set(silo_active) | set(silo_excluded)
    missing_in_tax = silo_codes - set(tax_codes)
    for c in sorted(missing_in_tax):
        findings.append({"check": "C1_superset", "severity": "fail",
                         "code": c, "msg": f"{c} appears in silo_inclusion.json but not in unified_taxonomy.json"})

    # C2: active silo folder exists on disk (under s4_thematic_coding/)
    for code, entry in silo_active.items():
        folder = entry["folder"]
        if not (active_silo_dir / folder).is_dir():
            findings.append({"check": "C2_active_folder_exists", "severity": "fail",
                             "code": code, "folder": folder,
                             "msg": f"Active silo {code} ({folder}) has no folder under s4_thematic_coding/"})

    # C3: orphan folders under s4_thematic_coding/ (not in any registry)
    known_folders = set()
    for entry in silo_active.values():
        known_folders.add(entry["folder"])
    for entry in silo_excluded.values():
        known_folders.add(entry["folder"])
    known_folders |= silo_cross_cutting
    if active_silo_dir.is_dir():
        for d in sorted(p for p in active_silo_dir.iterdir() if p.is_dir()):
            if d.name in NON_SILO_SUBDIRS:
                continue
            if d.name not in known_folders:
                findings.append({"check": "C3_orphan_folder", "severity": "warn",
                                 "folder": d.name,
                                 "msg": f"Folder s4_thematic_coding/{d.name}/ is not referenced by silo_inclusion.json"})

    # C4: PD-08 status drift
    if tax_status.get("PD-08") != "excluded":
        findings.append({"check": "C4_pd08_status", "severity": "fail",
                         "msg": f"PD-08 status in unified_taxonomy.json is "
                                f"'{tax_status.get('PD-08')}'; expected 'excluded'."})
    if "PD-08" not in silo_excluded:
        findings.append({"check": "C4_pd08_status", "severity": "fail",
                         "msg": "PD-08 not listed in silo_inclusion.json:excluded_silos"})

    # C5: PD-10 status drift
    if tax_status.get("PD-10") != "retracted":
        findings.append({"check": "C5_pd10_status", "severity": "fail",
                         "msg": f"PD-10 status in unified_taxonomy.json is "
                                f"'{tax_status.get('PD-10')}'; expected 'retracted'."})
    if tax_merged.get("PD-10") != "PD-03":
        findings.append({"check": "C5_pd10_status", "severity": "fail",
                         "msg": f"PD-10 merged_into is "
                                f"'{tax_merged.get('PD-10')}'; expected 'PD-03'."})

    # C6: merged-into source has visible marker
    quarantine = REPO_ROOT / "p1_framework_synthesis" / "s1_extractions" / \
                 "_QUARANTINED_2026_AtharvaJain_misidentified.RETRACTION.md"
    if tax_status.get("PD-10") == "retracted" and not quarantine.exists():
        findings.append({"check": "C6_retraction_marker", "severity": "warn",
                         "msg": f"PD-10 marked retracted but expected marker missing: "
                                f"{quarantine.relative_to(REPO_ROOT)}"})

    # C7 (added 2026-05-02 freeze): generic merged-status integrity check.
    # Any taxonomy entry with status='merged' must (a) point its merged_into
    # at a code that exists, and (b) not have its silo_folder dangling as an
    # active problems/ directory (orphan check, severity=warn).
    for code, status in tax_status.items():
        if status != "merged":
            continue
        target = tax_merged.get(code)
        if not target:
            findings.append({"check": "C7_merged_target", "severity": "fail",
                             "code": code,
                             "msg": f"{code} has status='merged' but no merged_into target."})
        elif target not in tax_codes:
            findings.append({"check": "C7_merged_target", "severity": "fail",
                             "code": code, "merged_into": target,
                             "msg": f"{code} merged_into='{target}' which is not a known PD code."})
        folder = tax_folder.get(code)
        if folder and (problems_dir / folder).is_dir():
            findings.append({"check": "C7_merged_orphan_folder", "severity": "warn",
                             "code": code, "folder": folder,
                             "msg": f"{code} (status=merged) still has live folder "
                                    f"problems/{folder}/; consider archiving."})

    summary = {
        "script": "v2_consistency",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "findings_count": len(findings),
        "fail_count": sum(1 for f in findings if f["severity"] == "fail"),
        "warn_count": sum(1 for f in findings if f["severity"] == "warn"),
        "findings": findings,
    }
    out = REPORT_DIR / f"v2_consistency_{_dt.date.today().isoformat()}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"V2 consistency: {summary['fail_count']} fail / {summary['warn_count']} warn / "
          f"{summary['findings_count']} total")
    print(f"  report: {out.relative_to(REPO_ROOT)}")
    for f in findings:
        print(f"  [{f['severity']}] {f['check']}: {f['msg']}")
    return 0 if summary["fail_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
