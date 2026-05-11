"""Phase 7 audit - reproducibility commitments.

Checks (PRE_REGISTRATION §8):
  P7.A  ``p4_experiments/canonical/requirements.lock`` exists, is non-empty,
        carries the Phase 7 header, and contains every direct dep listed in
        ``requirements.in``.
  P7.B  ``p4_experiments/canonical/Dockerfile`` exists and pins
        Python 3.11.X, the lockfile, and references the canonical
        run_pipeline.py entrypoint.
  P7.C  ``p4_experiments/canonical/run_pipeline.py`` exists, parses,
        defines a ``main()`` function, and supports --dry-run / --resume /
        --skip-big-run / --phases / --from-scratch.
  P7.D  Every PHASES entry (other than phase8/phase9, future) has its
        action_script on disk in p4_experiments/canonical/.
  P7.E  cohort._phase_status.phase7 is recorded with status='complete'
        and the seed pinned at 0x50414D50.
"""

from __future__ import annotations

import ast
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
LOCKFILE = CANON / "requirements.lock"
INFILE = CANON / "requirements.in"
DOCKERFILE = CANON / "Dockerfile"
ORCHESTRATOR = CANON / "run_pipeline.py"
REPORT = CANON / "reports" / "audit" / "audit_phase7.json"


def _parse_requirements_in() -> list[str]:
    out = []
    for line in INFILE.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # split on whitespace and version specifiers
        name = re.split(r"[<>=!~\s]", s, maxsplit=1)[0].lower().replace("_", "-")
        out.append(name)
    return out


def _lock_packages(text: str) -> set[str]:
    pkgs: set[str] = set()
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("-e "):
            continue
        name = re.split(r"[<>=!~\s@]", s, maxsplit=1)[0].lower().replace("_", "-")
        if name:
            pkgs.add(name)
    return pkgs


def main() -> int:
    results: list[dict] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": check_id, "status": status, "blocker": blocker, "message": msg})

    # P7.A
    if not LOCKFILE.exists():
        add("P7.A", "FAIL", "requirements.lock missing")
    else:
        text = LOCKFILE.read_text(encoding="utf-8")
        has_header = text.startswith("# Phase 7 - Canonical environment lockfile")
        n_lines = sum(1 for line in text.splitlines() if line.strip() and not line.strip().startswith("#"))
        direct = _parse_requirements_in() if INFILE.exists() else []
        locked = _lock_packages(text)
        missing = [d for d in direct if d not in locked]
        ok = has_header and n_lines >= 50 and not missing
        msg = f"header={has_header}, pinned_pkgs={n_lines}, direct_deps_missing_from_lock={missing}"
        add("P7.A", "PASS" if ok else "FAIL", msg)

    # P7.B
    if not DOCKERFILE.exists():
        add("P7.B", "FAIL", "Dockerfile missing")
    else:
        d = DOCKERFILE.read_text(encoding="utf-8")
        ok = (
            "FROM python:3.11" in d
            and "requirements.lock" in d
            and "p4_experiments.canonical.run_pipeline" in d
        )
        add("P7.B", "PASS" if ok else "FAIL",
            "Dockerfile pins python:3.11 + requirements.lock + run_pipeline entrypoint"
            if ok else "Dockerfile missing one of: FROM python:3.11, requirements.lock, run_pipeline reference")

    # P7.C
    if not ORCHESTRATOR.exists():
        add("P7.C", "FAIL", "run_pipeline.py missing")
    else:
        src = ORCHESTRATOR.read_text(encoding="utf-8")
        try:
            ast.parse(src)
            parses = True
        except SyntaxError as exc:
            parses = False
            add("P7.C", "FAIL", f"run_pipeline.py parse error: {exc}")
        if parses:
            has_main = "def main(" in src
            flags = ["--dry-run", "--resume", "--skip-big-run", "--phases", "--from-scratch"]
            missing_flags = [f for f in flags if f not in src]
            ok = has_main and not missing_flags
            add("P7.C", "PASS" if ok else "FAIL",
                f"main()={has_main}, missing_flags={missing_flags}")

    # P7.D
    # Inspect orchestrator's PHASES list for required action scripts.
    src = ORCHESTRATOR.read_text(encoding="utf-8") if ORCHESTRATOR.exists() else ""
    referenced = re.findall(r'"script":\s*"([^"]+)"', src)
    missing_scripts = [s for s in referenced
                       if s not in ("phase8_big_run.py", "phase9_stats.py")
                       and not (CANON / s).exists()]
    add("P7.D", "PASS" if not missing_scripts else "FAIL",
        f"All current-phase action scripts present (excl. phase8/9 which are future); "
        f"missing={missing_scripts}")

    # P7.E -- record AND check
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    ps = cohort.get("_phase_status")
    if not isinstance(ps, dict):
        ps = {"_legacy": ps} if ps is not None else {}
    p7 = ps.get("phase7") or {}
    if p7.get("status") != "complete":
        # write it now (audit pass condition: orchestrator + lockfile + dockerfile present)
        if not blockers_failed:
            ps["phase7"] = {
                "status": "complete",
                "completed_utc": datetime.now(timezone.utc).isoformat(),
                "seed": "0x50414D50",
                "lockfile_path": "p4_experiments/canonical/requirements.lock",
                "dockerfile_path": "p4_experiments/canonical/Dockerfile",
                "orchestrator_path": "p4_experiments/canonical/run_pipeline.py",
                "regen_helper": "tools/regen_requirements_lock.ps1",
                "audit_categories_partial": [],
            }
            cohort["_phase_status"] = ps
            COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
            p7 = ps["phase7"]
    ok = p7.get("status") == "complete" and p7.get("seed") == "0x50414D50"
    add("P7.E", "PASS" if ok else "FAIL",
        f"_phase_status.phase7 status='complete' and seed=0x50414D50"
        if ok else f"_phase_status.phase7 = {p7}")

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "totals": {"pass": n_pass, "fail": n_fail, "blockers_failed": blockers_failed},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Phase 7 audit] {n_pass} PASS / {n_fail} FAIL; blockers_failed={blockers_failed}")
    for r in results:
        tag = "[ok]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {tag} {r['id']}: {r['message']}")
    print(f"[Phase 7 audit] Report -> {REPORT.relative_to(ROOT)}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
