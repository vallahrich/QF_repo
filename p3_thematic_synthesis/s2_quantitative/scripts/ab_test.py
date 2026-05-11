"""A/B/C test for P3 quantitative extraction pipeline.

Compares three model strategies on the same 5 papers:
  A: gpt-5-mini (all 5 steps)
  B: gpt-5.1-batch (all 5 steps)  
  C: Hybrid — gpt-5-mini steps 1-4, gpt-5.1-batch step 5

Outputs per-paper comparison: experiment count, field completeness,
quote count, quality score, and estimated cost.

Usage:
    python -m p3_thematic_synthesis.s2_quantitative.scripts.ab_test
    python -m p3_thematic_synthesis.s2_quantitative.scripts.ab_test --model-b gpt-5.1
"""

import argparse
import json
import sys
import time
from datetime import date
from pathlib import Path

_QUANT_ROOT = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_project_root_str = str(_PROJECT_ROOT)
if _project_root_str not in sys.path:
    sys.path.insert(0, _project_root_str)
elif sys.path[0] != _project_root_str:
    sys.path.remove(_project_root_str)
    sys.path.insert(0, _project_root_str)

_shared_mod = sys.modules.get("shared")
if _shared_mod is not None:
    _shared_file = getattr(_shared_mod, "__file__", None) or ""
    if _PROJECT_ROOT.as_posix() not in Path(_shared_file).as_posix() if _shared_file else True:
        for _key in [k for k in sys.modules if k == "shared" or k.startswith("shared.")]:
            del sys.modules[_key]

from shared.tools.llm_client import LLMClient  # noqa: E402
from shared.tools.text_chunker import truncate_tokens  # noqa: E402

from p3_thematic_synthesis.s2_quantitative.scripts.run_extraction import (  # noqa: E402
    build_work_manifest,
    load_config,
    load_prompt,
    load_silo_metrics,
    merge_steps,
    run_step2,
    run_step3,
    run_step4,
    run_step5,
    _parse_json,
    _llm_call_with_retry,
    _save_result,
)

# Test papers: 2 small, 2 medium from portfolio-optimization
TEST_PAPERS = [
    "c07bf2c04ef9",  # 2.8 KB - small
    "d18096ef8f4c",  # 25.7 KB - small
    "d3580aed27bb",  # 35.0 KB - medium
    "7bdb6593ec48",  # 46.5 KB - medium
]

# Pricing per 1M tokens (Global Standard)
PRICING = {
    "gpt-5-mini":    {"input": 0.25,  "cached": 0.03,  "output": 2.00},
    "gpt-5.1-batch": {"input": 0.63,  "cached": 0.07,  "output": 5.00},
    "gpt-5.1":       {"input": 1.25,  "cached": 0.13,  "output": 10.00},
    "gpt-5.2":       {"input": 1.75,  "cached": 0.18,  "output": 14.00},
}

TEXT_DIR = _PROJECT_ROOT / "shared" / "extracted_text" / "text"
OUTPUT_DIR = _QUANT_ROOT / "output" / "ab_test"


def estimate_cost(model: str, input_tokens: int, cached_tokens: int,
                  output_tokens: int) -> float:
    """Estimate cost in USD."""
    p = PRICING.get(model, PRICING["gpt-5-mini"])
    return (input_tokens * p["input"] + cached_tokens * p["cached"] +
            output_tokens * p["output"]) / 1_000_000


def count_fields(data: dict) -> dict:
    """Count completeness of extracted data."""
    exps = data.get("experiments", [])
    n_exp = len(exps)
    n_results = sum(len(e.get("results", [])) for e in exps)
    n_baselines = sum(len(e.get("classical_baselines", [])) for e in exps)
    n_speedup = sum(len(e.get("speedup_claims", [])) for e in exps)
    n_scalability = sum(len(e.get("scalability_data", [])) for e in exps)

    # Count non-null fields in key sections
    resource_fields = 0
    for e in exps:
        qr = e.get("quantum_resources", {})
        for v in qr.values():
            if v is not None and v != {} and v != []:
                resource_fields += 1
        hw = e.get("hardware", {})
        for v in hw.values():
            if v is not None:
                resource_fields += 1
        ca = e.get("complexity_analysis") or {}
        for v in ca.values():
            if v is not None:
                resource_fields += 1

    has_advantage = sum(1 for e in exps
                        if (e.get("advantage_assessment") or {}).get("advantage_status"))

    return {
        "experiments": n_exp,
        "results": n_results,
        "baselines": n_baselines,
        "speedup_claims": n_speedup,
        "scalability_points": n_scalability,
        "resource_fields": resource_fields,
        "advantage_assessed": has_advantage,
    }


