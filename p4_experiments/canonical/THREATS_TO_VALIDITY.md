# Threats to Validity — Phase 4 Canonical Pipeline

> **Status note (2026-05-10): design-time limitations text retained for provenance.** Active Phase 4 claim semantics are controlled by [../FREEZE.md](../FREEZE.md) and [PRE_REGISTRATION.md](PRE_REGISTRATION.md): the active estimator cohort has 0 paper-faithful-strict labels, 13 paper-family-template labels, and 58 proxy-declared labels. Older F-tier/headline-subcohort wording below should be read as pre-freeze threat modelling unless explicitly restated in the current freeze/pre-registration.
>
> **Audience.** Manuscript reviewers, the Microsoft Quantum Applications
> team, future replicators. This is the source text for the
> Threats-to-Validity / Limitations section of the manuscript.
>
> **Stance.** Every threat below is named *before* the experiment runs
> under tag `p4-canonical-v1`. Each threat carries an explicit mitigation
> built into the canonical pipeline; where mitigation is partial or
> absent, this is stated and the threat is carried into the manuscript
> Discussion section.

---

## Construct validity

### CV-1. Template-proxy circuits do not measure paper-stated algorithms

**Threat.** A `proxy-declared` (P-tier) label uses a generic template
parameterised with paper-stated qubit count but not the paper's actual
oracle / state-preparation. The resource estimates are therefore
representative of the algorithm *family* at the paper's scale, not of
the paper's specific algorithm.

**Mitigation (built into the pipeline).**

- **Three-tier fidelity scheme** (PRE_REGISTRATION.md §2.2). Faithful
  (F) and proxy-declared (P) labels are separated; the headline
  bifurcation claim (H4) is reported on the F-tier sub-cohort only.
- **S2-backed manual adjudication** before any P assignment
  (PRE_REGISTRATION.md §6.2--6.3). P-tier labels are justified from the
  S2 quantitative extraction, Vincent review worksheets, and joint
  triage decisions. Each proxy justification states which paper fields
  remain unresolved and why the selected template is a proxy rather than
  a paper-faithful implementation.
- **`fidelity` field in every record.** Reviewers can recompute every
  table on the F-tier sub-cohort directly from the records.
- **Audit blocker `I.headline_excludes_proxy_labels`** mechanically
  verifies that the headline claim does not include P-tier labels.

**Residual risk.** If a P-tier label is used in a sensitivity table and
that table influences a discussion-section claim, the claim is bracketed
with "in the proxy-declared sensitivity sub-cohort". This convention is
documented in PRE_REGISTRATION.md §6 and in the Phase 10 discussion-claim
artifacts.

### CV-2. The four resource axes are not independent

**Threat.** `logical_qubits`, `t_count`, `t_depth`, `runtime_seconds`
are correlated within a (label, profile, ε, mode) cell. A pooled
hypothesis test that treats them as independent inflates apparent
power.

