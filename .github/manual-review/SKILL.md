---
name: manual-review
description: "Manuscript review workflow — capture PDF reading feedback, promote it into the structured pipeline, and resolve items one by one. Use when reviewing the compiled thesis PDF and you want comments captured to docs/manual-review-aleix.md without solving them yet, or when promoting raw notes to docs/manual-review-pipeline-aleix.md, or when working through pipeline items to apply fixes."
argument-hint: "Subcommand: 'start' (chat capture mode), 'build-pipeline' (promote raw notes to pipeline items), or 'fix' (resolve one pipeline item)"
---

# Manual Review — PDF feedback workflow

Three-stage workflow for thesis manuscript review:

1. **start** — chat capture mode while reading the PDF. Append clean, well-scoped notes to `docs/manual-review-aleix.md`. Do **not** propose solutions.
2. **build-pipeline** — promote raw notes from `docs/manual-review-aleix.md` into structured items in `docs/manual-review-pipeline-aleix.md` (with IDs, priorities, repo source-of-truth fields, raw-note preservation).
3. **fix** — pick one open pipeline item, gather context, propose and apply the fix, build-validate, then flip the item to `decided`.

## Files

- **Raw notes**: [docs/manual-review-aleix.md](docs/manual-review-aleix.md)
- **Structured pipeline**: [docs/manual-review-pipeline-aleix.md](docs/manual-review-pipeline-aleix.md)
- **Vincent counterparts** (read-only — do not edit from this skill): `docs/manual-review-vallahrich.md`, `docs/manual-review-pipeline-vallahrich.md`

---

## Subcommand: `start`

**Purpose**: act as a feedback-capture buddy while the researcher reads the PDF. The researcher will paste a quote from the PDF and add a short comment / edit / observation. The skill confirms the note is well-scoped, asks for missing details if needed, then appends it to `docs/manual-review-aleix.md` under the right chapter section.

### Rules
- **Never propose solutions, edits, rewrites, or interpretations.** Just gather, clarify, and log.
- **Never edit `.tex` files** in this mode. Only append to `docs/manual-review-aleix.md`.
- Stay in capture mode for the whole session; do not switch to fix mode unless the user types `fix` or `build-pipeline`.

### Per-comment procedure

1. **Read what the user pasted.** Typical shape: a quoted snippet from the PDF + a short comment.
2. **Check for clarity.** A note is "clear enough to log" if it has:
   - **Anchor**: which chapter / section / page / quoted text — even a short quote works.
   - **Observation**: what the researcher noticed (factual issue, awkward phrasing, missing reference, structural concern, etc.).
   - **Direction**: at least a hint of what the researcher wants done (rewrite / cut / expand / verify / move / question for collaborator). It does not need to be a full solution — "rewrite for clarity" is enough.
3. **If anything is missing, ask one focused question.** Examples:
   - "Which chapter/section is this from?"
   - "Is this a factual concern or a phrasing concern?"
   - "Do you want this rewritten, cut, or just flagged?"
   - Ask **at most 2** clarifying questions per note. If still unclear, log it as `[needs-triage]` and move on.
4. **Once clear, append to `docs/manual-review-aleix.md`** under the matching `### N. <Chapter>` section (create the section if missing — preserve existing structure, no reordering). Use this entry format:

   ```markdown
   - [<short tag>] <anchor> — <verbatim observation>. <direction>.
   ```

   Where `<short tag>` is one of: `factual`, `phrasing`, `structure`, `citation`, `figure`, `verify`, `cut`, `expand`, `move`, `question`, `needs-triage`.

5. **Confirm to the user**: one-line acknowledgement plus the exact line that was logged. Do not summarise the chapter or commentate.
6. **Do not commit.** Capture mode is a working state; the researcher commits in batches.

### Session housekeeping
- At session start, briefly confirm which chapter the user is reading (so notes go to the right section).
- If the user pastes 5+ comments without a chapter switch, do not re-ask the chapter; just keep appending.
- If the user types `done` or `stop`, summarise: how many notes were added, to which sections.

---

## Subcommand: `build-pipeline`

**Purpose**: promote raw notes from `docs/manual-review-aleix.md` into structured tracker items in `docs/manual-review-pipeline-aleix.md`.

### Procedure

