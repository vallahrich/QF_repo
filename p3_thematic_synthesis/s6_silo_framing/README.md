# s6_silo_framing — Per-silo finance framing pipeline

> **Status (verified 2026-05-02):** descriptive/silo-framing output is
> complete as currently scoped. Disk counts: **629** F1 per-paper JSON
> outputs under `extractions/papers/` and **8** F2 silo briefs under
> `briefs/*/f2_silo_brief.json`. This is a descriptive framing layer, not
> independent semantic validation.

## Purpose

Extracts and synthesises **financial-problem framing** that the Phase 3
thematic synthesis (s4) does not address. Answers two artifact-level questions
per silo:

1. **What is the financial problem?** (Q1)
2. **Why is it a problem (classical baselines, difficulty)?** (Q2)

Plus supporting material for two derivative questions:

3. What classical state-of-the-art does the corpus treat as baseline?
4. What are the business stakes (where the corpus mentions them)?

## Methodological position

s6 is a **descriptive/contextual** stage, not an analytical one. It does
not generate themes or claims. It consolidates already-present motivation
language from the original PDF text and feeds a researcher-authored
finance framing in the silo chapters.

This preserves Phase 3's inductive thematic synthesis (s4) as a
self-contained contribution. s6 sits *next to* s4, not downstream of it.

## Why a separate pipeline (and not a re-prompt of A1/A2)?

- Re-running A1/A2 would invalidate the FROZEN P3 outputs that P4 depends
  on, and would invalidate the silo handoffs and drafts in
  `manuscript/working/`.
- The questions s6 answers (Q1, Q2) are framing questions, not synthesis
  questions. Mixing them into A1/A2 would muddle the inductive movement
  of Phase 3.
- s6 reads the **same source** as Phase 2 (the raw PDF text in
  `shared/extracted_text/text/`), making it methodologically a *sibling*
  extraction, not a downstream interpretation.

## Pipeline stages

### F1 — per-paper framing extraction

- **Input**: raw PDF text from `shared/extracted_text/text/{paper_id}_{slug}.md`
- **Channel**: Azure OpenAI deployment via
  `shared.tools.llm_client.LLMClient` — same channel and infrastructure
  used for Phase 2 extraction
- **Model**: `gpt-5.4-mini`
- **Temperature**: `0.1` (enforced via API parameter)
- **Storage**: deduplicated, paper-keyed — multi-silo papers extracted once
- **Output**: `extractions/papers/{paper_id}.json` with verbatim quote
  evidence for each non-null field

### F2 — per-silo aggregation

- **Input**: all F1 records belonging to a silo (via paper_silo_index.json)
- **Output**: `briefs/{silo}/f2_silo_brief.json` — researcher-readable
  synthesis paragraphs with audit metrics (paper counts contributing to
  each field; silo silence flags)

F2 outputs are present for all 8 active silos.

## Channel decision (subagent vs API)

The pilot (5 papers, both channels) showed the API channel produces
measurably more specific extractions and is fully reproducible (model +
temperature enforced). The pilot artefacts are preserved in
`logs/f1_calls_pilot.jsonl`. Production fanout uses **API only**.

The methodology disclosure for s6 should state: "F1 extraction uses Azure
OpenAI gpt-5.4-mini at temperature 0.1, via the same LLMClient
infrastructure used for the Phase 2 extraction pipeline (see Chapter 4
§4.X). All quotes are verified against the source PDF text via L1-style
substring matching with three normalisation tiers; failed quotes are
dropped and the corresponding fields nulled."

## Storage layout (deduplicated, paper-keyed)

```
s6_silo_framing/
├── README.md
├── prompts/
│   ├── f1_per_paper_extraction_v2.txt
│   └── f2_per_silo_aggregation_v1.txt          (drafted after F1 fanout)
├── scripts/
│   ├── build_paper_silo_index.py               # consolidates 8 projection manifests
│   ├── render_f1_request.py                    # freezes per-paper request bundles
│   ├── run_f1_api.py                           # API runner (workers + resume + atomic + dry-run)
│   ├── sanitize_and_persist_f1.py              # L1 quote verification + JSON validation
│   └── render_f2_prompt.py                     (drafted after F1 fanout)
├── input_index/
│   └── paper_silo_index.json                   # paper_id -> silos, text path
├── extractions/
│   ├── _requests/{paper_id}.request.json       # frozen request bundles (one per paper)
│   ├── _raw/{paper_id}.raw_response.txt        # API raw response (atomically written)
│   ├── _raw/{paper_id}.sanitize_log.json       # per-paper sanitise audit
│   └── papers/{paper_id}.json                  # sanitised structured extraction
├── briefs/
│   └── {silo}/f2_silo_brief.json
└── logs/
    ├── f1_calls.jsonl                          # production audit log
    └── f1_calls_pilot.jsonl                    # pilot/comparison phase log (archived)
```

