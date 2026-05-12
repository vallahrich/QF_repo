---
name: p3-r1-review
description: "Walk the researcher through the P3/s4 R1 propagation-prioritised review one paper at a time. Triangulates the A2 memo against A1 codes, the L3 audit, and the original PDF text; presents a Paper Summary, an L3 Summary, and an Analysis (not a fragmented table); then asks for a verdict via a multi-option prompt and logs it to {silo}/reviewed/r1_review.jsonl. Use when working through r1_review_worklist.jsonl entries to close GL10_AUDIT.md G-02."
argument-hint: "Optional: a silo name (e.g. 'credit_lending') to scope the session, or 'status' for a coverage report"
---

# P3 / s4 — R1 Propagation-Prioritised Review

Assistive workflow for the per-paper review of the R1 sample produced by `p3_thematic_synthesis/scripts/r1_sample_worklist.py`. One paper at a time: read all relevant artefacts, present a coherent narrative + analysis, ask for a verdict, log it. Researcher always has the final say.

## Sampler context (read this before reasoning about coverage)

The R1 worklist is **not** a flat random sample. It is a propagation-prioritised tiered draw:

- **Per-silo eligible pool** = papers in the silo roster whose `propagation_count >= 1` (i.e. they actually feed at least one B1 DT or B2 DT/AT in that silo).
- **Tiers within the per-silo draw** (drawn A → B → C until target N):
  - `A` — paper has at least one L3 **major** problem
  - `B` — paper has only L3 **minor** problems
  - `C` — L3 record exists with no problems, or no L3 record at all
- **Per-silo top-up** (rare; tagged `sampling_tier: "topup"`) — used only if `|E| < N` for the silo. Drawn from `propagation_count == 0` papers.
- **Corpus-wide top-up** (tagged `sampling_tier: "topup_high_prop"`, with extra field `corpus_propagation_count`) — every major-flagged paper whose **summed** propagation across all silos and across B1+B2 is `>= HIGH_PROP_THRESHOLD = 10` and that the per-silo draws missed. Each is assigned to the silo where its per-silo `propagation_count` is highest.

Implication for review: `topup_high_prop` papers are **high-reach across the whole manuscript** even when their per-silo footprint is modest. They deserve careful attention because a single bad memo here can ripple through multiple silo chapters.

## Files

- **Worklists** (one per silo): `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/r1_review_worklist.jsonl`. Each row:
  ```json
  {"paper_id": "...", "silo": "...", "has_l3": true, "l3_problem_count": 4,
   "l3_severity_max": "major", "propagation_count": 10,
   "sampling_tier": "A" | "B" | "C" | "topup" | "topup_high_prop",
   "corpus_propagation_count": 12,   // only present on topup_high_prop rows
   "status": "pending" | "reviewed", "verdict": "..."  // verdict added on review
  }
  ```
- **Decision log** (one per silo, append-only): `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/r1_review.jsonl` — created on first decision in that silo.
- **Approved memo store**: `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/{paper_id}.json` — copy of the A2 memo for any paper the researcher approves (with or without caveat).
- **Pulled memo store**: `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/_pulled/{paper_id}.json` — copy of the memo for any paper the researcher marks `flag_for_pull`, with a `_pull_reason` field appended at the top level.
- **A2 memo** (read-only source): `p3_thematic_synthesis/s4_thematic_coding/{silo}/memos/{paper_id}.json`
- **A1 codes** (read-only source, jsonl): `p3_thematic_synthesis/s4_thematic_coding/{silo}/codes/{paper_id}.jsonl` — the per-span codes the A2 memo aggregates from (each row: `code_id, code_label, text_span, locator, dimension_hint, rationale, l1_status`).
- **L3 audit record** (when present): `p3_thematic_synthesis/s4_thematic_coding/papers/{paper_id}_l3.json`
- **Extracted PDF text**: `shared/extracted_text/text/{paper_id}_*.md` — the skill **reads** this file to ground the L3 triangulation. (The path is also surfaced in chat so the researcher can open it locally.)
- **Themes (DTs/ATs)**: `p3_thematic_synthesis/s4_thematic_coding/{silo}/themes/b1_*.json` and `b2_silo_themes.json` — search for `paper_id` to find which themes this paper supports.

