# Repository freeze — 2026-05-02

This file pins the **code/data freeze** for `p1_framework_synthesis/`,
`p2_systematic_review/`, `p3_thematic_synthesis/`, `p4_experiments/`, and
`shared/`. This file is a repository-artifact status record; manuscript files
are out of scope for the 2026-05-02 hardening pass.

| Folder | Status | Detail |
|---|---|---|
| `shared/` | **Frozen** | [shared/FREEZE.md](shared/FREEZE.md) |
| `p1_framework_synthesis/` | **Frozen** | [p1_framework_synthesis/FREEZE.md](p1_framework_synthesis/FREEZE.md) |
| `p2_systematic_review/` | **Frozen** | [p2_systematic_review/FREEZE.md](p2_systematic_review/FREEZE.md) |
| `p3_thematic_synthesis/` | **Frozen** | [p3_thematic_synthesis/FREEZE.md](p3_thematic_synthesis/FREEZE.md) |
| `p4_experiments/` | **Frozen** | [p4_experiments/FREEZE.md](p4_experiments/FREEZE.md) |
| `manuscript/` | not in scope | unchanged by this repository-artifact hardening pass |

## Headline numbers (cite from the per-folder FREEZE.md docs)

| Stage | Number |
|---|---|
| p1 active partition | **8 problem domains × 11 solution categories**; ten PD codes plus PD-11 (`forecasting-prediction`, status `merged → PD-04`) registered in the canonical taxonomy; ≈ 20 effective independent surveys (29 raw – 1 quarantined – 7 EXCLUSIONS – 1 Herman duplicate) |
| p2 SLR included for coding | **777** |
| p2 active downstream subset | **755** (777 – 22 retro-excluded as off-scope) |
| p2 screening recall | **1.000** Wilson 95 % CI [0.846, 1.000] (n=22) |
| p2 screening calibration κ | **0.692 → 0.849** |
| p3 active silos | **8** (PD-01..PD-09 minus PD-08 = excluded; PD-10 retracted into PD-03) |
| p3 active S2 extractions | **501 files / 1 046 experiments** (777 p2 processed papers minus 276 exclusions: 130 no quantitative results + 146 scope-out, per [corpus_lineage.json](p3_thematic_synthesis/s2_quantitative/output/audit/corpus_lineage.json) and [excluded_papers.csv](shared/bridge/excluded_papers.csv)) |
| p3 S3 rows after active-silo filter | **936** consensus/matrix rows; **46** disagreement cases (110 inactive-silo rows dropped from matrix/consensus; 4 dropped from disagreement cases) |
| p3 s6 finance framing | **629 F1 paper outputs / 8 F2 silo briefs**; descriptive framing only, not independent semantic validation |
| p4 cohort | **71 labels / 8 silos** |
| p4 implementation tier | Active P3/S3-selected estimator cohort: **0 paper-faithful-strict / 13 paper-family-template / 58 proxy**. |
| p4 canonical Phase-8 records | **2 556** = 71 cohort × 6 profiles × 3 ε × 2 modes (2 519 OK + 37 documented engine failures); the active cohort has no paper-faithful-strict estimator labels, so per-label strict-tier stats are N/A in this freeze — see [p4_experiments/FREEZE.md](p4_experiments/FREEZE.md) |
| p4 Phase-8d HHL/QAE scout records | **108** (72 OK + 36 engine failures) |

## Verification gates and accepted drift

Install the base reviewer/test dependencies before running pytest in a fresh venv:

```powershell
python -m pip install openai python-dotenv requests python-frontmatter pypdf pytest
```

The repository verifier uses existing artifacts only; it does not rerun P2
classification, P3 S2 extraction, or P4 Phase-8 jobs. V3 now exits 0 only when
all bridge gaps are either repaired or listed in
[tools/verify/v3_trace_label_allowlist.json](tools/verify/v3_trace_label_allowlist.json).

```powershell
python -m pytest                                                         # repo pytest surface; requires pytest installed
python tools/verify/v1_schema_validate.py                                # 20/20 pass
python tools/verify/v2_consistency.py                                    # 0 fail / 0 warn
python tools/verify/v3_trace_label.py                                    # direct bridge rows + accepted V3 exceptions
python tools/verify/v9_bridge.py                                         # exit 0; reports tracked in JSON
python p4_experiments/scripts/audit_implementation_type.py --dry-run      # 71-label cohort audit; strict tier = 0
python p4_experiments/scripts/audit_common_vs_core.py                    # 0 divergent
python p3_thematic_synthesis/s3_quantum_advantage/scripts/filter_consensus.py
python p1_framework_synthesis/scripts/build_review_data_done.py          # deterministic rebuild, no LLM calls
```

Remaining accepted drift is documented in
[tools/verify/reports/known_drift_2026-05.md](tools/verify/reports/known_drift_2026-05.md).

## Claim limitations

These are documented per-folder in each `FREEZE.md`; the historical
`docs/ARTIFACT_CLAIM_LEDGER.md` is in the source archive:

1. **p1 single-LLM extraction.** No second coder; no inter-coder κ. Suitable as a *scoping* synthesis (Cruzes & Dybå, Arksey & O'Malley); not a strict inductive content analysis (Elo & Kyngäs is named in the references explicitly as the historical / unexecuted approach).
2. **p2 single-LLM classification.** No κ on extraction tags; no `response_format=json_schema` enforcement; 22/777 ≈ 2.83 % off-scope FP rate handled via post-hoc exclusion; per-step timestamps for 761/777 papers were synthetic (now sentinel `unknown_pre_2026-05-02`).
3. **p3 QA triangulation.** Out-of-scope-for-this-freeze items: Q-6 stratified n>=30 reliability kappa, Q-8 historical script archival, and QA-2 Stilck-Franca scope expansion. QA-6 fixed Babbush S=1000 is retained with an accepted-risk claim boundary. QA-1 / QA-5 / QA-11 are closed in code (Ronnow gate, Dalzell QIPM gate, Beverland honest relabel).
4. **p4 strict tier is empty in the active cohort.** The 71-label Phase-8 grid is the P3/S3 most-viable cohort and has no `paper-faithful-strict` labels. Any "strict-tier H1/H2/H4 stat" is N/A in this freeze. **The H4=∅ result is conditional on the family-template + proxy implementation cohort, not a field-wide impossibility theorem.**
5. **p4 Azure Quantum.** No hardware jobs were run. "Azure" refers to Azure Linux VMs running the Microsoft Azure Quantum **Resource Estimator** (FT cost model). Artifact-facing claims must say "Resource Estimator on Azure Linux VMs", never "ran on Azure Quantum hardware".

## Outside current submission scope (future work, all listed in per-folder FREEZE.md)

- p1 inter-coder κ + filename↔embedded-title guard for any future re-extraction
- p2 inter-coder κ on extraction tags + `response_format=json_schema` re-classification
- p3 Q-6 stratified κ + s5/c2 regeneration with provenance siblings + Rønnow/Dalzell verdict re-aggregation
- p4 future paper-exact cohort design, if needed, using new labels selected through the P3/S3 cohort process + Phase-8d module package fold + cohort.json refresh with `implementation_type` baked in
- shared `RateLimiter` cross-process coordination + `paper_selector` indexing + manuscript-side `tiktoken` enforcement

## Tag

After committing the FREEZE.md files:

```powershell
git tag -a freeze-2026-05-02 -m "Code/data freeze; manuscript work begins on this tag"
git push origin freeze-2026-05-02
git switch -c manuscript-work
```

All subsequent edits happen on the `manuscript-work` branch; the freeze tag
is immutable.
