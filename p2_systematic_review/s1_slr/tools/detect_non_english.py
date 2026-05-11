"""
Exhaustive language audit for SLR corpus.

Scans every extracted markdown file and classifies the PRIMARY language
of the body text (not headers, not abstracts, not metadata).

Methodology:
  1. Skip first 20 lines (title/author/metadata) and last 10 lines (refs).
  2. Count CJK characters across the full body.
  3. Count language-specific function words across the full body.
  4. A paper is flagged non-English only if the body text is predominantly
     in a foreign language (not just a translated abstract or dedication).

Output: CSV report with per-file language classification and evidence.
"""

import csv
import os
import re
import sys
from pathlib import Path

# ── Patterns ──────────────────────────────────────────────────────────────

CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf]")  # CJK Unified + Extension A

# Function words that appear frequently ONLY in running prose of each language.
# These are stop-words / grammatical words unlikely to appear in English text.
INDONESIAN_FW = re.compile(
    r"\b(adalah|pada|dengan|untuk|dari|yang|dalam|tersebut|dapat|tidak|"
    r"atau|juga|oleh|serta|karena|bahwa|telah|secara|setiap|lebih|sudah|"
    r"hanya|tetapi|namun|mereka|ketika|antara|masih|selain|seperti|hingga|"
    r"melalui|terhadap|sangat|akan|harus|perlu|merupakan|dilakukan|digunakan)\b",
    re.I,
)

PORTUGUESE_FW = re.compile(
    r"\b(computação|quântica|através|também|análise|aplicação|trabalho|"
    r"proposta|resultados|método|sistema|objetivo|sobre|forma|são|podem|"
    r"como|mais|para|uma|dos|das|por|com|esta|este|pela|pelo|entre|"
    r"sido|onde|qual|ainda|assim|apenas|cada|desde|após|durante|muito|"
    r"nosso|nossa|seus|suas|mesmo|outra|outro|quando)\b",
    re.I,
)

SPANISH_FW = re.compile(
    r"\b(computación|cuántica|también|según|además|pueden|entre|tiene|"
    r"información|tecnología|como|para|una|los|las|por|con|del|esta|"
    r"este|pero|desde|hacia|donde|cual|cada|sido|muy|todo|otra|otro|"
    r"son|más|han|está|hay|sin|sobre|así|tan|aún|cómo|mientras|"
    r"cuando|aunque|porque|siendo|estos|estas|aquí|cual)\b",
    re.I,
)

# Discriminators: words that exist ONLY in one language, not the other
PORTUGUESE_ONLY = re.compile(
    r"\b(computação|quântica|não|são|pode|podem|através|também|análise|"
    r"aplicação|trabalho|proposta|resultados|método|objetivo|sobre|forma|"
    r"uma|dos|das|pela|pelo|ainda|apenas|após|durante|nosso|nossa|seus|suas|"
    r"mesmo|outra|outro|onde|qual|financeiro|mercado|problema|algoritmo|estado)\b",
    re.I,
)

SPANISH_ONLY = re.compile(
    r"\b(computación|cuántica|tecnología|información|según|además|"
    r"los|las|del|tiene|pueden|pero|hacia|siendo|estos|estas|"
    r"aquí|mientras|aunque|porque|muy|hay|sin|así|aún|cómo)\b",
    re.I,
)

ENGLISH_FW = re.compile(
    r"\b(the|and|of|to|in|is|for|that|with|this|are|was|from|"
    r"which|have|been|has|can|but|not|were|their|more|than|"
    r"between|such|however|these|those|using|based|results|"
    r"proposed|algorithm|method|approach|problem|model)\b",
    re.I,
)