---

## Modes

### `status`
Print a per-silo coverage table from the worklist + log:
- Counts of `pending` vs `reviewed` per silo, total %
- Verdict distribution per silo and overall
- **Coverage broken down by `sampling_tier`** (A / B / C / topup / topup_high_prop) — useful for the disclosure paragraph
- A list of any worklist/log inconsistencies (paper logged but worklist still `pending`, or vice versa)

### default — `review` (the main loop)

Pick the next pending paper. If a silo argument is given, restrict to that silo; otherwise round-robin across silos with remaining `pending` items, in this priority order:

1. `topup_high_prop` (highest cross-manuscript reach), sorted by `corpus_propagation_count` desc, then `paper_id` asc
2. `A` (per-silo, L3-major), sorted by `propagation_count` desc, then `paper_id` asc
3. `B` (per-silo, L3-minor), same sort
4. `C` then `topup` (rarely populated), same sort

Then for **one** paper:

1. **Read** all artefacts: worklist row, A2 memo, A1 codes, L3 record (if present), and the extracted PDF markdown. Search the silo's `themes/` for paper attribution.
2. **Present** the packet in the new prose format (see template below). Inline the memo content in summary form, the L3 evidence consolidated by theme, and an Analysis section that triangulates each L3 flag against the memo / A1 codes / PDF text.
3. **Ask** the researcher for a verdict using the multi-option prompt (see "Verdict prompt" below).
4. **Execute** the researcher's decision: log one JSON line (carrying sampling provenance), place the memo in the right destination folder, update the worklist row, and **stop**. Do not auto-advance unless the researcher types `next`.

Refuse to proceed if the worklist file is missing, malformed, or empty for the requested silo. If a paper already has a row in `r1_review.jsonl`, surface it and ask whether to skip or re-review.

---

## Per-paper packet template

Use this exact prose layout. **No fragmented tables.** The Paper Summary collapses A2 memo content into a single coherent paragraph (or short paragraphs); the L3 Summary consolidates flags by theme; the Analysis is the skill's triangulation work.

```
### {paper_id}  —  silo: {silo}  |  tier: {sampling_tier}  |  propagation: {propagation_count}{ + corpus {corpus_propagation_count} if topup_high_prop}  |  L3: {n_problems} ({n_major} major / {n_minor} minor)

**Title**: {memo.title if present, else first H1 in PDF text, else paper_id}
**PDF text**: shared/extracted_text/text/{paper_id}_<slug>.md

**Paper Summary**
{2–4 sentence prose synthesis of the A2 memo: what the paper studies, what it
finds for this silo, how confident the memo is, and which DTs/ATs in this silo
it supports. Quote at most one short phrase from the memo. End with: "The memo
attributes this paper to: {DT/AT ids}." — or "no theme attribution found" if
nothing.}

**L3 Summary**
{If has_l3 == false or problem_count == 0: "No L3 audit problems were
recorded for this paper." and skip to Analysis.

Otherwise: a single grouped narrative, not one bullet per flag. Group flags by
target (e.g. "claims about the AUC comparison", "framing of the scaling
limits") and within each group describe: (a) what the memo says, (b) what L3
flagged, (c) the L3 type/severity. Aim for one short paragraph per group, max
three groups. If flags are independent and don't group naturally, say so and
list them compactly.}

**Analysis**
{The skill's own triangulation. For each L3 flag (or flag-group), check it
against the A2 memo, the A1 codes that fed the memo, and the PDF text the
skill has read. Decide for each:
  - Confirmed: the L3 flag is correct — the memo really does over/mis-state
    the source. Quote the PDF span that proves it.
  - Partially confirmed: the memo is loose but the source partially supports
    the framing. Explain the slack.
  - Not confirmed: the L3 flag is itself wrong (e.g. it cited a partial
    sentence; the rest of the paragraph supports the memo). Quote the PDF
    span that exonerates the memo.

Then state the consequence for the silo's themes: which DTs/ATs would be
weakened or unsupported if this memo were pulled, and whether other papers
already carry that load. End with one sentence on what the skill would
recommend and why — but make clear this is advisory only.}
```

