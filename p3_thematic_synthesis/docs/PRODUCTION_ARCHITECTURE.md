# Thematic Pipeline — Production Architecture

> **Status note (2026-05-10): historical design-time architecture document (2026-04-19).** Retained as provenance for the Step 3.5 design rationale; not the current authority. Current truth: [../FREEZE.md](../FREEZE.md), [../P3_AUDIT_STATUS.md](../P3_AUDIT_STATUS.md), and [../../docs/PROJECT_STATE.yaml](../../docs/PROJECT_STATE.yaml). This document describes the high-volume A1/A2/L3 production architecture; it does not override the canonical within-paper contract **A1 -> L1 -> A2 -> L2 -> L3 -> A3 -> R1** or the freeze disclosure that A3 was deferred and R1 was post-freeze validation.

> Design decisions for the Phase 3 Step 3.5 production pipeline.
> Records the rationale behind each choice for methodology defence.
>
> Date: 2026-04-19
> Status: Approved — ready for implementation after pilot completion

---

## 1. Processing Architecture: Central + Silo Overlay

### Decision

Papers are processed in two stages:

1. **Central A1/A2/L3** — one run per unique paper_id (661 papers), silo-blind
2. **Silo overlay** — for multi-silo papers only (371 papers, 658 overlay calls), adds silo-specific interpretive lens

### Rationale

- **Methodological**: Thomas & Harden (2008) requires coding "within each silo." Central-only coding would produce global codes reused across silos — an examiner could challenge this as silo-sorting, not within-silo analysis. The overlay step restores the silo-specific interpretive act.
- **Practical**: Pure per-silo processing would duplicate 658 A1/A2/L3 calls (papers appear in avg 2 silos). Central + overlay saves ~33% of LLM calls.
- **Quality reviewed by**: methodology-guard, rubber-duck (2026-04-19). Rubber-duck flagged central-only as "blocking methodology risk." Overlay compromise was approved.

### Paper distribution

| Category | Papers | LLM calls |
|----------|--------|-----------|
| Single-silo (1 silo only) | ~290 | ~290 × 3 = 870 |
| Multi-silo (2+ silos) | ~371 | ~371 × 3 + ~648 overlays = ~1,761 |
| **Total** | **661** | **~2,631** |
| Excluded (corrupted extraction) | 3 | 0 |

### What each stage produces

**Central (per paper)**:
- `papers/<paper_id>.jsonl` — A1 inductive codes (silo-blind)
- `papers/<paper_id>.json` — A2 analytical memo (silo-blind)
- `papers/<paper_id>_l3.json` — L3 adversarial check

**Silo overlay (per paper × silo)**:
- `<silo>/memos/<paper_id>_overlay.json` — silo-specific re-reading of codes through the silo lens

**Fan-out (no LLM calls)**:
- Copies/indexes central codes + overlay memo into silo directories
- Creates projection manifest per silo for audit trail

---

## 2. Parallelisation: Worker-Based Batching

### Decision

Papers are split into N batches (configurable via `--workers`, default 8). Each worker processes a deterministic subset of papers. No hardcoded batch count.

### Rationale

- **API limits are not the bottleneck**: gpt-5.1 allows 4M tokens/min and 40K requests/min. Even 100 parallel streams won't hit the limit.
- **API latency is the bottleneck**: each call takes 60-90s to return. Parallelism reduces wall-clock time linearly.
- **Local compute is negligible**: each stream uses ~50 MB RAM, trivial CPU (HTTP client + JSON parsing). 20 streams = ~1 GB RAM.
- **Debuggability**: 8-16 streams is the practical sweet spot. Higher parallelism makes error diagnosis harder.

### Batch assignment

Deterministic partitioning: papers sorted by paper_id, assigned to batch `hash(paper_id) % N`. This ensures:
- Same paper always goes to same batch (no duplicates)
- Rerunning with same N produces same assignment
- Adding a paper doesn't reshuffle existing assignments

### Rate limits (for reference)

| Model | Tokens/min | Requests/min | Max safe streams |
|-------|-----------|-------------|-----------------|
| gpt-5.4-mini | 2,000,000 | 2,000 | ~125 |
| gpt-5.1 | 4,000,000 | 40,000 | ~250 |

