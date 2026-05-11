"""Audit how `topic_tags` / `methodology_tags` are emitted across the corpus.

The validators tolerate two LLM emission patterns observed in production:
slug form ("portfolio-optimization") and PD/SA-code form ("PD-01" / "sa-03"),
case-insensitive. This script makes that tolerance an *explicit, citable
artifact* by counting how many tags use each form and writing the result to
`output/audit/tag_normalization_report.json`.

No LLM calls. Read-only. Safe to run as a freeze-gate check.

Usage (from the repo root):

    python -m p2_systematic_review.s2_classification.scripts.audit_tag_normalization
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_S2_ROOT = _SCRIPT_DIR.parent
_P2_ROOT = _S2_ROOT.parent
_REPO_ROOT = _P2_ROOT.parent

for p in (str(_P2_ROOT), str(_REPO_ROOT)):
    if p not in sys.path:
        sys.path.insert(0, p)

from s2_classification.utils.frontmatter import read_frontmatter  # noqa: E402

PROCESSED_DIR = _P2_ROOT / "output" / "processed"
TAXONOMY_PATH = _REPO_ROOT / "shared" / "config" / "unified_taxonomy.json"
REPORT_PATH = _P2_ROOT / "output" / "audit" / "tag_normalization_report.json"

_PD_CODE = re.compile(r"^PD-\d{2}$", re.IGNORECASE)
_SA_CODE = re.compile(r"^SA-\d{2}$", re.IGNORECASE)


def _classify_tag(tag: str, slugs: set[str], codes: set[str], code_re: re.Pattern) -> str:
    t = (tag or "").strip()
    if not t:
        return "empty"
    if t in slugs:
        return "slug-canonical"
    if t.lower() in slugs:
        return "slug-case-variant"
    if t.upper() in codes:
        return "code-canonical"
    if code_re.match(t):
        return "code-case-variant"
    return "unregistered"


def main() -> None:
    if not PROCESSED_DIR.is_dir():
        print(f"Missing: {PROCESSED_DIR}", file=sys.stderr)
        sys.exit(1)

    tax = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    topic_slugs = set(tax.get("topic_tags", {}).keys())
    method_slugs = set(tax.get("methodology_tags", {}).keys())
    topic_codes = {v["code"].upper() for v in tax.get("topic_tags", {}).values() if v.get("code")}
    method_codes = {v["code"].upper() for v in tax.get("methodology_tags", {}).values() if v.get("code")}

    counts: dict[str, Counter[str]] = {
        "topic_tags": Counter(),
        "methodology_tags": Counter(),
    }
    unregistered_examples: dict[str, set[str]] = {
        "topic_tags": set(),
        "methodology_tags": set(),
    }
    papers_total = 0

    for md in sorted(PROCESSED_DIR.glob("*.md")):
        meta, _ = read_frontmatter(str(md))
        if not meta:
            continue
        papers_total += 1
        for field, slugs, codes, code_re in (
            ("topic_tags", topic_slugs, topic_codes, _PD_CODE),
            ("methodology_tags", method_slugs, method_codes, _SA_CODE),
        ):
            for tag in meta.get(field, []) or []:
                kind = _classify_tag(tag, slugs, codes, code_re)
                counts[field][kind] += 1
                if kind == "unregistered":
                    unregistered_examples[field].add(tag)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": str(PROCESSED_DIR.relative_to(_REPO_ROOT)),
        "taxonomy": str(TAXONOMY_PATH.relative_to(_REPO_ROOT)),
        "papers_total": papers_total,
        "counts": {field: dict(counter) for field, counter in counts.items()},
        "unregistered_examples": {
            field: sorted(items) for field, items in unregistered_examples.items()
        },
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"tag normalization audit -> {REPORT_PATH.relative_to(_REPO_ROOT)}")
    for field, counter in counts.items():
        total = sum(counter.values())
        print(f"  {field}: {total} total")
        for kind, n in counter.most_common():
            pct = (n / total * 100) if total else 0
            print(f"    {kind:22s} {n:6d}  ({pct:5.1f}%)")
        if unregistered_examples[field]:
            print(f"    unregistered_examples[{len(unregistered_examples[field])}]: "
                  f"{sorted(unregistered_examples[field])[:5]}")


if __name__ == "__main__":
    main()
