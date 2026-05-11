# c2_aggregate provenance note

| Field | Value |
|---|---|
| File | [`c2_aggregate.json`](c2_aggregate.json) |
| Sibling files for c1 | `c1.prompt.txt`, `c1.raw_response.txt`, `c1.meta.json`, `c1_manifest.jsonl`, `c1_meta_themes.json` |
| Sibling files for c3 | `c3_crosswalk.prompt.txt`, `c3_crosswalk.raw_response.txt`, `c3_crosswalk.meta.json`, `c3_crosswalk.json`, `crosswalk_shortlist.json` |
| Sibling files for c2 | **None** — only `c2_aggregate.json` exists |

## Status

`c2_aggregate.json` was generated as a **minimal interim draft** during the
pilot phase. Unlike `c1_meta_themes.json` and `c3_crosswalk.json`, the
prompt + raw response + meta provenance siblings were not captured at the
time. As of 2026-05-02 freeze, the original prompt + raw response are
**unrecoverable** from logs (the c2 generation pre-dated the JSONL
prompt-logging discipline added 2026-04-22).

## Implication for the manuscript

- The C1 meta-themes (in [`c1_meta_themes.json`](c1_meta_themes.json)) and the
  C3 literature crosswalk (in [`c3_crosswalk.json`](c3_crosswalk.json)) **are**
  reviewer-defendable: prompt, response, and metadata are all on disk.
- The C2 aggregate **is not** independently reviewer-defendable. Treat
  `c2_aggregate.json` as derivative summarisation of C1 + the per-silo
  `c2_grounding_check.json` artefacts under
  [`../s4_thematic_coding/<silo>/themes/c2_grounding_check.json`](../s4_thematic_coding/);
  cite those grounding files (which **do** carry provenance) rather than
  `c2_aggregate.json` for any thesis claim.

## Out of freeze

A regeneration of `c2_aggregate.json` with full provenance siblings would
require a new LLM call (one Opus 4.6 / 4.7 invocation against the same
inputs). Out of scope for the 2026-05-02 freeze; preregistered as a future
work item if a Stage-C re-run is performed.
