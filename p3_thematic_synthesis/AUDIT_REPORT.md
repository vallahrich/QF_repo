# PhD Audit Report — P3 Quantitative & Quantum Advantage

> ⚠️ **Historical document; paths predate the s2_/s3_ rename.** (Banner added 2026-05-02.)
>
> Every `p3_thematic_synthesis/quantitative/` reference below should be read as
> `p3_thematic_synthesis/s2_quantitative/`, and every
> `p3_thematic_synthesis/quantum_advantage/` reference should be read as
> `p3_thematic_synthesis/s3_quantum_advantage/`. Numeric counts (777 / 643 /
> 1957) are the **2026-04-17 freeze state**; the active baseline (501 / 1046)
> is superseded by [`FREEZE.md`](FREEZE.md) and
> [`P3_AUDIT_STATUS.md`](P3_AUDIT_STATUS.md). Use this report only for the
> historical design rationale and findings narrative; for live numbers and
> paths, defer to the freeze/status files.

# PhD Audit Report — P3 Quantitative & Quantum Advantage

**Scope audited**: `p3_thematic_synthesis/quantitative/` and `p3_thematic_synthesis/quantum_advantage/`, plus their wiring to `p1_framework_synthesis/`, `p2_systematic_review/`, `shared/bridge/`, `shared/config/`, and `shared/extracted_text/`.
**Thesis scope constraint**: **gate-based quantum computing only**. Quantum annealing (D-Wave, adiabatic, pure QUBO-on-annealer) is **out of scope** and must not appear in the frozen corpus or in any assessor verdict.
**Historical audited corpus**: 777 source markdowns -> 643 quantitative extractions -> 1,957 experiments.
**Date**: 2026-04-17 (updated after scope clarification).

> **Completed before this report was written:**
> - Removed `montanaro_2015` and `dequantization` from `FRAMEWORKS` in [_shared/verdict.py](p3_thematic_synthesis/quantum_advantage/_shared/verdict.py).
> - Removed the same two from the `framework` enum in [_shared/common_verdict_schema.json](p3_thematic_synthesis/quantum_advantage/_shared/common_verdict_schema.json).
> - Removed the "Legacy frameworks" paragraph from [combined/triangulate.py](p3_thematic_synthesis/quantum_advantage/combined/triangulate.py) docstring.
> - The only remaining references to "montanaro" / "dequantization" in the codebase are legitimate scholarly citations inside `derived_fields/algorithm_complexity.json` and the narrative `p4_experiments/` notes (Tang 2019 dequantization of recommendation systems). Those stay.

---

## 1. Overall verdict: **CONDITIONAL PASS — but the quantitative corpus must be re-run before freezing**

The cross-phase wiring is broadly correct: P1 codebook defines the taxonomy, P2 classifies every paper with topic_tags (`PD-01..PD-10`) and methodology_tags (`SA-01..SA-11`), `shared/extracted_text/` and `shared/bridge/paper_id_bridge.csv` carry the paper text and ID mapping, and P3 quantitative consumes all of these through [scripts/run_extraction.py](p3_thematic_synthesis/quantitative/scripts/run_extraction.py). The quantum-advantage framework reads only from P3 quantitative extractions, which is the intended layering. **However**, three problems make the current extraction output unsuitable as a frozen artefact:

1. **Scope leak**: P3 quantitative never filters on `methodology_tags`. ~45 papers tagged `SA-01` (quantum-annealing-qubo) passed through, producing **74 experiments with `algorithm.family = quantum-annealing`, 31 with `algorithm.family = qubo`, and 69 with `hardware.type = quantum_annealer`** — i.e. **~9 % of the 1,957-experiment corpus is out-of-scope**. The schema, the step-2 prompt, and the step-4 validation prompt all still advertise annealing as a valid extraction target.
2. **Extraction-reliability evidence**: `temperature = 0.1` plus a four-paper A/B test cannot defend the extraction pipeline at PhD level. Variant-B changed `algorithm.family` from `hybrid` to `quantum-annealing` for the same paper section; baseline counts drifted 4 → 8 between variants. This must be fixed before the re-run.
3. **Structural extraction bugs**: QBSolv (a classical decomposer) is extracted as a separate experiment on [d18096ef8f4c](p3_thematic_synthesis/quantitative/output/ab_test/d18096ef8f4c_A.json), violating the prompt's own rule; `num_qubits` is `null` for all D-Wave extractions; one paper has `validation_passed=true` while carrying two schema errors.

Once the quantitative folder is fixed, re-run, and frozen, the quantum-advantage folder becomes the next work package. That folder is internally consistent and faithful to its source papers on threshold cross-reference, but it carries follow-on issues that only matter once the upstream corpus is clean (L4 routing gaps for PD-05/PD-08, orphan Dalzell thresholds, Rønnow-on-gate-based applicability, fixed classical-parallelism `S`).

---

## 2. Cross-phase connectivity — does P3 use P1 and P2 outputs?

### 2.1 What exists upstream