**Mitigation.** Per-axis testing is the **primary** report; pooled
results are reported only with the explicit caveat
"`pooled_caveat: Pooled n double-counts the four resource axes within
each (label, profile, eps) cell; axes are not statistically independent.
Pooled p-value is conservative-low.`" (already in
`stats_report.json`).

### CV-3. The H4 anchor cell is one of 18 (profile, ε) cells

**Threat.** Choosing `(maj_e6_floquet, ε = 1e-4)` as the anchor could
be cherry-picking the cell that gives the cleanest result.

**Mitigation.**

- **Pre-registered.** The anchor is named in PRE_REGISTRATION.md before
  any record is written under the canonical tag, with explicit
  rationale (Microsoft Majorana floquet roadmap; gives FT cost the
  most-favourable hardware substrate).
- **Sensitivity over profiles.** H4-strict-subset construction is
  re-run at every (profile, ε) cell as a sensitivity table in the
  appendix; the bifurcation claim is reported as
  "strict subset is empty at the H4 anchor *and* at *k* of the other
  17 cells".
- **H3 result.** If H3 rejects (profile differences are real), this is
  evidence that profile choice does materially shift τ — and the
  sensitivity table over profiles becomes the central robustness check.

### CV-4. The "trivial oracle" criterion `full_t_count = 0` is template-induced

**Threat.** A paper-faithful implementation might have `t_count > 0`
even for an "ansatz" circuit, depending on transpilation. The
`t_count = 0` ⇔ Regime A partition could be an artifact of how our
templates compile down through QDK.

**Mitigation.**

- **F-tier audit.** For every F-tier label, the unit test asserts
  `count_t_gates(circuit)` matches the paper's stated T-count where
  available. Discrepancies trigger an audit blocker.
- **Cross-validation.** 5 spot-labels' T-counts are hand-calculated
  from Beverland et al. (2022) Appendix tables and compared to the
  RE engine's output. Discrepancies > 10% are reported in the audit.
- **Lemma argument.** The bifurcation argument is analytical from the FT
  cost decomposition; the empirical observation that the lemma holds exactly
  is the strong claim, not the template-induced one.

---

## Internal validity

### IV-1. Selection bias in the systematic review (Phase 2)

**Threat.** The Phase 2 inclusion criteria, screening protocol, and
inter-coder agreement determine which papers reach Phase 4. A
selection bias upstream contaminates Phase 4 findings.

**Mitigation.**

- **PRISMA-grade Phase 2.** The Phase 2 README documents the search
  string, databases, screening protocol, and inter-coder agreement
  (Cohen's κ).
- **Audit citation.** The Phase 2 screening folder records calibration
  κ, AI/human validation, and the gpt-5-mini screening decisions used
  upstream of the Phase 4 cohort.
- **Out-of-scope statement.** The manuscript explicitly limits the
  population to Phase-2-included papers; replication of the Phase 2
  screening with a different κ threshold would produce a different
  Phase 4 cohort and is left to a follow-up study.

### IV-2. Triangulated synthesis (Phase 3) consensus rule could be biased

**Threat.** "Majority-viable" is defined by the Phase 3 consensus rule
across the five layers. A different consensus rule (e.g. unanimous
viable, or any-two-layers viable) would produce a different cohort.

**Mitigation.**

- **Pre-registered rule.** The consensus rule was set in Phase 3 before
  Phase 4 began; no change after.
- **Sensitivity table.** Phase 4 reports the headline H4 result on the
  alternative cohort definitions (unanimous viable, any-two-layers
  viable) as an appendix. If the bifurcation thesis holds across all
  three cohort definitions, the finding is robust to the consensus
  rule.

### IV-3. Classical baseline cherry-picking

**Threat.** A weak classical baseline makes any quantum result look
better. A strong baseline (e.g. a state-of-the-art GPU implementation
of the same problem) makes the quantum result look worse.

**Mitigation.**

- **Pre-registered fallback chain** (PRE_REGISTRATION.md §4-§6):
  closed-form > standard-library > paper-cited > operator-quoted
  default.
- **Citation discipline.** Audit blocker
  `J.classical_baseline_citation_discipline` requires every baseline
  to carry `source: {paper_doi, page} OR {default_source_doi,
  rationale}`. No `pending-citation` baselines admitted.
- **±10× sensitivity grid.** H4 strict-subset construction is re-run
  at every classical baseline value perturbed ±10×; if the bifurcation
  result is robust to ±10× baseline error, baseline cherry-picking
  cannot account for it.

### IV-4. SEED could be cherry-picked

**Threat.** SEED affects metric simulation, classical-baseline RNG,
and bootstrap resampling. A cherry-picked SEED could give a
spuriously clean H4 result.

**Mitigation.**

- **Single SEED locked** in PRE_REGISTRATION.md §2.6.
- **SEED-robustness grid.** Every H1/H2/H3 test is re-run under
  SEED ∈ {SEED, SEED+1, SEED+2, SEED+3}. Any p-value that crosses
  α = 0.05 under any alternative SEED is reported as
  "SEED-sensitive" and demoted to discussion.

### IV-5. The RE engine could have bugs

**Threat.** The Microsoft Azure Quantum Resource Estimator is a
specific software package at a specific version. A bug in the engine
would propagate uniformly across all records and could distort
findings.

**Mitigation.**

- **Engine version pinned** in `requirements.lock` and printed in
  every record's `provenance.qdk_version`.
- **5-label cross-validation** against hand-calculated FT costs from
  Beverland et al. (2022) Appendix tables. The 5 labels are chosen
  before the run (3 trivial-oracle + 2 oracle-bound) and the
  cross-validation results are reported in the audit. > 10% deviation
  triggers a Phase-7 audit blocker.
- **Microsoft team review.** The manuscript is shared with the
  Microsoft Quantum Applications team at submission for a technical
  review of the RE methodology.

### IV-6. Hardware profiles reflect roadmap projections, not measured devices

**Threat.** Profile parameters (especially Majorana floquet) are
projections from physics roadmaps. Changes to the roadmap would change
findings.

**Mitigation.**

- **Profile JSONs pinned** under `re_profiles/` with SHA recorded in
  the record's `provenance.profile_sha`.
- **Sensitivity over profiles** (CV-3 above).
- **Discussion section.** The manuscript Discussion explicitly notes
  that the bifurcation thesis is derived under current 2026 roadmap
  parameters; future roadmap revisions could shift the per-silo
  τ-rankings without affecting the (label-level) partition fact.

### IV-7. Unit-test acceptance does not guarantee paper-faithfulness

**Threat.** Unit tests assert `circuit.num_qubits` and `circuit.depth()`
match paper-stated values. They do not assert that the circuit
implements the paper's actual algorithm.

**Mitigation.**

- **F-tier protocol** (PRE_REGISTRATION.md §5.2). For every F-tier
  label, the operator records the paper section (or supplementary
  material location) where the circuit is described, and the
  reimplementation is reviewed by the second author before the label
  is admitted to Phase 8.
- **Co-author review trail.** Each F-tier paper directory contains
  `faithful_review.md` with the second author's sign-off note and date.
- **Spot-checks.** A random 10% of F-tier circuits are re-implemented
  independently by the second author and the two implementations
  diff'd at the gate level; discrepancies are reported in the audit.

---

### IV-8. Linear-SVM substitution for paper-specified RBF kernels (Phase 8b) — RETIRED

**Retired 2026-04-20 (Phase B1 of Master Plan v2)**: scikit-learn 1.7.2 was already pinned in `requirements.lock`; the Phase 8b RBF SVC substitution has been reversed. Linear-SVM-primal is retained as a sensitivity baseline (see `classical_results/<label>_silo_default.json` for B3, B4, SQ5, SQ17, SQ18, and the upgraded B5 silo_default record). Paper-named baseline kernel for these five labels is now `svm_rbf_sklearn` (`sklearn.svm.SVC(kernel='rbf', C=1.0, gamma='scale', random_state=0x50414D50)`). See DECISIONS_LOG.md 2026-04-20 entry for rationale and re-run impact.

---

### IV-9. Selective Phase 8 incompleteness

**Threat.** The active S2-backed cohort has 71 labels and Phase 8 has now
produced the complete canonical result set: 2556 records, 2519 OK, 37
documented `engine_failure`, and 0 missing cells. The remaining threat is not
silent incompleteness but selective documented failure: if the 37 failures
cluster by silo, fidelity tier, hardware profile, or circuit family, inference
could be biased unless the failure pattern is reported.

**Mitigation.**

- **Complete runner preflight.** Before launch, every cohort label resolves to
  a live circuit path, a live instance path, and a runner registry entry.
- **No silent skips.** The canonical runner has `_SKIP_CELLS = set()`, no
  `_SKIP_CELLS.add(...)` calls, and per-cell timeout machinery that writes
  schema-valid `engine_failure` records instead of hanging indefinitely.
- **Audit boundary.** `audit_phase8.py` requires one record for each
  label/profile/epsilon/mode cell and reports any missing cells, unexpected
  files, schema violations, and engine-failure diagnostics. The current audit
  reports 2556/2556 records and 37 documented failures.
- **Phase 8c partial mitigation.** Phase 8c measures the top-3 silo-default
  classical methods at every label's instance scale for all 71 current cohort
  labels. For the 13 family/template labels this is template/family-comparable,
  not paper-exact; for the 58 proxy-declared labels the kernels run on the
  template-proxy instance scale and are reported as a cohort-coverage table only.

### IV-10. Azure RE convergence limits on trapped-ion bare mode

**Threat.** A subset of cells run on the Azure Resource Estimator's
trapped-ion qubit profiles (`qubit_gate_us_e3 + surface_code` and
`qubit_gate_us_e4 + surface_code`) in `mode = "bare"` fail to converge
within the 30-minute per-cell budget and are recorded as
`measured.status = "engine_failure"` with
`reason = "timeout_after_1800s"`. The pattern is concentrated in
labels whose Azure-QIR program emits a logical T-count > 10⁸ (e.g.
SR1/SR2 reservoir computing, several SM Monte-Carlo derivative-pricing
labels). Naively this looks like missing data, which would bias the
H1/H2/H3 axes against trapped-ion architectures.

**Why it happens.** The Azure RE solver searches over
`(code_distance, T-factory copies, layout)` triples to find a
configuration whose logical-volume capacity meets the program's
T-count under the ε budget. Trapped-ion *physical* gate times are
~10³× slower than superconducting/Majorana, so for circuits with
T-count > 10⁸ the feasible region collapses and the iterative search
makes no progress. **This is an algorithmic limit of Azure RE on
extreme inputs, not a hardware constraint of our compute infrastructure
or a defect in our code.** F-series VMs with more cores or memory-
optimised E-series do not change the result.

**Mitigation.**

- **Two-stage retry pass.** Phase 8 main run uses
  `P4_CELL_TIMEOUT_S = 1800` and `--workers 12`; an automatic retry
  pass ([../infra/azure/phase8_4vm_legacy_bootstrap/run_phase8_retry.sh](../infra/azure/phase8_4vm_legacy_bootstrap/run_phase8_retry.sh)) deletes every
  surviving `engine_failure` record and reruns the affected cells
  with `P4_CELL_TIMEOUT_S = 3600` and `--workers 1`. The longer
  budget plus the larger memory-per-worker rescues borderline cases
  (cells that hit a CPU contention spike inside a 12-worker pool but
  would have converged given full resources).
- **Surviving timeouts are a documented finding, not hidden.** Cells
  that still time out after the retry pass are kept as `engine_failure`
  records with `reason = "timeout_after_3600s"`. The audit blocker
  `D.coverage_completeness_or_documented_failures` requires every
  `(label × profile × ε × mode)` cell to be either an OK record or a
  documented failure; the retry-pass log appears in the manuscript
  appendix and the surviving-failure count is reported per label and
  per profile in `audit_phase8.json`.
- **Pre-registered "≥ 1 profile populated" rule absorbs single-profile
  loss.** A label that has a complete Majorana-floquet anchor cell
  (the H2/H4 anchor) remains H2/H4-eligible even if its trapped-ion
  bare cells time out. H1 sensitivity over per-profile coverage is
  reported in `stats_report.json` and in `evidence_report.json`.
- **No alternative engine substitution.** We do not silently swap to a
  cheaper estimator (analytic upper bounds, Litinski layout estimator,
  PyZX synthesis counts) for the timed-out cells — that would mix
  estimation methods and break Phase 8 cell-comparability. The honest
  report is "Azure RE could not produce a comparable estimate within
  3600s for these cells."

### IV-11. H3 non-runtime axes are profile-invariant by construction

**Threat.** H3 is pre-registered as a Friedman test "across QEC
profiles" on the four resource axes
`{logical_qubits, t_count, t_depth, runtime_seconds}`. A naive reader
of the schema would expect H3 to test all four axes for a profile
effect, and the historical `phase9_stats.py._h3()` output reported the
non-runtime axes as `skipped_low_n` — a label that misleadingly
suggests a data shortage rather than a structural identity.

**Why the non-runtime axes are untestable.** Three of the four axes
are determined entirely by the input QIR program and the
rotation-synthesis precision ε, not by the QEC code or the magic-state
distillation budget:

- `logical_qubits` is a count of distinct logical IDs in the QIR
  program, fixed at QIR generation time;
- `t_count` is the count of `T` and `T†` instructions after
  rotation synthesis at the target ε, fixed by the QIR pass;
- `t_depth` is the longest T-dependency chain in the synthesised
  circuit, also fixed by the QIR pass.

The choice of QEC code (`surface_code` vs `floquet_code`) affects
*physical* qubit count, *physical* runtime, and *physical* T-factory
overhead — none of which are these three axes. So `τ` (= the cell
value normalised against the Majorana-floquet anchor) is identically
1.0 across profiles for these three axes, and the Friedman test on
constant data is mathematically degenerate.

**Mitigation.**

- **Schema makes the structural identity explicit.** As of the
  2026-04-19 phase-9 update (DECISIONS_LOG: "H2 mixed-effects
  sensitivity and H3 structural-invariants reporting"),
  `stats_report.json.H3.structural_invariants` emits a per-axis
  block of the form `{axis_invariant_by_construction: true,
  reason: "..."}` for `logical_qubits`, `t_count`, and `t_depth`. No
  test is run on those axes; the field name itself states the
  reason.
- **Runtime axis is the one meaningful H3 test.** `_h3()` runs the
  Friedman test on `runtime_seconds` only. The current result is
  p = 0.0961 with Kendall's W = 0.110, so the runtime profile effect is
  directionally visible but not a headline rejection at alpha = 0.05.
- **Artifact wording.** H3 claim artifacts are scoped to runtime:
  "H3 (Friedman test on `log10(tau_runtime)` across six QEC profiles)".
  The other three axes are metadata-limited and must not be presented as
  failed tests.

### IV-12. H2 anchor-cell test is small-n; pooled tests are anti-conservative

**Threat.** The pre-registered H2 headline is a Kruskal-Wallis test on
`log10(τ_runtime)` at the Majorana-floquet anchor (one cell per label), giving
n = 13 family/template labels distributed across 4 active family/template silos in the
current run. With few labels per silo, H2 has low statistical power. A reviewer
might propose pooling all populated `(label x profile x epsilon)` cells into a
single non-parametric test, but that would not be valid evidence of a silo
effect because repeated cells from the same label are highly clustered.

**Why pooling is anti-conservative.** A mixed-effects sensitivity on the same
pooled data, `log10_tau ~ C(silo) + (1|label)`, axis = `runtime_seconds`, now
uses 231 rows across 13 family/template labels and 4 silos. It gives a joint silo
p-value of 0.729 and label ICC = 0.993. An ICC near 1 means nearly all
variation in `log10(τ_runtime)` is between labels, not within repeated
profile/epsilon cells. A non-hierarchical pooled KW or ANOVA would therefore
inflate the effective sample size and overstate evidence for a silo effect.

**Mitigation.**

- **Pre-registered test is the headline.** The H2 acceptance rule
  `accept_h2_overall` is tied to the anchor-cell KW + Holm Mann-Whitney
  posthocs, not to any pooled test. The 2026-04-19 phase-9 update
  added `stats_report.json.H2.mixed_effects_sensitivity` as a clearly-
  labelled sensitivity, not a replacement headline.
- **Manuscript wording is explicit.** The H2 paragraph reports the
  anchor-cell KW result (p = 0.8728, do not reject), the MixedLM sensitivity
  result (joint p = 0.729, ICC = 0.993), and the interpretation: no headline
  silo effect is supported in the current Faithful cohort, and pooled
  non-hierarchical tests would be anti-conservative.
- **Power note in PRE_REGISTRATION.** PRE_REGISTRATION.md H2 was written for
  the current 71-label cohort with the eligible n determined by Phase 8
  completion at the analysis anchor. The pre-registered acceptance rule does
  not change after seeing the result.
- **No retroactive headline swap.** If the MixedLM p crosses 0.05
  after the retry pass we will report it explicitly as "MixedLM
  sensitivity rejected at α = 0.05; pre-registered anchor-cell test
  did not reject." The MixedLM cannot retroactively become the H2
  headline.

---

## External validity (generalisability)

### EV-1. Population is quantum finance only

**Threat.** Findings may not generalise to other application domains
(chemistry, materials, optimisation more broadly).

**Mitigation.** **None claimed.** The manuscript is explicit that the
population is quantum finance; the methodological contribution
(systematic review → triangulated synthesis → pre-registered FT-RE) is
generalisable but the empirical findings are not.

### EV-2. Population is up to the Phase 2 cutoff date

**Threat.** Papers published after the Phase 2 cutoff are not in the
cohort. The bifurcation thesis could be falsified by a paper published
during the Phase 4 run.

**Mitigation.**

- **Cutoff documented** in the Phase 2 SLR protocol and search logs,
  and cited in the Methods section.
- **Manuscript cutoff statement.** "Findings reflect the
  quantum-finance literature as of [Phase 2 cutoff date]; subsequent
  publications are out of scope and addressed in the Discussion."
- **Watch-list.** The Discussion section names ≥ 3 prominent
  publications that appeared after the Phase 2 cutoff and would be
  candidates for the next iteration of the cohort, including any
  candidates for strict-H4 falsification.

### EV-3. Findings apply only to the FT regime

**Threat.** Under the canonical pipeline we report FT estimates only.
Many quantum-finance papers report NISQ-era findings; the bifurcation
thesis may not transfer.

**Mitigation.**

- **L5 NISQ veto layer.** Phase 3's five-layer scoring includes the L5
  NISQ veto, which is not a Phase 4 finding but is upstream context.
  Papers vetoed by L5 are reported separately as "NISQ-only viable"
  in Phase 3 outputs and are explicitly out of Phase 4 scope.
- **Discussion section.** The manuscript Discussion explicitly limits
  the bifurcation finding to the FT regime; near-term NISQ findings
  are out of scope.

---

### EV-4. Instance-scale scope

**Threat.** Every cell estimated under `p4-canonical-v1` uses the paper's
published instance scale (typically ≤ 10 logical qubits; the Faithful
sub-cohort spans n_qubits ∈ {3, …, 16} at the H4 anchor). The headline
H4 verdict and the bifurcation structural property reported in
Chapter 5 are therefore claims about the **published instance scale**,
not about any advantage-relevant N in the asymptotic regime cited by
Hoefler 2023 or Babbush 2021.

**Mitigation.** The Phase 8d appendix is a fixed-precision QAE/HHL high-N
scout. It varies problem size `N` while holding precision qubits `m` on an
explicit grid, so it does not conflate scaling with an `m=N` precision blow-up.
The appendix is disclosed as post-headline evidence: it can inform scaling
discussion beyond the published instance scale, but it does not promote labels
or alter the Phase 8/9 headline verdict.

---

## Conclusion validity

### CnV-1. Multiple-comparisons inflation across hypothesis families

**Threat.** Testing H1, H2, H3, H4 increases the family-wise Type I
error rate.

**Mitigation.**

- **No correction across families** is the pre-registered choice
  (PRE_REGISTRATION.md §3 and §6), with rationale: the four hypotheses test
  logically distinct claims and a Bonferroni-style correction would
  inflate Type II error.
- **Within-family Holm-Bonferroni** is applied (H1 across 4 axes; H2
  across silo-pair posthocs).
- **Effect-size thresholds** mean a marginally significant p-value
  with small effect size does not promote a finding to the headline.

### CnV-2. Optional-stopping (running until results are clean)

**Threat.** Earlier pilot ladders explored changing cohort definitions. A
reviewer might worry the active P4 cohort was adjusted after seeing downstream
resource-estimation behavior.

**Mitigation.**

- **Canonical pipeline starts from a fresh `output/`.** Historical pilot outputs
  are recoverable from git history and are NOT mixed with canonical records.
- **Current cohort size was fixed before Phase 8.** The active S2-backed cohort
  has 71 labels (`F=13`, `P=58`) and was locked before the 2556-cell big run.
  There is no "stop early" option.
- **Sub-cohort sensitivity.** The headline result is reported on the 13-label
  Faithful sub-cohort. The manuscript explicitly distinguishes the current
  canonical-pipeline cohort from earlier pilot ladders.
- **Discussion section.** The Discussion explicitly addresses the
  v1–v5 ladder as the "methodological pilot that informed the
  canonical pipeline" and acknowledges the optional-stopping concern.

### CnV-3. Investigator confirmation bias

**Threat.** The operator's prior is the bifurcation thesis. Confirmation
bias could shape implementation choices toward the prior.

**Mitigation.**

- **Pre-registered hypotheses with falsification criteria.** A
  non-empty strict-H4 subset under any sensitivity perturbation is
  reported as the headline counter-example (see PRE_REGISTRATION.md
  §3 H4 falsification criterion).
- **Two-author independent review** of all F-tier circuits (IV-7).
- **External replication** at Phase 11 by a person other than the
  primary operator.
- **Microsoft Quantum Applications team review** at submission.
- **The methodology is the contribution.** The manuscript reports
  whichever finding the data produces; either outcome is publishable.

### CnV-4. Strict-H4 is over-specified and trivially empty

**Threat.** A reviewer might argue the 5-conjunct strict-H4 criterion
is so stringent that it is trivially empty regardless of data.

**Mitigation.**

- **Each conjunct is justified** in the pre-registration and exposed in the
  Phase 10 H4 failure-taxonomy artifacts.
- **Naive subset is reported.** The 2-conjunct naive subset
  (`τ < 10` AND beats classical) is reported as a sub-strict
  comparison; the strict subset is the strict subset of the naive
  subset.
- **Lemma argument.** The bifurcation argument is derived analytically from the
  FT cost decomposition; the strict-H4 emptiness is not just an empirical
  observation but a structural property.
- **Falsifiable.** A non-empty strict-H4 subset is the headline
  positive finding; the design is symmetric.

---

## Operational threats

### OT-1. Resource estimator can fail (engine errors, OOM)

**Threat.** Some heavy cells may fail to complete (RE engine error,
timeout > 12 h, Windows OOM).

**Mitigation.**

- **`engine_failure` status.** Failed cells are recorded with
  `measured.status = "engine_failure"` plus diagnostic output and
  retry log.
- **Audit blocker `D.coverage_completeness_or_documented_failures`.**
  Every (label × profile × ε × mode) cell must have either a record
  or a documented failure.
- **One retry policy.** Each failed cell is retried once after the
  full matrix completes. A cell that fails twice is permanently
  recorded as failed and the failure rate is reported as a finding
  in the manuscript. Current canonical accounting reports 37 documented
  failures out of 2556 expected cells.
- **No silent skips.** The canonical pipeline removes the v3–v5
  trapped-ion blanket skip entirely.

### OT-2. Two-author divergent F-tier implementations

**Threat.** The 10% spot-check (IV-7) could reveal that the two
authors implement the same paper differently, undermining
"paper-faithful".

**Mitigation.**

- **Discrepancies become decisions.** Each spot-check discrepancy is
  resolved by joint re-reading of the paper and (a) one
  implementation chosen, (b) the alternative archived in
  `<paper_dir>/alternative_implementation.py`, (c) the choice
  documented in `<paper_dir>/notes.md`.
- **Aggregate discrepancy rate reported.** The manuscript reports
  the spot-check discrepancy rate (e.g. "2 / 6 spot-check labels
  produced divergent implementations on first reading; both were
  resolved by joint re-reading").

### OT-3. Wall-clock budget overrun

**Threat.** A full canonical rerun could exceed the available wall clock. The
current S2-backed run is 2556 cells, and the external Phase 8d HHL/QAE scout is
separate VM-backed appendix compute.

**Mitigation.**

- **Complete accounting.** The current canonical Phase 8 audit confirms
  2556/2556 records with no missing cells.
- **Resume support.** `run_pipeline.py --resume` skips completed phases, and
  Phase 8 records are keyed by deterministic filenames.
- **Per-cell timeout and documented failures.** A cell that cannot complete is
  written as `engine_failure` rather than silently omitted.

---

## Summary

The canonical pipeline is designed so that **each named threat has a
mechanical mitigation embedded in the audit, the pre-registration, or
the pipeline orchestrator**. Threats without mechanical mitigation
(EV-1 through EV-3, CV-3 partial, CV-4 partial) are explicitly
discussed in the manuscript Discussion section.

A reviewer applying any of the named threats to the canonical pipeline
will find either a mitigation or an explicit acknowledgement; no
threat is silently absorbed.


---

## Addendum 2026-05-02 - audit-surfaced threats CV-5..CV-7

The following three threats were surfaced by a senior-review pass on
2026-05-02 and added here for completeness. They are not new design
choices; they document *existing* construct-validity weaknesses that
reviewers familiar with the field will press on.

### CV-5. HHL classical baseline inflated to clear the strict-H4 C5 floor

The classical baselines for SP1 / SP2 / SH1 (the HHL-family labels)
in `p4_experiments/core/run_unit.py` (lines ~182-233) construct a
**synthetic dense 1024x1024 system explicitly sized to clear the
strict-H4 10 ms wall-clock floor**. The source comment is candid:
"problem-faithful baseline (paper's actual A) would be sub-ms and
therefore disqualify the classical leg under strict-H4". The headline
H4 result is then computed against this inflated baseline.

Because the H4 verdict is **negative** (no winners), CV-5 *helps* the
bifurcation argument - the bar is generous and still nothing passes.
If a future iteration produced an H4 winner, the inflated baseline
would have to be replaced with a paper-faithful one (or a tuned
modern competitor) before the result could be published.

**Mitigation in this release:** disclosure here, in the matching
PRE_REGISTRATION.md section 0a callout, and in the
`outputs/manuscript_artifacts/caption_pack.md` per-figure caveat
banner for any figure that touches SP1 / SP2 / SH1.

### CV-6. Hoefler crossover figure uses optimistic constants

`pipeline/phase10_hoefler_scaling_figure.py` faithfully reproduces
Hoefler-Haner-Troyer's Table 1 fp16 numbers (A100 GPU 195 Top/s,
ASIC 0.55 Pop/s, FT-quantum 10.5 kop/s, deadline 1e6 s) and the
crossover formula `N* = (t_q / t_c)^(1 / (k-1))`. The constants are
correct as-cited but optimistic for the quantum side: a 10k-logical-
qubit fp16 Majorana machine is the limit-of-possibility scenario,
not a near-term forecast. The figure also fixes the classical
exponent `k = 2`; for any exponential-speedup claim, `k` is the
whole story.

**Mitigation:** disclosure here. A `k in {1.5, 2, 3}` panel sweep is
recorded as a Stronger-version remediation item; the current figure
should be read as one slice through that family, not as the family
itself.

### CV-7. Single-thread numpy/scipy classical baselines vs idealised future quantum

Phase 8b / 8c classical baselines run as numpy + scipy + single
thread (`OMP_NUM_THREADS=1`), while the future-quantum side is
given the optimistic Hoefler constants from CV-6 (10k logical qubits,
fp16 Majorana, deadline 1e6 s). This is the **standard quantum-
advantage tilt**: a generous quantum future against a deliberately
small classical present. As with CV-5, this *helps* the negative
H4 verdict and *would have to be revisited* if any label flipped
positive. A Stronger-version remediation step adds a tuned
classical sensitivity tier (e.g. CPLEX for SP4 mean-variance QP;
QuantLib MC with control variates for derivative-pricing labels)
on at least 2-3 labels; that work is out of MDV scope.
