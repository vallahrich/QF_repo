"""Quick syntax/format check of P3 quantitative configs and prompts."""
import json
import re
from pathlib import Path

QUANT = Path("p3_thematic_synthesis/s2_quantitative")

print("=== Prompt format check ===")
for pf in sorted(QUANT.glob("prompts/step*.txt")):
    text = pf.read_text(encoding="utf-8")
    placeholders = set(re.findall(r"(?<!\{)\{(\w+)\}(?!\})", text))
    try:
        text.format(**{v: "T" for v in placeholders})
        print(f"  {pf.name}: OK  vars={sorted(placeholders)}")
    except Exception as e:
        print(f"  {pf.name}: BROKEN  {e}")

print("\n=== JSON validity ===")
for jp in [
    QUANT / "config" / "benchmark_schema.json",
    QUANT / "config" / "extraction_config.json",
    QUANT / "config" / "silo_metrics.json",
]:
    try:
        json.loads(jp.read_text(encoding="utf-8"))
        print(f"  {jp.name}: OK")
    except Exception as e:
        print(f"  {jp.name}: BROKEN  {e}")

print("\n=== Scope consistency ===")
schema = json.loads((QUANT / "config" / "benchmark_schema.json").read_text(encoding="utf-8"))
fam_enum = schema["$defs"]["experiment"]["properties"]["algorithm"]["properties"]["family"]["enum"]
hw_enum = schema["$defs"]["experiment"]["properties"]["hardware"]["properties"]["type"]["enum"]
print(f"  algorithm.family enum: {fam_enum}")
print(f"  hardware.type enum:    {hw_enum}")
assert "quantum-annealing" not in fam_enum, "quantum-annealing still in family enum"
assert "qubo" not in fam_enum, "qubo still in family enum"
assert "quantum_annealer" not in hw_enum, "quantum_annealer still in hardware enum"
print("  schema scope: OK (no annealing/qubo/annealer)")

step2 = (QUANT / "prompts/step2_experiments.txt").read_text(encoding="utf-8")
assert "THESIS SCOPE" in step2, "step2 missing scope banner"
assert "quantum-annealing, quantum-svm, qubo" not in step2, "step2 still advertises annealing/qubo in enum"
print("  step2 scope banner + enum: OK")

step4 = (QUANT / "prompts/step4_validation.txt").read_text(encoding="utf-8")
assert "THESIS SCOPE" in step4, "step4 missing scope banner"
assert "scope_violation" in step4, "step4 missing scope self-check"
print("  step4 scope banner + self-check: OK")

config = json.loads((QUANT / "config/extraction_config.json").read_text(encoding="utf-8"))
assert config["temperature"] == 0.0, f"temperature not 0: {config['temperature']}"
assert config.get("scope") == "gate_based", f"scope not gate_based: {config.get('scope')}"
print(f"  config: temperature={config['temperature']}, seed={config.get('seed')}, scope={config['scope']}")

runext = (QUANT / "scripts/run_extraction.py").read_text(encoding="utf-8")
assert "SCOPE_OUT_METHODOLOGY_TAGS" in runext, "Q-0 scope filter missing"
assert "quantum-annealing-qubo" in runext, "Q-0 SA-01 tag not filtered"
print("  run_extraction.py Q-0 filter: OK")

print("\nALL CHECKS PASSED")
