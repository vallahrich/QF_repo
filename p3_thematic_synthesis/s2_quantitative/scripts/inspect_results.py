"""Inspect extraction results — show what data was captured per paper."""

import json
import os
import sys
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
EXT_DIR = _QUANT_ROOT / "output" / "extractions"


def inspect_all():
    jsons = sorted(
        f for f in os.listdir(EXT_DIR)
        if f.endswith(".json") and not f.startswith("_")
    )
    print(f"=== {len(jsons)} EXTRACTION FILES ===\n")

    total_numeric = 0
    total_baselines = 0
    total_experiments = 0
    missing_qubits = 0
    missing_depth = 0
    missing_hardware = 0
    missing_baselines = 0
    papers_with_summary = 0

    for fn in jsons:
        with open(EXT_DIR / fn, encoding="utf-8") as f:
            d = json.load(f)

        pid = d.get("paper_id", "?")
        silo = (d.get("finance_domain") or {}).get("primary_silo", "?")
        title = (d.get("paper_metadata") or {}).get("title", "?")[:55]
        has_q = d.get("has_quantitative_results", False)
        summary = d.get("summary") or ""
        q_score = (d.get("extraction_metadata") or {}).get("quality_score")

        if not has_q:
            print(f"[SKIP] {pid} | {silo} | Non-quantitative | {title}")
            continue

        if summary:
            papers_with_summary += 1

        print(f"--- {pid} [{silo}] quality={q_score} ---")
        print(f"  Title: {title}")
        if summary:
            print(f"  Summary: {summary[:140]}")

        for i, exp in enumerate(d.get("experiments", [])):
            total_experiments += 1
            algo = (exp.get("algorithm") or {}).get("family", "?")
            variant = (exp.get("algorithm") or {}).get("variant") or ""
            qr = exp.get("quantum_resources") or {}
            hw = exp.get("hardware") or {}
            hw_type = hw.get("type") or "?"
            provider = hw.get("provider") or ""
            pi = exp.get("problem_instance") or {}

            qubits = qr.get("num_qubits")
            depth = qr.get("circuit_depth")
            shots = qr.get("num_shots")

            if qubits is None:
                missing_qubits += 1
            if depth is None:
                missing_depth += 1
            if hw_type in ("?", "not_specified"):
                missing_hardware += 1

            # Count results
            numeric_res = [
                (r["metric_name"], r["value"])
                for r in exp.get("results", [])
                if isinstance(r.get("value"), (int, float))
            ]
            string_res = [
                (r["metric_name"], str(r["value"])[:40])
                for r in exp.get("results", [])
                if isinstance(r.get("value"), str)
            ]
            baselines = [
                (b.get("method_name", "?")[:25], b.get("metric_name", "?"), b.get("value"))
                for b in exp.get("classical_baselines", [])
            ]
            speedups = [
                (s.get("type", "?"), s.get("factor"), s.get("is_demonstrated"))
                for s in exp.get("speedup_claims", [])
            ]

            total_numeric += len(numeric_res)
            total_baselines += len(baselines)
            if not baselines:
                missing_baselines += 1

            # Problem size
            size_parts = []
            if pi.get("num_assets"):
                size_parts.append(f"{pi['num_assets']} assets")
            if pi.get("dataset_size"):
                size_parts.append(f"{pi['dataset_size']} samples")
            if pi.get("num_features"):
                size_parts.append(f"{pi['num_features']} features")
            problem_size = ", ".join(size_parts) if size_parts else "not specified"

            print(f"  Exp {i+1}: {algo}" + (f" ({variant[:30]})" if variant else ""))
            print(f"    HW: {hw_type} {provider} | Qubits: {qubits} | Depth: {depth} | Shots: {shots}")
            print(f"    Problem: {problem_size}")
            if numeric_res:
                print(f"    Results ({len(numeric_res)} numeric): {numeric_res[:5]}")
            if string_res:
                print(f"    Results ({len(string_res)} string): {string_res[:3]}")
            if baselines:
                bl_display = [(m, n, v) for m, n, v in baselines[:3]]
                print(f"    Baselines ({len(baselines)}): {bl_display}")
            else:
                print(f"    Baselines: NONE")
            if speedups:
                print(f"    Speedup: {speedups}")
        print()

    print("=" * 60)
    print("SUMMARY")
    print(f"  Total experiments: {total_experiments}")
    print(f"  Total numeric results: {total_numeric}")
    print(f"  Total baselines: {total_baselines}")
    print(f"  Papers with summary: {papers_with_summary}")
    print(f"  Missing qubits: {missing_qubits}/{total_experiments}")
    print(f"  Missing depth: {missing_depth}/{total_experiments}")
    print(f"  Missing hardware spec: {missing_hardware}/{total_experiments}")
    print(f"  Missing baselines: {missing_baselines}/{total_experiments}")


if __name__ == "__main__":
    inspect_all()
