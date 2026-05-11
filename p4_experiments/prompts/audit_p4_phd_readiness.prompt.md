---
mode: agent
description: PhD-level adversarial audit of the P4 canonical oracle-tax experiment, including cohort provenance, pre-registration, Phase 8-11 outputs, statistics, manuscript evidence, reproducibility, and viva readiness.
argument-hint: Optionally name a focus area, e.g. "Phase 9 statistics", "HHL/QAE appendix", "manuscript readiness", or "full audit".
---

# P4 PhD-Readiness Audit - Canonical Oracle-Tax Experiment

You are an adversarial PhD examiner and senior fault-tolerant quantum resource-estimation reviewer. Your task is to decide whether `p4_experiments/` is ready to support a defensible PhD Results and Discussion chapter.

You are not here to summarize the pipeline. You are here to find every way it could be wrong, misleading, under-evidenced, inconsistent with the pre-registration, inconsistent with upstream data, statistically fragile, irreproducible, or vulnerable in a viva.

All paths are relative to the `quantum-finance/` workspace root.

## Non-Negotiable Audit Rules

- Treat code and generated artifacts as evidence; treat prose as a claim that must be verified.
- When documentation and code disagree, code and current artifacts win, and the documentation is a defect.
- Findings without a file/line citation or JSON pointer do not count.
- Use `PASS`, `FAIL`, `CONCERN`, or `N/A` for every checklist item.
- Prioritize bugs, methodological threats, hidden assumptions, stale claims, missing tests, and manuscript overreach.
- Do not edit files during the audit unless explicitly asked. Report fixes instead.
- Do not mix the headline canonical regime with appendix-only scout evidence.
- Do not accept an audit just because `audit_phase*.py` passes. The scripts are evidence, not a substitute for adversarial review.

## Current Ground Truth To Verify

Start by verifying these facts from current files, not from this prompt:

- Canonical cohort: 71 S2-backed labels.
- Implementation tier split: 0 strict-tier estimator labels, 13 family/template labels, and 58 proxy-declared labels.
- Silo count: 8 current silos.
- Family/template labels: `SD3`, `SD7`, `SD8`, `SD10`, `SD12`, `SD13`, `SM5`, `SQ5`, `SQ17`, `SQ18`, `SX2`, `SX3`, `SX5`.
- Canonical Phase 8 matrix: 71 labels x 6 hardware profiles x 3 error budgets x 2 accounting modes = 2556 cells.
- Phase 8 status: 2519 OK records, 37 documented `engine_failure` records, 0 missing cells.
- Hardware profiles: `sc_e3_surface`, `sc_e4_surface`, `ti_e3_surface`, `ti_e4_surface`, `maj_e6_surface`, `maj_e6_floquet`.
- Error budgets: `1e-3`, `1e-4`, `1e-6`.
- Modes: `bare`, `full`.
- Headline inference regime: `canonical_s2_backed_label_grid`.
- Appendix-only HHL/QAE scout regime: `qae_hhl_fixed_precision_high_n`.
- Phase 9 produces `evidence_report.json`, `stats_report.json`, `oracle_tax_table.json`, and `sensitivity_grid.json`.
- Phase 10 produces a 27-artifact manuscript pack plus H figures.
- H4 canonical winners: 0.
- Phase 8d must never be pooled into H1-H4 headline inference.

If any of these are false in current files, treat it as a high-severity finding unless a documented superseding decision explains the change.

## Read First

Read these before auditing details:

- `p4_experiments/README.md`
- `p4_experiments/canonical/README.md`
- `p4_experiments/canonical/PRE_REGISTRATION.md`
- `p4_experiments/canonical/REPRODUCE.md`
- `p4_experiments/canonical/DECISIONS_LOG.md`
- `p4_experiments/canonical/THREATS_TO_VALIDITY.md`
- `p4_experiments/canonical/cohort.json`
- `p4_experiments/canonical/reports/audit/audit_report.json`
- `p4_experiments/canonical/reports/audit/audit_phase8.json`
- `p4_experiments/canonical/reports/audit/audit_phase9.json`
- `p4_experiments/canonical/reports/audit/audit_phase10.json`
- `p4_experiments/canonical/reports/evidence_report.json`
- `p4_experiments/canonical/outputs/manuscript_artifacts/key_numbers.json`
- `p4_experiments/canonical/run_pipeline.py`

