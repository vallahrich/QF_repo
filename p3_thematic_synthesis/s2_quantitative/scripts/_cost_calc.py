"""Cost calculator for P3 quantitative extraction pipeline."""

papers = 647

# Per-paper token estimates (from actual test output sizes)
step2_input = 22000   # paper text (~20K) + prompt (~2K)
step3_input_uncached = 3000   # instructions + experiment context
step3_input_cached = 20000    # paper text (cached from step2)
step4_input = 8000            # merged data (no paper text)

step2_output = 8000    # experiments + resources JSON
step3_output = 6000    # results + baselines JSON
step4_output_nonreasoning = 3000   # assessment JSON
step4_output_reasoning = 10000     # reasoning models use thinking tokens

# Pricing per 1M tokens (Global Standard)
models = {
    "gpt-5-mini":      {"input": 0.25,  "cached": 0.03,  "output": 2.00,  "reasoning": True,  "speed_s": 90},
    "gpt-5-nano":      {"input": 0.05,  "cached": 0.01,  "output": 0.40,  "reasoning": False, "speed_s": 1},
    "gpt-4.1-mini":    {"input": 0.40,  "cached": 0.10,  "output": 1.60,  "reasoning": False, "speed_s": 5},
    "gpt-4.1-nano":    {"input": 0.10,  "cached": 0.03,  "output": 0.40,  "reasoning": False, "speed_s": 1},
    "gpt-5.1":         {"input": 1.25,  "cached": 0.13,  "output": 10.00, "reasoning": False, "speed_s": 10},
    "gpt-5.1-codex-mini": {"input": 0.25, "cached": 0.03, "output": 2.00, "reasoning": False, "speed_s": 5},
    "gpt-5.2":         {"input": 1.75,  "cached": 0.18,  "output": 14.00, "reasoning": True,  "speed_s": 60},
    "gpt-5.3":         {"input": 1.75,  "cached": 0.18,  "output": 14.00, "reasoning": True,  "speed_s": 10},  # estimated same as 5.2
    "gpt-5.4-mini":    {"input": 0.40,  "cached": 0.10,  "output": 1.60,  "reasoning": False, "speed_s": 1},   # estimated like 4.1-mini
}

def cost_per_paper(m2, m3, m4):
    p2 = models[m2]
    p3 = models[m3]
    p4 = models[m4]
    s2 = step2_input * p2["input"] / 1e6 + step2_output * p2["output"] / 1e6
    s3 = step3_input_uncached * p3["input"] / 1e6 + step3_input_cached * p3["cached"] / 1e6 + step3_output * p3["output"] / 1e6
    out4 = step4_output_reasoning if p4["reasoning"] else step4_output_nonreasoning
    s4 = step4_input * p4["input"] / 1e6 + out4 * p4["output"] / 1e6
    return s2 + s3 + s4

options = [
    ("A", "gpt-5.4-mini", "gpt-5.4-mini", "gpt-5.3",     "CURRENT: 5.4-mini + 5.3"),
    ("B", "gpt-5.1",      "gpt-5.1",      "gpt-5.2",     "Previous: 5.1 + 5.2"),
    ("C", "gpt-5.1",      "gpt-5.1",      "gpt-5.3",     "5.1 extract + 5.3 assess"),
    ("D", "gpt-5.4-mini", "gpt-5.4-mini", "gpt-5.2",     "5.4-mini + 5.2"),
    ("E", "gpt-4.1-mini", "gpt-4.1-mini", "gpt-5.3",     "4.1-mini + 5.3"),
    ("F", "gpt-5-mini",   "gpt-5-mini",   "gpt-5.3",     "5-mini + 5.3"),
    ("G", "gpt-5.4-mini", "gpt-5.4-mini", "gpt-5.4-mini","All 5.4-mini (no reasoning)"),
    ("H", "gpt-4.1-mini", "gpt-4.1-mini", "gpt-4.1-mini","All 4.1-mini"),
]

print(f"{'Opt':<4} {'Step2':<18} {'Step3':<18} {'Step4':<18} {'$/paper':>8} {'Total$':>8} {'EUR':>7} {'Fit70':>6} {'Speed':>10}")
print("-" * 100)
for opt, m2, m3, m4, desc in options:
    cpp = cost_per_paper(m2, m3, m4)
    total = cpp * papers
    eur = total * 0.92
    fits = "YES" if eur <= 70 else "NO"
    secs = models[m2]["speed_s"] + models[m3]["speed_s"] + models[m4]["speed_s"]
    hrs = secs * papers / 3600 / 8  # parallel 8
    speed = f"{hrs:.1f}h @p8"
    print(f"{opt:<4} {m2:<18} {m3:<18} {m4:<18} {cpp:>7.4f} {total:>7.1f} {eur:>6.1f} {fits:>6} {speed:>10}")

print(f"\nBudget: EUR 70 (~$76)")
print(f"Papers: {papers}")
