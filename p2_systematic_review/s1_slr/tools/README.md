# `s1_slr/tools/` — SLR toolkit and tests

| Folder / file | Purpose |
|---------------|---------|
| `slr_toolkit/` | Python package implementing the SLR CLI: API search adapters, dedup, ingest, LLM-assisted screening, Zotero import. See [`slr_toolkit/README.md`](slr_toolkit/README.md). |
| `tests/` | Pytest suite for the SLR toolkit. See [`tests/README.md`](tests/README.md). |
| `apply_non_english_exclusions.py` | Apply the non-English-language exclusion pass to the screening dataset. |
| `detect_non_english.py` | Language detection helper that produces the input list above. |
| `push_to_zotero.py` | Sync the included corpus back into the Zotero library. |
