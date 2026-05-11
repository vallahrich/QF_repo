# Stage C (Cross-Silo Synthesis) Quality Rubric v1

**Pre-committed**: 2026-04-22, before Stage C Opus call.
**Signatory**: Aleix Telesforo

Stage C produces cross-silo meta-themes. This rubric defines the acceptance gate. **The rubric is frozen before the Opus call runs.** Any post-hoc relaxation must be logged as a decision-log entry with justification.

## Structural validation (automated — L-C1)

| Check | Rule |
|---|---|
| SC1 | JSON parses; matches schema (`meta_themes` list + `meta_synthesis_note` string). |
| SC2 | 5 ≤ `len(meta_themes)` ≤ 8. |
| SC3 | Every meta-theme has `silos_grounded_in` with ≥ 3 silos from the 8-silo set. |
| SC4 | Every `grounded_in_themes[silo][i]` matches an existing `AT-<silo>-NNN` in the Stage B2 output. |
| SC5 | No meta-theme name contains a Phase 1 taxonomy code (`PD-\d{2}`, `SA-\d{2}`). |
| SC6 | `divergence_notes`, `implication_for_field`, `meta_synthesis_note` are all non-empty (> 20 chars each). |

## Content rubric (researcher-scored, 1–5 per criterion)

| Criterion | 1 (Unacceptable) | 3 (Acceptable) | 5 (Excellent) |
|---|---|---|---|
| **C1 — Non-obviousness**: Would this meta-theme have been stated in a generic "QC in finance" essay without the 8-silo analysis? | Yes, trivially. | Requires some cross-silo data. | Only visible from the 8-silo synthesis; would make a reader go "huh, I didn't see that coming". |
| **C2 — Divergence engagement**: Is the `divergence_notes` genuinely engaging a counter-case (another silo's contradicting theme) or is it a hand-wave? | Empty or generic. | Cites a divergent silo in name. | Names the contradicting silo + contradicting theme_id + the nature of the divergence. |
| **C3 — Implication precision**: Is `implication_for_field` actionable or generic? | Generic ("more research needed"). | Specific to the field. | Specific to the field + falsifiable or testable claim. |
| **C4 — P4 linkage**: Does `implication_for_phase4` connect to concrete experiment selection criteria? | Empty or "see Phase 4". | Generic direction. | Names a concrete experiment-selection criterion Phase 4 can adopt. |
| **C5 — Meta-synthesis note**: Is `meta_synthesis_note` publishable as the headline of Chapter 6's cross-silo section? | Generic observation. | Could serve as opening sentence. | Is itself a thesis-level claim that could be the single quote from Chapter 6. |

### Gate
- **Structural (SC1–SC6)**: all MUST pass. Any failure → re-run with repaired output or re-render.
- **Content (C1–C5)**: mean score ≥ 4.0 AND no criterion < 3. Any criterion < 3 → re-run with prompt tightening.

## Failure dispositions

- **Structural failure**: sanitize output if possible (drop meta-themes with <3 silos; strip invented theme_ids with warning). Re-run if >20% of meta-themes invalid.
- **Content failure on C1 (non-obviousness)**: reject the specific meta-theme; if ≥2 fail C1, re-run entire call with a tightened prompt stressing non-obviousness.
- **Content failure on C5 (meta-synthesis note)**: re-run the call; this field is load-bearing for Chapter 6.

## Provenance

- Prompt: `prompts/c1_cross_silo_synthesis_v1.txt` (SHA-256 recorded at render time).
- Model: `claude-opus-4.6-1m` (aggregated input will exceed 200K tokens).
- Stateless single call (no inter-run memory).
- Rendered prompt + raw response + meta stored at `s5_cross_silo/c1_{prompt,raw_response,meta}.{txt,json}`.

---

**Signed, 2026-04-22**: Aleix Telesforo
