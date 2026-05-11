"""Build the local Chroma vector index over the thesis repo.

    python -m tools.rag.index                # incremental, all tiers
    python -m tools.rag.index --rebuild      # wipe and full rebuild
    python -m tools.rag.index --tier 1 2     # only specific tiers
    python -m tools.rag.index --dry-run      # write manifest, no embedding
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from collections import defaultdict
from pathlib import Path

from tools.rag import config, manifest, readers


def _print(msg: str) -> None:
    print(msg, flush=True)


def _load_state() -> dict:
    if config.STATE_FILE.exists():
        try:
            return json.loads(config.STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def _save_state(state: dict) -> None:
    config.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.STATE_FILE.write_text(json.dumps(state, indent=2))


def _db_size() -> int:
    if not config.CHROMA_DIR.exists():
        return 0
    return sum(p.stat().st_size for p in config.CHROMA_DIR.rglob("*") if p.is_file())


def _build_index(documents, persist_dir: Path):
    """Lazy import LlamaIndex/Chroma so --dry-run works without them."""
    import chromadb
    from llama_index.core import StorageContext, VectorStoreIndex, Settings
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.vector_stores.chroma import ChromaVectorStore

    Settings.embed_model = OllamaEmbedding(
        model_name=config.EMBED_MODEL,
        base_url=config.OLLAMA_BASE_URL,
    )
    Settings.llm = None  # never call an LLM during indexing

    persist_dir.mkdir(parents=True, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=str(persist_dir))
    chroma_collection = chroma_client.get_or_create_collection(config.COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    return VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the offline RAG index.")
    parser.add_argument("--rebuild", action="store_true",
                        help="Wipe the existing Chroma DB and rebuild from scratch.")
    parser.add_argument("--tier", nargs="+", type=int, choices=[1, 2, 3, 4],
                        help="Only index these tiers (default: all).")
    parser.add_argument("--dry-run", action="store_true",
                        help="Discover files and write manifest; do not embed.")
    args = parser.parse_args()

    tiers = args.tier or [1, 2, 3, 4]

    if args.rebuild and config.CHROMA_DIR.exists() and not args.dry_run:
        _print(f"Removing {config.CHROMA_DIR} (rebuild requested)…")
        shutil.rmtree(config.CHROMA_DIR)

    # 1. Discover all (path, kind, tier) triples
    discovered: list[tuple[Path, str, int]] = []
    by_kind: dict[str, int] = defaultdict(int)
    for tier in tiers:
        for path, kind in readers.discover(tier):
            discovered.append((path, kind, tier))
            by_kind[kind] += 1
    _print(f"Discovered {len(discovered)} files across tiers {tiers}.")
    for k, n in sorted(by_kind.items()):
        _print(f"  {k:18s} {n:>5d}")

    if args.dry_run:
        _print("\n[dry-run] writing manifest only…")
        path = manifest.write_manifest()
        _print(f"Wrote {path}")
        return 0

    # 2. Incremental: skip files whose mtime hasn't changed since last index.
    state = _load_state() if not args.rebuild else {}
    todo: list[tuple[Path, str, int]] = []
    for path, kind, tier in discovered:
        rel = str(path.relative_to(config.REPO_ROOT)).replace("\\", "/")
        mtime = path.stat().st_mtime
        if state.get(rel) == mtime:
            continue
        todo.append((path, kind, tier))

    if not todo:
        _print("All files up-to-date. Regenerating manifest only.")
        manifest.write_manifest(db_size_bytes=_db_size())
        return 0

    _print(f"\nReading {len(todo)} new/changed files…")
    documents = []
    chunk_counts: dict[Path, int] = {}
    t0 = time.time()
    for i, (path, kind, tier) in enumerate(todo, 1):
        docs = readers.read(path, kind, tier)
        chunk_counts[path] = len(docs)
        documents.extend(docs)
        if i % 50 == 0 or i == len(todo):
            _print(f"  read {i}/{len(todo)}  ({len(documents)} docs so far)")
    _print(f"Read {len(documents)} document chunks in {time.time() - t0:.1f}s.")

    if not documents:
        _print("Nothing to embed.")
        manifest.write_manifest(db_size_bytes=_db_size())
        return 0

    # 3. Build index
    _print(f"\nEmbedding via Ollama ({config.EMBED_MODEL})…")
    t0 = time.time()
    try:
        _build_index(documents, config.CHROMA_DIR)
    except Exception as exc:
        _print(f"\nERROR during embedding: {exc}")
        _print("Tip: run `python -m tools.rag.ollama_health` to verify Ollama is up.")
        return 1
    _print(f"Indexed in {time.time() - t0:.1f}s.")

    # 4. Update state
    new_state = dict(state) if not args.rebuild else {}
    for path, _, _ in todo:
        rel = str(path.relative_to(config.REPO_ROOT)).replace("\\", "/")
        new_state[rel] = path.stat().st_mtime
    _save_state(new_state)

    # 5. Manifest. We need chunk counts for ALL discovered files, not just todo;
    # for unchanged files, chunk count is unknown without re-reading, so we only
    # populate counts for files we touched this run.
    manifest.write_manifest(chunk_counts=chunk_counts, db_size_bytes=_db_size())
    _print(f"\nManifest written to {config.MANIFEST_PATH}")
    _print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