The skill must actually read the PDF markdown for the triangulation. If the PDF text file is missing, say so explicitly in the Analysis and downgrade confidence rather than fabricate.

---

## Verdict prompt (multi-option)

After presenting the packet, ask the researcher with a multi-option question. The options are:

- `approved` — memo accurately represents the source; safe to keep as-is.
- `approved_with_caveat` — memo is usable but needs a small qualifier; provide the caveat in the free-text (one sentence, will be stored as `_r1_caveat` on the placed memo).
- `requires_revision` — memo has a real issue that should be fixed before any chapter cites it; describe what to fix in the free-text. Memo is **not** copied to `reviewed/`.
- `flag_for_pull` — memo's load-bearing claim is wrong/unsupported; pull from the propagation. Provide the pull reason in the free-text (will be stored as `_pull_reason`); memo is copied to `reviewed/_pulled/`.
- `defer` — researcher wants to come back later; no log row is written, status stays `pending`.

The researcher chooses one option and supplies their own `notes` (after double-checking the source on the side). The skill's Analysis is shown only to orient the review — it is not logged, and the researcher's notes should reflect their own judgement, not a copy-paste of the Analysis.

---

## Orientation hint (ephemeral)

The skill may surface a non-binding orientation hint in chat to anchor the researcher's reading of the Analysis. Any such hint is **chat-only and non-persistent**: it is never written to `r1_review.jsonl`, the worklist, or any other artefact. The verdict and rationale are always selected and authored by the researcher after independently checking the source.

The internal heuristics that produced any orientation hint in past sessions have been intentionally omitted from this published bundle to avoid the appearance of a pre-baked verdict. The researcher's verdict is the only output that exists.

---

## Decision log schema

Append one JSON line per paper to `p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/r1_review.jsonl`. **Only the researcher's decision and their own notes are logged.** The skill's Analysis, recommended verdict, recommended rubric scores, and triangulation findings are ephemeral chat scaffolding and are **not** persisted in any field.

```json
{
  "paper_id": "80db1bf3c910",
  "silo": "credit_lending",
  "reviewed_at": "2026-05-07T14:32:11+02:00",
  "verdict": "approved_with_caveat",
  "notes": "Checked source: epoch-reduction claim is conditional on the 350-epoch matched comparison; memo overstates. Caveat-level only — does not unsupport AT-CL-003.",
  "sampling_provenance": {
    "sampling_tier": "A",
    "propagation_count": 10,
    "corpus_propagation_count": null,
    "l3_severity_max": "major",
    "l3_problem_count": 4
  },
  "time_spent_sec": 240
}
```

Rules:
- One line, UTF-8, LF newline, `ensure_ascii=False` style.
- `notes` is the **researcher's** rationale, written in their own words after they double-check the original source on the side. Do not auto-fill from the skill's Analysis. Notes are **allowed (and encouraged) on every verdict, including `approved`** — e.g. "spot-checked the AUC table; memo accurate" or "no issues, but flagging the small sample size for the silo discussion." Only `requires_revision` and `flag_for_pull` *require* non-empty notes (see below).
- `sampling_provenance` echoes the worklist row (factual metadata, not AI output) so disposition refresh can stratify outcomes by tier without re-joining files. `corpus_propagation_count` is `null` for non-`topup_high_prop` rows.
- `time_spent_sec` is best-effort (timestamp delta from packet display to confirmation); omit rather than guess.
- Any verdict of `requires_revision` or `flag_for_pull` MUST have non-empty `notes` naming which DT/AT or which memo span is at issue.
- `defer` writes nothing to the log; the worklist row remains `pending`.
- **Forbidden fields** (do not add even "for traceability"): `rubric_scores`, `triangulation_summary`, `recommended_verdict`, `ai_analysis`, or any other field derived from the skill's reasoning. The chat session is the only place that information lives.

