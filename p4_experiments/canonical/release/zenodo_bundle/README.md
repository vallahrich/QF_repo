# QF P4 Canonical Pipeline - Zenodo bundle

Generated: 2026-05-11T15:12:17.053154+00:00
Freeze tag: freeze-2026-05-02 (see top-level FREEZE.md in the source repo)

## Contents
- `cohort.json` - 71-label S2-backed canonical cohort with `_phase_status` history.
- `reports/stats_report.json` - H1/H2/H3/H4 statistical test results on the
        family-template implementation cohort; the active cohort contains no
        paper-faithful-strict estimator labels.
- `reports/oracle_tax_table.json` - per-(label, profile, eps) tau ratios.
- `reports/sensitivity_grid.json` - H4 sensitivity across tau-thresholds and baseline scales.
- `reports/evidence_report.json` - Phase 9b evidence layer linking H1-H4 results to manuscript claims.
- `reports/audit/audit_phase{1..11}.json` - per-phase audit reports (all blockers green at tag time).
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
- N labels in cohort: 71
- Implementation tiers:
        - paper-faithful-strict: 0 active estimator labels
        - paper-family-template: 13
        - proxy: 58
- N records (Phase 8 grid): 2556
- H4 canonical winners: 0
- H4 bifurcation holds (family-template cohort): True

## What is N/A in this bundle
The active cohort contains no paper-faithful-strict estimator labels. Any
"strict-tier H1/H2/H4 statistic" therefore reads as N/A. The H4=empty result
reported here is conditional on the family-template implementation cohort and
is NOT a field-wide impossibility theorem.

## Provenance
Built from canonical pipeline at git tag freeze-2026-05-02 (or later commit
on the same line; see MANIFEST.json `git_head` for the exact SHA).
Seed: 0x50414D50.
