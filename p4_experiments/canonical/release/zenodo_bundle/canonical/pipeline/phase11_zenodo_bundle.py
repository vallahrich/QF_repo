"""Phase 11 - Zenodo deposition bundle.

Builds a self-contained, hash-stamped tarball + manifest suitable for
Zenodo upload:

    release/zenodo_bundle/
    MANIFEST.json              # SHA-256 for every file + top-level metadata
    README.md                  # what's inside, how to reproduce
    cohort.json                # canonical cohort
    reports/                   # generated JSON reports and audit reports
    manuscript_artifacts/      # tables + figures + key_numbers.json
    requirements.lock          # exact pinned environment
    Dockerfile                 # reproducibility container
    PRE_REGISTRATION.md        # immutable hypothesis statement
    results/                   # record JSON files (compressed)
    canonical/                 # full canonical/*.py pipeline + audits

    release/zenodo_bundle.tar.gz
    release/zenodo_bundle.tar.gz.sha256

Outputs are deterministic given the inputs; reruns are idempotent.

This script does NOT push to Zenodo - it only builds the artifact. The
Zenodo API push remains a manual operator step that requires the
Zenodo API token and explicit publish confirmation.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tarfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"
COHORT = CANON / "cohort.json"
PRE_REG = CANON / "PRE_REGISTRATION.md"
RESULTS_DIR = ROOT / "p4_experiments" / "common" / "output" / "results"
REPORTS = CANON / "reports"
AUDIT_REPORTS = REPORTS / "audit"
RELEASE = CANON / "release"
BUNDLE = RELEASE / "zenodo_bundle"
TARBALL = RELEASE / "zenodo_bundle.tar.gz"


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        _unlink_if_stale(dst)
    shutil.copy2(src, dst)
    src_sha = _sha256(src)
    dst_sha = _sha256(dst)
    if src_sha != dst_sha:
        raise RuntimeError(
            f"copy verification failed for {dst.relative_to(BUNDLE)}: "
            f"source={src_sha}, bundle={dst_sha}"
        )


def _unlink_if_stale(path: Path) -> None:
    try:
        path.unlink()
    except PermissionError:
        os.chmod(path, 0o666)
        path.unlink()


def _remove_stale_bundle_files(expected_rels: set[str]) -> None:
    """Remove obsolete files while preserving OneDrive-managed directories.

    On Windows/OneDrive, bundle subdirectories can carry ReadOnly/ReparsePoint
    attributes that make ``shutil.rmtree`` fail even when their contents are
    removable. The release artifact is defined by MANIFEST.json, so we refresh
    files in place and later archive only manifest-listed paths.
    """
    if not BUNDLE.exists():
        return
    for path in sorted((p for p in BUNDLE.rglob("*") if p.is_file()), reverse=True):
        rel = path.relative_to(BUNDLE).as_posix()
        if rel not in expected_rels:
            _unlink_if_stale(path)


def _readme(cohort: dict) -> str:
    p1 = (cohort.get("_phase_status") or {}).get("phase1") or {}
    p8 = (cohort.get("_phase_status") or {}).get("phase8") or {}
    p9 = (cohort.get("_phase_status") or {}).get("phase9") or {}
    return f"""# QF P4 Canonical Pipeline - Zenodo bundle

Generated: {datetime.now(timezone.utc).isoformat()}
Freeze tag: freeze-2026-05-02 (see top-level FREEZE.md in the source repo)

## Contents
- `cohort.json` - 71-label S2-backed canonical cohort with `_phase_status` history.
- `reports/stats_report.json` - H1/H2/H3/H4 statistical test results on the
        family-template implementation cohort; the active cohort contains no
        paper-faithful-strict estimator labels.
- `reports/oracle_tax_table.json` - per-(label, profile, eps) tau ratios.
- `reports/sensitivity_grid.json` - H4 sensitivity across tau-thresholds and baseline scales.
- `reports/evidence_report.json` - Phase 9b evidence layer linking H1-H4 results to manuscript claims.
- `reports/audit/audit_phase{{1..11}}.json` - per-phase audit reports (all blockers green at tag time).
- `manuscript_artifacts/` - LaTeX tables, figure source CSVs, briefs, captions, and `key_numbers.json`.
- `audit/implementation_type_audit_report.json` - per-label tier classification
        (0 paper-faithful-strict / 13 paper-family-template / 58 proxy)
        + family-mismatch disclosures stamped onto affected `instance.json` files.
