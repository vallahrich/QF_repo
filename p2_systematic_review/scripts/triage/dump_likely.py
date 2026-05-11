"""Dump head + results-relevant sections for the 18 remaining LIKELY papers."""
import re
import json
from pathlib import Path

PIDS = [
    "0fb8e2505865", "20c7e1972b0b", "2a5efc7b8178", "32f6aa86e556",
    "4dc6746d80a2", "5081ec6b6068", "559b94bd12c0", "732f54a585cf",
    "7c2e539656f7", "85e9109e6bb0", "8feb8231bb32", "a143717759af",
    "c94ec3a9d152", "e02980089334", "e13c1293dd99", "f35eb73554d8",
    "1502fad8d8ac", "7cc9ce4dad7d",
]

TEXT_DIR = Path("shared/extracted_text/text")
P2_DIR = Path("p2_systematic_review/output/processed")

RESULTS_HEADERS = re.compile(
    r"(?i)^\s*(\d+\.?\s*)?(results?|experimental results?|experiments?|evaluation|"
    r"findings|performance|comparative analysis|discussion|conclusions?|case stud(y|ies))\b",
    re.M,
)
TABLE_RE = re.compile(r"(?i)\bTABLE\s+[IVXLC0-9]+\b")

def get_p2_meta(pid):
    files = list(P2_DIR.glob(f"{pid}*.json"))
    if not files:
        return {}
    try:
        d = json.loads(files[0].read_text(encoding="utf-8"))
        return {
            "title": d.get("title"),
            "authors": d.get("authors"),
            "year": d.get("year"),
            "venue": d.get("journal_or_venue"),
            "doi": d.get("doi"),
            "arxiv_id": d.get("arxiv_id"),
            "abstract": (d.get("abstract_summary") or "")[:800],
            "method": (d.get("methodology_description") or "")[:800],
            "topic_tags": d.get("topic_tags"),
        }
    except Exception:
        return {}


def extract_chunks(t: str) -> list[tuple[int, int]]:
    """Find result/table anchor positions; return list of (start, end) windows."""
    anchors = []
    for m in RESULTS_HEADERS.finditer(t):
        anchors.append(m.start())
    for m in TABLE_RE.finditer(t):
        anchors.append(m.start())
    anchors = sorted(set(anchors))
    # Merge windows of +/- 1500 chars
    windows = []
    for a in anchors:
        start = max(0, a - 200)
        end = min(len(t), a + 2500)
        if windows and start < windows[-1][1] + 500:
            windows[-1] = (windows[-1][0], max(windows[-1][1], end))
        else:
            windows.append((start, end))
    # Cap total windows
    return windows[:8]


def main():
    out = []
    for pid in PIDS:
        mds = list(TEXT_DIR.glob(f"{pid}*.md"))
        if not mds:
            out.append(f"=== {pid} === MISSING MARKDOWN\n")
            continue
        t = mds[0].read_text(encoding="utf-8", errors="replace")
        meta = get_p2_meta(pid)
        chunks = extract_chunks(t)

        out.append("=" * 80)
        out.append(f"PID {pid}  size={len(t)}  file={mds[0].name}")
        out.append(f"TITLE:   {meta.get('title')}")
        out.append(f"AUTHORS: {meta.get('authors')}")
        out.append(f"YEAR:    {meta.get('year')}   VENUE: {meta.get('venue')}")
        out.append(f"DOI:     {meta.get('doi')}   ARXIV: {meta.get('arxiv_id')}")
        out.append(f"TAGS:    {meta.get('topic_tags')}")
        out.append("-- ABSTRACT --")
        out.append(meta.get("abstract", "")[:700])
        out.append("-- METHOD --")
        out.append(meta.get("method", "")[:700])
        out.append("-- HEAD (first 1200 chars) --")
        out.append(t[:1200])
        for i, (s, e) in enumerate(chunks):
            out.append(f"-- RESULTS WINDOW {i + 1} [{s}:{e}] --")
            out.append(t[s:e])
        out.append("\n")

    Path("dump_likely.txt").write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote dump_likely.txt ({sum(len(x) for x in out)} chars)")


if __name__ == "__main__":
    main()