| Phase | Artefact | Where | Role downstream |
|---|---|---|---|
| P1 | [codebook.md](p1_framework_synthesis/s4_outputs/codebook.md) | `p1_framework_synthesis/s4_outputs/` | Authoritative source of PD-01..PD-10 (problem domains) and SA-01..SA-11 (solution approaches). SA-01 explicitly defined as quantum-annealing / D-Wave / QUBO / adiabatic. |
| P1 | [problem-space.md](p1_framework_synthesis/s3_taxonomy/problem-space.md), [solution-space.md](p1_framework_synthesis/s3_taxonomy/solution-space.md) | `s3_taxonomy/` | Taxonomy narratives; published into codebook. |
| P1 | [s1_extractions/*](p1_framework_synthesis/s1_extractions/) | 26 curated framework-paper extractions | Feeds codebook construction; not consumed by P3. |
| P2 | per-paper `*_extraction.json` | `p2_systematic_review/output/processed/` | For every paper: `source_type`, `topic_tags`, `methodology_tags`, `has_quantitative_results`, `quantum_advantage_claim`, plus metadata. 643 files. |
| P2 | per-paper `*.md` | same folder | Markdown summary with frontmatter. |
| shared | [unified_taxonomy.json](shared/config/unified_taxonomy.json) | `shared/config/` | Canonical ID ↔ label mapping (v2.0). `SA-01 = quantum-annealing-qubo` still listed. |
| shared | [paper_id_bridge.csv](shared/bridge/paper_id_bridge.csv) | `shared/bridge/` | 643 rows: slr_id ↔ doi ↔ zotero ↔ title ↔ source_type. |
| shared | [extracted_text/text/*.md](shared/extracted_text/text/) | 777 markdowns | Source text for P3 quantitative LLM input. |

### 2.2 How P3 quantitative connects

[scripts/run_extraction.py#L150-L205](p3_thematic_synthesis/quantitative/scripts/run_extraction.py#L150) reads:
- P2 outputs at `p2_systematic_review/output/processed/` → pulls `has_quantitative_results`, `topic_tags`, `methodology_tags`, `source_type`.
- `shared/extracted_text/text/` → supplies paper text to the LLM.
- [config/silo_metrics.json#L3](p3_thematic_synthesis/quantitative/config/silo_metrics.json#L3) — self-declared `_source: p1_framework_synthesis/s4_outputs/codebook.md` — supplies per-silo primary/secondary metric vocabularies to step-3 extraction.

**Filters applied at manifest time** ([run_extraction.py#L184-L186](p3_thematic_synthesis/quantitative/scripts/run_extraction.py#L184)):
- `has_quantitative_results == true`
- `source_type not in {survey, editorial, meta-analysis, book-chapter, commentary}`

**Filters NOT applied** (these are the leaks):
- No filter on `methodology_tags` → SA-01 (quantum-annealing-qubo) papers pass through.
- No filter on `hardware.type` at extraction time → D-Wave/annealer hardware is captured without gating.
- No filter on `algorithm.family` output → the LLM happily returns `quantum-annealing` / `qubo` values.

**Verdict**: P3 quantitative is **wired to P1 and P2 but under-uses them**. The taxonomy sidecar is read for silo routing but ignored for scope enforcement. P2 correctly tags 40+ papers as `SA-01`, P3 loads that tag, then silently drops it on the floor.

### 2.3 How P3 quantum_advantage connects

[_shared/extraction_loader.py#L12](p3_thematic_synthesis/quantum_advantage/_shared/extraction_loader.py#L12) reads only from `p3_thematic_synthesis/quantitative/output/extractions/*.json`. It does **not** re-read P2 classifications, P1 codebook, or the unified taxonomy. That is the intended layering — QA is a consumer of the quantitative output — but it also means the annealing leak from §2.2 propagates through untouched.

**Verdict**: correctly layered; inherits the scope problem from its upstream.

### 2.4 Annealing-leak quantification

| Signal | Count (experiments) | Sample file |
|---|---|---|
| `algorithm.family == "quantum-annealing"` | **74** (~40 papers) | [00c17032f4af.json#L89](p3_thematic_synthesis/quantitative/output/extractions/00c17032f4af.json#L89), [2c74be1a024b.json](p3_thematic_synthesis/quantitative/output/extractions/2c74be1a024b.json) |
| `algorithm.family == "qubo"` | **31** (~13 papers) | [296dd193c78f.json#L67](p3_thematic_synthesis/quantitative/output/extractions/296dd193c78f.json#L67), [2e35d78fa802.json](p3_thematic_synthesis/quantitative/output/extractions/2e35d78fa802.json) |
| `hardware.type == "quantum_annealer"` | **69** (~30 papers) | [0757b9aa9a3b.json](p3_thematic_synthesis/quantitative/output/extractions/0757b9aa9a3b.json), [73f3adac41d9.json](p3_thematic_synthesis/quantitative/output/extractions/73f3adac41d9.json) |
| Total unique out-of-scope experiments (de-duplicated) | **≈ 174 of 1,957** | |
| Total unique out-of-scope papers (de-duplicated) | **≈ 45 of 643** | |

This is ~9 % of the experiment-level corpus and ~7 % of the paper-level corpus. An examiner looking at the `portfolio-optimization` silo will see annealing dominate the verdict distribution unless this is fixed.

---

## 3. Quantitative folder — priorities for the re-run and freeze

These are the only changes needed to go from the current state to a frozen, PhD-defensible quantitative corpus. Everything below is **inside `p3_thematic_synthesis/quantitative/` and `shared/`**; quantum-advantage changes are Section 5.

### 3.1 Fix scope filter — **CRITICAL (Q-0)**

[scripts/run_extraction.py#L184-L186](p3_thematic_synthesis/quantitative/scripts/run_extraction.py#L184) currently:
```python
if not d.get("has_quantitative_results"): continue
if source_type in SKIP_SOURCE_TYPES: continue
```
Add immediately after:
```python
methodology_tags = d.get("methodology_tags", []) or []
if "quantum-annealing-qubo" in methodology_tags:
    continue  # Out-of-scope: thesis is gate-based only (P1 codebook SA-01)
# Defensive second-line filter on any raw tag drift
if any(t in methodology_tags for t in ("SA-01", "quantum-annealing", "annealing", "qubo", "d-wave")):
    continue
```

Also add a hard check on the actual extracted text if you want belt-and-braces: reject the manifest entry when the title or abstract contains "D-Wave" or "annealer" and `quantum-annealing-qubo` is missing from `methodology_tags` (i.e., P2 mis-classification recovery). This is optional.

### 3.2 Schema — **CRITICAL (Q-1)**

[config/benchmark_schema.json](p3_thematic_synthesis/quantitative/config/benchmark_schema.json):

- **`algorithm.family` enum (L131-L151)**: remove `"quantum-annealing"`, `"qubo"`. Keep `"other-gate-based"` and `"other"` as catch-alls.
- **`hardware.type` enum (L199)**: remove `"quantum_annealer"`.
- **`num_binary_variables` field (L129)**: either remove it entirely (it exists because of QUBO-on-annealer) or repurpose its description to *QUBO-on-gate-based* (QAOA/Grover-on-QUBO problems, where the variable count still matters for problem-size normalisation).
- **Add a top-level `scope` field** to `paper_metadata`:
  ```json
  "scope": { "type": "string", "enum": ["gate_based"], "description": "Thesis scope. Must be 'gate_based'." }
  ```
  This makes the scope assertion machine-visible and lets [validate_benchmarks.py](p3_thematic_synthesis/quantitative/scripts/validate_benchmarks.py) reject any regression.

### 3.3 Prompts — **CRITICAL (Q-2)**

[prompts/step2_experiments.txt](p3_thematic_synthesis/quantitative/prompts/step2_experiments.txt):
- **L26** — `algorithm.family` enum: drop `quantum-annealing`, `qubo`. Replace the "For QUBO/annealing papers: set num_qubits to the number of binary variables" instruction (L127) with *"For QAOA/Grover-on-QUBO problems on gate-based hardware, set `algorithm.family` to `qaoa` or `grover` and record the binary-variable count in `num_binary_variables`."*
- **L37** — encoding_method: keep `QUBO` as a problem-formulation tag but add an explicit gate-based-only note: *"A QUBO/Ising problem encoding is in scope only if the solver is gate-based (QAOA, Grover, amplitude-estimation, etc.)."*
- **L66** — `hardware.type` enum: drop `quantum_annealer`.
- **L67** — providers list: drop `D-Wave`.
- **At the top of the prompt**, add a 1-line scope banner: *"THESIS SCOPE: gate-based quantum computing only. If the paper's primary solver is a quantum annealer (D-Wave, adiabatic), set `has_quantitative_results=false` and stop."*

[prompts/benchmark_extraction.txt](p3_thematic_synthesis/quantitative/prompts/benchmark_extraction.txt) (legacy single-shot prompt — still referenced by ab_test but otherwise superseded): same edits as step2, OR move to `_legacy/` (see Q-8).

[prompts/step3_silo_results.txt](p3_thematic_synthesis/quantitative/prompts/step3_silo_results.txt) and [step4_validation.txt](p3_thematic_synthesis/quantitative/prompts/step4_validation.txt): add the same scope banner at the top. Step 4 should additionally include a self-check rule: *"If any experiment's `hardware.type` is absent from the allowed enum or `algorithm.family` is annealing-related, emit a validation error with `error_type = 'scope_violation'`."*

### 3.4 Validator — **MAJOR (Q-3)**

[scripts/validate_benchmarks.py](p3_thematic_synthesis/quantitative/scripts/validate_benchmarks.py):

1. **Block papers with schema errors from being written to `extractions/`**. Today, [5413b7728054.json](p3_thematic_synthesis/quantitative/output/extractions/5413b7728054.json) has 2 schema errors and `validation_passed=true`. Change the rule to `validation_passed = (len(validation_errors) == 0)` and drop the paper from the manifest if it fails.
2. **Add cross-field checks**:
   - `physical_qubits ≥ logical_qubits` when both present.
   - `circuit_depth_transpiled ≥ circuit_depth` when both present.
   - Reject `paper_metadata.year ∉ [2015, 2027]`.
   - Reject `hardware.type == "quantum_annealer"` (scope).
   - Reject `algorithm.family ∈ {"quantum-annealing", "qubo"}` (scope).
3. **Expand `_BOUNDED_METRICS`** beyond the 9 current entries: add `price_error ≥ 0`, `cvar_estimation_error ≥ 0`, `var_accuracy ∈ [0,1]`, `execution_time ≥ 0`. For any metric not in the whitelist, emit a *warning* (not an error) that it was not range-checked.
4. **Unit-vocabulary**: add a `_UNIT_VOCAB = {"seconds","ms","us","ns","shots","count","ratio","percent","unitless", null}` check on each `results[].unit`.
5. **Emit `scope_violation` errors** when Q-0 escapes: if the final extraction nonetheless contains annealing hardware or family, the validator catches it at the last mile.

### 3.5 Extraction config — **MAJOR (Q-4)**

[config/extraction_config.json](p3_thematic_synthesis/quantitative/config/extraction_config.json):

- **`temperature = 0.0`** for all extraction steps (L3). Non-zero temperature is the root cause of the A/B test `hybrid` ↔ `quantum-annealing` disagreement. Factual extraction must be deterministic.
- Add `"seed": 42` (or any fixed int) at the top level; pass through to the Azure OpenAI client in [run_extraction.py](p3_thematic_synthesis/quantitative/scripts/run_extraction.py) and [run_batch_api.py](p3_thematic_synthesis/quantitative/scripts/run_batch_api.py). Reproducibility is a common viva question.
- Pin every step's model in `step_models` explicitly (step 4 currently uses `gpt-5.3` — confirm that is the intended reasoning model).
- Add a `scope: "gate_based"` field so the config itself declares the thesis scope and `_bug_check.py` can verify prompts + schema match.

### 3.6 QBSolv / classical-as-experiment fix — **MAJOR (Q-5)**

[prompts/step2_experiments.txt](p3_thematic_synthesis/quantitative/prompts/step2_experiments.txt) already says "Classical baselines are NOT separate experiments" — the issue is the LLM ignores it for hybrid decomposers. Tighten:

- Add an explicit deny-list block:
  *"The following software artefacts are ALWAYS classical, never quantum experiments, even when they appear in a quantum paper's experimental section: QBSolv, simulated annealing, CPLEX, Gurobi, MOEA/D, NSGA-II, classical SVM, random forest, logistic regression. If the paper's **only** solver is in this list, set `has_quantitative_results=false`."*
- Step 4 validator: if `algorithm.family ∈ {"qubo","other","classical-simulation"}` and `hardware.type` starts with `"simulator_"` or is `"not_specified"`, flag the experiment as `extraction_error: classical_masquerading_as_quantum`.

### 3.7 A/B test — **MAJOR (Q-6)**

[scripts/ab_test.py](p3_thematic_synthesis/quantitative/scripts/ab_test.py) currently runs 4 papers × 3 variants. Expand to:
- **n ≥ 30 papers**, stratified random by silo (PD-01..PD-10 excluding PD-05 and PD-08 if you prefer, or include all 10 and report per-silo agreement).
- Hand-annotate ground truth for three fields: `algorithm.family`, `classical_baselines[]` count, `speedup_claims[].type`.
- Report inter-variant Cohen's κ per field and 95 % CI. This is the evidence an examiner will ask for.
- Keep variant C (hybrid: cheap for extraction, reasoning model for validation) as the primary production configuration; the current A/B already shows it is cost-effective.

### 3.8 Provenance, aggregation, housekeeping — **MINOR (Q-7 … Q-11)**

- **Q-7** Make `experiment.provenance` **required** in [benchmark_schema.json](p3_thematic_synthesis/quantitative/config/benchmark_schema.json). Today ~60 % of the corpus is classified `untagged` by [scripts/audit_provenance.py](p3_thematic_synthesis/quantitative/scripts/audit_provenance.py). After the re-run, enforce this.
- **Q-8** Move [scripts/extract_benchmarks.py](p3_thematic_synthesis/quantitative/scripts/extract_benchmarks.py) and [prompts/benchmark_extraction.txt](p3_thematic_synthesis/quantitative/prompts/benchmark_extraction.txt) into `_legacy/`. The canonical pipeline is `run_extraction.py` (per its own header). Keep only if still referenced by `ab_test.py`.
- **Q-9** Run [scripts/_bug_check.py](p3_thematic_synthesis/quantitative/scripts/_bug_check.py) before the re-run and after each config change. Wire it into a pre-commit hook.
- **Q-10** Document the 777 → 643 drop: create `shared/bridge/excluded_papers.csv` with columns `slr_id, filename, exclusion_reason ∈ {no_quantitative_results, survey, editorial, book_chapter, meta_analysis, commentary, scope_out, duplicate}, date_excluded`. Generate from P2 + scope filter.
- **Q-11** Embed `extraction_schema_version`, `prompt_version_hash`, `run_timestamp` into every extraction JSON's `extraction_metadata` so the frozen corpus is self-identifying.

### 3.9 Recommended re-run order

1. Apply Q-1 (schema), Q-2 (prompts), Q-3 (validator), Q-4 (temperature=0 + seed), Q-5 (classical deny-list). Commit.
2. Run Q-9 (`_bug_check.py`) — must pass.
3. Run Q-6 on ≥ 30 stratified papers. Collect ground truth. Publish κ.
4. Apply Q-0 (scope filter) + Q-10 (excluded_papers.csv) + Q-11 (metadata stamps).
5. Re-run the full corpus. Spot-check 20 random extractions for `scope_violation` errors.
6. Run [scripts/audit_provenance.py](p3_thematic_synthesis/quantitative/scripts/audit_provenance.py); confirm `untagged` drops below 10 %.
7. Run [scripts/aggregate_benchmarks.py](p3_thematic_synthesis/quantitative/scripts/aggregate_benchmarks.py); commit `output/tables/`.
8. **Freeze.** Tag the commit `p3-quant-freeze-vN`. Record sample counts in `p3_thematic_synthesis/quantitative/README.md`.

---

## 4. Strengths worth defending

- Verdict-construction contract is clean and single-sourced. [_shared/verdict.py#L36](p3_thematic_synthesis/quantum_advantage/_shared/verdict.py#L36) + [aggregation.py#L18](p3_thematic_synthesis/quantum_advantage/_shared/aggregation.py#L18) — every active assessor uses them, no ad-hoc verdict dicts.
- Threshold cross-references match the source papers on every sampled numerical value: Hoefler Table 2 (L20, L23-25), Babbush Eq. (5), Stilck França Lemma 1 ($pL = 1$), Chakrabarti Table 1 (T-count 1.2×10¹⁰, T-depth 5.4×10⁷, 8 k logical qubits).
- Bridge provenance: [_shared/extraction_loader.py#L211-L216](p3_thematic_synthesis/quantum_advantage/_shared/extraction_loader.py#L211) logs every source→target mapping into `provenance.bridged_fields`.
- Derived-field provenance: every enriched value in [derived_fields.json](p3_thematic_synthesis/quantum_advantage/derived_fields/enriched/derived_fields.json) carries a `_derived=true` flag and a `_formula`/`_citation`.
- Consensus arithmetic: 921+557+205+181+51+42 = 1,957 = `total_experiments` in [consensus_summary.json](p3_thematic_synthesis/quantum_advantage/combined/output/consensus_summary.json).
- Full end-to-end lineage trace ran cleanly for paper `0030bd185e0d`: [paper_id_bridge.csv#L2](shared/bridge/paper_id_bridge.csv#L2) → [extractions/0030bd185e0d.json](p3_thematic_synthesis/quantitative/output/extractions/0030bd185e0d.json) → 7 framework `results/*.json` → [triangulation_matrix.json](p3_thematic_synthesis/quantum_advantage/combined/output/triangulation_matrix.json) row 1.
- L5 veto is cap-only-downgrade as designed ([triangulate.py#L232-L259](p3_thematic_synthesis/quantum_advantage/combined/triangulate.py#L232)); observed application count is 1 of 1,957, matching Stilck França's own "unlikely, not impossible" wording.
- Taxonomy vocabulary is tight across P2 prompts and P3 schema — [step6_synthesis.txt#L24-L63](p2_systematic_review/s2_classification/prompts/step6_synthesis.txt#L24) quotes the exact 10 PD and 11 SA codes verbatim from [unified_taxonomy.json](shared/config/unified_taxonomy.json).

---

## 5. Quantum-advantage folder — after the quantitative freeze

These are the QA-side fixes. They should **not** be started until the quantitative corpus is frozen, because they depend on the re-extracted experiment list.

### 5.1 Critical

- **QA-0 — Scope filter at load time.** Even with upstream scope-filtering, add a belt-and-braces guard in [_shared/extraction_loader.py](p3_thematic_synthesis/quantum_advantage/_shared/extraction_loader.py): skip any experiment where `algorithm.family ∈ {"quantum-annealing","qubo"}` or `hardware.type == "quantum_annealer"`. This protects the framework from any future regression in the quantitative output.
- **QA-1 — Rønnow applicability gate.** Rønnow 2014 is a quantum-annealing benchmark-validity framework. In a gate-based-only thesis, applying its full rubric to QAOA / Grover / AE papers is a stretch. Add an algorithm-family gate in [assess_ronnow.py#L175](p3_thematic_synthesis/quantum_advantage/ronnow/assess_ronnow.py#L175): return `not_applicable` unless the paper explicitly frames itself as a benchmark-validity study (e.g., claims "quantum speedup" against a classical baseline with scaling plots). Alternative: drop Rønnow entirely and promote Hoefler+Babbush alone as L1+L2, making the triangulation a 3-core + 1-veto design.
- **QA-2 — Stilck França scope note.** [stilck_franca_thresholds.json#L4](p3_thematic_synthesis/quantum_advantage/stilck_franca_2021/stilck_franca_thresholds.json#L4) explicitly mentions "QAOA, VQE, quantum annealing" as applicable families. Remove `quantum-annealing` / `quantum_annealing` from [L25-L50](p3_thematic_synthesis/quantum_advantage/stilck_franca_2021/stilck_franca_thresholds.json#L25). Add a `_scope_note`: *"Applied to NISQ variational gate-based algorithms only (QAOA/VQE/QNN/QGAN/QCBM/hybrid). Annealing papers are pre-filtered upstream."*

### 5.2 Major

- **QA-3 — L4 routing documentation.** [combined/triangulate.py#L87-L97](p3_thematic_synthesis/quantum_advantage/combined/triangulate.py#L87): PD-05 (fraud-detection) and PD-08 (cryptography-security) are in neither `_CHAKRABARTI_SILOS` nor `_DALZELL_SILOS`. Current fallback returns `not_applicable`. Either (a) add a `scope_notes` block to [quantum_advantage/README.md](p3_thematic_synthesis/quantum_advantage/README.md) formally declaring these silos out-of-scope for L4, or (b) introduce a new L4 assessor for cryptography-security. PD-08 should probably be excluded from the finance thesis altogether since Gidney-Ekerå 2025 is cryptanalysis.
- **QA-4 — Dalzell orphan thresholds.** [dalzell_thresholds.json#L63-L155](p3_thematic_synthesis/quantum_advantage/dalzell_2023/dalzell_thresholds.json#L63) defines per-silo MSA numbers for `risk-management`, `insurance-actuarial`, `simulation-monte-carlo` — but the router sends those silos to Chakrabarti, so those thresholds are never reached. Either prune them or make Dalzell a fallback when Chakrabarti returns `not_applicable`. Also prune the `cryptography-security` RSA-2048 block (out of finance scope).
- **QA-5 — Dalzell `portfolio-optimization: is_infeasible: true`.** [dalzell_thresholds.json#L101-L110](p3_thematic_synthesis/quantum_advantage/dalzell_2023/dalzell_thresholds.json#L101) blanket-fails the entire silo on the basis of QIPM. Algorithm-gate it: `qaoa` / `grover` / `amplitude-estimation` get their own resource thresholds; only `qipm` is flagged `is_infeasible`.
- **QA-6 — Classical parallelism `S` per-problem.** [babbush_thresholds.json#L43](p3_thematic_synthesis/quantum_advantage/babbush_2021/babbush_thresholds.json#L43) locks `S=1000`; Hoefler assumes `S=1`. Add `classical_parallelism_S` per algorithm or per problem-class (Monte Carlo ≈ 10⁶, grid search ≈ 10³, inherently serial ≈ 1). This is the single largest driver of the 47 % `unanimous_fails` rate in [consensus_summary.json#L18](p3_thematic_synthesis/quantum_advantage/combined/output/consensus_summary.json#L18).
- **QA-7 — `make_verdict()` runtime checks.** [_shared/verdict.py#L54-L58](p3_thematic_synthesis/quantum_advantage/_shared/verdict.py#L54) validates only `verdict`/`confidence`/`framework`. Add non-empty-string checks on `paper_id`, `experiment_id`, `silo`, `algorithm_family`, `reasoning`. Optionally validate `silo` against the 10-PD whitelist.
- **QA-8 — `speedup.py` source-provenance flag.** Change [_shared/speedup.py](p3_thematic_synthesis/quantum_advantage/_shared/speedup.py) `infer_speedup_order()` to return `(order, k, source, reasoning)` with `source ∈ {paper_reported, derived, family_fallback}`, and propagate to `framework_specific.speedup_source` in every assessor. Today assessors cannot tell whether the speedup order is paper-reported or a family default.
- **QA-9 — `algorithm_complexity.json` coverage gap.** [consensus_summary.json `by_algorithm`](p3_thematic_synthesis/quantum_advantage/combined/output/consensus_summary.json) lists 17 algorithm families; [algorithm_complexity.json](p3_thematic_synthesis/quantum_advantage/derived_fields/algorithm_complexity.json) keys 12. Missing: `error-mitigation`, `qft-phase-estimation`, `quantum-cryptography`, `variational-nisq`, `other`, `other-gate-based`. 328 of 1,957 experiments get no complexity enrichment. Add at minimum `qft-phase-estimation` (exponential via QPE) and a `none_proven` default for the `other*` buckets.
- **QA-10 — Stilck França noise inference.** [assess_stilck_franca.py#L52-L91](p3_thematic_synthesis/quantum_advantage/stilck_franca_2021/assess_stilck_franca.py#L52) infers gate-error rate from hardware-name substring matching and depth from `num_layers × 2`. Replace with paper-reported values; if not available, return `insufficient_data` rather than a pessimistic default.
- **QA-11 — Beverland modelling depth.** [assess_beverland.py#L111-L114](p3_thematic_synthesis/quantum_advantage/beverland_2022/assess_beverland.py#L111) reduces the full Beverland stack to Babbush Eq. (5) applied six times. At minimum, add logical-qubit count per scenario and T-factory overhead as second-order constraints.

### 5.3 Minor

- **QA-12** `build_output_payload()` should embed `timestamp`, `schema_version`, `run_id` ([_shared/aggregation.py#L18](p3_thematic_synthesis/quantum_advantage/_shared/aggregation.py#L18)).
- **QA-13** Wrap [_shared/extraction_loader.py](p3_thematic_synthesis/quantum_advantage/_shared/extraction_loader.py) reads in try/except so one malformed JSON doesn't halt the whole batch.
- **QA-14** Add a threshold-indexing summary table in [quantum_advantage/README.md](p3_thematic_synthesis/quantum_advantage/README.md): Rønnow (family-blind), Hoefler (family/speedup-order-indexed), Babbush (speedup-order-indexed), Beverland (scenario-indexed), Chakrabarti (application-indexed), Dalzell (silo-indexed), Stilck França (family-gated). Each assessor has a different evaluation granularity — worth one paragraph per assessor.
- **QA-15** Integrate [chakrabarti_qaoa_2025.md](p3_thematic_synthesis/quantum_advantage/chakrabarti_2021/chakrabarti_qaoa_2025.md) into [assess_chakrabarti.py](p3_thematic_synthesis/quantum_advantage/chakrabarti_2021/assess_chakrabarti.py) so QAOA-based pricing papers are evaluated against the 2025 update, not only the 2021 QAE Table 1.

### 5.4 Scope clean-up for QA (matches Q-1/Q-2)

When the quantitative schema and prompts drop `quantum-annealing` and `qubo`, the QA side needs matching drops:
- [hoefler_thresholds.json#L55-L58](p3_thematic_synthesis/quantum_advantage/hoefler_assessment/hoefler_thresholds.json#L55) — remove `quantum-annealing` / `qubo` entries.
- [babbush_thresholds.json#L128-L153](p3_thematic_synthesis/quantum_advantage/babbush_2021/babbush_thresholds.json#L128) — remove `quantum_simulated_annealing` / `quantum_annealing`.
- [ronnow_thresholds.json](p3_thematic_synthesis/quantum_advantage/ronnow/ronnow_thresholds.json) — annealing-time and fixed-time keywords stay (they're Rønnow's paper content), but the assessor should refuse to apply them outside `{qaoa, grover, amplitude-estimation}` (QA-1).
- [algorithm_complexity.json](p3_thematic_synthesis/quantum_advantage/derived_fields/algorithm_complexity.json) — remove the `"quantum-annealing"` entry (L68-80); `"qubo"` is an encoding and can stay as such, repurposed for gate-based QUBO solvers.
- [compute_derived_fields.py#L109](p3_thematic_synthesis/quantum_advantage/derived_fields/compute_derived_fields.py#L109) — remove `"quantum-annealing"` from the family tuple.
- [unified_taxonomy.json](shared/config/unified_taxonomy.json) — keep SA-01 defined (P1 codebook still describes it historically) but **mark it `out_of_scope: true`** in the methodology_tags block. This lets downstream filtering remain purely tag-based.

---

## 6. Cross-phase inconsistencies (what an examiner will probe)

### 6.1 Silo × L4 coverage matrix

| PD | silo | Chakrabarti | Dalzell | Dalzell threshold defined? | L4 outcome |
|---|---|---|---|---|---|
| 01 | portfolio-optimization | — | ✓ | ✓ `is_infeasible` | Dalzell → fails (QA-5 fix) |
| 02 | derivative-pricing | ✓ | — | ✓ | Chakrabarti |
| 03 | risk-management | ✓ | — | ✓ **(orphan)** | Chakrabarti |
| 04 | quantum-ml-finance | — | ✓ | ✓ null MSA | Dalzell → not_applicable |
| **05** | **fraud-detection** | — | — | ✓ | **fallback → not_applicable** |
| 06 | trading-execution | — | ✓ | ✓ | Dalzell |
| 07 | credit-lending | — | ✓ | ✓ | Dalzell |
| **08** | **cryptography-security** | — | — | ✓ RSA-2048 | **fallback → not_applicable** (recommend remove silo entirely from finance scope) |
| 09 | simulation-monte-carlo | ✓ | — | ✓ **(orphan)** | Chakrabarti |
| 10 | insurance-actuarial | ✓ | — | ✓ **(orphan)** | Chakrabarti |

### 6.2 Algorithm-family many-to-one

The quantitative schema declares 15 families, `consensus_summary.json` reports 17 (including 5 that are not in the schema enum), and `algorithm_complexity.json` keys 12. See QA-9. After Q-1 drops `quantum-annealing` and `qubo` from the schema, the alignment becomes: 13 schema families, 12 complexity entries, ≤15 consensus values. Document the many-to-one mapping in [shared/config/README.md](shared/config/README.md).

### 6.3 Paper-ID lineage

| Stage | Count | Source |
|---|---|---|
| Source markdowns | 777 | [shared/extracted_text/text/*.md](shared/extracted_text/text/) |
| Bridge-mapped | 643 (gap 134, undocumented — Q-10) | [shared/bridge/paper_id_bridge.csv](shared/bridge/paper_id_bridge.csv) |
| Quantitative extractions (current) | 643 | [p3/quantitative/output/extractions/](p3_thematic_synthesis/quantitative/output/extractions/) |
| Experiments (current) | 1,957 | sum of `experiments[]` |
| Out-of-scope experiments (annealing) | 174 (≈ 9 %) | §2.4 |
| Expected quantitative extractions **post-freeze** | ≈ 598 papers, ≈ 1,783 experiments | 643 − 45 annealing papers; 1,957 − 174 annealing experiments (subject to Q-6 re-run) |

### 6.4 Taxonomy vocabulary

P2 prompts quote `unified_taxonomy.json` verbatim — no drift. The only vocabulary inconsistency is that SA-01 (`quantum-annealing-qubo`) is used as a filter key throughout but has no `out_of_scope` marker; adding one (§5.4) closes the loop.

---

## 7. Examiner-ready defenses

Paraphrased challenges from the brief's §5, updated after the scope clarification.

**§5.1 LLM extraction reliability.**
*Defense (post-freeze):* extraction runs at `temperature = 0` with a fixed seed. A/B test on n ≥ 30 stratified papers reports inter-variant Cohen's κ per field. Two-layer validation (Draft 2020-12 schema + semantic + cross-field + scope) blocks malformed papers. Every extraction carries `extraction_schema_version`, `prompt_version_hash`, `run_timestamp`, `quality_score`, `validation_errors`, and per-field `data_source`. *Concession:* the current (pre-freeze) A/B at n = 4 is under-powered; the thesis reports the re-run numbers.

**§5.2 Why these seven frameworks and this layering?**
*Defense:* L1 Rønnow (gated to annealing-adjacent benchmark-validity claims post-QA-1) — without a legitimate classical baseline, everything downstream is meaningless. L2 Hoefler + Babbush — same question, two assumptions (single-chip vs parallel-classical); conjunctive (min-score) merge. L3 Beverland — resource feasibility in full-stack form. L4 Chakrabarti ∨ Dalzell — domain realism. L5 Stilck França — unconditional noise bound as a veto, never an upgrade. Reordering does not change conclusions (L2 merge is commutative; L5 caps the consensus label), but the interpretive narrative degrades.

**§5.3 L2 min-score merge.**
*Defense:* Hoefler and Babbush address the same question under different assumptions. Taking the minimum is conjunctive: both must agree practical. Mean-score rewards borderline-viable-under-one-assumption. *Concession:* this contributes to the 47 % `unanimous_fails` rate; QA-6 (per-problem `S`) mitigates.

**§5.4 L4 silo routing gap (PD-05, PD-08).**
*Defense:* neither source paper has end-to-end numbers for fraud-detection or cryptography-security, so synthesising an L4 verdict would be misapplying an adjacent framework. *Concession:* currently undocumented; QA-3 adds a `scope_notes` README. PD-08 is out of finance-thesis scope and should be excluded from the corpus.

**§5.5 L5 veto scope.**
*Defense (post-QA-2):* L5 applies only to NISQ gate-based variational algorithms on non-noiseless hardware. Observed veto count 1 of 1,957 in the historical audited corpus matches Stilck França's "unlikely, not impossible" framing. *Concession:* hardware-name substring matching for noise is brittle (QA-10).

**§5.6 Rønnow applicability to gate-based algorithms.**
*Defense (post-QA-1):* Rønnow's *taxonomy* (provable/strong/potential/limited/no speedup) is algorithm-agnostic; it applies to any paper claiming quantum advantage. His *experimental pitfalls* (annealing-time tuning, fixed-time artifacts) do not apply to gate-based algorithms. Assessor now returns `not_applicable` outside `{qaoa, grover, amplitude-estimation}` unless the paper explicitly frames itself as a benchmark-validity study. *Alternative (stronger defense):* drop Rønnow as L1 entirely and recast the framework as 3-core + 1-veto (Hoefler+Babbush / Beverland / Chakrabarti∨Dalzell / Stilck França). This will be discussed in the limitations chapter.

**§5.7 Threshold currency.**
*Defense:* Hoefler Table 1 (2023) assumes ~10 k logical qubits at 10 µs gate time — roughly the 2025-2027 IBM/Google/Microsoft roadmap. Babbush Eq. (5) is algebraic. Chakrabarti 2021 already re-parameterised down 7×; [chakrabarti_qaoa_2025.md](p3_thematic_synthesis/quantum_advantage/chakrabarti_2021/chakrabarti_qaoa_2025.md) captures the 2025 QAOA update (to be integrated, QA-15). Dalzell 2023 MSA numbers are < 3 years old. Stilck França's bound is hardware-generation-independent.

**§5.8 Derived-field fallback accuracy.**
*Defense (post-QA-8):* `speedup.py` returns a `source ∈ {paper_reported, derived, family_fallback}` flag; every downstream verdict records which level was used. Enrichment coverage is `1,629 / 1,957 = 83.2 %`; QA-9 closes most of the remaining gap.

**§5.9 Selection bias — the 134 excluded papers.**
*Defense (post-Q-10):* `shared/bridge/excluded_papers.csv` documents every exclusion with a reason code (no-experiments / pure-theory / duplicate / OCR-fail / survey / out-of-scope). The exclusions are uniformly distributed across PD-01..PD-10 (to be verified in aggregate stats). Plus the ≈ 45 scope exclusions from Q-0.

**§5.10 Consensus labels with n ≥ 3 unanimity.**
*Defense:* with 4 core layers (L1–L4), the typical experiment has 4 scored layers; `n ≥ 3` allows one dissent or `not_applicable` while still permitting unanimous labelling. Below `n < 3`, labels degrade to `low_coverage_*`. *Concession:* the choice is soft; an appendix sensitivity analysis reruns with `n ≥ 2` and `n ≥ 4` will accompany the thesis.

---

## 8. Priority summary

| Tier | ID | What | Where | Why |
|---|---|---|---|---|
| **Freeze blockers (quantitative)** | Q-0 | Add `methodology_tags` scope filter | [run_extraction.py#L184](p3_thematic_synthesis/quantitative/scripts/run_extraction.py#L184) | Removes 45 annealing papers, 174 experiments. |
| | Q-1 | Drop annealing from schema enums; add `scope` field | [benchmark_schema.json](p3_thematic_synthesis/quantitative/config/benchmark_schema.json) | Schema must forbid what the thesis forbids. |
| | Q-2 | Drop annealing from prompt enums; add scope banner + "For QAOA/Grover-on-QUBO" instruction | [step2_experiments.txt](p3_thematic_synthesis/quantitative/prompts/step2_experiments.txt), [step3_silo_results.txt](p3_thematic_synthesis/quantitative/prompts/step3_silo_results.txt), [step4_validation.txt](p3_thematic_synthesis/quantitative/prompts/step4_validation.txt) | LLM must not elicit annealing data. |
| | Q-3 | Block schema-error papers; cross-field & scope checks; expand `_BOUNDED_METRICS`; unit vocabulary | [validate_benchmarks.py](p3_thematic_synthesis/quantitative/scripts/validate_benchmarks.py) | Last-mile scope and consistency enforcement. |
| | Q-4 | `temperature = 0`, fixed seed, pinned step models | [extraction_config.json](p3_thematic_synthesis/quantitative/config/extraction_config.json) | Reproducibility. |
| | Q-5 | Classical-solver deny-list; `classical_masquerading_as_quantum` flag | [step2_experiments.txt](p3_thematic_synthesis/quantitative/prompts/step2_experiments.txt), [step4_validation.txt](p3_thematic_synthesis/quantitative/prompts/step4_validation.txt) | Stops QBSolv-as-experiment. |
| | Q-6 | n ≥ 30 A/B with hand-annotated κ | [ab_test.py](p3_thematic_synthesis/quantitative/scripts/ab_test.py) | Extraction-reliability evidence. |
| **Quantitative polish** | Q-7 | Make `provenance` required | [benchmark_schema.json](p3_thematic_synthesis/quantitative/config/benchmark_schema.json) | Examiner-relevant after re-run. |
| | Q-8 | Move `extract_benchmarks.py` + `benchmark_extraction.txt` to `_legacy/` | [scripts/](p3_thematic_synthesis/quantitative/scripts/), [prompts/](p3_thematic_synthesis/quantitative/prompts/) | Dead code removal. |
| | Q-9 | Wire `_bug_check.py` into CI / pre-commit | [_bug_check.py](p3_thematic_synthesis/quantitative/scripts/_bug_check.py) | Config ↔ prompt ↔ schema consistency. |
| | Q-10 | `excluded_papers.csv` with reason codes | `shared/bridge/excluded_papers.csv` | Closes selection-bias challenge. |
| | Q-11 | `extraction_schema_version`, `prompt_version_hash`, `run_timestamp` in every JSON | [run_extraction.py](p3_thematic_synthesis/quantitative/scripts/run_extraction.py) | Freeze-identifiable. |
| **Quantum-advantage (after freeze)** | QA-0..QA-2 | Scope filter at load; Rønnow family gate; Stilck scope note | `_shared/extraction_loader.py`, `ronnow/`, `stilck_franca_2021/` | Scope rigour. |
| | QA-3..QA-6 | L4 docs; Dalzell thresholds pruned/wired; portfolio-opt algorithm gating; per-problem `S` | `combined/triangulate.py`, `dalzell_2023/`, `babbush_2021/`, `hoefler_assessment/` | Largest verdict bias drivers. |
| | QA-7..QA-11 | `make_verdict()` checks; speedup provenance; complexity-enum coverage; Stilck noise; Beverland depth | `_shared/`, assessors, `derived_fields/` | Correctness polish. |
| | QA-12..QA-15 | Payload metadata; loader robustness; README threshold-indexing table; Chakrabarti 2025 integration | `_shared/aggregation.py`, README, `chakrabarti_2021/` | Minor. |
| | QA-scope | Drop annealing from assessor thresholds + complexity; mark SA-01 `out_of_scope: true` | §5.4 | Match QA to the frozen quantitative scope. |

---

### Appendix — evidence index

- Quantitative pipeline: [benchmark_schema.json](p3_thematic_synthesis/quantitative/config/benchmark_schema.json), [extraction_config.json](p3_thematic_synthesis/quantitative/config/extraction_config.json), [silo_metrics.json](p3_thematic_synthesis/quantitative/config/silo_metrics.json), [validate_benchmarks.py](p3_thematic_synthesis/quantitative/scripts/validate_benchmarks.py), [run_extraction.py](p3_thematic_synthesis/quantitative/scripts/run_extraction.py), [ab_test_results.json](p3_thematic_synthesis/quantitative/output/ab_test/ab_test_results.json)
- Shared QA infra: [verdict.py](p3_thematic_synthesis/quantum_advantage/_shared/verdict.py), [extraction_loader.py](p3_thematic_synthesis/quantum_advantage/_shared/extraction_loader.py), [speedup.py](p3_thematic_synthesis/quantum_advantage/_shared/speedup.py), [aggregation.py](p3_thematic_synthesis/quantum_advantage/_shared/aggregation.py), [common_verdict_schema.json](p3_thematic_synthesis/quantum_advantage/_shared/common_verdict_schema.json)
- Triangulation: [triangulate.py](p3_thematic_synthesis/quantum_advantage/combined/triangulate.py), [triangulation_matrix.json](p3_thematic_synthesis/quantum_advantage/combined/output/triangulation_matrix.json), [consensus_summary.json](p3_thematic_synthesis/quantum_advantage/combined/output/consensus_summary.json), [disagreement_cases.json](p3_thematic_synthesis/quantum_advantage/combined/output/disagreement_cases.json)
- Cross-phase: [unified_taxonomy.json](shared/config/unified_taxonomy.json), [paper_id_bridge.csv](shared/bridge/paper_id_bridge.csv), [p1 codebook.md](p1_framework_synthesis/s4_outputs/codebook.md), [p2 step6_synthesis.txt](p2_systematic_review/s2_classification/prompts/step6_synthesis.txt), P2 processed extractions at `p2_systematic_review/output/processed/`