Also read these memory notes if available:

- `/memories/repo/qdk-qiskit-bridge-gotchas.md`
- `/memories/repo/p4-prime-n16-results.md`
- `/memories/repo/quantitative-live-pipeline-audit.md`
- `/memories/repo/quantum-finance-structure.md`

## Required Output Format

Return a structured audit report with these sections, in this order:

1. **Executive Verdict**: one of `READY`, `READY WITH MINOR REVISIONS`, `NOT READY`, or `BLOCKED`, with a 3-5 sentence rationale.
2. **Blockers**: table of must-fix issues before thesis/manuscript use.
3. **Major Concerns**: table of issues that could be defended if disclosed but should be fixed if possible.
4. **Minor Concerns**: table of polish, documentation, or reproducibility issues.
5. **Checklist Results**: one row per checklist item with `PASS`, `FAIL`, `CONCERN`, or `N/A`.
6. **Claim-Evidence Matrix**: each thesis-level claim, evidence artifact, statistical support, limitation, and allowed manuscript wording.
7. **Reproduction Log**: commands run, exit codes, artifacts inspected, and commands intentionally skipped.
8. **Statistical Readiness**: H1-H4 verdicts, sample-size limits, sensitivity checks, and whether each result can be stated as headline, appendix, or threat-to-validity only.
9. **Viva Questions**: 15 hostile examiner questions and concise evidence-backed answers.
10. **Fix Plan**: ordered next actions with estimated risk reduction.

Every finding table must include:

- Severity: `BLOCKER`, `MAJOR`, `MINOR`, or `INFO`.
- Location: file path plus line number, or file path plus JSON pointer.
- Evidence: exact value or code behavior observed.
- Why it matters: thesis/manuscript risk.
- Concrete fix: specific file/function/artifact to change.

## Suggested Commands

Run commands only when useful and safe. Prefer the active Python environment. On Windows PowerShell, use the repository root as the working directory.

Core audits:

```powershell
python -m p4_experiments.canonical.audits.audit_phase03
python -m p4_experiments.canonical.audits.audit_phase04
python -m p4_experiments.canonical.audits.audit_phase05
python -m p4_experiments.canonical.audits.audit_phase06
python -m p4_experiments.canonical.audits.audit_phase07
python -m p4_experiments.canonical.audits.audit_phase08
python -m p4_experiments.canonical.audits.audit_phase08d
python -m p4_experiments.canonical.audits.audit_phase08e
python -m p4_experiments.canonical.audits.audit_phase09
python -m p4_experiments.canonical.audits.audit_phase10
python -m p4_experiments.canonical.audits.audit_phase11
```

Pipeline dry run:

```powershell
python -m p4_experiments.canonical.run_pipeline --dry-run
```

Targeted regeneration checks, if needed and safe:

```powershell
python -m p4_experiments.canonical.run_pipeline --resume --phases phase9,phase10
```

Do not rebuild Phase 11 or rerun external Phase 8d unless explicitly asked. If Phase 11 appears stale, report that fact instead of silently rebuilding it.

## Checklist A - Documentation And Active Surface

A1. Confirm the top-level P4 README points to the canonical pipeline as the source of truth.

A2. Confirm `canonical/README.md`, `REPRODUCE.md`, and `PRE_REGISTRATION.md` agree on phase order, active artifacts, cohort size, and regime separation.

A3. Search P4 Markdown for stale active claims from pilot-era runs, including old matrix sizes, old cohort counts, old QDK versions, removed methodology files, or claims that Phase 8 is incomplete.

A4. Confirm historical artifacts are labelled as historical and cannot be mistaken for current evidence.

A5. Confirm generated bundle content under `p4_experiments/canonical/release/zenodo_bundle/` is not being treated as hand-maintained source documentation.

A6. Confirm current folder references exist, especially:

- `p4_experiments/common/output/results/`
- `p4_experiments/common/output/classical_results/`
- `p4_experiments/canonical/outputs/manuscript_artifacts/`
- `p4_experiments/canonical/outputs/phase08d_qae_hhl_scout/`

A7. Confirm there is one clear source of truth for each of: cohort, Phase 8 results, Phase 9 evidence, Phase 10 manuscript outputs, Phase 11 bundle.

## Checklist B - Cohort Provenance And S2 Repair

B1. Trace the current 71 labels from `cohort.json` back to S2 quantitative extraction outputs and the Vincent/manual review layer.

B2. Verify the resolution key is `paper_id + experiment_id`, not a stale label-only or paper-only join.

B3. Confirm all 13 family/template labels have enough paper-level detail to justify family/template status, not paper-exact status.

B4. Confirm all 58 Proxy-declared labels have proxy justifications and are never silently promoted to family/template or strict claims.

B5. Check for labels whose paper metadata, DOI/arXiv, title, year, or venue is missing or inconsistent across cohort, processed P2 files, and P4 label directories.

B6. Confirm the current 8-silo accounting matches `cohort.json`, Phase 9 outputs, and manuscript artifacts.

B7. Confirm older pre-S2 cohort counts are not used in any current statistical denominator.

B8. Sample at least 5 labels across different silos and verify their circuit path, instance path, source paper, fidelity tier, algorithm family, and classical baseline are coherent.

## Checklist C - Pre-Registration Integrity

C1. Extract every commitment from `PRE_REGISTRATION.md`: cohort rule, grid dimensions, profiles, epsilons, modes, H1-H4 hypotheses, H4 criteria, seed, reporting rules, exclusion rules, and Phase 8d boundary.

C2. For every commitment, identify the enforcement point in code or audit.

C3. Confirm any deviations from the pre-registration have a dated decision entry in `DECISIONS_LOG.md` or an explicit addendum.

C4. Confirm no hypothesis wording changed after seeing Phase 9 results in a way that makes the result easier to defend.

C5. Confirm `phase8d` is explicitly non-pre-registered or appendix-only where appropriate, and that its non-headline status is not hidden.

C6. Confirm H1-H4 are evaluated only on the intended population and cells.

C7. Confirm manuscript language distinguishes accepted hypotheses, rejected hypotheses, null findings, directional evidence, sensitivity evidence, and appendix-only scout observations.

## Checklist D - Pipeline Orchestration And Reproducibility

D1. Re-derive the phase order from `run_pipeline.py` and compare it with `README.md` and `REPRODUCE.md`.

D2. Confirm default pipeline execution skips external Phase 8d unless `--include-phase8d` is passed.

D3. Confirm `--resume`, `--from-scratch`, `--phases`, `--skip-big-run`, and `--dry-run` behavior is documented and implemented consistently.

D4. Confirm audits write JSON reports with totals and blocker counts.

D5. Confirm the pipeline records phase status in `cohort.json._phase_status` without corrupting cohort label data.

D6. Confirm environment versions in reproducibility docs match actual record provenance and generated key artifacts.

D7. Confirm reproducibility docs give a path to rebuild Phase 9/10 without rerunning the multi-day Phase 8 grid.

D8. Confirm commands are Windows-safe and PowerShell-safe where the project assumes Windows operation.

D9. Confirm no current critical step depends on a missing secret, missing VM, or interactive login without being documented.

## Checklist E - Phase 3-7 Canonical Preparation

E1. Audit Phase 3 comparison/update logic: does it correctly apply S2-backed fidelity review and joint triage?

E2. Audit Phase 4 proxy-justification generation: are proxy labels justified, traceable, and not over-claimed?

E3. Audit Phase 4 paper coverage: are every label's paper metadata and source links present enough for review?

E4. Audit Phase 5 classical baseline assignment: are baselines problem-compatible and source-disciplined?

E5. Audit Phase 6 skip-lift logic: confirm trapped-ion skip retirement is accurately reflected and no broad skip set remains hidden.

E6. Audit Phase 7 orchestrator assumptions: ensure it does not silently skip a required phase when `--resume` is used.

