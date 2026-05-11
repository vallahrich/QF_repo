# `prompts/` — Phase 1 LLM extraction prompts

Versioned prompt templates used by Phase 1 extraction scripts.

## Contents

| File | Purpose |
|------|---------|
| `extraction.txt` | Structured per-document extraction prompt (problem/solution candidates + verbatim quotes + locations). Consumed by [`../scripts/extract_document.py`](../scripts/extract_document.py). |

## Provenance

Prompt edits are recorded in [`../audit-trail.md`](../audit-trail.md). For the controlling LLM-assistance protocol see [`../../docs/METHODOLOGY_DESIGN.md`](../../docs/METHODOLOGY_DESIGN.md) and Appendix H of the manuscript.

> See parent [`../README.md`](../README.md) for Phase 1 status and methodology.
