"""Quick health check for the RAG stack.

Run:  python -m tools.rag.ollama_health
Returns exit code 0 if Ollama is reachable and required models are present.
"""
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

from tools.rag import config


REQUIRED_MODELS = (config.EMBED_MODEL, config.LLM_DEFAULT, config.LLM_DEEP)


def list_models() -> list[str]:
    """Query Ollama's /api/tags. Returns list of model names."""
    url = config.OLLAMA_BASE_URL.rstrip("/") + "/api/tags"
    with urllib.request.urlopen(url, timeout=5) as resp:
        payload = json.loads(resp.read())
    return [m["name"] for m in payload.get("models", [])]


def main() -> int:
    print(f"Ollama at: {config.OLLAMA_BASE_URL}")
    try:
        models = list_models()
    except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
        print(f"  ERROR: cannot reach Ollama ({exc})")
        print("  Start it with:  ollama serve   (or open the Ollama app)")
        return 2

    print(f"  Found {len(models)} installed models.")
    missing = []
    for required in REQUIRED_MODELS:
        # Match either exact name or name without quant suffix
        if any(required == m or required.split(":")[0] == m.split(":")[0] and required in m for m in models):
            print(f"  ✅ {required}")
        else:
            # Looser match: same base name
            base = required.split(":")[0]
            siblings = [m for m in models if m.startswith(base)]
            if siblings:
                print(f"  ⚠️  {required} not found, but related models present: {siblings}")
            else:
                print(f"  ❌ {required} (missing)")
                missing.append(required)

    if missing:
        print()
        print("Pull the missing models with:")
        for m in missing:
            print(f"  ollama pull {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
