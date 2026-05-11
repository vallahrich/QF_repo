"""Phase 8 audit - big-run completeness, schema validity, and engine_failure disclosure.

Checks:
  P8.A  cohort._phase_status.phase8.status == "complete".
    P8.B  Total record count in results/ equals expected (n_labels * 36)
        OR every missing cell has a documented engine_failure record.
  P8.C  Every record file is JSON and validates against
        result_record.schema.json.
  P8.D  Every (label, profile, eps, mode) cell of the canonical grid
        has exactly one record (no duplicates, no holes that aren't
        explained by an engine_failure).
  P8.E  All engine_failure records carry a non-empty
        ``measured.reason`` and a numeric ``measured.wall_clock_seconds``.
  P8.F  results_breakdown in cohort matches a fresh scan of the
        results directory.

Reports per-silo and per-profile completion fractions.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
RESULTS = ROOT / "p4_experiments" / "common" / "output" / "results"
SCHEMA = ROOT / "p4_experiments" / "core" / "schemas" / "result_record.schema.json"
REPORTS = CANON / "reports"
REPORT = REPORTS / "audit" / "audit_phase8.json"
SURVIVING_FAILURES = REPORTS / "surviving_engine_failures.json"

PROFILES = [
    "sc_e3_surface", "sc_e4_surface",
    "ti_e3_surface", "ti_e4_surface",
    "maj_e6_surface", "maj_e6_floquet",
]
EPSILONS = [1e-3, 1e-4, 1e-6]
MODES = ["bare", "full"]
EXPECTED_PER_LABEL = len(PROFILES) * len(EPSILONS) * len(MODES)  # 36


def _read_json(path: Path, attempts: int = 5) -> dict:
    for attempt in range(attempts):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (PermissionError, OSError, json.JSONDecodeError):
            if attempt == attempts - 1:
                raise
            time.sleep(0.2)
    raise RuntimeError(f"unreachable read retry state for {path}")


def _eps_str(eps: float) -> str:
    return f"{eps:.0e}"


def _expected_filename(label: str, profile: str, eps: float, mode: str) -> str:
    return f"{label}_{profile}_eps{_eps_str(eps)}_{mode}.json"


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    labels = sorted(cohort["labels"].keys())
    n_labels = len(labels)
    expected_total = n_labels * EXPECTED_PER_LABEL

    results: list[dict] = []
    blockers_failed = 0

    def add(check_id: str, status: str, msg: str, blocker: bool = True) -> None:
        nonlocal blockers_failed
        if status == "FAIL" and blocker:
            blockers_failed += 1
        results.append({"id": check_id, "status": status, "blocker": blocker, "message": msg})

    # P8.A
    p8 = (cohort.get("_phase_status") or {}).get("phase8") or {}
    add("P8.A", "PASS" if p8.get("status") == "complete" else "FAIL",
        f"cohort._phase_status.phase8.status='{p8.get('status')}'")

    # Scan results directory.
    record_files: dict[str, Path] = {}  # filename -> path
    if RESULTS.exists():
        for p in RESULTS.glob("*.json"):
            record_files[p.name] = p

    # Build expected filename set.
    expected_files: set[str] = set()
    for lid in labels:
        for prof in PROFILES:
            for eps in EPSILONS:
                for mode in MODES:
                    expected_files.add(_expected_filename(lid, prof, eps, mode))

    found = set(record_files.keys()) & expected_files
    missing = expected_files - set(record_files.keys())
    extra = set(record_files.keys()) - expected_files - {"_skipped.log", "_engine_failures.log"}

    parsed_records: dict[str, dict] = {}
    parse_errors: dict[str, str] = {}
    for fn in sorted(found):
        try:
            parsed_records[fn] = _read_json(record_files[fn])
        except Exception as exc:
            parse_errors[fn] = f"parse_error:{exc}"

    # P8.B
    add("P8.B", "PASS" if not missing else "FAIL",
        f"Records present={len(found)} / expected={expected_total} (missing={len(missing)})"
        + (f"; first missing: {sorted(missing)[:5]}" if missing else ""))

    # P8.C - schema validation.
    try:
        from jsonschema import Draft202012Validator
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        invalid = [f"{fn}:{msg}" for fn, msg in sorted(parse_errors.items())]
        for fn, rec in sorted(parsed_records.items()):
            errors = list(validator.iter_errors(rec))
            if errors:
                invalid.append(f"{fn}:{errors[0].message[:80]}")
        add("P8.C", "PASS" if not invalid else "FAIL",
            f"All {len(found)} records schema-valid"
            if not invalid else f"{len(invalid)} schema violations; first: {invalid[:3]}")
    except ImportError:
        add("P8.C", "FAIL", "jsonschema not installed; cannot validate.")

    # P8.D - duplicates / hole analysis (per-cell counts already implied by set arithmetic).
    add("P8.D", "PASS" if not extra else "FAIL",
        f"No unexpected record filenames in results/"
        if not extra else f"{len(extra)} unexpected files: {sorted(extra)[:5]}")

    # P8.E - engine_failure records carry reason + wall_clock_seconds.
    n_engine_failure = 0
    bad_failures: list[str] = []
    for fn, rec in sorted(parsed_records.items()):
        m = rec.get("measured") or {}
        if m.get("status") == "engine_failure":
            n_engine_failure += 1
            if not m.get("reason") or not isinstance(m.get("wall_clock_seconds"), (int, float)):
                bad_failures.append(fn)
    add("P8.E", "PASS" if not bad_failures else "FAIL",
        f"engine_failure records={n_engine_failure}; all carry reason+wall_clock_seconds"
        if not bad_failures else f"{len(bad_failures)} malformed engine_failure records; first: {bad_failures[:3]}")

    # P8.F
    rb = p8.get("results_breakdown") or {}
    fresh = {
        "total_records": len(record_files),
        "ok": 0, "engine_failure": 0,
    }
    for rec in parsed_records.values():
        s = (rec.get("measured") or {}).get("status")
        if s == "engine_failure":
            fresh["engine_failure"] += 1
        else:
            fresh["ok"] += 1
    fresh["total_records"] = len(record_files)
    consistent = (rb.get("ok") == fresh["ok"]) and (rb.get("engine_failure") == fresh["engine_failure"])
    add("P8.F", "PASS" if consistent else "FAIL",
        f"cohort breakdown matches fresh scan: cohort={rb}, fresh={fresh}"
        if consistent else f"MISMATCH: cohort={rb}, fresh={fresh}")

    # Per-label silo lookup (used by P8.G and the per-silo completion summary).
    silo_of = {lid: e.get("silo") for lid, e in cohort["labels"].items()}

    # P8.G - engine_failure forensic artifact for IV-10 manuscript appendix.
    # Emits surviving_engine_failures.json with per-(label, profile, eps, mode)
    # breakdown so the appendix table is mechanically reproducible from this
    # single artifact (no rescan required). PASS when the file is written and
    # the per-axis sums equal the global engine_failure count from P8.F.
    failure_records: list[dict] = []
    by_label: dict[str, int] = {}
    by_profile: dict[str, int] = {}
    by_eps: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    by_label_profile: dict[str, int] = {}
    by_silo: dict[str, int] = {}
    for fn, rec in sorted(parsed_records.items()):
        m = rec.get("measured") or {}
        if m.get("status") != "engine_failure":
            continue
        lid = rec.get("label") or "unknown"
        prof = rec.get("hardware_profile") or "unknown"
        eps = rec.get("epsilon")
        mode = rec.get("accounting_mode") or "unknown"
        eps_key = _eps_str(eps) if isinstance(eps, (int, float)) else str(eps)
        silo = silo_of.get(lid, "unknown")
        failure_records.append({
            "filename": fn,
            "label": lid,
            "silo": silo,
            "profile": prof,
            "eps": eps,
            "mode": mode,
            "reason": m.get("reason"),
            "wall_clock_seconds": m.get("wall_clock_seconds"),
        })
        by_label[lid] = by_label.get(lid, 0) + 1
        by_profile[prof] = by_profile.get(prof, 0) + 1
        by_eps[eps_key] = by_eps.get(eps_key, 0) + 1
        by_mode[mode] = by_mode.get(mode, 0) + 1
        by_silo[silo] = by_silo.get(silo, 0) + 1
        key = f"{lid}|{prof}"
        by_label_profile[key] = by_label_profile.get(key, 0) + 1

    surviving = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total_engine_failures": len(failure_records),
        "by_label": dict(sorted(by_label.items())),
        "by_silo": dict(sorted(by_silo.items())),
        "by_profile": dict(sorted(by_profile.items())),
        "by_eps": dict(sorted(by_eps.items())),
        "by_mode": dict(sorted(by_mode.items())),
        "by_label_profile": dict(sorted(by_label_profile.items())),
        "records": failure_records,
        "note": ("Appendix-ready forensic table for THREATS_TO_VALIDITY IV-10. "
                 "All entries here are documented engine_failures: the Azure RE "
                 "did not converge on the cell within the configured timeout. "
                 "Counts here equal the engine_failure_records total reported "
                 "by P8.F (verified by P8.G)."),
    }
    SURVIVING_FAILURES.parent.mkdir(parents=True, exist_ok=True)
    SURVIVING_FAILURES.write_text(json.dumps(surviving, indent=2), encoding="utf-8")
    sums_match = (
        sum(by_label.values()) == len(failure_records)
        and sum(by_profile.values()) == len(failure_records)
        and sum(by_eps.values()) == len(failure_records)
        and sum(by_mode.values()) == len(failure_records)
        and len(failure_records) == n_engine_failure
    )
    add("P8.G", "PASS" if sums_match else "FAIL",
        f"surviving_engine_failures.json written ({len(failure_records)} records); "
        f"per-axis sums consistent with P8.F count={n_engine_failure}"
        if sums_match else
        f"sum mismatch: by_label={sum(by_label.values())}, "
        f"by_profile={sum(by_profile.values())}, by_eps={sum(by_eps.values())}, "
        f"by_mode={sum(by_mode.values())}, records={len(failure_records)}, "
        f"P8.F_count={n_engine_failure}")

    # Per-silo / per-profile completion fractions.
    silo_present: dict[str, int] = {}
    silo_expected: dict[str, int] = {}
    for lid in labels:
        s = silo_of.get(lid, "unknown")
        silo_expected[s] = silo_expected.get(s, 0) + EXPECTED_PER_LABEL
        for prof in PROFILES:
            for eps in EPSILONS:
                for mode in MODES:
                    if _expected_filename(lid, prof, eps, mode) in record_files:
                        silo_present[s] = silo_present.get(s, 0) + 1

    profile_present: dict[str, int] = {}
    profile_expected: dict[str, int] = {}
    for prof in PROFILES:
        profile_expected[prof] = n_labels * len(EPSILONS) * len(MODES)
        for lid in labels:
            for eps in EPSILONS:
                for mode in MODES:
                    if _expected_filename(lid, prof, eps, mode) in record_files:
                        profile_present[prof] = profile_present.get(prof, 0) + 1

    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "n_labels": n_labels,
        "expected_total_cells": expected_total,
        "found_records": len(found),
        "extra_records": len(extra),
        "engine_failure_records": n_engine_failure,
        "per_silo_completion": {s: f"{silo_present.get(s, 0)}/{silo_expected[s]}" for s in sorted(silo_expected)},
        "per_profile_completion": {p: f"{profile_present.get(p, 0)}/{profile_expected[p]}" for p in PROFILES},
        "results": results,
        "totals": {"pass": n_pass, "fail": n_fail, "blockers_failed": blockers_failed},
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"[Phase 8 audit] {n_pass} PASS / {n_fail} FAIL; blockers_failed={blockers_failed}")
    for r in results:
        tag = "[ok]" if r["status"] == "PASS" else "[FAIL]"
        print(f"  {tag} {r['id']}: {r['message']}")
    print(f"[Phase 8 audit] per-silo:    {summary['per_silo_completion']}")
    print(f"[Phase 8 audit] per-profile: {summary['per_profile_completion']}")
    print(f"[Phase 8 audit] Report -> {REPORT.relative_to(ROOT)}")
    return 0 if blockers_failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
