"""Bug analysis script for P3 quantitative folder."""
import re
from pathlib import Path

QUANT = Path("p3_thematic_synthesis/s2_quantitative")

print("=== 1. Prompt Format Tests ===")
for pf in sorted(QUANT.glob("prompts/step*.txt")):
    text = pf.read_text()
    placeholders = set(re.findall(r'(?<!\{)\{(\w+)\}(?!\})', text))
    try:
        kwargs = {p: "TEST" for p in placeholders}
        text.format(**kwargs)
        print(f"  {pf.name}: OK — vars: {sorted(placeholders)}")
    except Exception as e:
        print(f"  {pf.name}: BROKEN — {e}")

print("\n=== 2. run_extraction.py Analysis ===")
src = (QUANT / "scripts/run_extraction.py").read_text()

# What keys does the code read from step1?
step1_gets = set(re.findall(r'step1\.get\("(\w+)"', src) + re.findall(r"step1\.get\('(\w+)'", src))
print(f"  step1.get() keys: {sorted(step1_gets)}")

# What keys does step1 prompt produce? (from the JSON example in prompt)
s1_prompt = (QUANT / "prompts/step1_evidence.txt").read_text()
s1_output_keys = re.findall(r'"(\w+)":\s', s1_prompt)
print(f"  step1 prompt output keys: {sorted(set(s1_output_keys))}")

# Do they match?
expected_from_code = {"has_quantitative_results", "estimated_experiment_count", "brief_summary", "quotes"}
produced_by_prompt = set(s1_output_keys)
missing = expected_from_code - produced_by_prompt
extra = produced_by_prompt - expected_from_code
if missing:
    print(f"  BUG: code expects but prompt doesn't produce: {missing}")
if extra:
    print(f"  INFO: prompt produces but code doesn't use: {extra}")

# Check step5 format variable name
step5_format_vars = set(re.findall(r'(?<!\{)\{(\w+)\}(?!\})', (QUANT / "prompts/step5_validation.txt").read_text()))
step5_code_vars = re.findall(r'\.format\((.*?)\)', src[src.find("run_step5"):src.find("run_step5") + 2000])
print(f"  step5 prompt expects: {sorted(step5_format_vars)}")

# Check merge_steps for old step1 references
merge_start = src.find("def merge_steps")
merge_end = src.find("\ndef ", merge_start + 10)
merge_src = src[merge_start:merge_end]
old_refs = re.findall(r'step1\[.quotes.\]|step1\.get\(.quotes.', merge_src)
if old_refs:
    print(f"  BUG: merge_steps still references old step1 quotes: {old_refs}")

# Check validation field names match between step5 prompt and merge_steps
print(f"\n=== 3. merge_steps field mapping ===")
# Check what step5 keys are accessed in merge_steps
step5_gets = re.findall(r'step5\.get\("(\w+)"', merge_src) + re.findall(r"step5\.get\('(\w+)'", merge_src)
print(f"  merge_steps reads from step5: {sorted(set(step5_gets))}")
# What does step5 prompt produce?
s5_prompt = (QUANT / "prompts/step5_validation.txt").read_text()
s5_keys = re.findall(r'"(\w+)":', s5_prompt)
print(f"  step5 prompt output keys: {sorted(set(s5_keys))}")

# Check for old "validation.contradicted_values" vs new "validation.flagged_values"
if "contradicted_values" in merge_src:
    print("  BUG: merge_steps still references 'contradicted_values' (renamed to 'flagged_values')")
if "unverified_values" in merge_src:
    print("  BUG: merge_steps still references 'unverified_values' (removed)")

print(f"\n=== 4. ab_test.py Analysis ===")
ab_src = (QUANT / "scripts/ab_test.py").read_text()
ab_step1_gets = set(re.findall(r'step1\.get\("(\w+)"', ab_src) + re.findall(r"step1\.get\('(\w+)'", ab_src))
print(f"  ab_test step1.get() keys: {sorted(ab_step1_gets)}")
if "quotes" in ab_step1_gets:
    print("  BUG: ab_test still reads step1.get('quotes') — old format")

# Check for duplicate {paper_text} in any prompt
print(f"\n=== 5. Duplicate paper_text Check ===")
for pf in sorted(QUANT.glob("prompts/step*.txt")):
    text = pf.read_text()
    count = text.count("{paper_text}")
    if count > 1:
        print(f"  BUG: {pf.name} has {count} occurrences of paper_text")
    elif count == 1:
        print(f"  {pf.name}: 1 paper_text — OK")
    else:
        print(f"  {pf.name}: no paper_text (expected for step5)")

# Check config consistency
print(f"\n=== 6. Config Checks ===")
import json
ec = json.loads((QUANT / "config/extraction_config.json").read_text())
sm = json.loads((QUANT / "config/silo_metrics.json").read_text())
bs = json.loads((QUANT / "config/benchmark_schema.json").read_text())
silos_in_metrics = [k for k in sm if not k.startswith("_")]
silos_in_schema = bs.get("properties", {}).get("finance_domain", {}).get("properties", {}).get("primary_silo", {}).get("enum", [])
silos_in_schema = [s for s in silos_in_schema if s and s != "other"]
missing_in_schema = set(silos_in_metrics) - set(silos_in_schema)
missing_in_metrics = set(silos_in_schema) - set(silos_in_metrics)
if missing_in_schema:
    print(f"  BUG: silos in metrics but not schema: {missing_in_schema}")
if missing_in_metrics:
    print(f"  BUG: silos in schema but not metrics: {missing_in_metrics}")
print(f"  Silos aligned: {len(silos_in_metrics)} metrics, {len(silos_in_schema)} schema")

print("\n=== DONE ===")
