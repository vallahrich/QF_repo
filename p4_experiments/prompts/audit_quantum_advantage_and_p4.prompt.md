---
mode: agent
description: PhD-level adversarial peer review of (A) the P3 quantum-advantage triangulation framework and (B) the P4 oracle-tax experimental pipeline. Cross-checked against P1 framework synthesis, P2 SLR extractions, and shared taxonomies. Produces a structured findings report with severity, evidence, and concrete fixes.
---

# PhD Audit — P3 Quantum-Advantage Framework & P4 Oracle-Tax Experiments

You are an academic peer reviewer with expertise in **systematic literature reviews (SLR)**,
**fault-tolerant quantum resource estimation**, and **quantitative finance**. You are
reviewing two coupled artefacts of a PhD thesis on quantum computing in financial
services:

- **Part A — `p3_thematic_synthesis/quantum_advantage/`**: a triangulated quantum-advantage
  assessment framework (4 core layers + 1 NISQ veto + 2 legacy frameworks) applied to the
  P2 extraction corpus.
- **Part B — `p4_experiments/`**: a pre-registered, oracle-inclusive resource-estimation
  pipeline (QDK + Azure Quantum RE) that measures the *oracle tax* — the gap between
  paper-claimed and end-to-end logical resources — across the current 71-label
  S2-backed canonical cohort.

Both artefacts must be defensible at viva. Your job is **not** to summarise what exists,
but to find every way the current implementation could be **wrong, misleading, biased
toward the thesis, or inconsistent with the upstream phases**. Treat every threshold,
schema field, mapping, and decision rule as a **claim** that must be re-verified against
either the primary source paper or the code itself. **When code and documentation
disagree, the code wins and the documentation is a defect.**

All paths are relative to the `quantum-finance/` workspace root.

---

## 0 · Repository context (read first)

This is a multi-phase research system. You must understand the data flow before
auditing any single artefact:

- **Phase 1** (`p1_framework_synthesis/`): 5 manually-curated framework papers
  (Bouland, Herman, Pasupuleti, Chawla, Tagatil) defining the problem-domain taxonomy.
  Outputs: `s1_extractions/*.json`.
- **Phase 2** (`p2_systematic_review/`): SLR of 900+ papers → 6-step LLM extraction
  (`s2_classification/prompts/step{1..6}_*.txt`) → 1554 processed markdown files
  with YAML frontmatter (topic_tags, methodology_tags, idea_tags, contradiction_flags).
- **Shared** (`shared/`): unified taxonomy (`config/unified_taxonomy.json`),
  tier definitions (`config/tier_definitions.json`), source types
  (`config/source_types.json`), 777 paper markdown files
  (`extracted_text/text/*.md`), paper-ID bridge (`bridge/paper_id_bridge.csv`),
  and the LLM client (`llm_client.py`).
- **Phase 3** (`p3_thematic_synthesis/`): domain silos + quantitative benchmarking
  (`quantitative/`, 643 extractions, 1957 experiments) + quantum-advantage
  triangulation (`quantum_advantage/`, frozen output).
- **Phase 4** (`p4_experiments/`): consumes S2 quantitative extraction outputs,
  Vincent/manual review, and joint triage to drive a 2556-cell canonical RE
  matrix (71 labels × 6 hardware profiles × 3 ε × 2 modes), classical baselines,
  Phase 9 H1-H4 statistics, Phase 10 manuscript artifacts, and the appendix-only
  Phase 8d HHL/QAE high-N scout.

Memory notes (read before auditing):
- `/memories/repo/quantum-advantage-full-exploration.md` — prior findings on each
  P3 framework, including known bugs in `beverland_2022`, `chakrabarti_2021`,
  `dalzell_2023`, and `combined/triangulate.py` consensus exclusion behaviour.
- `/memories/repo/qdk-qiskit-bridge-gotchas.md` — pathological gate sets,
  optimization-level pitfalls, and the documented skip cells for QDK RE.
- `/memories/repo/quantitative-live-pipeline-audit.md` — prior P3 quantitative
  audit findings; relevant because P4 consumes those extractions transitively.

Frozen manifest: `p3_thematic_synthesis/quantum_advantage/FROZEN.md`
P4 pre-registration: `p4_experiments/P4_PLAN.md`, `p4_experiments/PRE_REGISTRATION.md`

---

## 1 · Audit checklist