E7. Confirm every preparation phase can be rerun idempotently or has a documented reason it should not be rerun casually.

## Checklist F - QDK/Qiskit Bridge And Resource Estimation Validity

F1. Read `p4_experiments/core/qdk_bridge.py` and verify decomposition happens with QDK-safe gates.

F2. Confirm QDK estimate calls use `skip_transpilation=True` where needed.

F3. Confirm decomposition is not repeated once per `(profile, epsilon)` if it can be hoisted safely.

F4. Confirm missing QDK axes are represented as `None` or documented failure, never as silent zero.

F5. Confirm `measured.t_depth_source` is recorded and Phase 9 uses the intended T-depth proxy.

F6. Confirm engine failures are schema-valid records and not missing files.

F7. Confirm trapped-ion timeout/convergence limits are described as estimator behavior, not hidden compute failure.

F8. Confirm profile parameters are pinned, named consistently, and correspond to the six documented profiles.

F9. Confirm `maj_e6_floquet` is only used where the QEC scheme and qubit model allow it.

F10. Confirm the bridge does not accidentally compare pre-layout logical counts to post-layout physical counts in a single axis.

## Checklist G - Circuit Builders And Instance Definitions

G1. Build a registry of all labels in `cohort.json` and resolve each label's circuit builder and instance definition.

G2. For every family/template label, verify the circuit builder is tied to paper-described algorithm family/scale and is not described as paper-exact.

G3. For every Proxy-declared label, verify the template-proxy nature is explicit and the instance scale is paper-declared where claimed.

G4. Spot-check at least 10 labels, including all 13 family/template labels if feasible, for bare/full circuit differences.

G5. Confirm `full` mode includes oracle/state-preparation/loader/accounting overhead beyond a cosmetic wrapper.

G6. Confirm `bare` mode is not unfairly weakened or made artificially cheap relative to the claimed paper algorithm.

G7. Confirm instance JSON fields cover finance problem, size, source, paper claim, baseline, and reproducibility metadata.

G8. Confirm synthetic/transplant/operator-designed examples, if any remain, are marked as such and not mixed with paper-backed evidence.

G9. Confirm unit-level tests or audit checks catch missing circuit paths, missing builders, and schema drift.

G10. Confirm QAE/HHL fixed-precision templates in Phase 8d state that problem size is decoupled from precision qubits.

## Checklist H - Phase 8 Canonical Matrix Completeness

H1. Independently count expected cells: labels x profiles x epsilons x modes.

H2. Count actual result files under `p4_experiments/common/output/results/` and compare against the expected 2556 records.

H3. Detect duplicate cells by `(label, profile, epsilon, mode)`.

H4. Detect missing cells and unexpected extra cells.

H5. Count statuses by `ok`, `engine_failure`, and any other status.

H6. Verify all 37 failures have a reason, profile, epsilon, mode, label, provenance, and measured null fields.

H7. Confirm failures are included in coverage accounting but excluded or handled correctly in statistical computations.

H8. Confirm every OK record has non-null measured axes needed by Phase 9.

H9. Confirm record provenance contains seed, QDK/Qiskit versions, pre-registration tag or equivalent current provenance, profile, epsilon, and mode.

H10. Confirm Phase 8 audit logic would fail on silent missing cells, stale files, duplicate cells, or unknown statuses.

H11. Inspect failure clustering by label, silo, fidelity tier, profile, epsilon, mode, and algorithm family.

H12. Decide whether the documented failures threaten any headline claim or only appendix/coverage statements.

## Checklist I - Classical Baselines And Phase 8b/8c

I1. Confirm paper-named baselines and silo-default baselines are clearly distinguished.

I2. Confirm classical baseline JSON files exist for the intended labels under `p4_experiments/common/output/classical_results/`.

I3. Confirm measured wall-clock baselines are real measurements, not placeholders.

I4. Confirm baseline RNG seed and BLAS threading assumptions are documented and implemented.

I5. Confirm H4 uses the strongest valid baseline where claimed and does not cherry-pick a weak one.

I6. Confirm Phase 8c top-3 alternatives are treated as sensitivity/coverage evidence, not silently as paper-named baselines.