def run_pipeline_variant(client: LLMClient, entry: dict, config: dict,
                         silo_metrics: dict, model_steps14: str,
                         model_step5: str) -> tuple[dict, dict]:
    """Run 5-step pipeline with specified models. Returns (result, stats)."""
    paper_id = entry["paper_id"]
    text_path = None
    for tp in TEXT_DIR.glob(f"{paper_id}*"):
        text_path = tp
        break
    if not text_path:
        return {}, {"error": "no text file"}

    text = text_path.read_text("utf-8", errors="replace")
    text = truncate_tokens(text, config.get("input_token_limit", 60000))
    text_tokens = len(text) // 4

    stats = {
        "paper_id": paper_id,
        "text_chars": len(text),
        "text_tokens": text_tokens,
        "steps_ok": [],
        "steps_failed": [],
        "total_time": 0,
    }

    t0 = time.time()

    # Override model in config for steps 1-4
    cfg14 = {**config, "model": model_steps14}
    cfg5 = {**config, "model": model_step5}

    try:
        # Step 2 (P2 already confirmed has_quantitative_results)
        step2 = run_step2(client, text, entry, cfg14)
        n_exps = len(step2.get("experiments", []))
        stats["quotes"] = n_exps  # reuse field for comparison
        stats["steps_ok"].append(2)
        print(f"    step2: {n_exps} experiments")

        if n_exps == 0:
            stats["total_time"] = time.time() - t0
            return {"paper_id": paper_id, "has_quantitative_results": False,
                    "experiments": []}, stats

        # Step 3
        step3 = run_step3(client, text, step2, entry, cfg14, silo_metrics)
        stats["steps_ok"].append(3)
        print(f"    step3: silo results OK")

        # Step 4
        step4 = run_step4(client, text, step2, cfg14)
        stats["steps_ok"].append(4)
        print(f"    step4: resources OK")

        # Step 5 (possibly different model)
        pre_merged = {"experiments": step2.get("experiments", []),
                      "results": step3, "resources": step4}
        step5 = run_step5(client, pre_merged, entry, cfg5, silo_metrics)
        stats["steps_ok"].append(5)
        confidence = step5.get("extraction_confidence", 0)
        stats["confidence"] = confidence
        print(f"    step5: confidence={confidence:.2f}")

        result = merge_steps(step2, step3, step4, step5, entry, cfg14)
        stats["total_time"] = time.time() - t0

        # Estimate cost (4 LLM calls: steps 2-5)
        uncached = text_tokens + 2 * 2000 + 3000  # step instructions + step 5
        cached = 2 * text_tokens  # steps 3-4 cached paper text
        output = 3000 + 3000 + 3000 + 2000  # rough per-step output
        stats["cost_usd"] = (estimate_cost(model_steps14, uncached, cached, output - 2000) +
                             estimate_cost(model_step5, 3000, 0, 2000))

        return result, stats

    except Exception as e:
        stats["error"] = str(e)[:200]
        stats["total_time"] = time.time() - t0
        print(f"    ERROR: {str(e)[:100]}")
        return {}, stats


