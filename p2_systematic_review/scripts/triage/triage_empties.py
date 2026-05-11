"""Triage the 63 empty-experiment papers by keyword signatures.

Classifies each paper into categories to decide which need full manual
extraction (likely has results) vs which are correctly flagged as empty
(out of scope, survey, position paper, etc.).

Usage:
    python triage_empties.py
"""
import re
import json
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TARGETS_FILE = REPO / "p2_systematic_review" / "output" / "audit" / "manual_extraction_targets.txt"
TEXT_DIR = REPO / "shared" / "extracted_text" / "text"
P2_DIR = REPO / "p2_systematic_review" / "output" / "processed"
OUTPUT_FILE = REPO / "p2_systematic_review" / "output" / "audit" / "triage_classification.json"

FAILED = {"0fb65bb44954", "48cd8220e3b2", "bcd1adfba1e5"}

FINANCE_KW = re.compile(
    r"\b(portfolio|stock|asset|market|option|derivative|volatilit|returns|sharpe|"
    r"risk|credit|fraud|financ|insurance|banking|trading|VaR|CVaR|hedge|arbitrage|"
    r"investment|lending|bond|equity|blockchain|cryptocurr)",
    re.I,
)
QUANT_KW = re.compile(
    r"\b(accuracy|MAE|MSE|RMSE|R\^?2|fidelity|approximation ratio|F1|AUC|precision|"
    r"recall|confusion matrix|speed-?up|runtime|execution time|optimality gap|"
    r"ground state probability|success probability|KL divergence|loss)\b",
    re.I,
)
QPU_KW = re.compile(
    r"\b(qubit|QAOA|VQE|QFT|Grover|Shor|HHL|amplitude estimation|quantum circuit|"
    r"quantum simulator|quantum annealer|IBM.?Q|IonQ|Rigetti|Xanadu|Quantinuum|"
    r"superconducting|trapped[ -]?ion|statevector)",
    re.I,
)
NUMERIC_RESULT = re.compile(r"[0-9]+\.[0-9]+\s*(%|percent|ratio|sec|minutes|hours|dB)")
OOS = re.compile(
    r"\b(protein folding|medical (diagnosis|imaging)|healthcare diagnostics|"
    r"autonomous (vehicle|driving)|neocortex|cognition|cosmolog|atmospher|"
    r"weather|climate|nor.?easter|quantum chemistry|condensed matter|"
    r"exciton|solid[ -]?state|fermi gas|wigner crystal|HP model|"
    r"coherence-gated|dimensional access)",
    re.I,
)


def classify(pid: str) -> dict:
    mds = list(TEXT_DIR.glob(f"{pid}*.md"))
    if not mds:
        return {"pid": pid, "class": "NO_MARKDOWN"}
    md = mds[0]
    t = md.read_text(encoding="utf-8", errors="replace")
    first2k = t[:2500]

    p2_files = list(P2_DIR.glob(f"{pid}*.json"))
    p2_title = ""
    p2_silo = None
    if p2_files:
        try:
            d = json.loads(p2_files[0].read_text(encoding="utf-8"))
            p2_title = (d.get("title") or "")[:90]
            tags = d.get("topic_tags") or []
            if tags:
                p2_silo = tags[0]
        except Exception:
            pass

    oos_match = OOS.search(first2k)
    has_finance = bool(FINANCE_KW.search(first2k))
    has_qpu = bool(QPU_KW.search(t))
    has_quant = bool(QUANT_KW.search(t))
    has_numeric = bool(NUMERIC_RESULT.search(t))
    size = md.stat().st_size

    if oos_match:
        klass = "OUT_OF_SCOPE"
    elif size < 8000:
        klass = "TOO_SHORT_abstract_only"
    elif not has_finance:
        klass = "NON_FINANCE"
    elif not has_qpu:
        klass = "NO_QUANTUM_CONTENT"
    elif not has_quant and not has_numeric:
        klass = "NO_QUANT_METRICS"
    elif has_finance and has_qpu and has_quant and has_numeric:
        klass = "LIKELY_HAS_RESULTS"
    else:
        klass = "BORDERLINE"

    return {
        "pid": pid,
        "class": klass,
        "size": size,
        "title": p2_title,
        "p2_silo": p2_silo,
        "oos_hit": oos_match.group(0) if oos_match else "",
        "has_finance": has_finance,
        "has_qpu": has_qpu,
        "has_quant": has_quant,
        "has_numeric": has_numeric,
    }


def main() -> None:
    empties = [
        line
        for line in TARGETS_FILE.read_text().splitlines()
        if line and line not in FAILED
    ]
    out = [classify(pid) for pid in empties]
    OUTPUT_FILE.write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )

    summary = Counter(x["class"] for x in out)
    print("=== CLASSIFICATION SUMMARY ===")
    for k, v in sorted(summary.items(), key=lambda x: -x[1]):
        print(f"  {v:3d}  {k}")
    print()

    for cls in [
        "LIKELY_HAS_RESULTS",
        "BORDERLINE",
        "NO_QUANT_METRICS",
        "NO_QUANTUM_CONTENT",
        "NON_FINANCE",
        "TOO_SHORT_abstract_only",
        "OUT_OF_SCOPE",
    ]:
        matches = [e for e in out if e["class"] == cls]
        if not matches:
            continue
        print(f"--- {cls} ({len(matches)}) ---")
        for e in matches:
            oos = f"  [oos:{e['oos_hit']}]" if e["oos_hit"] else ""
            print(f"  {e['pid']}  {e['size']:>8}  {e['title']}{oos}")
        print()


if __name__ == "__main__":
    main()