For every item below, record **`PASS`**, **`FAIL`**, or **`CONCERN`** with a
one-sentence justification *and* a `file:line` (or `file:JSON-pointer`) citation.
Do not skip items; if an item is genuinely not applicable, write `N/A` and explain why.
Findings without a citation do not count.

### Part A — P3 quantum-advantage framework

#### A1. Each framework assessor vs. its source paper

For **each** of `ronnow/`, `hoefler_assessment/`, `babbush_2021/`,
`beverland_2022/`, `chakrabarti_2021/`, `dalzell_2023/`, `stilck_franca_2021/`
(and the legacy `montanaro_2015/`, `dequantization/` if still present):

- Open the source PDF (or the converted `_shared/<paper>.md`) and **spot-check
  ≥2 numerical thresholds** in the corresponding `*_thresholds.json` /
  `*_scenarios.json` against the paper's tables/equations. Any mismatch → `FAIL`.
- Confirm `assess_<framework>.py` actually **uses every threshold it loads**.
  Unused thresholds are `CONCERN` (silent scope reduction).
- Confirm the **resource axes** the assessor reads from extractions match the
  axes the paper's thresholds define. Known-bad cases to re-verify (per memory
  note 2026-04-16): `beverland_2022` collapses a scenario sweep to a best-case
  verdict; `chakrabarti_2021` and `dalzell_2023` declare a T-depth axis in JSON
  but never compare it.
- Confirm `make_verdict()` in `_shared/verdict.py` is called with a `confidence`
  that **reflects data availability**, not a hard-coded `"high"`.
- Confirm the assessor neither **over-claims** (verdict above what the paper's
  methodology supports) nor **under-claims** (e.g. defaulting to `fails` when
  `insufficient_data` is honest).

#### A2. Triangulation logic

`p3_thematic_synthesis/quantum_advantage/combined/triangulate.py` and
`_shared/aggregation.py`, `_shared/verdict.py`, `_shared/common_verdict_schema.json`:

- Re-derive the consensus rule from code and compare it to `README.md` and
  `FROZEN.md`. The advertised design is **4 core + 1 veto** — verify which
  frameworks are core, which is veto, and that the code enforces the veto
  (i.e. `stilck_franca_2021` can downgrade an otherwise viable verdict).
- Confirm `not_applicable` and `insufficient_data` are handled **explicitly**,
  not by silent exclusion. If they are excluded from the panel, verify this is
  documented and that it does not inflate `unanimous_viable` counts by reducing
  the effective panel size below a published minimum.
- Check that `disagreement_score` normalisation is monotone (higher = more
  disagreement) and that the sort order in `disagreement_cases.json` matches.
- Run the pipeline end-to-end and **diff outputs against the frozen JSON files**
  referenced in `FROZEN.md`. Any divergence is a `FAIL` (P4 depends on these).

#### A3. Derived-fields enrichment

`p3_thematic_synthesis/quantum_advantage/derived_fields/compute_derived_fields.py` +
`algorithm_complexity.json`:

- For **3 randomly chosen experiments**, recompute `oracle_complexity_M`,
  `speedup_order`, `num_qubits`, and `gate_count_total` by hand from the
  extraction JSON and compare to `enriched/derived_fields.json`. Any mismatch → `FAIL`.
- Confirm every derived field carries `_derived=True` and that downstream
  assessors can distinguish derived from paper-reported values.
- Confirm the algorithm-family → complexity mapping is consistent with the
  speedup mapping in `_shared/speedup.py` and with each framework's
  `algorithm_speedup_mapping`.

#### A4. P3 ↔ P1/P2/shared cross-phase alignment

This is where the bulk of examiner-facing risk lives. Verify **all four**
chains are consistent:

- **Silo / topic vocabulary.** `shared/config/unified_taxonomy.json::topic_tags`
  vs `p3_thematic_synthesis/quantitative/config/benchmark_schema.json::finance_domain.primary_silo.enum`
  vs `quantum_advantage/combined/triangulate.py::_CHAKRABARTI_SILOS / _DALZELL_SILOS`
  vs `p2_systematic_review/s2_classification/prompts/step6_synthesis.txt` tag
  vocabulary. Any silo present in one but missing in another → `FAIL`.
- **Algorithm families.** `benchmark_schema.json::algorithm.family.enum`
  vs `unified_taxonomy.json::methodology_tags` vs
  `quantum_advantage/_shared/speedup.py` vs each framework's
  `algorithm_speedup_mapping` vs `step3_methodology.txt` vocabulary. Flag
  every divergence.
