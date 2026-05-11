"""Verify NON_FINANCE + NO_QUANTUM_CONTENT classifications with stronger regex."""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
data = json.loads((REPO / "p2_systematic_review" / "output" / "audit" / "triage_classification.json").read_text())
text_dir = REPO / "shared" / "extracted_text" / "text"

finance_strong = re.compile(
    r"\b(portfolio optim|stock price|option pricing|credit risk|fraud detection|"
    r"Value[- ]at[- ]Risk|VaR|CVaR|Sharpe|Black[- ]Scholes|yield curve|"
    r"derivative pric|bankrupt|hedging|loan|mortgage|stock market)",
    re.I,
)
quantum_strong = re.compile(
    r"\b(QAOA|VQE|variational quantum eigensolver|quantum approximate optim|"
    r"quantum amplitude|HHL|Grover|Shor|QFT|QGAN|QSVM|quantum neural network|"
    r"parameterized quantum circuit|ansatz)",
    re.I,
)

for e in data:
    if e.get("class") not in ("NON_FINANCE", "NO_QUANTUM_CONTENT"):
        continue
    pid = e["pid"]
    mds = list(text_dir.glob(f"{pid}*.md"))
    if not mds:
        continue
    t = mds[0].read_text(encoding="utf-8", errors="replace")
    fhits = finance_strong.findall(t)
    qhits = quantum_strong.findall(t)
    print(
        f"{pid}  {e['class']:<20}  size={e['size']:>8}  "
        f"fin={len(fhits):>3}  q={len(qhits):>3}  {mds[0].name[:80]}"
    )
    if fhits[:3]:
        print(f"       fin hits: {list(set(fhits))[:5]}")
    if qhits[:3]:
        print(f"       q   hits: {list(set(qhits))[:5]}")
