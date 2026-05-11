"""Query the offline RAG index.

    python -m tools.rag.ask "what does the fraud detection silo conclude?"
    python -m tools.rag.ask "..." --deep                  # use Qwen 32B
    python -m tools.rag.ask "..." --tier 4 --silo X       # filter retrieval
    python -m tools.rag.ask "..." --paper-id 0757b9aa9a3b
    python -m tools.rag.ask "..." --k 12 --show-context
    python -m tools.rag.ask "..." --no-cite
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.rag import config


SYSTEM_PROMPT = """You are an offline research assistant for an MSc thesis on
"Quantum Computing in Financial Services" (Copenhagen Business School, 2026).

The thesis is structured in four phases:
- P1: Inductive framework synthesis (taxonomy construction)
- P2: Systematic literature review (777 papers, PRISMA-compliant)
- P3: Thematic synthesis across domain silos (frozen)
- P4: Experiment replication & quantum advantage validation

Domain silos: credit_lending, derivative_pricing, fraud_detection,
insurance_actuarial, portfolio_optimization, quantum_ml_finance, risk_management,
simulation_monte_carlo, trading_execution.

Taxonomy codes are PD-XX (problem domains) and SA-XX (solution approaches),
defined in shared/config/unified_taxonomy.json.

RULES:
1. Answer ONLY using the provided context chunks. If the answer is not in the
   context, say "Not in the provided context." Do not guess.
2. Cite every factual claim using [1], [2], ... matching the chunk numbers.
3. Be concise and use a technical academic register.
4. Distinguish between primary findings (manuscript, P3 syntheses) and raw
   source claims (Tier 4 papers) when relevant.
"""

QA_TEMPLATE = """{system}

Context (numbered chunks):
{context}

Question: {query}

Answer (with [n] citations):"""


def _format_context(nodes) -> tuple[str, list[dict]]:
    parts = []
    citations = []
    for i, node in enumerate(nodes, 1):
        meta = node.metadata or {}
        path = meta.get("path", "?")
        section = meta.get("section_path") or ""
        title = meta.get("paper_title")
        header = f"[{i}] {path}"
        if section and section != "<preface>":
            header += f" § {section}"
        if title and meta.get("tier") == 4:
            header += f"  ({title})"
        parts.append(f"{header}\n{node.get_content()}")
        citations.append({
            "n": i,
            "path": path,
            "section": section,
            "paper_id": meta.get("paper_id"),
            "paper_title": title,
            "tier": meta.get("tier"),
        })
    return "\n\n".join(parts), citations


def _format_citations(citations: list[dict]) -> str:
    lines = ["", "---", "**Sources**"]
    for c in citations:
        head = f"[{c['n']}] {c['path']}"
        if c.get("section") and c["section"] != "<preface>":
            head += f" § {c['section']}"
        extras = []
        if c.get("paper_id"):
            extras.append(f"paper_id={c['paper_id']}")
        if c.get("paper_title"):
            extras.append(f'"{c["paper_title"]}"')
        if extras:
            head += "  (" + ", ".join(extras) + ")"
        lines.append(f"- {head}")
    return "\n".join(lines)


def _build_filters(args):
    """Build a LlamaIndex MetadataFilters object from CLI flags. Returns None if no filters."""
    from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator

    fl: list[MetadataFilter] = []
    if args.tier:
        fl.append(MetadataFilter(key="tier", value=args.tier, operator=FilterOperator.EQ))
    if args.phase:
        fl.append(MetadataFilter(key="phase", value=args.phase, operator=FilterOperator.EQ))
    if args.silo:
        fl.append(MetadataFilter(key="silo", value=args.silo, operator=FilterOperator.EQ))
    if args.paper_id:
        fl.append(MetadataFilter(key="paper_id", value=args.paper_id, operator=FilterOperator.EQ))
    if args.kind:
        fl.append(MetadataFilter(key="kind", value=args.kind, operator=FilterOperator.EQ))
    if args.exclude_drafts:
        fl.append(MetadataFilter(key="status", value="draft", operator=FilterOperator.NE))
    if not fl:
        return None
    return MetadataFilters(filters=fl)


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the offline RAG index.")
    parser.add_argument("query", help="Your question (quote it).")
    parser.add_argument("--deep", action="store_true",
                        help=f"Use {config.LLM_DEEP} (slower, deeper synthesis).")
    parser.add_argument("--k", type=int, default=config.DEFAULT_TOP_K,
                        help=f"Top-k chunks to retrieve (default: {config.DEFAULT_TOP_K}).")
    parser.add_argument("--tier", type=int, choices=[1, 2, 3, 4],
                        help="Restrict retrieval to a single tier.")
    parser.add_argument("--phase", help="Restrict to phase: p1/p2/p3/p4/manuscript/docs/shared/root.")
    parser.add_argument("--silo", help="Restrict to a domain silo (e.g., fraud_detection).")
    parser.add_argument("--paper-id", help="Restrict to a single paper (12-hex paper_id).")
    parser.add_argument("--kind", help="Restrict to a file kind (tex/md/json/raw_paper/bib/yaml).")
    parser.add_argument("--exclude-drafts", action="store_true",
                        help="Exclude in-progress manuscript/working/ drafts.")
    parser.add_argument("--show-context", action="store_true",
                        help="Print retrieved chunks before the answer.")
    parser.add_argument("--no-cite", action="store_true",
                        help="Suppress the citation footer.")
    args = parser.parse_args()

    if not config.CHROMA_DIR.exists():
        print(f"No index found at {config.CHROMA_DIR}.")
        print("Run:  python -m tools.rag.index")
        return 1

    # Lazy imports
    import chromadb
    from llama_index.core import VectorStoreIndex, Settings
    from llama_index.embeddings.ollama import OllamaEmbedding
    from llama_index.llms.ollama import Ollama
    from llama_index.vector_stores.chroma import ChromaVectorStore

    model = config.LLM_DEEP if args.deep else config.LLM_DEFAULT

    Settings.embed_model = OllamaEmbedding(
        model_name=config.EMBED_MODEL,
        base_url=config.OLLAMA_BASE_URL,
    )
    Settings.llm = Ollama(
        model=model,
        base_url=config.OLLAMA_BASE_URL,
        request_timeout=600.0,
        context_window=config.LLM_NUM_CTX,
        additional_kwargs={"num_ctx": config.LLM_NUM_CTX},
    )

    chroma_client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    chroma_collection = chroma_client.get_or_create_collection(config.COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store)

    filters = _build_filters(args)
    retriever = index.as_retriever(similarity_top_k=args.k, filters=filters)
    nodes = retriever.retrieve(args.query)

    if not nodes:
        print("(no chunks retrieved — try a different query or relax filters)")
        return 0

    context_str, citations = _format_context(nodes)

    if args.show_context:
        print("=" * 70)
        print("RETRIEVED CONTEXT")
        print("=" * 70)
        print(context_str)
        print("=" * 70)
        print()

    prompt = QA_TEMPLATE.format(system=SYSTEM_PROMPT, context=context_str, query=args.query)
    print(f"[model: {model}, k={args.k}{', filters=' + str(filters) if filters else ''}]")
    print()

    response = Settings.llm.complete(prompt)
    print(str(response).strip())

    if not args.no_cite:
        print(_format_citations(citations))
    return 0


if __name__ == "__main__":
    sys.exit(main())
