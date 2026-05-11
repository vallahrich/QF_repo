# `shared/scripts/` — Shared P3 utility scripts

| Script | Purpose |
|--------|---------|
| `build_citation_graph.py` | Build per-silo citation graphs from P2 metadata. |
| `build_indices.py` | Build cross-silo paper / theme indices. |
| `detect_contradictions.py` | Cross-silo contradiction scan (uses `../prompts/contradiction_detection.txt`). |
| `fetch_silo_docs.py` | Stage paper texts into per-silo working folders. |
| `report_missing_papers.py` | Diagnose papers expected by a silo but absent from the working set. |

See parent [`../README.md`](../README.md).