### Estimated production times

| Workers | gpt-5.4-mini | gpt-5.1 |
|---------|-------------|---------|
| 4 | ~11 hours | ~12 hours |
| 8 | ~5.5 hours | ~6 hours |
| 16 | ~3 hours | ~4 hours |

---

## 3. Model Selection

### Decision (finalized 2026-04-22)

**Hybrid configuration** — different models for different pipeline stages:

| Stage | Model | Prompt | Rationale |
|-------|-------|--------|-----------|
| A1 (open coding) | gpt-5.4-mini | v2 | 97.4% L1, 0 hallucinations, 0 prompt leakage, 4.0/5.0 quality (Opus 4.6 assessment) |
| A2 (memo compression) | gpt-5.1 | v2 | Wins 8/10 papers on content depth vs mini A2; 31% fewer L3 problems |
| L3 (adversarial check) | gpt-5.1 | v2 | Audit sample only (113 papers, 10%/silo). L3 is a review tool, not filter (flags 93-100% structurally) |
| Silo overlays | gpt-5.4-mini | v2 | Filtering/selection task on pre-synthesised input; mini sufficient |
| B1/B2/A3/C1 (synthesis) | Claude Opus 4.6 | v2 | Isolated agent mode; strongest reasoning for interpretive tasks. See §8 |

### Evidence

- **11 pilot iterations** (iter_01–iter_10 + iter_11 partial) on trading_execution (44 papers)
- **Deep A1 quality assessment** (Claude Opus 4.6, 10 papers cross-referenced against source text):
  - Mini: coverage 4.0, precision 4.5, quote quality 4.4, overall 4.0/5.0
  - GPT-5.1: coverage 4.8, precision 3.9, quote quality 3.8, overall 3.9/5.0
  - Mini wins on precision (zero hallucinations); 5.1 wins on coverage but has prompt leakage (6/10 papers)
- **comparison_01** (mini v2 vs gpt-5.1 v1): researcher-reviewed with notes
- **comparison_02** (mini A2 vs gpt-5.1 A2 hybrid): gpt-5.1 A2 confirmed superior for memo synthesis
- **v4 prompt experiment** (2026-04-22): enhanced coverage checklist tested on 5 papers, then validated in pipeline (14/44). No meaningful improvement over v2. Stopped.

### Key finding from pilot

gpt-5.1 is a **reasoning model** that consumes tokens for internal thinking before producing output. With `max_tokens=8000`, all tokens were used for reasoning (0 for content). Fix: `max_tokens=32000` for A1, `16000` for A2/L3.

### Temperature

- gpt-5.1: temperature parameter ignored (reasoning model)
- gpt-5.4-mini: temperature=0.0 for faithful extraction

---

## 4. Multi-Silo Paper Handling

### Decision

One core A1/A2 run per paper (central, silo-blind). Multi-silo papers get additional silo-specific overlay memos. Single-silo papers use central memo directly.

### Rationale

- **Methodological defence**: "Fresh coding within each silo" (Thomas & Harden) is preserved because multi-silo papers get silo-specific interpretive overlays.
- **Practical**: 293 single-silo papers need no overlay. 371 multi-silo papers get 658 overlay calls. Total savings vs pure per-silo: ~33%.
- **Cross-silo contradictions**: Same paper coded once centrally means codes are consistent when comparing across silos. The overlay adds silo emphasis, not different codes.

### Paper counts by silo membership

| Silos | Papers |
|-------|--------|
| 1 silo | 293 |
| 2 silos | 234 |
| 3 silos | 74 |
| 4 silos | 24 |
| 5+ silos | 39 |

### Risk mitigation

Papers with 5+ silo memberships (39 papers) are flagged as **cross-silo anchor papers**. These are the analytically richest papers — they get extra attention in B1/B2 theme generation and are marked as shared-source evidence (not independent corroboration).

---

## 5. Provenance & Audit Trail

### Decision

Hierarchical provenance with four levels:

1. **Campaign manifest** — entire production run metadata (corpus snapshot, model, prompts, git commit)
2. **Batch manifests** — per-worker: subset processed, start/end time, failures
3. **Paper metadata** — per-paper: source text hash, prompt hash, timestamps, output checksums
4. **Projection manifests** — per-silo: which central artifacts were materialised, with or without overlay

### Rationale

- **CBS GenAI compliance** (Pillar 3: audit trail): a reviewer must be able to trace any silo memo back to: which paper text → which prompt → which model → which LLM call → which researcher decision.
- **CBS GenAI compliance** (Pillar 4: reproducibility): campaign manifest pins model version, git commit, API version, temperature. Another researcher with the same manifest can re-run and compare.
- **Methodology defence**: the iteration log tracks quality improvements across pilot iterations, demonstrating instrument calibration.

### A2 enrichment safeguard

P2 frontmatter is injected into A2 for enrichment (quantitative data, triangulation verdicts). To preserve inductiveness:
- **Stripped from A2 input**: `topic_tags`, `methodology_tags` (silo labels that could anchor coding)
- **Kept in A2 input**: `year`, `source_type`, `has_quantitative_results`, `evaluation_type` (factual metadata, not interpretive)

---

## 6. Output Structure

### Production folder layout

```
s4_thematic_coding/
├── papers/                         # Central outputs (one per unique paper)
│   ├── <paper_id>.jsonl            # A1 codes
│   ├── <paper_id>.json             # A2 memo (silo-blind)
│   └── <paper_id>_l3.json          # L3 adversarial
│
├── <silo>/                         # Per-silo projected outputs
│   ├── codes/<paper_id>.jsonl      # → copy from papers/
│   ├── memos/<paper_id>.json       # → copy from papers/ (single-silo)
│   │                               #   OR overlay memo (multi-silo)
│   ├── reviewed/<paper_id>.json    # R1 researcher-approved memos
│   ├── themes.json                 # B1/B2 theme hierarchy
│   ├── REVIEW_LOG.md               # Researcher decision trail
│   └── projection_manifest.json    # What was projected + how
│
├── cross_silo/                     # Step 3.7 outputs
├── pilot/                          # Pilot iterations (preserved)
│
├── campaign_manifest.json          # Production run metadata
└── iteration_log.jsonl             # Append-only run log
```

---

## 7. Decision Log