## Decision execution

After logging, the skill physically realises the verdict:

| Verdict | Action on `{silo}/memos/{paper_id}.json` (source, untouched) | Destination |
|---|---|---|
| `approved` | copy verbatim | `{silo}/reviewed/{paper_id}.json` |
| `approved_with_caveat` | copy + add top-level `_r1_caveat: "<notes>"` | `{silo}/reviewed/{paper_id}.json` |
| `requires_revision` | no copy | (none — log row carries the actionable note) |
| `flag_for_pull` | copy + add top-level `_pull_reason: "<notes>"` | `{silo}/reviewed/_pulled/{paper_id}.json` |
| `defer` | no copy, no log | (none) |

Notes:
- Copies use `ensure_ascii=False` and a trailing newline. If the destination already exists (paper re-reviewed), overwrite and mention it in the chat summary.
- The skill **never** modifies the source memo, A1 codes, themes, projection manifests, or any downstream artefact. Theme/projection cleanup for `flag_for_pull` papers is a separate workstream that consumes `reviewed/_pulled/`.
- After execution, update the worklist row for that paper: set `status` from `pending` to `reviewed` and add `verdict`. Rewrite the worklist file (preserve row order).
- Print a one-line summary: `[silo] paper_id (tier {sampling_tier}) → {verdict} — memo placed at {dest|none} — silo cumulative: R/W reviewed`.
- **Stop.** Wait for `next` (or a silo switch / explicit silo argument) before drawing the next paper.

---

## Per-silo completion

When a silo's worklist has zero `pending` rows:
1. Print the silo's verdict distribution **and** the same distribution stratified by `sampling_tier` (so the disclosure can say e.g. "of the 4 corpus-top-up papers in CL, 3 approved / 1 caveat").
2. List any `requires_revision` / `flag_for_pull` paper_ids with their notes.
3. Stage and commit (include the materialised memo copies):
   ```
   git add p3_thematic_synthesis/s4_thematic_coding/{silo}/reviewed/
   git commit -m "feat(p3/s4/{silo}): R1 review complete — {approved+caveat}/{total} memos placed in reviewed/" \
              -m "Verdict distribution: approved={A} caveat={B} revise={C} pull={D}." \
              -m "By tier: A={...} B={...} C={...} topup={...} topup_high_prop={...}." \
              -m "Pulled paper_ids (memos copied to reviewed/_pulled/): {list or 'none'}."
   ```
4. Do **not** touch `_disposition.json`. That refresh runs once all 8 silos are complete.

---

## Hard rules

- **One paper per turn.** Never present, log, or move more than one paper without an explicit `next` from the researcher.
- **Triangulate, don't paraphrase.** The Analysis section must reference what the skill actually read in the PDF text — quoted spans, not vibes. If the PDF text is unavailable, say so and lower confidence.
- **No fragmented per-axis tables in chat.** The packet has three prose sections (Paper Summary / L3 Summary / Analysis) plus the multi-option verdict prompt.
- **AI analysis is ephemeral.** The Analysis section, recommended verdict, and any dimensional reasoning live only in the chat. They are never written to `r1_review.jsonl`, the worklist, or any other artefact. The researcher double-checks the source on the side and writes their own `notes`.
- **Source memos / A1 codes / themes / projection manifests are read-only.** The skill writes only inside `{silo}/reviewed/` (worklist update, log, approved-memo copies, `_pulled/` copies).
- **Researcher decides.** The chat-side recommendation is shown to anchor the review; only the researcher's chosen verdict is executed and logged.
- **No PDF inlining.** The skill reads the PDF markdown to triangulate, but only quoted spans appear in the Analysis. Cite the path so the researcher can open it locally.
- **No methodology prose, no manuscript edits, no L3 hardening.** Out of scope. If a `requires_revision` or `flag_for_pull` verdict implies a downstream chapter edit, log it in `notes` and stop — the edit happens in its own workstream.