def main():
    parser = argparse.ArgumentParser(description="A/B/C test for P3 quantitative extraction")
    parser.add_argument("--model-a", default="gpt-5-mini", help="Model A (default: gpt-5-mini)")
    parser.add_argument("--model-b", default="gpt-5.1-batch", help="Model B (default: gpt-5.1-batch)")
    args = parser.parse_args()

    model_a = args.model_a
    model_b = args.model_b

    print(f"=== P3 Quantitative A/B/C Test ===")
    print(f"  A: {model_a} (all 5 steps)")
    print(f"  B: {model_b} (all 5 steps)")
    print(f"  C: Hybrid ({model_a} steps 1-4, {model_b} step 5)")
    print(f"  Papers: {len(TEST_PAPERS)} from portfolio-optimization")
    print()

    config = load_config()
    silo_metrics = load_silo_metrics()
    manifest = build_work_manifest()

    # Find test paper entries
    manifest_map = {e["paper_id"]: e for e in manifest}
    test_entries = []
    for pid in TEST_PAPERS:
        if pid in manifest_map:
            test_entries.append(manifest_map[pid])
        else:
            print(f"WARNING: {pid} not found in manifest, skipping")

    if not test_entries:
        print("No test papers found!")
        sys.exit(1)

    client = LLMClient()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = {"A": [], "B": [], "C": []}

    from concurrent.futures import ThreadPoolExecutor, as_completed

    for entry in test_entries:
        pid = entry["paper_id"]
        print(f"\n{'='*60}")
        print(f"Paper: {pid} | silo={entry['primary_silo']}")
        print(f"  Running A/B/C in parallel...")
        print(f"{'='*60}")

        variants = [
            ("A", model_a, model_a),
            ("B", model_b, model_b),
            ("C", model_a, model_b),
        ]

        def _run_variant(args):
            variant, m14, m5 = args
            print(f"\n  --- Variant {variant} (steps1-4={m14}, step5={m5}) ---")
            result, stats = run_pipeline_variant(client, entry, config,
                                                  silo_metrics, m14, m5)
            stats["variant"] = variant
            stats["fields"] = count_fields(result)
            out_path = OUTPUT_DIR / f"{pid}_{variant}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False, default=str)
            return variant, stats

        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(_run_variant, v): v[0] for v in variants}
            for future in as_completed(futures):
                try:
                    variant, stats = future.result()
                    all_results[variant].append(stats)
                except Exception as exc:
                    v = futures[future]
                    print(f"  Variant {v} ERROR: {exc}")
                    all_results[v].append({"paper_id": pid, "error": str(exc)[:200], "fields": {}})

            all_results[variant].append(stats)

    # Print comparison table
    print(f"\n\n{'='*80}")
    print("COMPARISON SUMMARY")
    print(f"{'='*80}")
    print(f"\n{'Paper':<14} {'Var':>3} {'Quotes':>7} {'Exps':>5} {'Results':>8} "
          f"{'Baselines':>10} {'Resources':>10} {'Adv':>4} {'Conf':>5} "
          f"{'Time':>6} {'Cost':>7}")
    print("-" * 95)

    for pid in TEST_PAPERS:
        for variant in ["A", "B", "C"]:
            stats_list = [s for s in all_results[variant] if s.get("paper_id") == pid]
            if not stats_list:
                continue
            s = stats_list[0]
            f = s.get("fields", {})
            print(f"{pid[:12]:<14} {variant:>3} {s.get('quotes',0):>7} "
                  f"{f.get('experiments',0):>5} {f.get('results',0):>8} "
                  f"{f.get('baselines',0):>10} {f.get('resource_fields',0):>10} "
                  f"{f.get('advantage_assessed',0):>4} {s.get('confidence',0):>5.2f} "
                  f"{s.get('total_time',0):>5.1f}s "
                  f"${s.get('cost_usd',0):>5.3f}")
        print()

    # Aggregate per variant
    print(f"\n{'='*60}")
    print("AGGREGATE")
    print(f"{'='*60}")
    for variant in ["A", "B", "C"]:
        vr = all_results[variant]
        if not vr:
            continue
        total_exp = sum(s.get("fields", {}).get("experiments", 0) for s in vr)
        total_res = sum(s.get("fields", {}).get("results", 0) for s in vr)
        total_bl = sum(s.get("fields", {}).get("baselines", 0) for s in vr)
        total_rf = sum(s.get("fields", {}).get("resource_fields", 0) for s in vr)
        total_adv = sum(s.get("fields", {}).get("advantage_assessed", 0) for s in vr)
        avg_conf = sum(s.get("confidence", 0) for s in vr) / max(len(vr), 1)
        total_time = sum(s.get("total_time", 0) for s in vr)
        total_cost = sum(s.get("cost_usd", 0) for s in vr)
        total_ok = sum(len(s.get("steps_ok", [])) for s in vr)
        total_fail = sum(len(s.get("steps_failed", [])) for s in vr)
        n_errors = sum(1 for s in vr if "error" in s)

        print(f"\n  Variant {variant}:")
        print(f"    Experiments: {total_exp} | Results: {total_res} | "
              f"Baselines: {total_bl} | Resources: {total_rf}")
        print(f"    Advantage assessed: {total_adv} | Avg confidence: {avg_conf:.2f}")
        print(f"    Steps OK: {total_ok} | Errors: {n_errors}")
        print(f"    Total time: {total_time:.1f}s | Cost (5 papers): ${total_cost:.3f}")
        # Project to 580 papers
        cost_580 = total_cost / max(len(vr), 1) * 580
        print(f"    Projected cost (580 papers): ${cost_580:.2f} (~EUR{cost_580*0.92:.2f})")

    # Save full results
    summary_path = OUTPUT_DIR / "ab_test_results.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nFull results saved to {summary_path}")


if __name__ == "__main__":
    main()