def classify_file(filepath: str) -> dict:
    """Classify the primary language of a markdown file."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    total_lines = len(lines)

    # Skip metadata (first 20 lines) and references (last 10 lines)
    body_start = min(20, total_lines)
    body_end = max(body_start + 1, total_lines - 10)
    body_lines = lines[body_start:body_end]
    body = " ".join(l.strip() for l in body_lines)
    body_chars = len(body)

    # Also check the FIRST HALF of the body only — catches bilingual papers
    # where a full translation is appended after the English text.
    half = len(body_lines) // 2
    first_half = " ".join(l.strip() for l in body_lines[:half])
    first_half_chars = len(first_half)
    first_half_cjk = len(CJK_RE.findall(first_half))
    first_half_en = len(ENGLISH_FW.findall(first_half))

    if body_chars < 200:
        return {"language": "too_short", "confidence": "low", "evidence": f"body={body_chars} chars"}

    # CJK character ratio
    cjk_count = len(CJK_RE.findall(body))
    cjk_pct = cjk_count / body_chars * 100

    # Function word counts
    en_count = len(ENGLISH_FW.findall(body))
    id_count = len(INDONESIAN_FW.findall(body))
    pt_count = len(PORTUGUESE_FW.findall(body))
    es_count = len(SPANISH_FW.findall(body))

    # Normalise per 1000 chars
    en_rate = en_count / body_chars * 1000
    id_rate = id_count / body_chars * 1000
    pt_rate = pt_count / body_chars * 1000
    es_rate = es_count / body_chars * 1000

    # Classification logic
    if cjk_pct > 8:
        # Check if paper is bilingual (English first half + Chinese translation appended)
        first_half_cjk_pct = first_half_cjk / max(first_half_chars, 1) * 100
        first_half_en_rate = first_half_en / max(first_half_chars, 1) * 1000
        if first_half_cjk_pct < 3 and first_half_en_rate > 10:
            return {
                "language": "English",
                "confidence": "high",
                "evidence": f"Bilingual: first_half CJK={first_half_cjk_pct:.1f}%, EN={first_half_en_rate:.1f}/1k; full CJK={cjk_pct:.1f}% (appended translation)",
            }
        return {
            "language": "Chinese",
            "confidence": "high",
            "evidence": f"CJK={cjk_pct:.1f}% ({cjk_count} chars in {body_chars})",
            "en_rate": en_rate,
        }

    # For non-CJK: require foreign rate > 3.0/1000 AND foreign > english * 0.3
    # Disambiguate Spanish vs Portuguese using language-specific markers
    pt_only = len(PORTUGUESE_ONLY.findall(body))
    es_only = len(SPANISH_ONLY.findall(body))

    if (es_rate > 3.0 or pt_rate > 3.0) and (es_count + pt_count) > en_count * 0.3:
        # Use discriminator counts to pick the right language
        if pt_only > es_only:
            return {
                "language": "Portuguese",
                "confidence": "high" if pt_rate > 6.0 else "medium",
                "evidence": f"PT_fw={pt_count} ({pt_rate:.1f}/1k), PT_only={pt_only} vs ES_only={es_only}, EN_fw={en_count} ({en_rate:.1f}/1k)",
            }
        else:
            return {
                "language": "Spanish",
                "confidence": "high" if es_rate > 6.0 else "medium",
                "evidence": f"ES_fw={es_count} ({es_rate:.1f}/1k), ES_only={es_only} vs PT_only={pt_only}, EN_fw={en_count} ({en_rate:.1f}/1k)",
            }

    if id_rate > 3.0 and id_count > en_count * 0.3:
        return {
            "language": "Indonesian",
            "confidence": "high" if id_rate > 6.0 else "medium",
            "evidence": f"ID_fw={id_count} ({id_rate:.1f}/1k) vs EN_fw={en_count} ({en_rate:.1f}/1k)",
        }

    return {
        "language": "English",
        "confidence": "high" if en_rate > 15 else "medium",
        "evidence": f"EN_fw={en_count} ({en_rate:.1f}/1k), CJK={cjk_pct:.1f}%, ID={id_rate:.1f}, PT={pt_rate:.1f}, ES={es_rate:.1f}",
    }


def main():
    text_dir = Path(__file__).resolve().parents[2] / ".." / "shared" / "extracted_text" / "text"
    if not text_dir.exists():
        # Fallback: relative from cwd
        text_dir = Path("shared/extracted_text/text")

    if not text_dir.exists():
        print(f"ERROR: text directory not found: {text_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted(f for f in os.listdir(text_dir) if f.endswith(".md"))
    # Deduplicate by paper_id (keep longest filename = most descriptive)
    by_pid = {}
    for f in files:
        pid = f[:12]
        if pid not in by_pid or len(f) > len(by_pid[pid]):
            by_pid[pid] = f

    print(f"Scanning {len(by_pid)} unique papers in {text_dir}\n")

    non_english = []
    english_count = 0

    for pid in sorted(by_pid):
        fname = by_pid[pid]
        result = classify_file(str(text_dir / fname))
        lang = result["language"]

        if lang != "English" and lang != "too_short":
            non_english.append({
                "paper_id": pid,
                "filename": fname,
                "language": lang,
                "confidence": result["confidence"],
                "evidence": result["evidence"],
            })
        else:
            english_count += 1

    print(f"English papers: {english_count}")
    print(f"Non-English papers: {len(non_english)}")
    print()

    if non_english:
        print("NON-ENGLISH PAPERS DETECTED:")
        print("-" * 100)
        for p in non_english:
            print(f"  {p['paper_id']}  |  {p['language']:12s}  |  conf={p['confidence']:6s}  |  {p['evidence']}")
            print(f"    file: {p['filename']}")
        print("-" * 100)

    # Write CSV report
    report_path = Path(__file__).resolve().parent.parent / "03_screening" / "non_english_audit.csv"
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["paper_id", "filename", "language", "confidence", "evidence"])
        writer.writeheader()
        writer.writerows(non_english)
    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