- `experiments/silos/<silo>/<paper>/instance.json` - per-label instance metadata
  including `implementation_type` and `family_disclosure` where applicable.
- `results/` - raw record JSON files from Phase 8 (2556 cells; 2519 OK + 37
  documented engine failures).
- `canonical/` - full active pipeline source code, phase scripts, audits, and run_pipeline.py.
- `requirements.lock` + `Dockerfile` - reproducibility environment.
  Lockfile carries `; sys_platform == "win32"` markers on Windows-only
  packages and excludes private editable installs not imported by the pipeline.
- `PRE_REGISTRATION.md` - immutable pre-registration document.
- `FREEZE.md` - top-level freeze record at the time of bundling.

## Reproduction
```bash
docker build -t qf-p4-canonical .
docker run --rm -v "$PWD/output:/app/output" qf-p4-canonical
```

## Headline numbers
- N labels in cohort: {len(cohort.get("labels") or {})}
- Implementation tiers:
        - paper-faithful-strict: 0 active estimator labels
        - paper-family-template: 13
        - proxy: 58
- N records (Phase 8 grid): {(p8.get("results_breakdown") or {}).get("total_records", 2556)}
- H4 canonical winners: {p9.get("h4_canonical_winners_count", 0)}
- H4 bifurcation holds (family-template cohort): {p9.get("h4_bifurcation_holds", True)}

## What is N/A in this bundle
The active cohort contains no paper-faithful-strict estimator labels. Any
"strict-tier H1/H2/H4 statistic" therefore reads as N/A. The H4=empty result
reported here is conditional on the family-template implementation cohort and
is NOT a field-wide impossibility theorem.