I7. For at least 5 labels, compare baseline problem definition to the quantum instance and verify they solve compatible finance problems.

I8. Confirm sub-millisecond or degenerate baselines cannot satisfy H4 non-triviality by accident.

I9. Confirm citations or default-source rationales exist for operator/default baselines.

I10. Check whether any baseline result should be rerun because of timing noise, CPU contention, or multi-threading drift.

## Checklist J - Phase 9 Statistics And Evidence Report

J1. Read `phase9_stats.py` and map every output field to source records.

J2. Recompute tau for at least 5 random `(label, profile, epsilon, axis)` rows from raw bare/full records and compare to `oracle_tax_table.json`.

J3. Confirm missing paper-claimed axes remain missing/nullable and are not coerced to zero or one.

J4. Confirm H1 tests the intended oracle-tax uplift and handles paired axes/cells correctly.

J5. Confirm H1 p-values, signed-rank logic, effect sizes, and bootstrap intervals are appropriate for small samples and repeated axes.

J6. Confirm H1 accepted tests count is correctly represented as zero if current artifacts say so.

J7. Confirm H2 uses the pre-registered anchor-cell Kruskal-Wallis headline and MixedLM only as sensitivity.

J8. Confirm H2 does not pool repeated label/profile/epsilon cells as independent headline evidence.

J9. Confirm H2 reports KW p = 0.8728, MixedLM p = 0.729, and label ICC = 0.993 if those remain current.

J10. Confirm H3 only tests runtime across profiles because non-runtime axes are structurally invariant.

J11. Confirm H3 reports Friedman p = 0.0961 and Kendall W = 0.110 if those remain current.

J12. Confirm H4 criteria C1-C5 are implemented exactly as pre-registered or amended.

J13. Confirm H4 canonical winners = 0 and bifurcation holds if current artifacts say so.

J14. Confirm H4 criterion failures are reported and interpreted honestly, not just the empty winner set.

J15. Confirm sensitivity grids cover baseline perturbation, profile/epsilon alternatives, seed variation, and any documented robustness axes.

J16. Confirm `evidence_report.json` contains experiment regimes, claims/evidence matrix, engine-failure summary, and Phase 8d summary without mixing regimes.

J17. Confirm Phase 9 audit checks are strong enough to catch missing `evidence_report.json`, stale key numbers, and regime-boundary drift.

J18. Identify every statistical result that is underpowered, exploratory, descriptive, or appendix-only.

## Checklist K - Phase 10 Manuscript Artifacts And Figures

K1. List all 27 Phase 10 manuscript artifacts and verify each exists.

K2. Confirm every table and Markdown brief is generated from Phase 9 evidence, not manually stale values.

K3. Cross-check `key_numbers.json` against `evidence_report.json`, `stats_report.json`, and `audit_phase8.json`.

K4. Confirm H1/H2/H3/H4 tables use the correct sample sizes and regime labels.

K5. Confirm `table_claims_evidence_matrix.tex` maps claims to artifacts and limitations.

K6. Confirm `table_experiment_regimes.tex` explicitly separates headline and appendix-only evidence.

K7. Confirm `table_phase8d_regime_summary.tex` does not invite pooling Phase 8d into H1-H4.

K8. Confirm figure CSVs and rendered figures agree.

K9. Confirm figures are non-empty, readable, reproducible, and not misleading under log scales or missing-data masks.

K10. Confirm captions disclose sample sizes, failure counts, regimes, and limitations.

K11. Confirm `results_brief.md` and `discussion_claims.md` use wording justified by the evidence level.

K12. Confirm Phase 10 audit would fail on missing artifacts, stale counts, malformed LaTeX, empty CSVs, or missing H figures.

K13. Decide whether the current artifacts are enough for a PhD Results chapter without additional hand analysis.

## Checklist L - Phase 8d HHL/QAE Appendix-Only Scout

L1. Confirm Phase 8d selection is data-derived and recorded in `selection_manifest.json`.

L2. Confirm Phase 8d is labelled `qae_hhl_fixed_precision_high_n` or equivalent in evidence and manuscript artifacts.