| Date | Decision | Rationale | Reviewed by |
|------|----------|-----------|-------------|
| 2026-04-19 | Central A1 + silo overlay for multi-silo papers | Balance efficiency vs methodology | rubber-duck, methodology-guard |
| 2026-04-19 | Worker-based parallelism (default 8, configurable) | API latency is bottleneck, not rate limits | Rate limit analysis |
| 2026-04-19 | Model selection deferred to pilot | Data-driven: compare gpt-5.1 vs gpt-5.4-mini | Pilot iterations 01-04 |
| 2026-04-19 | max_tokens=32000 for A1 (reasoning model fix) | gpt-5.1 consumes tokens for thinking; 8000 too low | Debug session, API response analysis |
| 2026-04-19 | Hierarchical provenance (campaign→batch→paper→projection) | CBS GenAI compliance Pillars 3+4 | rubber-duck, genai-compliance |
| 2026-04-19 | Strip topic_tags from A2 enrichment input | Preserve inductiveness; prevent Phase 2 anchoring | rubber-duck finding #7 |
| 2026-04-19 | Percentage-based audit sampling (10%, min 5/silo) | Reproducible validation for methodology defence | AUDIT_GUIDE.md |
| 2026-04-19 | response_format: json_object for all LLM calls | Eliminates JSON parse failures | Pilot iterations 01-02 |
| 2026-04-19 | 8 active silos, PD-10→PD-03, PD-08 excluded | Meeting with vallahrich | Meeting transcript 2026-04-19 |
| 2026-04-19 | Writing assistance via Copilot (disclosure-capable design) | CBS "idea generation" classification | Plan v3 §2.6 |
| 2026-04-22 | A1: gpt-5.4-mini + v2 prompt (production config) | 10-iteration pilot: 97.4% L1, 0 hallucinations, 4.0/5.0 quality. v4 tested — no improvement | Pilot analysis, Opus 4.6 deep assessment |
| 2026-04-22 | A2/L3: gpt-5.1 hybrid (receives mini A1 codes) | Comparison_02: wins 8/10 on depth, 31% fewer L3 problems | comparison_01 + comparison_02 |
| 2026-04-22 | Skip 3 token-overflow papers (567b25a75e80, 9a926e905d18, dc60950e60b9) | Corrupted PDF extraction (1.1-1.5MB of mixed unrelated content). 567b/9a9 are duplicates of a toy HHL demo; dc6 is a shallow survey. 0.45% of corpus, zero methodological loss | Manual review of P2 frontmatter + extracted text |
| 2026-04-22 | Exclude 5087f7c0e2a3 (font-encoded garbled text) and dd6b533767c3 (Russian paper) | Garbled text produces hallucinated codes; Russian paper not in English corpus scope | A1 production L1 quality investigation |
| 2026-04-22 | Keep 4 OCR-artifact papers (46db6505e091, cb19eb039ea0, 75cd91455541, d746904e8cbb) | 8-16 valid codes each; all high P3 relevance; L1 fails are OCR noise, not fabrication | A1 production L1 quality investigation |
| 2026-04-22 | Cost-optimised pipeline: L3 on audit sample only (113 papers), overlay with mini | L3 is structural noise (flags 93-100%); overlay is a filtering task. Saves ~$47/~300 DKK | Cost analysis vs quality assessment |
| 2026-04-22 | Dual-LLM strategy: API batch for A1/A2/L3/overlay; isolated Copilot agent for B1/B2/A3/C1 | Strongest reasoning model for low-volume interpretive synthesis; API for high-volume extraction. See §8 | Researcher decision, methodology-guard defensible |
| 2026-04-22 | B1 model routing: `claude-opus-4.6` for payloads ≤200K tokens, `claude-opus-4.6-1m` for larger silos | Same underlying model, larger context window only. Preserves single-batch synthesis per silo (no cross-batch coalescence step needed). | B1 execution log |
| 2026-04-22 | B1/B2 pilot + production run complete | 8 silos processed; 139 B1 descriptive → 95 B2 merged descriptive + 45 analytical themes. 3 minor code-ID sanitizations. L-B1/L-B2 passed all silos. | `docs/B1_B2_COALESCENCE_REPORT.md` |

---

## 8. Dual-LLM Execution Strategy

### Decision (2026-04-22)

The pipeline uses **two distinct LLM execution modes**, selected per stage based on the nature of the task:

| Mode | Mechanism | Model | Best for |
|------|-----------|-------|----------|
| **API batch** | Azure OpenAI API, parallel workers, automated | gpt-5.4-mini / gpt-5.1 | High-volume mechanical tasks (A1, A2, L3, overlay) |
| **Isolated agent** | Copilot CLI sub-agent, stateless, one call per agent | Claude Opus 4.6 (or current best reasoning model) | Low-volume interpretive tasks (B1, B2, A3, C1) |

### Stage assignment

| Stage | Calls | Mode | Model | Justification |
|-------|:-----:|------|-------|---------------|
| A1 open coding | ~660 | API batch | gpt-5.4-mini | Extraction task; volume demands parallelism; pilot-validated |
| A2 memo compression | ~660 | API batch | gpt-5.1 | Analytical depth needed; volume still high; pilot-validated |
| L3 adversarial | ~113 | API batch | gpt-5.1 | QA check on audit sample; consistency with A2 model |
| Overlay | ~1,013 | API batch | gpt-5.4-mini | Filtering/selection task; high volume |
| **B1 descriptive themes** | 8 (one per silo, single-batch) | **Isolated agent** | **Claude Opus 4.6** (200K ctx) or **Claude Opus 4.6 1M** (1M ctx) — routed by payload size | Synthesising 43–313 memos into themes per silo; largest silos require 1M context |
| **B2 analytical themes** | 8 | **Isolated agent** | **Claude Opus 4.6** | One call per silo; most interpretive step in the pipeline |
| **A3 contradiction scan** | ~8 | **Isolated agent** | **Claude Opus 4.6** | Cross-paper comparison; nuanced judgment |
| **C1 cross-silo patterns** | 1 | **Isolated agent** | **Claude Opus 4.6** | Single most analytical call; benefits from deepest reasoning |