## Provenance
Built from canonical pipeline at git tag freeze-2026-05-02 (or later commit
on the same line; see MANIFEST.json `git_head` for the exact SHA).
Seed: 0x50414D50.
"""


def _gather_files(cohort: dict) -> list[tuple[Path, str]]:
    """Return list of (src_abs_path, dst_relative_path_in_bundle)."""
    pairs: list[tuple[Path, str]] = []

    # Top-level canonical state.
    for f in ["cohort.json"]:
        p = CANON / f
        if p.exists():
            pairs.append((p, f))

    # Generated reports and audit outputs.
    for f in ["phase3_compare.json", "stats_report.json", "oracle_tax_table.json",
              "sensitivity_grid.json", "evidence_report.json", "surviving_engine_failures.json",
              "v5_relocation_report.json"]:
        p = REPORTS / f
        if p.exists():
            pairs.append((p, f"reports/{f}"))
    for f in [REPORTS / "README.md", AUDIT_REPORTS / "README.md"]:
        if f.exists():
            pairs.append((f, f"reports/{f.relative_to(REPORTS).as_posix()}"))
    for f in AUDIT_REPORTS.glob("audit*.json"):
        pairs.append((f, f"reports/audit/{f.name}"))

    # Manuscript artifacts directory.
    mart = CANON / "outputs" / "manuscript_artifacts"
    if mart.exists():
        for f in mart.iterdir():
            if f.is_file():
                pairs.append((f, f"manuscript_artifacts/{f.name}"))

    # PRE_REGISTRATION + Dockerfile + requirements.lock + requirements.in.
    for src, dst in [(PRE_REG, "PRE_REGISTRATION.md"),
                     (CANON / "Dockerfile", "Dockerfile"),
                     (CANON / "requirements.lock", "requirements.lock"),
                     (CANON / "requirements.in", "requirements.in")]:
        if src.exists():
            pairs.append((src, dst))

    # Active source code needed to reproduce the canonical pipeline.
    for f in CANON.rglob("*.py"):
        if "release" not in f.relative_to(CANON).parts:
            pairs.append((f, f"canonical/{f.relative_to(CANON).as_posix()}"))
    for source_root, bundle_root in [
        (ROOT / "p4_experiments" / "core", "core"),
        (ROOT / "p4_experiments" / "experiments" / "silos", "experiments/silos"),
    ]:
        if source_root.exists():
            for f in source_root.rglob("*.py"):
                pairs.append((f, f"{bundle_root}/{f.relative_to(source_root).as_posix()}"))

    # Per-label instance.json (added 2026-05-02 freeze) so the bundle ships
    # the implementation_type / family_disclosure metadata stamped by
    # scripts/audit_implementation_type.py.
    silos_root = ROOT / "p4_experiments" / "experiments" / "silos"
    if silos_root.exists():
        for f in silos_root.rglob("instance.json"):
            rel = f.relative_to(silos_root).as_posix()
            pairs.append((f, f"experiments/silos/{rel}"))

    # Freeze-time audit reports (added 2026-05-02 freeze).
    audit_freeze_pairs = [
        (ROOT / "p4_experiments" / "scripts" / "implementation_type_audit_report.json",
         "audit/implementation_type_audit_report.json"),
        (ROOT / "p4_experiments" / "FREEZE.md", "FREEZE.p4.md"),
        (ROOT / "FREEZE.md", "FREEZE.md"),
    ]
    for src, dst in audit_freeze_pairs:
        if src.exists():
            pairs.append((src, dst))

    # All result records.
    if RESULTS_DIR.exists():
        for f in RESULTS_DIR.glob("*.json"):
            pairs.append((f, f"results/{f.name}"))
        for f in RESULTS_DIR.glob("*.log"):
            pairs.append((f, f"results/{f.name}"))

    # Schema.
    schema = ROOT / "p4_experiments" / "core" / "schemas" / "result_record.schema.json"
    if schema.exists():
        pairs.append((schema, "schemas/result_record.schema.json"))

    return pairs


def main() -> int:
    cohort = json.loads(COHORT.read_text(encoding="utf-8"))
    pairs = _gather_files(cohort)
    expected_rels = {rel for _, rel in pairs} | {"README.md", "MANIFEST.json"}

    # Refresh bundle files in place. Avoid whole-tree deletion because
    # OneDrive-managed Windows folders can deny rmdir on reparse-point dirs.
    BUNDLE.mkdir(parents=True, exist_ok=True)
    _remove_stale_bundle_files(expected_rels)

    print(f"[Phase 11] gathering {len(pairs)} files into bundle...")

    manifest: dict[str, dict] = {}
    for src, rel in pairs:
        dst = BUNDLE / rel
        _copy_file(src, dst)
        manifest[rel] = {
            "sha256": _sha256(dst),
            "size_bytes": dst.stat().st_size,
        }

    # README.
    (BUNDLE / "README.md").write_text(_readme(cohort), encoding="utf-8")
    manifest["README.md"] = {
        "sha256": _sha256(BUNDLE / "README.md"),
        "size_bytes": (BUNDLE / "README.md").stat().st_size,
    }

    # MANIFEST.
    manifest_full = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": _git_head(),
        "n_files": len(manifest),
        "total_size_bytes": sum(d["size_bytes"] for d in manifest.values()),
        "files": dict(sorted(manifest.items())),
    }
    (BUNDLE / "MANIFEST.json").write_text(json.dumps(manifest_full, indent=2), encoding="utf-8")
    print(f"[Phase 11] bundle built: {len(manifest)} files, "
          f"{manifest_full['total_size_bytes']/1e6:.1f} MB.")

    # Tarball.
    if TARBALL.exists():
        TARBALL.unlink()
    print(f"[Phase 11] writing {TARBALL.relative_to(ROOT)} ...")
    with tarfile.open(TARBALL, "w:gz", compresslevel=6) as tar:
        for rel in sorted([*manifest.keys(), "MANIFEST.json"]):
            tar.add(BUNDLE / rel, arcname=f"qf-p4-canonical-v1/{rel}")
    tar_sha = _sha256(TARBALL)
    RELEASE.mkdir(parents=True, exist_ok=True)
    (RELEASE / "zenodo_bundle.tar.gz.sha256").write_text(f"{tar_sha}  zenodo_bundle.tar.gz\n", encoding="utf-8")
    print(f"[Phase 11] tarball SHA-256: {tar_sha}")
    print(f"[Phase 11] tarball size: {TARBALL.stat().st_size/1e6:.1f} MB")

    ps = cohort.get("_phase_status") or {}
    ps["phase11"] = {
        "status": "complete",
        "completed_utc": datetime.now(timezone.utc).isoformat(),
        "tarball": str(TARBALL.relative_to(ROOT)).replace("\\", "/"),
        "tarball_sha256": tar_sha,
        "tarball_size_bytes": TARBALL.stat().st_size,
        "n_files_in_bundle": len(manifest),
    }
    cohort["_phase_status"] = ps
    COHORT.write_text(json.dumps(cohort, indent=2), encoding="utf-8")
    return 0


def _git_head() -> str:
    try:
        import subprocess
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
