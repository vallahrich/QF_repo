# `pdfs/` — Phase 1 source PDFs (EXCLUDED FROM SUBMISSION)

The 29 source PDFs for the Phase 1 corpus are **not distributed** with this submission repository due to publisher copyright restrictions.

## How to obtain the original papers

Each Phase 1 paper has a corresponding extraction JSON in [`..`](..) whose filename stem encodes the citation key (e.g., `2024_Abbas_<title-slug>.json`). To recover the originals:

1. Open the extraction JSON for the paper of interest.
2. Read the `doi` (or arXiv id) recorded in the `paper_metadata` block.
3. Resolve the DOI via your institution or the publisher.

A consolidated list of all corpus papers (Phase 1 + Phase 2) with DOI / Zotero key mappings is provided at [`../../../shared/bridge/paper_id_bridge.csv`](../../../shared/bridge/paper_id_bridge.csv).

## Original layout (preserved as empty subdirectories for provenance)

- `<paper_stem>.pdf` — primary location for each Phase 1 source.
- Numbered subdirectories (`1/`, `4/`, `11/`, `12/`) — per-paper PDF holding folders inherited from the original Zotero export. Empty here; non-empty in the operational repository.

See the project root [`FAIR_USE.md`](../../../FAIR_USE.md) for the full rationale on why source PDFs are excluded while extractions and downstream artifacts ship in full.

## Cross-references

- Pipeline overview: [`../README.md`](../README.md)
- Phase 1 methodology: [`../../README.md`](../../README.md)
- Manuscript: Annex L (Repository Structure) and §5 (Phase 1 inductive coding)