### B1 model routing (executed 2026-04-22)

| Silo | B1 payload (~tokens) | Model used |
|------|---------------------:|------------|
| trading_execution | 95K | `claude-opus-4.6` |
| credit_lending | 141K | `claude-opus-4.6` |
| fraud_detection | 217K | `claude-opus-4.6-1m` |
| derivative_pricing | 321K | `claude-opus-4.6-1m` |
| risk_management | 365K | `claude-opus-4.6-1m` |
| simulation_monte_carlo | 478K | `claude-opus-4.6-1m` |
| portfolio_optimization | 485K | `claude-opus-4.6-1m` |
| quantum_ml_finance | 634K | `claude-opus-4.6-1m` |

The 1M-context variant is the same underlying model with an expanded context window; only the routing differs, not the reasoning capability. This preserves methodological equivalence across silos.

### Isolated agent protocol

Each agent call must satisfy these constraints to be methodologically equivalent to an API call:

1. **Stateless**: Each call runs in a fresh sub-agent context. No memory, conversation history, or prior paper context is carried between calls. The agent receives ONLY the prompt template + input data.
2. **Same prompt**: The agent receives the identical prompt template used for API calls (stored in `p3_thematic_synthesis/prompts/`). No additional instructions beyond what the prompt specifies.
3. **Same output schema**: The agent produces JSON in the exact same format the pipeline expects. Output is written to the same file paths.
4. **Provenance logged**: Each call logs: model name and version, prompt template path, input data hash, timestamp, output file path. Stored in the campaign/batch manifest alongside API-mode calls.
5. **No cross-contamination**: The agent does NOT see outputs from other papers, other silos, or previous calls. Each paper/silo is processed in complete isolation.

### Rationale

- **Quality**: Interpretive synthesis (B1/B2/A3/C1) benefits disproportionately from stronger reasoning models. These stages compress hundreds of memos into a small number of themes — the quality of each call directly shapes the thesis findings. Using the best available reasoning model maximises analytical depth.
- **Cost efficiency**: API batch mode is cost-effective for high-volume stages (660+ calls). For low-volume stages (~40 calls total), the marginal API cost is small, but the quality improvement from a stronger model is significant.
- **Methodological defensibility**: The isolated-agent protocol ensures each call is functionally identical to an API call — stateless, prompt-driven, logged. The model difference is disclosed and justified: "extraction stages used gpt-5.4-mini/gpt-5.1 (pilot-validated); synthesis stages used Claude Opus 4.6 for deeper reasoning, following the same prompt protocol." This is analogous to a researcher choosing different analytical tools for different stages of a mixed-methods study.
- **CBS GenAI compliance**: Both modes satisfy the five CBS pillars — declaration (model named), role framing (LLM as assistant), audit trail (prompts + outputs logged), reproducibility (prompt templates versioned), and validation (researcher review gates between stages). The isolated-agent mode actually strengthens Pillar 3 (audit trail) because the full prompt and response are captured in the sub-agent context.

### Examiner defence

**Q: "Why did you use different models for different stages?"**

A: We selected models based on task requirements and empirical evidence. Extraction (A1) was pilot-validated on gpt-5.4-mini (97% L1, 4.0/5.0 quality across 10 iterations). Memo synthesis (A2) used gpt-5.1 for analytical depth (validated in comparison_02: 8/10 papers improved). Theme generation (B1/B2) used the strongest available reasoning model because these ~40 calls produce the thesis findings — each call synthesises 30+ memos into analytical themes. All calls followed the same prompt protocol, were stateless, and are fully auditable.

**Q: "How do you ensure the Copilot agent calls are equivalent to API calls?"**

A: Each agent call is isolated (fresh context, no memory), receives only the prompt template and input data, and produces output in the same JSON schema. The protocol is documented and the provenance chain (model, prompt, timestamp, output) is logged identically to API calls. The only difference is the model — which we selected deliberately for its stronger reasoning capability on interpretive tasks.
