# tools/verify/

Lightweight verification harness for the quantum-finance repository. Each
script operates on **existing artefacts only** — none of them re-run any
LLM jobs, the P2 classification pipeline, the P3 quantitative extraction,
or any P4 Phase 8 cells.

Run all checks via the repo-root aggregator:

```powershell
python -m pip install openai python-dotenv requests python-frontmatter pypdf pytest
pwsh ./verify.ps1
```

Reports are written to `tools/verify/reports/`. Non-zero exit code from any
single check fails the aggregate run.

## Scripts

| Script | Purpose |
|---|---|
| `v1_schema_validate.py` | JSON-Schema validation of every config / phase-3 manifest under `shared/`. |
| `v2_consistency.py` | Cross-file consistency between `unified_taxonomy.json` ↔ `silo_inclusion.json` ↔ `p3_thematic_synthesis/problems/`. |
| `v3_trace_label.py` | For each P4 cohort label, walk back to P3 row → P3 extraction → P2 paper → bridge DOI/Zotero row; accepts only explicitly listed bridge exceptions in `v3_trace_label_allowlist.json`. |
| `v5_recompute_p3.py` | Recompute consensus-label distribution from `triangulation_matrix.json`; diff against documented claims. |
| `v6_check_doc_claims.py` | Regex-extract numeric claims from README / status docs and compare to actual file counts. |
| `v7_algorithm_families.py` | Enumerate `algorithm.family` values across P3 extractions; flag uncovered values. |
| `v9_bridge.py` | Bridge-file audit: DOI casing, duplicate detection, preprint↔published candidates. |
| `v_make_active_fingerprints.py` | (planned, Phase 3) Generate sha256 manifest for the active P3 baseline. |

## Conventions

- All scripts are runnable as `python -m tools.verify.<name>` from repo root.
- Reports go to `tools/verify/reports/<script>_YYYY-MM-DD.json`.
- Exit codes: 0 = pass, 1 = drift detected, 2 = script error.

## Accepted drift

Known drift is tracked in [reports/known_drift_2026-05.md](reports/known_drift_2026-05.md).
V3 bridge-only gaps must either be repaired in [../../shared/bridge/paper_id_bridge.csv](../../shared/bridge/paper_id_bridge.csv)
or listed in [v3_trace_label_allowlist.json](v3_trace_label_allowlist.json)
with label, reason, source artifact, and claim-use boundary. New unaccepted V3
breaks still make `verify.ps1` fail.