- **Tier and source-type usage.** Confirm `shared/config/tier_definitions.json`
  and `source_types.json` are honoured by both the P2 step-1 classifier and
  any P3/P4 filter that uses tier/source-type. Mismatched enums → `FAIL`.
- **Paper-ID flow.** `shared/extracted_text/text/*.md` (777) →
  `shared/bridge/paper_id_bridge.csv` →
  `p3_thematic_synthesis/quantitative/output/extractions/*.json` (643) →
  `quantum_advantage/_shared/extraction_loader.py::iter_experiments` →
  framework `results/*.json` → `combined/triangulation_matrix.json` →
  `p4_experiments/core/p4_shortlist.json`. Pick **one paper-ID** and trace
  it through every link; any break is a `FAIL`.
- **P1 framework anchoring.** Open 2 of the 5 JSONs in
  `p1_framework_synthesis/s1_extractions/` and verify the silos and methodology
  tags they introduce are still represented in the P3 quantum-advantage
  framework choice (e.g. is the rationale for choosing Hoefler/Babbush/etc.
  traceable to a P1 framework paper, or did it appear ex nihilo in P3?).

#### A5. P3 data integrity and LLM-extraction reliability

- Examine **3–5 random extraction JSONs** in
  `p3_thematic_synthesis/quantitative/output/extractions/`: are field names
  correct, are values plausible, do experiment array structures match
  `benchmark_schema.json`?
- Verify `_shared/extraction_loader.py::_bridge_experiment()` correctly maps
  array fields (`classical_baselines`, `speedup_claims`) to the flat fields
  the assessors expect; missing/incorrect mappings cause silent
  `insufficient_data` verdicts → `FAIL`.
- Spot-check the LLM extraction prompt (`quantitative/prompts/benchmark_extraction.txt`)
  for: schema drift relative to `benchmark_schema.json`; over-eager defaulting
  (e.g. coercing missing fields to plausible-looking numbers); and absence of
  an explicit "decline if not present" instruction. Also check
  `quantitative/scripts/validate_benchmarks.py` is actually invoked in the run
  pipeline (`scripts/run_batch.py`), not just defined.

---

### Part B — P4 oracle-tax experiments

#### B1. Pre-registration integrity

- Read `p4_experiments/canonical/PRE_REGISTRATION.md`,
  `p4_experiments/canonical/README.md`, and
  `p4_experiments/canonical/REPRODUCE.md`. List every commitment (matrix size
  71×6×3×2=2556, profiles, ε values, hypotheses H1–H4, statistical tests, and
  the Phase 8d appendix-only regime boundary) as a bullet.
- For each commitment, find the **enforcement point in code** (file/function).
  Commitments without an enforcement point → `CONCERN`.
- Confirm `provenance.preregistration_tag` in every
  `common/output/results/*.json` matches the **current** pre-registration
  version. Mixed or stale tags → `FAIL`.
- Confirm the 2556-cell matrix is fully accounted for as OK records plus
  documented `engine_failure` records, with no unexplained missing cells. Any
  unexplained gap → `FAIL`.

#### B2. QDK ↔ Qiskit bridge

`p4_experiments/core/qdk_bridge.py` + `/memories/repo/qdk-qiskit-bridge-gotchas.md`:

- Verify `_SAFE_BASIS_GATES` is a **subset** of the QDK `QirTarget` gate set
  (defined in `qsharp/interop/qiskit/backends/qirtarget.py`). Any gate outside
  that set → `FAIL`.
- Verify `_decompose_for_qdk` uses `optimization_level=0`. Higher levels merge
  rotations into arbitrary-angle `u/u3/p` gates that hang QDK rotation synthesis.
- Verify `estimate()` passes `skip_transpilation=True` and that decomposition
  runs **once per circuit**, not once per (profile, ε) tuple.
- Confirm the documented skip set
  `{(B4, ti_e3_surface, ≤1e-4, full), (B4, ti_e4_surface, ≤1e-4, full)}` is
  still narrow; any broadening → `CONCERN`.

#### B3. Circuit builders and instance definitions

For **each active label** in `p4_experiments/canonical/cohort.json`:

- Read `experiments/silos/<silo>/<paper_or_label>/circuit.py`. Confirm the **bare** vs **full**
  circuits differ by **more than a cosmetic factor** (full = bare + oracle /
  state-prep / loader machinery). A bare ≈ full pair → `FAIL` (the tax
  collapses to 1 by construction, fabricating the negative result).
- Confirm the instance JSON carries every field required by
  `core/schemas/result_record.schema.json` (especially `instance_id`,
  `finance_problem`, `paper_claimed`).
- For labels with a custom classical baseline branch, verify `core/run_unit._classical_for` runs a baseline that
  (a) solves the **same finance problem** (not a proxy) and (b) takes long
  enough for wall-clock to be non-trivial. Sub-millisecond baselines
  invalidate **H4** → `CONCERN` at minimum.

#### B4. Result records

Walk `p4_experiments/common/output/results/`:

- Count records by `(label, profile, ε, mode)`. `288 − #skip_cells` must
  equal the file count. Anything else → `FAIL`.
- For 5 randomly chosen records, validate against
  `result_record.schema.json` and confirm `measured.{num_qubits, t_count,
  t_depth, runtime_seconds}` are all present and non-null when the unit did
  not hit a documented metric-skip path.
- Confirm `classical_ref.algorithm_label` is populated and that the wall-clock
  is a **real measurement**, not a placeholder `0.0` / `None`.

#### B5. Oracle-tax aggregation

`p4_experiments/canonical/pipeline/phase09_stats.py` (the canonical replacement
of the old `common/compare.py`) → `p4_experiments/canonical/reports/oracle_tax_table.json`:

- Recompute τ for **3 random** `(label, profile, ε, axis)` rows directly from
  the bare/full record pair. Any disagreement > `1e-9` → `FAIL`.
- Confirm `log10_tau_vs_claim` is `None` (not `0.0` or a silent fallback to
  `tau_vs_bare`) when the paper did not report that axis.
- Confirm `logical_qubits` τ_vs_bare ≡ 1 across the entire table; any row ≠ 1
  → `CONCERN` (oracle expansion that should have been caught by the bridge).

#### B6. Statistical tests

`p4_experiments/canonical/pipeline/phase09_stats.py` (the canonical replacement
of the old `common/stats.py`) → `p4_experiments/canonical/reports/stats_report.json`:

- **H1.** One-sided Wilcoxon against `median log10(τ) = 1`. Confirm
  `alternative="greater"` and that the fallback from `log10_tau_vs_claim` to
  `log10_tau_vs_bare` is explicit and reported per axis.
- **H2.** Kruskal–Wallis on `log10(τ_vs_bare)` across silos. Confirm
  Holm–Bonferroni is applied **only after** the omnibus is rejected. Count
  silos with n ≥ 3; fewer than 2 such silos must surface as an explicit
  error, not a silent pass.
- **H3.** Friedman paired across the 6 profiles. Confirm constant blocks
  are excluded **before** invoking `scipy.stats.friedmanchisquare` (otherwise
  p-values are NaN or 0).
- **H4.** Subset at `(maj_e6_floquet, ε=1e-4, runtime_seconds)`. Confirm
  `beats_classical` uses the **measured** classical wall-clock, not a
  theoretical bound. `subset_size = 0` → `CONCERN` (contradicts the
  constructive half of the thesis).
- Independently rerun `stats.py` and diff against the saved
  `stats_report.json`. Any non-deterministic field (other than timestamps)
  → `FAIL`.

#### B7. P4 ↔ P3 frozen-boundary discipline

- Confirm **no P4 module imports any P3 assessor module directly**. P4 must
  consume frozen JSON only. Any
  `from p3_thematic_synthesis.quantum_advantage.<framework>` import → `FAIL`.
- Confirm the (now-archived) `common/build_p4_shortlist.py` would read from the frozen
  `combined/output/triangulation_matrix.json` referenced in `FROZEN.md`,
  not from a re-run.
- Spot-check 3 shortlist entries: each must be present in the frozen
  triangulation matrix with the same `(paper_id, experiment_id)` key.

---

### Part C — Cross-cutting

- **Determinism.** Rerun `compare.py` and `stats.py`; on-disk files must be
  byte-identical (ignoring timestamps). Non-determinism → `FAIL`.
- **Logging.** Every long-running operation in P3 and P4 must write to
  `logs/` in JSONL with timestamps and a run identifier. Untracked runs →
  `CONCERN`.
