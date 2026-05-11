# P4 Pre-Registration - Active S2-Backed Canonical Spec

## 0. Status

This file is the active Phase 4 canonical contract after the S2 quantitative
source-provenance repair. It replaces any generated downstream reports that
were tied to the earlier cohort state.

### 0a. Tier semantics callout (added 2026-05-02)

**STRICT TIER = 0.** No P4 cohort label is `paper-faithful-strict`. The
H4 headline (no winners under the strict-advantage scoreboard) operates
at the **paper-family-template tier (13 labels)** and the
**proxy tier (58 labels)** only. Many template labels share
`_u_proxy` (`core/templates/hhl.py`) or `grover_proxy`
(`core/templates/qae.py`) scaffolding; the negative H4 result is robust
*as a statement about the template family at the paper's stated scale*
and cannot support the stronger reading "no current finance paper passes
any QA bar". See [`THREATS_TO_VALIDITY.md`](THREATS_TO_VALIDITY.md) CV-5
(HHL classical baseline inflated to clear C5 floor) and CV-6 (Hoefler
optimistic constants) for the matched honest qualifications. The
`paper_exact_claim_eligible` field in [`outputs/manuscript_artifacts/key_numbers.json`](outputs/manuscript_artifacts/key_numbers.json)
is correctly 0; manuscript prose must not slip into stronger language.

The active provenance rule has three layers:

- Quantitative source extraction directory: `p3_thematic_synthesis/s2_quantitative/output/extractions/`
- S2 resolution key: `paper_id + experiment_id`
- Manual audit inputs: Vincent review worksheets in `p4_experiments/experiments/review/phase8_faithfulness_review/vincent/`, joint triage decisions in `p4_experiments/experiments/review/phase8_faithfulness_review/triage/TRIAGE_INDEX.md`, and the quantitative triage artifacts `p2_systematic_review/output/audit/triage_classification.json` plus `p2_systematic_review/output/audit/manual_extraction_targets.txt`
- Complete checked data file for P4: `p4_experiments/canonical/cohort.json`
- Canonical comparison file: `p4_experiments/canonical/reports/phase3_compare.json`
- Result-record provenance tag: `s2-quantitative-canonical`

S2 provides extracted paper facts. Manual audit and joint triage adjudicate how
those facts are used for P4 fidelity and circuit decisions. The downstream
pipeline consumes the checked cohort file, not raw S2 files by themselves.

If the checked cohort, Phase 4 proxy layer, or Phase 5 baseline layer changes,
downstream Phase 6-11 outputs must be regenerated before they are used in
manuscript claims.

Execution-status addendum, 2026-04-26: the current downstream run has completed
the 2556-cell canonical Phase 8 grid with 2519 OK records, 37 documented
`engine_failure` records, and 0 missing records. Phase 9 now writes
`evidence_report.json` in addition to `stats_report.json`,
`oracle_tax_table.json`, and `sensitivity_grid.json`. Phase 10 now writes a
27-artifact manuscript pack plus H figures. Phase 8d is explicitly
appendix-only HHL/QAE fixed-precision high-N evidence and remains outside the
headline H1-H4 inference.

Faithfulness-tier addendum, 2026-04-28: the current audited implementation tier
split is `paper-faithful-strict=0`, `paper-family-template=13`, and `proxy=58`.
The legacy `F` label is therefore a template/family-faithful reporting stratum,
not evidence that a label is paper-exact. Paper-exact claims require an explicit
`paper-faithful-strict` tier promotion.

## 1. Cohort

The active P4 cohort contains 71 Tier-1 experiment labels. Each label resolves
to exactly one experiment object in the S2 quantitative extraction JSON for its
paper and then carries the audited P4 decision after Vincent review and joint
triage adjudication.

Current fidelity split:

- Faithful (`F`): 13 labels
- Proxy-declared (`P`): 58 labels
- Total: 71 labels

Faithful labels:

`SD3`, `SD7`, `SD8`, `SD10`, `SD12`, `SD13`, `SM5`, `SQ5`, `SQ17`, `SQ18`,
`SX2`, `SX3`, `SX5`.

All 13 current `F` labels are audited as `paper-family-template`. None are
currently audited as `paper-faithful-strict`.

## 2. Phase Flow

The active rebuilt flow is:

1. S2 quantitative extraction files provide the paper-level experiment facts.
2. Vincent's manual review and the joint triage worksheets adjudicate fidelity,
   demotions, accepted corrections, and circuit-remediation decisions.
3. `phase3_compare.py` resolves each cohort label against S2 quantitative
   extraction data, applies the reviewed faithful/adjudicated decision set, and
   emits `phase3_compare.json`.
