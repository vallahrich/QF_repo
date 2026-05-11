"""Token-aware text truncation and chunking.

Uses tiktoken when available for exact token counts; falls back to a
4-chars/token heuristic when tiktoken or a model-specific encoder is
unavailable. The public API (`truncate_tokens`, `chunk_by_sections`)
is unchanged for backward compatibility; both gain an optional `model`
kwarg that is ignored on the heuristic path.
"""

import re
from functools import lru_cache

from .logger import get_logger

_logger = get_logger("text_chunker")

# Approximate ratio for the heuristic fallback: 1 token ≈ 4 characters.
# Used when tiktoken is not installed or no encoder is available for the model.
_CHARS_PER_TOKEN = 4

try:  # pragma: no cover - import probe only
    import tiktoken as _tiktoken  # type: ignore
except Exception:  # pragma: no cover
    _tiktoken = None  # type: ignore[assignment]

# One-time observability flag: emit an info-level message the first time we
# fall back to the char heuristic, so silent degradation is detectable.
_fallback_warned = False


@lru_cache(maxsize=32)
def _get_encoder(model: str | None):
    """Return a tiktoken encoder for `model`, or None if unavailable.

    Tries `encoding_for_model(model)` first, then `cl100k_base` as a
    sensible default. Returns None if tiktoken itself is missing; emits
    a one-time INFO log so the heuristic-fallback path is observable.
    """
    global _fallback_warned
    if _tiktoken is None:
        if not _fallback_warned:
            _logger.info(
                "tiktoken not installed; text_chunker is using the "
                "4-chars/token heuristic. Install tiktoken (>=0.7) for "
                "exact token counts and to silence this notice."
            )
            _fallback_warned = True
        return None
    if model:
        try:
            return _tiktoken.encoding_for_model(model)
        except Exception:
            pass
    try:
        return _tiktoken.get_encoding("cl100k_base")
    except Exception:
        return None


def _count_tokens(text: str, model: str | None = None) -> int:
    """Exact token count via tiktoken; heuristic fallback otherwise."""
    enc = _get_encoder(model)
    if enc is None:
        return max(1, len(text) // _CHARS_PER_TOKEN)
    return len(enc.encode(text))


def truncate_tokens(text: str, max_tokens: int, model: str | None = None) -> str:
    """Truncate text to approximately `max_tokens`.

    Uses an exact tiktoken encode/decode round-trip when an encoder is
    available; otherwise falls back to a 4-chars/token character cut.
    If `max_tokens <= 0`, returns the full text (no truncation).
    """
    if max_tokens <= 0:
        return text

    enc = _get_encoder(model)
    if enc is not None:
        ids = enc.encode(text)
        if len(ids) <= max_tokens:
            return text
        return enc.decode(ids[:max_tokens])

    max_chars = max_tokens * _CHARS_PER_TOKEN
    if len(text) <= max_chars:
        return text
    return text[:max_chars]


def chunk_by_sections(text: str, max_tokens: int, model: str | None = None) -> list[str]:
    """Split text into chunks at section boundaries.

    Splits on markdown headings (lines starting with #) and double newlines.
    Each chunk should be under `max_tokens`. Uses tiktoken-exact counts when
    available; otherwise falls back to a 4-chars/token character budget.
    Returns a list of text chunks.
    """
    if max_tokens <= 0:
        return [text]

    enc = _get_encoder(model)

    def _within_budget(s: str) -> bool:
        if enc is not None:
            return len(enc.encode(s)) <= max_tokens
        return len(s) <= max_tokens * _CHARS_PER_TOKEN

    if _within_budget(text):
        return [text]

    parts = re.split(r"(?=^#{1,3}\s)", text, flags=re.MULTILINE)
    if len(parts) <= 1:
        parts = re.split(r"\n\n+", text)

    chunks: list[str] = []
    current = ""

    def _hard_cut(s: str) -> list[str]:
        """Cut `s` into pieces each under `max_tokens`.

        Uses tiktoken slice-and-decode when available; otherwise a
        word-boundary-preserving character cut.
        """
        if enc is not None:
            ids = enc.encode(s)
            return [enc.decode(ids[i:i + max_tokens]).strip()
                    for i in range(0, len(ids), max_tokens)]
        max_chars = max_tokens * _CHARS_PER_TOKEN
        out = []
        i = 0
        while i < len(s):
            end = min(i + max_chars, len(s))
            # Prefer breaking on whitespace if possible (avoid mid-word cuts).
            if end < len(s):
                space = s.rfind(" ", i + max_chars - 200, end)
                if space > i:
                    end = space
            out.append(s[i:end].strip())
            i = end
        return out

    for part in parts:
        if not part:
            continue
        if current and not _within_budget(current + part):
            chunks.append(current.strip())
            current = ""
        if not _within_budget(part):
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_hard_cut(part))
        else:
            current += part

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text]