- **Provenance chain.** Pick **one τ row** in `oracle_tax_table.json`; trace
  it back through the tax table → the two underlying records → the circuit
  builder → the instance JSON → the pre-registered shortlist → the frozen
  triangulation row → the P3 extraction JSON → the P2 processed markdown →
  the original paper PDF in `shared/extracted_text/`. Any break → `FAIL`.
- **Independence assumption.** Confirm the Wilcoxon/Friedman tests' assumption
  of independent units is at least addressed (papers that contribute multiple
  experiments may violate it). Silent ignorance → `CONCERN`.

---

## 2 · Anticipated examiner challenges

For each, draft an **examiner-ready defence** (≤ 100 words) grounded in code
and outputs, *or* admit the gap:

1. Is LLM extraction reliable enough to support quantitative thesis claims?
   What is the validation strategy and inter-rater equivalent?
2. Is the **4-core + 1-veto** triangulation justified, or could a different
   layer arrangement materially change conclusions?
3. Are the Hoefler / Babbush thresholds **too pessimistic** for NISQ-era papers?
4. Is the Rønnow benchmark-validity layer **too generous** (most papers pass)
   or too strict?
5. Does the Stilck França veto apply too broadly or too narrowly?
6. Selection bias in framework choice — why these 5 and not others
   (e.g. Aaronson 2015, Tang dequantization, Gidney–Ekerå 2021)?
7. Are the Dalzell MSA thresholds appropriate for **all** finance sub-domains,
   or only the silos Dalzell explicitly analysed?
8. Pre-registration discipline: were H1–H4 fixed before any P4 result was
   inspected? What is the audit trail?
9. The 6-profile RE grid samples QDK's parameter space — does it cover the
   axes that matter for finance workloads, or is it convenient rather than
   adversarial?
10. Statistical multiple-comparison burden across H1–H4: is a global
    family-wise error rate controlled, or only per-hypothesis?
11. Generalisability of the 71-label canonical cohort to the wider S2/P3
  quantitative corpus — is the cohort representative or cherry-picked?
12. The appendix-only `qae_hhl_fixed_precision_high_n` scout varies HHL/QAE
  problem size outside the headline regime — is this boundary documented
  clearly enough to prevent accidental pooling into H1-H4?

---

## 3 · Method

1. Read the two memory notes listed in §0; they encode prior lessons.
2. For every checklist item in §1, open the referenced files and verify
   directly. **Never** accept README/PLAN at face value when code is available.
3. When you find a `FAIL`, immediately check whether the **same root cause**
   exists elsewhere (pattern-match across frameworks / silos).
4. When you find a `CONCERN`, propose the **minimal fix** as a diff-style
   snippet (≤ 50 LOC).
5. You may rerun `compare.py` and `stats.py` for determinism checks. Do
   **not** launch new QDK RE runs. If an audit item requires fresh RE data,
   tag it `REQUIRES-NEW-RUN` and state the smallest experiment that would
   close the gap.

---

## 4 · Deliverable

Write a single file: `p4_experiments/analysis/audit_report.md` with sections:

1. **Verdict.** `PASS` / `CONDITIONAL PASS` / `FAIL` overall, plus a one-line
   summary per checklist item: `A1 PASS | A2 FAIL | A3 CONCERN | … | B7 PASS | C PASS`.
2. **Strengths.** What works well academically (≤ 10 bullets, each citing
   evidence).
3. **Findings.** For every `FAIL` or `CONCERN`: title, severity
   (`blocker` / `major` / `minor`), `file:line` citation, evidence (quoted
   code or numbers from output JSON), root cause, and recommended fix.
4. **Hypotheses & RQs at risk.** For each of H1–H4 and the two RQs in
   `P4_PLAN.md §1`, state whether the audit findings change the conclusion
   and how.
5. **Examiner-ready defences.** One paragraph per item in §2.
6. **Patch queue.** Ordered list of concrete code/data changes the
   implementing agent should apply next, scoped so each fix is < 50 LOC.
   Blockers first.
7. **Items that could not be audited without new data.** Listed as
   `REQUIRES-NEW-RUN` with the smallest experiment that would close each gap.

Keep findings **short**: one tight paragraph each. No fluff, no re-summarising
the plan or README. **Every claim must cite a file path + line number or a
numerical value from an actual output file.** Vague feedback is not useful —
this is a real PhD audit.