4. `phase3_update_cohort.py` writes the complete checked P4 data file at
   `cohort.json`.
5. `phase4_generate_proxy_justifications.py` writes proxy justifications only
   for labels that remain `P` and clears stale proxy metadata from non-P labels.
6. `phase5_assign_classical_baselines.py` assigns paper-stated or silo-default
   classical baselines using the same S2-backed resolution.
7. `phase6_lift_skip.py` records the no-silent-skip and documented-failure
   policy.
8. `phase8_big_run.py` writes the canonical 2556-cell resource-estimation grid.
9. Phase 8b/8c measure classical baselines and top-3 alternatives.
10. `phase9_stats.py` writes H1-H4 statistics, sensitivity, oracle-tax ratios,
    and `evidence_report.json`.
11. Phase 8d selection/finalization is optional external appendix compute for
    the `qae_hhl_fixed_precision_high_n` regime only.
12. `phase10_manuscript_artifacts.py` writes the manuscript evidence pack.
13. Phase 8e and Phase 11 build per-silo synthesis cards and the release bundle.

The obsolete paper-fidelity subphase scripts and generated downstream artifacts
are not part of the active contract.

## 3. Hypothesis Discipline

Phase 4 estimates remain a validation layer over the frozen P4 cohort. P4
results do not retroactively change Phase 3 thematic findings.

Headline quantum-advantage claims about the current canonical implementation are
restricted to the legacy `F` template/family stratum. Paper-exact claims are
restricted to `paper-faithful-strict` labels; the current strict tier is empty.
Proxy labels may be used for sensitivity, coverage, and appendix reporting only.

Amendment, 2026-04-28: H2 silo-level inference is restricted to active Phase 3
problem-domain silos as declared in `shared/config/silo_inclusion.json` and
recorded in `cohort.json::_p3_scope_disposition`. Labels in cohort silos outside
the active Phase 3 problem-domain scope remain part of full-corpus coverage and
appendix reporting, but they are excluded from the H2 Kruskal-Wallis headline
test and the H2 MixedLM sensitivity. Rationale: H2 is the statistical companion
to the Phase 3 propositions and must test the same silo universe argued in the
Phase 3 chapter.

## 4. Hardware And Runs

Each active label is evaluated over 6 hardware profiles, 3 error budgets, and 2
accounting modes in the canonical runner. Result records are written under
`p4_experiments/common/output/results/` and must carry the
`s2-quantitative-canonical` provenance tag.

Generated result records, figures, tables, release bundles, and aggregate JSON
reports are disposable build artifacts. If their input cohort changes, delete
them and regenerate.

## 5. Validation Gates

The active minimum gates before using P4 results are:

- Every one of the 71 labels resolves to an S2 extraction file and experiment.
- Manual audit and joint triage inputs are present and pinned as cohort
   provenance.
- `cohort.json` and `phase3_compare.json` agree on `F=13`, `P=58`, total `71`.
- Phase 3, Phase 4, Phase 4 paper-coverage, and Phase 5 audits pass.
- No non-P label carries proxy-justification metadata.
- Downstream Phase 8, Phase 9, and Phase 10 audits pass after the current
   cohort state.
- Before release deposition, Phase 11 is rerun so the bundle manifest and
   tarball hash match the final evidence pack.

## 6. Reporting Rules

### 6.1 Faithful Headline Rule

Only `paper-faithful-strict` labels are eligible for paper-exact headline claims
about the source literature. The current strict tier is empty. Legacy `F` labels
remain eligible only for explicitly scoped template/family-faithful headline
reporting.

### 6.2 Proxy Disclosure Rule

Each `P` label must carry a proxy justification that states what the paper does
and does not specify, and why the selected template is a proxy rather than a
paper-faithful implementation.

### 6.3 Source And Audit Rule

Paper facts used in Phase 3-5 must come from the active S2 quantitative
extraction files. Fidelity, demotion, and circuit-remediation decisions must be
traceable to the manual audit and joint triage layer. Generated cohort metadata
is not classification evidence by itself.

### 6.4 Proxy Reporting Rule

P-tier labels are excluded from headline H4 reporting. They may appear only in
declared proxy sensitivity, full-cohort appendix, coverage, or limitations
tables where the proxy status is explicit.

### 6.5 Experiment-Regime Boundary Rule

Headline H1-H4 inference is restricted to `canonical_s2_backed_label_grid`.
The `qae_hhl_fixed_precision_high_n` Phase 8d HHL/QAE scout is appendix-only
scaling evidence. It may support discussion of fixed-precision high-N behavior,
but it must not be pooled into H1-H4 or used to promote/demote canonical labels.