1. **Diff raw vs. pipeline.** Read both files. Identify raw notes in `docs/manual-review-aleix.md` that do not yet have a corresponding pipeline entry. Use anchor-text matching (a raw note's quoted snippet or section reference appears as the `Raw:` field of a pipeline entry).
2. **Group related notes.** Multiple raw notes about the same paragraph/decision should become one pipeline item.
3. **Assign IDs.** Use the existing scheme:
   - `IN-NN` Introduction · `BG-NN` Background · `RW-NN` Related Work · `M4-NN` Methodology · `P3I-NN` Ch6 intro · per-silo `<SILO>-NN` (e.g. `PO-01`)
   - Global / cross-cutting: `GL-NN`
   - Discussion seed / idea: `ID-NN`
   - Find the highest used number per prefix (grep `^### <PREFIX>-`) and continue.
4. **Create the pipeline entry** with this exact shape (matches existing items):

   ```markdown
   ### <ID> [<type> · <priority> · open] <one-line title>
   - **Repo source of truth**: <files / paths the fix will touch>
   - **Raw**: "<verbatim raw note>"
   - **Context**: <1–3 sentences of why this matters / what the constraint is> (optional, only if raw is terse)
   - **Decision**: _pending_
   ```

   Where `<type>` ∈ `E` (edit), `T` (task), `Q` (question), `I` (idea); `<priority>` ∈ `P0` (blocker), `P1` (should-have), `P2` (nice-to-have).
5. **Insert into the right section** of `docs/manual-review-pipeline-aleix.md` (use existing section headers; do not reorder).
6. **Update the changelog** at the bottom: `- <date>  build-pipeline: promoted N raw notes to <ID list>.`
7. **Do not delete raw notes** — leave the entry in `docs/manual-review-aleix.md` so the audit trail survives. The pipeline `Raw:` field carries the verbatim quote.
8. **Report to user**: table of `ID | section | priority | one-line title` for review before commit.
9. **Commit**: `docs(trackers): build-pipeline promote N raw notes to <ID list>` after user approval.

### Tracker-count update
Run the count snippet at the end and report progress vs. previous baseline:
```powershell
$a = Get-Content docs/manual-review-pipeline-aleix.md
$ah = $a | Where-Object { $_ -match '^### ' }
$ao = ($ah | Where-Object { $_ -match '\[[^\]]*\b(open|in-progress)\b' }).Count
"Aleix: decided=$($ah.Count - $ao) open=$ao total=$($ah.Count)"
```

---

## Subcommand: `fix`

**Purpose**: pick **one** open pipeline item, gather context, apply the fix end-to-end, and flip status to `decided`.

### Procedure

1. **Pick the item.** If the user named an ID, use it. Otherwise pick the highest-priority open item (P0 > P1 > P2; ties broken by lower numeric ID).
2. **Read the entry in full** in `docs/manual-review-pipeline-aleix.md`. Note the Repo source of truth, the Raw note, any sub-decisions or linked items.
3. **Read the source files** named in *Repo source of truth* before proposing anything.
4. **Propose the fix in 3–8 bullets**: anchor (file:line), what changes, why, build-validation plan. **Wait for user approval** before editing.
5. **Apply the fix** using `multi_replace_string_in_file` for atomic edits. Keep diffs minimal and focused — do not re-architect surrounding prose.
6. **Build-validate** when LaTeX is touched (run the `LaTeX: Fast build` task or `latexmk` per `manuscript/`). Report any new undefined refs / errors vs. the pre-edit baseline.
7. **Flip the item to decided** in `docs/manual-review-pipeline-aleix.md`:
   - Change the bracket from `[<type> · <priority> · open]` (or `in-progress`) to `[<type> · <priority> · decided <YYYY-MM-DD>]`.
   - Append a short closure note under the entry: `- **Closure (<date>)**: <1–3 lines describing what shipped, with file paths>`.
   - If the item was deferred to another collaborator or to a later wave, use `decided <date> (deferred to <target>)` and note in closure.
8. **Commit** with message: `fix(<ID>): <one-line title>` (multiline body with closure detail).
9. **Stop after one item.** Do not chain. The user may invoke `fix` again for the next.

### Refuse-to-fix conditions
- The Repo source of truth is in a frozen subtree (`*/FREEZE.md` declared) — surface the constraint, propose a deferred-cleanup framing (see existing `[ ] open → decided (deferred to ...)` pattern in the Vallahrich tracker), do not edit the frozen file.
- The fix would cross into Vincent-owned territory (Ch4 Methodology main, P2, P3/s1–s3, P4 manuscript prose). In that case, flip to `decided <date> (handed off to Vallahrich tracker as <ID>)` and add a stub to `docs/manual-review-pipeline-vallahrich.md` only with explicit user confirmation.
- The item is `[I · ...]` (idea/discussion seed) and the Discussion chapter (Ch8) is not yet ready for that argument — flip to `decided <date> (deferred to Ch8 drafting)` and stop.

---

## General notes

- All three subcommands operate on the Aleix-owned trackers only. The Vallahrich files are read-only references unless the user explicitly asks for cross-tracker work.
- The naming pair `manual-review-aleix.md` (raw) ↔ `manual-review-pipeline-aleix.md` (structured) is symmetric to the `*-vallahrich.md` pair — preserve that convention.
- Page targets and the 120 pp CBS cap are tracked separately by the `formal-requirements-check` skill; this skill should not perform that audit.
- When in doubt, prefer **logging more notes in capture mode** over **interpreting too aggressively in build-pipeline mode**. The pipeline is the bottleneck; capture is cheap.