## Exclusions

`run_f1_api.py` carries a hardcoded `EXCLUDED_PAPERS` set:

| paper_id | reason |
|---|---|
| 567b25a75e80 | corrupted PDF (multi-paper merge) — mirror of A1 exclusion |
| 9a926e905d18 | duplicate of 567b25a75e80 — mirror of A1 exclusion |
| dc60950e60b9 | corrupted PDF (multi-paper merge) — mirror of A1 exclusion |
| 5087f7c0e2a3 | font encoding bug — mirror of A1 exclusion |
| dd6b533767c3 | Russian-language paper — mirror of A1 exclusion |
| 4eb84ca51d29 | proceedings volume (840KB, not a single paper) — F1-specific |

Of these, only `4eb84ca51d29` is actually present in the s4 silo
projection. The others are listed for documentation of the inheritance
from A1.

## Verification (L1-equivalent)

`sanitize_and_persist_f1.py` verifies that every quote returned by the
model appears as a substring of the supplied paper text. Three
normalisation tiers handle benign formatting variants:

1. Whitespace-collapsed substring match
2. Hyphen + whitespace rejoin (handles `complex-\nity` ↔ `complexity`)
3. Inline hyphen strip (handles `complex-ity` model rejoin ↔ `complex-\nity`)

A hallucinated quote cannot pass — the underlying text must exist in the
paper. Quotes that fail all three tiers are dropped. If a non-null field
has zero surviving quotes, the field is nulled and the action logged.

Wrapper-marks (`"..."`, smart quotes) are stripped from quotes before
persistence — they are model formatting, not source text.

## Audit trail

Every F1 API call appends a JSONL entry to `logs/f1_calls.jsonl`:

```json
{
  "call_id": "f1-{paper_id}",
  "stage": "f1",
  "paper_id": "...",
  "silos": ["..."],
  "started_at": "...", "finished_at": "...",
  "channel": "azure_openai_api",
  "model_requested": "gpt-5.4-mini",
  "model_actual_reported_by_runtime": "gpt-5.4-mini",
  "temperature_requested": 0.1,
  "temperature_enforced": true,
  "max_tokens": 4000,
  "prompt_template_version": "f1_v2",
  "raw_response_path": "...",
  "request_bundle_path": "...",
  "status": "ok",
  "response_length_chars": 1234
}
```

Per-paper sanitise actions are recorded in
`extractions/_raw/{paper_id}.sanitize_log.json`.

## Verified output counts

The 2026-05-02 hardening audit counted outputs with:

```pwsh
Get-ChildItem p3_thematic_synthesis/s6_silo_framing/extractions/papers/*.json | Measure-Object
Get-ChildItem p3_thematic_synthesis/s6_silo_framing/briefs/*/f2_silo_brief.json | Measure-Object
```

Current counts: **629** F1 paper outputs and **8** F2 silo briefs
(`credit_lending`, `derivative_pricing`, `fraud_detection`,
`portfolio_optimization`, `quantum_ml_finance`, `risk_management`,
`simulation_monte_carlo`, `trading_execution`).

## Typical commands

```pwsh
# 1. Build the index (already done; rebuild only if projection manifests change)
python -m p3_thematic_synthesis.s6_silo_framing.scripts.build_paper_silo_index

# 2. Render per-paper request bundles
python -m p3_thematic_synthesis.s6_silo_framing.scripts.render_f1_request --all-silos

# 3. Dry-run to see how many calls would be made
python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f1_api --all-papers --dry-run

# 4. Run F1 across the full corpus (resume-friendly; safe to re-invoke)
python -m p3_thematic_synthesis.s6_silo_framing.scripts.run_f1_api --all-papers --workers 8

# 5. Sanitise everything in _raw/
python -m p3_thematic_synthesis.s6_silo_framing.scripts.sanitize_and_persist_f1
```
