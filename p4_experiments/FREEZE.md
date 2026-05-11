# `p4_experiments/` — freeze record

| Field | Value |
|---|---|
| Freeze date | 2026-05-02 |
| Status | **Frozen** for code/data. No further QDK runs before manuscript. |
| Cohort | 71 labels / 8 silos (per [canonical/cohort.json](canonical/cohort.json)) |
| Canonical Phase-8 records | **2 556** (2 519 OK + 37 documented engine failures) under `common/output/results/` in the source archive |
| Phase-8d HHL/QAE scout records | **108** (72 OK + 36 documented engine failures) |
| Classical baselines | measured + paper-cited fallbacks under `common/output/classical_results/` in the source archive |

## Three tiers (artifact claim boundary)

| Tier | Active estimator-cohort count | Definition | Phase-8 strict-path records |
|---|---:|---|---:|
| `paper-faithful-strict` | **0** | Paper-exact implementation tier. Empty in the active 71-label estimator cohort. | **0** |
| `paper-family-template` | **13** | Legacy F labels whose measured circuits are family/scale-faithful templates or aliases rather than paper-exact circuits. | n/a |
| `proxy` | **58** | Proxy-declared labels outside the reviewed F set. | n/a |

The honest reading of the audit, made explicit in [scripts/implementation_type_audit_report.json](scripts/implementation_type_audit_report.json) and `canonical/outputs/manuscript_artifacts/key_numbers.json` in the source archive:

> **The Phase-8 grid covers all 71 active cohort labels** (71 × 6 profiles × 3 ε × 2 modes = 2 556 cells; 2 519 OK + 37 documented engine failures). The active grid supports family/template and proxy/cohort claims only. It does **not** support paper-exact estimator claims, and any "strict-tier H1/H2/H4 statistic" is N/A in this freeze.

## Family ↔ marker mismatches (disclosed, not bugs)

[scripts/implementation_type_audit_report.json](scripts/implementation_type_audit_report.json) lists **15 labels** whose declared `algorithm_family` does not match the template their `circuit.py` actually uses (e.g., `SD15` declares `amplitude-estimation` but its evidence_marker is `sim_mc_state_prep`). Treat the report's `family_disclosure` field as the artifact-level disclosure rather than re-deriving the mismatch from `circuit.py`:

| Label | Declared family | Evidence marker |
|---|---|---|
| SD15 | amplitude-estimation | sim_mc_state_prep |
| SF1 | amplitude-estimation | sim_mc_state_prep |
| SM2 | amplitude-estimation | sim_mc_state_prep |
| SM7 | amplitude-estimation | sim_mc_state_prep |
| SM8 | amplitude-estimation | sim_mc_state_prep |
| SQ7 | vqe | no template marker; defaults to family-template |
| ST1 | hhl | ansatz_stretch |
| ST2 | hhl | ansatz_stretch |
| SX1 | hhl | ansatz_stretch |
| SX2 | hhl | ansatz_stretch |
| SX3 | hhl | ansatz_stretch |
| SX4 | hhl | ansatz_stretch |
| SX5 | amplitude-estimation | ansatz_stretch |
| SX6 | amplitude-estimation | ansatz_stretch |
| SX7 | amplitude-estimation | ansatz_stretch |

These are template-faithful proxies at paper-stated scale, not paper-faithful implementations of the declared family. Treat them as appendix evidence, not headline claims.

## Reproducibility

- **`canonical/requirements.lock`** carries OS environment markers (`pywin32`, `pywinpty`, `win32_setctime`, `pymsalruntime` are `; sys_platform == "win32"`); `qfre` and `quantum-finance-slr` editable installs are commented out (verified not imported anywhere under `p4_experiments/`).
- **`.gitattributes`** at repo root pins `* text=auto eol=lf` plus binary excludes; retires the CRLF/LF SHA-mismatch carve-out previously needed by `_pipeline_freeze_validation.json`.
- **Provenance** is on every record (`profile_sha`, `qdk_version`, `preregistration_tag`).
- **Pre-registration / Reproduce / Threats / Decisions logs** in [canonical/](canonical/) are unchanged (mixed-encoding files; never edited via text-replacement tooling — see user memory `mixed-encoding-files`).

## Audit / freeze gates

The two p4 audit scripts are **freeze gates**: they exit non-zero on structural drift.

```powershell
# from repo root
python p4_experiments/scripts/audit_implementation_type.py --dry-run  # exit 2 if missing-instance > 0; avoids instance timestamp churn
python p4_experiments/scripts/audit_common_vs_core.py        # exit 2 if any divergent pair
```

Both currently exit 0.

## What is publishable

| Item | Verdict |
|---|---|
| Canonical Phase-8 grid (2 556 records, 71 active labels × 6 profiles × 3 ε × 2 modes) | **Publishable** as methodology + negative-result artifact with 13 family-template and 58 proxy labels |
| Phase-9 H1-H4 statistics + evidence_report.json | **Publishable** with explicit "strict tier was not estimator-run; H4 is conditional on the family/template + proxy implementation cohort" disclosure |
| Phase-10 manuscript artifact pack (27 artifacts) | **Publishable** |
| Phase-8b/8c classical baselines | **Publishable** |
| Phase-8d HHL/QAE high-N scout (108 records) | **Appendix only** — already framed correctly via PHASE8D_ACADEMIC_GUARDRAILS |
| `family_template` proxy circuits | **Publishable as proxies** at paper-stated scale; H4-as-implementation-test framing required |

## Test-equivalent gates

p4 has no pytest suite (the audit scripts serve as its CI). The repo-level pytest run still discovers `shared/`, `p2/`, `p3/` tests and is green:

```powershell
pytest   # 798 passed, 22 skipped
```

## Deferred (out of freeze)

- **Promote future labels to a real `paper-faithful-strict` Phase-8 run.** Would require selecting paper-exact labels through the P3/S3 cohort process and running the Phase-8 estimator grid on them (~6 × 3 × 2 = 36 cells per label, on existing Linux VMs). Bounded QDK cost; not in this freeze.
- **Phase-8d module fold** into `canonical/phase8d/` package. Cosmetic; deferred per the original plan.
- **Cohort.json refresh** with `implementation_type` baked into each entry. The instance.json files now carry this field individually; the cohort.json refresh is a convenience for downstream phase9/10/11 stats and is not required for the freeze.

## Known historical files (kept for provenance, not authoritative)

- `canonical/outputs/manuscript_artifacts/key_numbers.json` (28-Apr, in the source archive) — pre-audit cohort counts (`n_labels_faithful=13`, `paper-faithful-strict=0`). Superseded for the strict/family distinction by [scripts/implementation_type_audit_report.json](scripts/implementation_type_audit_report.json).
- `canonical/outputs/phase08d_hhl_tail_exploratory/` (in the source archive) — exploratory N=20000 OOM runs; documented negative evidence.
- `infra/azure/phase8_4vm_legacy_bootstrap/` (in the source archive) — frozen legacy infra.