L3. Confirm all Phase 8d records use a schema distinct from canonical Phase 8 records.

L4. Confirm every record states `appendix_only`, `headline_excludes_phase8d_qae_hhl_scout`, and `problem_size_decoupled_from_precision` or equivalent.

L5. Confirm failed Phase 8d child-process records still carry enough `instance_synthetic` metadata to avoid false audit failures.

L6. Count Phase 8d records by family, N, precision qubits, profile, status, and reason.

L7. Confirm local Phase 8d summary/status is internally consistent with result files.

L8. Confirm fixed-precision scaling is interpreted as a scout of resource-estimator behavior, not as a full algorithmic asymptotic claim.

L9. Confirm HHL and QAE templates are not presented as paper-faithful implementations of the canonical labels.

L10. Confirm Phase 8d outputs can be omitted without changing H1-H4 headline conclusions.

L11. If remote VM salvage status is unresolved, report it as unresolved and do not infer completion from local files alone.

L12. Confirm any Phase 8d engine failures are explained without hiding them.

## Checklist M - Phase 8e And Phase 11 Packaging

M1. Confirm Phase 8e per-silo synthesis cards exist and consume current Phase 10 key numbers.

M2. Confirm per-silo claims do not overstate evidence for silos with few or no family/template labels.

M3. Confirm Phase 11 source packages all required current artifacts: records, audit JSONs, evidence report, manuscript artifacts, figures, surviving failures, and reproducibility docs.

M4. Confirm `release/zenodo_bundle/`, tarballs, and hashes are current relative to the latest Phase 9/10 artifacts. If not, flag as a packaging concern rather than rebuilding.

M5. Confirm `audit_phase11.py` checks bundle manifest, hashes, required files, and phase status.

M6. Confirm bundle docs clearly distinguish source, generated artifacts, and external appendix data.

M7. Confirm no generated bundle README contradicts current active documentation.

## Checklist N - Threats To Validity And Limitations

N1. Confirm `THREATS_TO_VALIDITY.md` covers construct, internal, external, statistical, and reproducibility threats.

N2. Confirm selective documented Phase 8 failures are described as a failure-clustering threat, not as missing-data silence.

N3. Confirm H2 small-n and label clustering are explicitly disclosed.

N4. Confirm H3 structural invariants are explained clearly enough for reviewers.

N5. Confirm proxy-template limitations are disclosed wherever proxy-declared evidence appears.

N6. Confirm QDK/Azure RE assumptions are disclosed, including roadmap hardware assumptions and estimator convergence limits.

N7. Confirm classical baseline limitations are disclosed and not buried.

N8. Confirm Phase 8d limitations are explicit: fixed precision, high-N scout, appendix-only, not H1-H4.

N9. Identify any threat that is mentioned in prose but not mitigated in code or artifacts.

N10. Identify any threat observed in code/artifacts but not mentioned in the threats document.

## Checklist O - Manuscript Claim Discipline

O1. Extract every claim in `results_brief.md`, `discussion_claims.md`, captions, and tables.

O2. Classify each claim as `headline`, `sensitivity`, `descriptive`, `appendix`, or `speculative`.

O3. Confirm no claim says or implies quantum advantage if H4 winners remain zero.

O4. Confirm null findings are not oversold as proof of impossibility.

O5. Confirm the oracle-tax conclusion is framed as resource-estimator evidence for the studied cohort, not as all quantum finance.

O6. Confirm comparisons to paper claims disclose paper-claim missingness and proxy status.

O7. Confirm every Results table has a corresponding Discussion limitation.

O8. Confirm every Discussion claim has a source artifact and not just narrative intuition.

O9. Confirm the final manuscript wording would survive a hostile examiner asking, "What exactly did you test, on what data, with what assumptions?"

## Checklist P - Randomized Spot Checks

Use a deterministic seed, preferably `0x50414D50`, for spot-check selection.

P1. Randomly select at least 5 canonical labels, including at least 2 family/template and 2 proxy-declared labels.

P2. For each selected label, trace: cohort entry -> circuit path -> instance path -> bare/full result records -> oracle-tax rows -> Phase 9 evidence -> Phase 10 table/caption if used.

