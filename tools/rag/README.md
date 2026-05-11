# Offline RAG over the thesis repo

A small, offline tool that lets you ask questions about your thesis repository
using local Ollama models. Indexes documentation, pipeline outputs, per-paper
extraction JSONs, and the ~777 raw paper texts.

**See [USAGE.md](USAGE.md) for the how-to-use guide.**
**See [INDEX_MANIFEST.md](INDEX_MANIFEST.md) for what is currently indexed.**

## Quick reference

```bash
# One-time setup
pip install -r tools/rag/requirements-rag.txt
python -m tools.rag.ollama_health           # verify models are present
python -m tools.rag.index                   # build the index (first run is slow)

# Daily use
python -m tools.rag.ask "your question"
python -m tools.rag.ask "deep question" --deep
python -m tools.rag.ask "question about paper X" --paper-id 0757b9aa9a3b
```

## Stack

- **LlamaIndex** for retrieval orchestration
- **ChromaDB** for the local vector store (persisted at `tools/rag/.chroma/`)
- **Ollama** for embeddings and generation (all local, no internet required)
  - Embeddings: `nomic-embed-text`
  - Default LLM: `qwen2.5:14b-instruct-q4_K_M`
  - Deep LLM (`--deep`): `qwen2.5:32b-instruct-q4_K_M`
