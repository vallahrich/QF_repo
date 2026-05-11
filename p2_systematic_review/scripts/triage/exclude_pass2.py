"""Second-pass triage: move 9 verified OOS papers to excluded_papers.csv."""
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXTRACTIONS = ROOT / "p3_thematic_synthesis" / "quantitative" / "output" / "extractions"
EXCLUDED_CSV = ROOT / "shared" / "bridge" / "excluded_papers.csv"

# Reviewed 2026-04-17: these are confirmed out-of-scope
DECISIONS = [
    # (pid, reason, note, short_title)
    ("11807719b419", "scope_out_non_finance", "quantum foundations / non-contextuality; no finance content", "Testing quantum theory by generalizing noncontextuality"),
    ("55025d58c227", "scope_out_non_finance", "quantum decoherence simulator / fractal correction; no finance content", "Recursive Quantum Decoherence simulator"),
    ("2f9096b00d49", "scope_out_non_finance", "VMC scalability for condensed matter; no finance content", "Overcoming barriers to scalability in variational quantum Monte Carlo"),
    ("862fc759b55d", "scope_out_non_finance", "alternative sampling for VMC condensed matter; no finance content", "Alternative sampling for variational quantum Monte Carlo"),
    ("c7e723b86ecc", "scope_out_non_finance", "VMC quasiparticle effective mass 2D fluid; no finance content", "VMC study of quasiparticle effective mass"),
    ("3432da9937d2", "scope_out_non_finance", "LNCS proceedings volume; target paper is 2D HP protein folding not finance", "2D HP Model quantum evolutionary algorithm"),
    ("aa5b834c3a1d", "scope_out_non_finance", "quantum-semantic stability framework; uses CVaR terminology but not finance", "Antifragile Quantum-Semantic Systems via CVaR-POVM"),
    ("cb7047eb4b01", "scope_out_non_finance", "SlimeLearning vs VAE disentanglement for representation learning; not finance", "Deterministic Commutative Normalization (SlimeLearning)"),
    ("e52f3f130a75", "scope_out_non_finance", "generic hybrid quantum-classical workload partitioning; not finance application", "SparseEA-AGDS hybrid workload partitioning"),
    ("c65b93ca030a", "scope_out_quantum_inspired", "quantum-inspired jaguar algorithm (classical simulation); uses portfolio as benchmark but no gate-based quantum computation", "Quantum-inspired Jaguar Algorithm for combinatorial optimization"),
]


def load_existing_ids() -> set[str]:
    ids = set()
    if not EXCLUDED_CSV.exists():
        return ids
    with EXCLUDED_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.reader(f):
            if row and row[0] and row[0] != "paper_id":
                ids.add(row[0])
    return ids


def main() -> None:
    existing = load_existing_ids()
    today = date.today().isoformat()
    new_rows = []
    for pid, reason, note, title in DECISIONS:
        if pid in existing:
            # ensure JSON removed
            jp = EXTRACTIONS / f"{pid}.json"
            if jp.exists():
                jp.unlink()
            continue
        note_full = f"{note}; triaged 2026-04-17 (manual review pass 2)"
        safe_title = title.replace(",", ";")
        new_rows.append(f"{pid},{safe_title},,,{reason},{note_full},{today}")
        jp = EXTRACTIONS / f"{pid}.json"
        if jp.exists():
            jp.unlink()

    if new_rows:
        with EXCLUDED_CSV.open("a", encoding="utf-8", newline="") as f:
            for row in new_rows:
                f.write(row + "\n")

    print(f"rows added: {len(new_rows)}")
    print(f"total in excluded_papers.csv: {len(load_existing_ids())}")


if __name__ == "__main__":
    main()
