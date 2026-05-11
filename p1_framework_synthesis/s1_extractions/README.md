# `s1_extractions/` — Phase 1 LLM-assisted extractions

One JSON profile per source document, produced by [`../scripts/extract_document.py`](../scripts/extract_document.py) using the prompt in [`../prompts/extraction.txt`](../prompts/extraction.txt). Each file follows the `(field, extracted_value, quote, location)` structure described in the parent README.

## Contents

- `*.json` — one extraction per paper; filename matches the source PDF stem.
- `_QUARANTINED_*` — retracted / misidentified extractions kept for audit; see the adjacent `*.RETRACTION.md` for rationale (Divergence Log D-1 in [`../audit-trail.md`](../audit-trail.md)).
- Source PDFs are not present in this clean submission tree; they are covered by the external source archive manifest named in the repository root README.

## Downstream

Consumed by:
- [`../scripts/build_review_data_done.py`](../scripts/build_review_data_done.py) → `s2_coding/review_data_done.json`
- [`../scripts/build_taxonomy.py`](../scripts/build_taxonomy.py) → `s3_taxonomy/`

## Status

Frozen as part of Phase 1 (see [`../FREEZE.md`](../FREEZE.md)). New papers are *not* added here; supplementary chapter sources go to [`../../shared/chapter_supporting_literature/`](../../shared/chapter_supporting_literature/) (decision GL-15).

> See parent [`../README.md`](../README.md) for Phase 1 status and the active 8×11 partition disclosure.
