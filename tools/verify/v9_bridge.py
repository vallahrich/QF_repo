"""V9: paper_id_bridge.csv hygiene audit.

Scans `shared/bridge/paper_id_bridge.csv` for:
  - DOI casing collisions (lower-cased DOI shared by >1 slr_paper_id).
  - Zotero key collisions (same zotero_item_key under >1 slr_paper_id).
  - Title near-duplicates by exact match (cheap heuristic for
    preprint↔published linkage).
  - Missing required columns / blank values.

Read-only; informational. Reports drift; does not modify the bridge.

Run: python -m tools.verify.v9_bridge
"""

from __future__ import annotations

import csv
import datetime as _dt
import json
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = REPO_ROOT / "tools" / "verify" / "reports"
BRIDGE = REPO_ROOT / "shared" / "bridge" / "paper_id_bridge.csv"


def _norm_doi(doi: str | None) -> str:
    if not doi:
        return ""
    return doi.strip().lower()


def _norm_title(t: str | None) -> str:
    if not t:
        return ""
    return " ".join(t.lower().split())


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    with BRIDGE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    by_doi: dict[str, list[str]] = defaultdict(list)
    by_zk: dict[str, list[str]] = defaultdict(list)
    by_title: dict[str, list[str]] = defaultdict(list)
    blank_doi = 0
    blank_zk = 0
    for r in rows:
        sid = r.get("slr_paper_id", "").strip()
        d = _norm_doi(r.get("doi"))
        zk = (r.get("zotero_item_key") or "").strip()
        title = _norm_title(r.get("title"))
        if not d:
            blank_doi += 1
        else:
            by_doi[d].append(sid)
        if not zk:
            blank_zk += 1
        else:
            by_zk[zk].append(sid)
        if title:
            by_title[title].append(sid)

    doi_dups = {d: ids for d, ids in by_doi.items() if len(ids) > 1}
    zk_dups = {z: ids for z, ids in by_zk.items() if len(ids) > 1}
    title_dups = {t: ids for t, ids in by_title.items() if len(ids) > 1}

    summary = {
        "script": "v9_bridge",
        "timestamp_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "bridge_path": str(BRIDGE.relative_to(REPO_ROOT)).replace("\\", "/"),
        "row_count": len(rows),
        "blank_doi_count": blank_doi,
        "blank_zotero_key_count": blank_zk,
        "doi_collision_count": len(doi_dups),
        "zotero_key_collision_count": len(zk_dups),
        "title_collision_count": len(title_dups),
        "doi_collisions": doi_dups,
        "zotero_key_collisions": zk_dups,
        "title_collisions_first20": dict(list(title_dups.items())[:20]),
    }
    out = REPORT_DIR / f"v9_bridge_{_dt.date.today().isoformat()}.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"V9 bridge audit: {len(rows)} rows")
    print(f"  blank DOI:               {blank_doi}")
    print(f"  blank Zotero key:        {blank_zk}")
    print(f"  DOI collisions:          {len(doi_dups)}")
    print(f"  Zotero-key collisions:   {len(zk_dups)}")
    print(f"  title-string collisions: {len(title_dups)}")
    print(f"  report: {out.relative_to(REPO_ROOT)}")
    if doi_dups:
        print(f"  first DOI collision: {next(iter(doi_dups.items()))}")
    # Always 0 (informational); the report is the deliverable.
    return 0


if __name__ == "__main__":
    sys.exit(main())