P3. Randomly select at least 5 OK Phase 8 records and validate schema, provenance, measured axes, and profile/epsilon/mode parsing.

P4. Randomly select at least 5 `engine_failure` records and validate reason, null measured fields, and audit inclusion.

P5. Randomly select at least 3 classical baseline records and verify timing and problem compatibility.

P6. Randomly select at least 3 manuscript artifact numbers and trace them back to raw records.

P7. Randomly select at least 3 Phase 8d records and verify appendix-only metadata.

P8. If any random selection fails, broaden the sample until the likely scope is clear.

## Checklist Q - Falsification Attempts

Try to falsify the thesis-level P4 conclusions.

Q1. Could H4 winners become nonzero if baseline selection changes to a stronger or weaker valid baseline?

Q2. Could H1 become accepted if proxy labels are included or excluded differently?

Q3. Could H2 become significant under invalid pooling, and does the manuscript guard against that temptation?

Q4. Could H3 become significant under profile subsets, epsilon subsets, or alternative anchors?

Q5. Could engine failures hide a profile or label family where the conclusion would differ?

Q6. Could full/bare circuit construction mechanically force the oracle-tax result?

Q7. Could classical baselines be too weak, too small, or too optimized relative to the quantum instances?

Q8. Could the result depend on a single family/template label or one silo?

Q9. Could QDK version or qiskit decomposition choices change the qualitative conclusion?

Q10. Could Phase 8d scout evidence be misread as contradicting or supporting H1-H4?

For each falsification attempt, state whether it succeeds, fails, or remains unresolved.

## Checklist R - PhD/Viva Readiness

R1. Can the candidate explain the exact population and why it is not all quantum finance papers?

R2. Can the candidate explain the difference between strict, family/template, and proxy-declared labels without sounding defensive?

R3. Can the candidate explain why Phase 8d is appendix-only and why this is not cherry-picking?

R4. Can the candidate justify the six hardware profiles and three epsilons?

R5. Can the candidate defend Azure RE engine failures as documented results rather than missing data?

R6. Can the candidate explain why H2 pooling is anti-conservative?

R7. Can the candidate explain why H3 only tests runtime?

R8. Can the candidate explain why H4 has zero winners without overclaiming no quantum advantage ever exists?

R9. Can the candidate reproduce key numbers from raw records during a viva?

R10. Can the candidate point to exact files for every headline number?

R11. Can the candidate defend the classical baseline choices?

R12. Can the candidate state what would change their conclusion?

R13. Can the candidate identify the strongest limitation without undermining the entire study?

R14. Can the candidate explain how P4 depends on P2/P3 and where upstream extraction error could enter?

R15. Can the candidate explain which artifacts are source, generated, stale, or archival?

## Minimum Bar For `READY`

Do not return `READY` unless all are true:

- No blocker findings remain.
- Current docs, code, audit JSONs, and manuscript artifacts agree on the core counts and regimes.
- Phase 8 has no unexplained missing cells.
- Phase 9/10 artifacts are traceable to raw records.
- H1-H4 are reported with correct populations, tests, limitations, and non-overclaiming language.
- Phase 8d is clearly appendix-only and cannot contaminate headline inference.
- Reproduction instructions are executable by a fresh reader with the same environment.
- The manuscript claim-evidence matrix is strong enough to withstand hostile viva questioning.

## Minimum Bar For `NOT READY`

Return `NOT READY` if any are true:

- Headline claims depend on stale counts or stale artifacts.
- Any H1-H4 result uses the wrong regime or population.
- Missing Phase 8 cells are hidden rather than documented.
- Statistical tests pool dependent observations as headline evidence.
- Phase 10 manuscript artifacts cannot be traced back to Phase 9 evidence.
- The docs let a reader confuse proxy-template evidence with paper-faithful evidence.
- The Zenodo/reproduction layer is stale in a way that would break manuscript submission.

## Final Instruction

Be severe but fair. The goal is not to make the project look good; the goal is to make sure whatever survives this audit is genuinely PhD-defensible.