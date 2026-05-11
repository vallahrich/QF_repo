# `shared/` — freeze record

| Field | Value |
|---|---|
| Freeze date | 2026-05-02 |
| Status | **Frozen** for code/data; no further changes before manuscript submission. |
| Tag | `freeze-2026-05-02` (set at repo-root freeze gate) |
| Tests | `pytest shared/tests/` — 14/14 passing |
| Verify scripts | `python tools/verify/v1_schema_validate.py` + `python tools/verify/v2_consistency.py` + `python tools/verify/v9_bridge.py` — all pass |
| Taxonomy | `shared/config/unified_taxonomy.json` v2.0 (PD-01..PD-11 with lifecycle annotations) |

## What this folder is

Decoupled foundation for the four phases:

- **Code** ([shared/tools/](tools/)): single shared `find_project_root` ([_paths.py](tools/_paths.py)); thread-safe `LLMClient` with rate limiting + exponential backoff + Azure-AD-keyless preference + per-call `system_fingerprint` + token-usage capture; JSONL `logger` with per-line `pid` + `git_sha`; `env_loader._sync_env` warns on divergent values; `text_chunker` is tiktoken-aware with observable heuristic fallback; `OpenAlexClient` distinguishes transport failure from not-found.
- **Config** ([shared/config/](config/)): canonical `unified_taxonomy.json`, `tier_definitions.json`, `silo_inclusion.json`, `source_types.json`, `extraction_config.json`, `zotero_collection_map.json`, plus matching `schemas/` files. v1 backup archived in `_archive/`.
- **Data artifacts** ([shared/extracted_text/](extracted_text/), [shared/bridge/](bridge/), [shared/phase3/](phase3/)): consumed read-only by p2/p3/p4.

## Invariants enforced at freeze

1. Every taxonomy entry with `status="merged"` has a resolvable `merged_into` (enforced by `v2_consistency.py:C7`).
2. Every active silo in `silo_inclusion.json` has a code in `unified_taxonomy.json` (`v2_consistency.py:C1`).
3. Every `problems/<silo>/` folder is referenced by `silo_inclusion.json` or carries a known cross-cutting marker (`v2_consistency.py:C3`).
4. PD-08 = `excluded`; PD-10 = `retracted`, `merged_into=PD-03` (`v2_consistency.py:C4` / `C5`).
5. PD-10 retraction marker file is present (`v2_consistency.py:C6`).
6. All `shared/tools/*` modules import `find_project_root` from `_paths.py`; no local re-implementations remain.
7. Every `LLMClient` log line carries `model_returned`, `system_fingerprint`, and (for chat completions) `prompt_tokens`/`completion_tokens`/`total_tokens` from `response.usage`.
8. Every JSONL log record carries `timestamp`, `pid`, `git_sha`.

## Test surface

- [shared/tests/test_text_chunker.py](tests/test_text_chunker.py) — 8 tests (truncate, section split, oversized hard-cut, heuristic-fallback path).
- [shared/tests/test_env_loader.py](tests/test_env_loader.py) — 4 tests (forward + reverse sync, divergence WARNING via `caplog`, no-op).
- [shared/tests/test_paths.py](tests/test_paths.py) — 2 tests (real repo root, env override).

## Deferred (out of freeze; documented limitations)

- `RateLimiter` is per-process only. Concurrent multi-process runs can collectively exceed the 4000 RPM ceiling. Not a correctness defect for the executed pipelines (each was a single process).
- `paper_selector.py` does an O(n·m) DOI lookup and hardcodes default p2 paths. Acceptable for the ~900-paper corpus; would need a dict index and dependency injection for any paper count beyond ~10 000.
- `text_chunker` falls back silently to a 4-chars/token heuristic when `tiktoken` is unavailable. The fallback now emits a one-time INFO log; `tiktoken>=0.7` is pinned in `p2_systematic_review/s1_slr/pyproject.toml`. Behaviour is correct either way.

## Reproduce

```powershell
# from repo root
pytest shared/tests/
python tools/verify/v1_schema_validate.py
python tools/verify/v2_consistency.py
python tools/verify/v9_bridge.py
```

All four must exit 0.
