# Using the offline RAG tool

This tool answers questions about your thesis repository **without internet
access**, using local Ollama models. Everything stays on your machine.

---

## 1. Prerequisites

You need:

1. **Ollama** running locally (the app or `ollama serve`).
2. Three models pulled:
   - `qwen2.5:14b-instruct-q4_K_M` — default chat model
   - `qwen2.5:32b-instruct-q4_K_M` — deep mode (`--deep`)
   - `nomic-embed-text` — embeddings
3. Python ≥ 3.10 with the dependencies listed in `requirements-rag.txt`.

Verify everything is in place:

```bash
python -m tools.rag.ollama_health
```

You should see three green checkmarks. If any model is missing, the script
prints the exact `ollama pull` command to run.

---

## 2. First-time setup

```bash
# (one-time) install Python deps
pip install -r tools/rag/requirements-rag.txt

# (one-time) build the index — takes a while on first run
python -m tools.rag.index
```

What happens:

1. The tool walks your repo using the rules in `tools/rag/config.py`.
2. It splits each file into chunks (LaTeX by `\section`, markdown by headings,
   JSONs per record, raw papers by paragraph blocks).
3. It embeds all chunks with `nomic-embed-text` and stores them in
   `tools/rag/.chroma/`.
4. It writes a human-readable summary to **`tools/rag/INDEX_MANIFEST.md`** so
   you always know exactly what the tool can see.

Expect ~12k–18k chunks and ~300–500 MB on disk.

---

## 3. Daily use

### Ask a question

```bash
python -m tools.rag.ask "What does the fraud detection silo conclude about quantum advantage?"
```

The model answers using only the retrieved chunks and prints a list of sources
(file paths and section headings). If the answer isn't in the corpus, you'll
see "Not in the provided context."

### Deep mode

For complex synthesis or critique, use the bigger 32B model:

```bash
python -m tools.rag.ask "Compare the methodologies of P1 and P3 syntheses" --deep
```

It's slower (~20 s per query) but noticeably better at multi-step reasoning.

### Show what was retrieved

To see exactly which chunks were fed to the model:

```bash
python -m tools.rag.ask "..." --show-context
```

Useful when you're debugging "why did it say X?".

---

## 4. Filtering retrieval

You can restrict the search to specific parts of the corpus using metadata
filters. See `INDEX_MANIFEST.md` for what's available.

| Flag | Effect | Example |
|---|---|---|
| `--tier N` | Only one tier (1=docs, 2=outputs, 3=extractions, 4=raw papers) | `--tier 4` |
| `--phase X` | One phase: `p1`, `p2`, `p3`, `p4`, `manuscript`, `docs`, `shared`, `root` | `--phase manuscript` |
| `--silo X` | One domain silo | `--silo fraud_detection` |
| `--paper-id X` | A single paper (12-hex id) | `--paper-id 0757b9aa9a3b` |
| `--kind X` | A file kind: `tex`, `md`, `json`, `raw_paper`, `bib`, `yaml` | `--kind bib` |
| `--exclude-drafts` | Skip in-progress `manuscript/working/` drafts | `--exclude-drafts` |
| `--k N` | Number of chunks retrieved (default 8) | `--k 16` |

You can combine them:

```bash
python -m tools.rag.ask "Which methods does this paper benchmark?" \
    --paper-id 0757b9aa9a3b --tier 4
```

---

## 5. Refreshing the index

The index is **incremental** — it tracks file mtimes and only re-embeds files
that changed since the last run.

```bash
# Pick up new files / changes (fast)
python -m tools.rag.index

# Wipe everything and rebuild from scratch (after editing config.py)
python -m tools.rag.index --rebuild

# Only one tier (faster iteration on docs)
python -m tools.rag.index --tier 1

# See what would be indexed without embedding (just regenerates the manifest)
python -m tools.rag.index --dry-run
```

After every run, **`INDEX_MANIFEST.md` is regenerated**.

---

## 6. Knowing what the tool knows

Open **[INDEX_MANIFEST.md](INDEX_MANIFEST.md)** at any time. It shows:

- Every folder/glob currently indexed, with file counts and chunk counts
- Every hard-excluded path pattern (with reason)
- Files skipped due to size (>2 MB)
- Counts by phase and by silo

If something is missing from your queries' answers, check the manifest first —
the file may not be in scope. To fix: edit `tools/rag/config.py` (the `TIERS`
dict) and rerun `python -m tools.rag.index --rebuild`.

---

## 7. Worked examples

### Find what the methodology says about a concept

```bash
python -m tools.rag.ask "What is the abductive reasoning cycle?"
```

Expected: cites `docs/METHODOLOGY_DESIGN.md` and Chapter 4 of the manuscript.

### Survey what your raw papers claim

```bash
python -m tools.rag.ask "Which papers report quantum advantage in option pricing?" --tier 4 --k 16
```

Expected: multiple `paper_id`s in the citations, drawn from
`shared/extracted_text/text/`.

### Drill into one paper

```bash
python -m tools.rag.ask "What's the encoding scheme used here?" --paper-id 0608ad48d5b8
```

Expected: answer drawn solely from chunks of that paper plus any extraction
JSONs that reference it.

### Check project status

```bash
python -m tools.rag.ask "What is currently blocked in P3?"
```

Expected: cites `docs/PROJECT_STATE.yaml`.

### Look up a taxonomy code

```bash
python -m tools.rag.ask "What does code SA-03 cover?"
```

Expected: cites `shared/config/unified_taxonomy.json`.

### Sanity check (out of corpus)

```bash
python -m tools.rag.ask "What is the capital of Mongolia?"
```

Expected: "Not in the provided context."

### Find papers you cite about a topic

```bash
python -m tools.rag.ask "Which cited works discuss QAOA convergence?" --kind bib
```

Expected: BibTeX entries with abstracts mentioning QAOA convergence.

---

## 8. Troubleshooting

### "cannot reach Ollama"
Start the Ollama app, or run `ollama serve` in a terminal.

### First query is slow (~30 s)
Ollama loads the model on first use. Subsequent queries reuse the loaded model
and are much faster (~3–8 s on the 14B). Models are unloaded after a few
minutes of idleness.

### Out of memory on `--deep`
The 32B model needs ~24 GB free. Close VS Code helpers, browsers, or fall back
to the default 14B (~12 GB).

### Slow indexing
First-time indexing of all 4 tiers can take 30–60 minutes (most of it is
embedding ~777 raw papers). Subsequent incremental runs take seconds.

### Answer mentions things that aren't in the corpus
This is the classic RAG failure mode (hallucination through context bleed).
Mitigation:
- Use `--show-context` to see what was actually retrieved.
- Use `--deep` — Qwen 32B sticks to context more rigorously.
- Tighten retrieval with `--tier`, `--silo`, or `--paper-id`.
- If a single paper is poisoning answers, exclude it by ID via filters at the
  CLI level (or add the path to `EXCLUDE_SUBSTRINGS` in `config.py`).

### "No index found"
Run `python -m tools.rag.index` first.

---

## 9. Limitations

- **No multi-turn memory.** Each query is independent.
- **No live web access.** This is by design — fully offline.
- **No code execution.** The tool reads, retrieves, and answers; it doesn't
  run scripts or modify files.
- **Context window is bounded** to ~16k tokens during generation. Very long
  retrieved chunks may be truncated.
- **Local models hallucinate more than Claude/GPT-4.** Always verify
  citations before quoting in the manuscript.
