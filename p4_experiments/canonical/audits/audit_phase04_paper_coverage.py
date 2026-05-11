"""Audit: do all Phase-4 P-tier labels have a real paper backing?

Phase 4 generates label-specific proxy justification files for every
Proxy-tier (P) label (70 of 71). For each P label the cohort entry should carry:
  * paper_id            (non-empty)
  * paper_metadata.title (non-empty, real title)
  * a citation we can resolve: doi OR arxiv_id  OR a recognisable
    legacy/transplant/deliverable identifier
    * P3 S2 quantitative extraction present for paper_id + experiment_id
    * <circuit_dir>/proxy_justification_<label>.md present (Phase 4 writes it)

This script reports any P-tier label missing any of these and prints
totals so we know if "everything in Phase 4 has a paper".
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CANON = ROOT / "p4_experiments" / "canonical"

from p4_experiments.canonical.data.s2_extraction_index import has_s2_experiment

cohort = json.loads((CANON / "cohort.json").read_text(encoding="utf-8"))
labels = cohort["labels"]

p_labels = {lid: e for lid, e in labels.items() if e.get("fidelity") == "P"}
f_labels = {lid: e for lid, e in labels.items() if e.get("fidelity") == "F"}

# P-tier labels without an on-disk circuit_path are out of Phase 4 scope;
# phase4_generate_proxy_justifications.py explicitly skips them.
no_circuit_path_p = {lid for lid, e in p_labels.items() if not e.get("circuit_path")}
p_labels_in_scope = {lid: e for lid, e in p_labels.items() if lid not in no_circuit_path_p}

print(f"N labels total : {len(labels)}")
print(f"  Faithful (F) : {len(f_labels)}  -> not in Phase 4 scope")
print(f"  Proxy    (P) : {len(p_labels)}  -> Phase 4 scope")
print(f"    of which have no circuit_path and are skipped by Phase 4: {len(no_circuit_path_p)}")
print(f"    in scope for paper-coverage check: {len(p_labels_in_scope)}")
print()

issues_no_pid       = []
issues_no_title     = []
issues_no_real_title= []  # title looks like a placeholder
issues_no_citation  = []  # neither doi nor arxiv nor recognised legacy id
issues_no_extraction= []
issues_no_pj_md     = []

LEGACY_PID_PREFIXES = ("legacy-", "transplant-", "deliverable-", "operator-")

for lid, e in p_labels_in_scope.items():
    pid  = e.get("paper_id") or ""
    meta = e.get("paper_metadata") or {}
    title    = (meta.get("title") or "").strip()
    doi      = (meta.get("doi") or "").strip()
    arxiv    = (meta.get("arxiv_id") or meta.get("arxiv") or "").strip()
    authors  = meta.get("authors") or []
    year     = meta.get("year")

    if not pid:
        issues_no_pid.append(lid)
    if not title:
        issues_no_title.append(lid)
    elif title.lower().startswith(("(legacy", "(transplant", "(deliverable", "tba", "n/a")):
        issues_no_real_title.append((lid, title[:60]))

    is_legacy_pid = any(pid.startswith(p) for p in LEGACY_PID_PREFIXES)
    has_citation  = bool(doi or arxiv or is_legacy_pid)
    if not has_citation:
        issues_no_citation.append((lid, pid, title[:60]))

    # P3 S2 extraction file + experiment_id present?
    if not has_s2_experiment(e):
        issues_no_extraction.append(lid)

    # proxy_justification.md present where Phase 4 wrote it?
    # Cohort records the resolved path in `proxy_justification_path`;
    # `circuit_dir` is silo-relative and does NOT include the
    # p4_experiments/ prefix that Phase 4 actually used.
    pj_path = e.get("proxy_justification_path")
    if pj_path:
        pj = ROOT / pj_path
        if not pj.exists():
            issues_no_pj_md.append((lid, pj_path))
    else:
        issues_no_pj_md.append((lid, "<no proxy_justification_path in cohort>"))

# ------------------------------------------------------------------ report
print(f"P-tier labels checked: {len(p_labels_in_scope)}")
print(f"  missing paper_id          : {len(issues_no_pid):>3}")
print(f"  missing paper_metadata.title: {len(issues_no_title):>3}")
print(f"  placeholder title         : {len(issues_no_real_title):>3}")
print(f"  missing citation (doi+arxiv+legacy-pid): {len(issues_no_citation):>3}")
print(f"  missing P3 S2 paper/experiment source : {len(issues_no_extraction):>3}")
print(f"  missing proxy_justification.md        : {len(issues_no_pj_md):>3}")
print()

if issues_no_pid:
    print("[FAIL] missing paper_id:")
    for x in issues_no_pid: print("  ", x)
    print()
if issues_no_title:
    print("[FAIL] missing title:")
    for x in issues_no_title: print("  ", x)
    print()
if issues_no_real_title:
    print("[WARN] placeholder-looking title:")
    for lid, t in issues_no_real_title: print(f"  {lid} -> {t!r}")
    print()
if issues_no_citation:
    print(f"[INFO] {len(issues_no_citation)} P-tier labels carry no DOI / arXiv ID / legacy-prefixed paper_id:")
    for lid, pid, t in issues_no_citation:
        print(f"  {lid:<6} pid={pid:<24} title={t}")
    print()
if issues_no_extraction:
    print(f"[FAIL] {len(issues_no_extraction)} P-tier labels missing P3 S2 paper/experiment source:")
    for x in issues_no_extraction: print("  ", x)
    print()
if issues_no_pj_md:
    print(f"[FAIL] {len(issues_no_pj_md)} P-tier labels missing proxy_justification.md:")
    for lid, path in issues_no_pj_md: print(f"  {lid:<6} -> {path}")
    print()

print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
all_ok = (
    not issues_no_pid and
    not issues_no_title and
    not issues_no_extraction and
    not issues_no_pj_md
)
if all_ok:
        print("PASS: every P-tier label in Phase 4 has paper_id, title,"
            " P3 S2 source, and proxy_justification.md.")
else:
    print("FAIL: see issues above.")
print()
print(f"Citation-quality note: {len(issues_no_citation)}/{len(p_labels_in_scope)} P-tier")
print("labels carry no DOI nor arXiv ID nor a 'legacy-/transplant-/deliverable-'")
print("prefixed paper_id — paper_id is a hash but the entry still has a real")
print("title + authors + year. Whether that counts as 'has a paper' is a")
print("citation-quality question, not a Phase-4-completeness question.")

# ------------------------------------------------------------------ machine-readable summary
import sys
import datetime as _dt

_n_blocking = (
    len(issues_no_pid) + len(issues_no_title)
    + len(issues_no_extraction) + len(issues_no_pj_md)
)
_report = {
    "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(),
    "phase": "phase4_paper_coverage",
    "n_labels": len(labels),
    "n_p_tier": len(p_labels),
    "n_p_tier_in_scope": len(p_labels_in_scope),
    "n_p_tier_no_circuit_path_skipped": len(no_circuit_path_p),
    "n_f_tier": len(f_labels),
    "issues": {
        "no_paper_id": issues_no_pid,
        "no_title": issues_no_title,
        "placeholder_title": [lid for lid, _ in issues_no_real_title],
        "no_citation": [lid for lid, _, _ in issues_no_citation],
        "no_p3_s2_source": issues_no_extraction,
        "no_proxy_justification_md": [lid for lid, _ in issues_no_pj_md],
    },
    "totals": {
        "pass": 4 - sum(1 for n in (
            len(issues_no_pid), len(issues_no_title),
            len(issues_no_extraction), len(issues_no_pj_md),
        ) if n > 0),
        "fail": sum(1 for n in (
            len(issues_no_pid), len(issues_no_title),
            len(issues_no_extraction), len(issues_no_pj_md),
        ) if n > 0),
        "blockers_failed": _n_blocking,
        "info": len(issues_no_citation) + len(issues_no_real_title),
    },
}
_report_path = CANON / "reports" / "audit" / "audit_phase4_paper_coverage.json"
_report_path.parent.mkdir(parents=True, exist_ok=True)
_report_path.write_text(
    json.dumps(_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"[Phase 4 paper-coverage audit] Report -> {_report_path.relative_to(ROOT)}")
sys.exit(0 if _n_blocking == 0 else 1)
