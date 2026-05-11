"""Automated rubric checks on B2 outputs — produce quality signals per silo."""
import json, re
from pathlib import Path
from p3_thematic_synthesis.scripts.b1_b2_lib import P3_ROOT

SILOS = ['trading_execution', 'credit_lending', 'fraud_detection', 'derivative_pricing',
        'risk_management', 'simulation_monte_carlo', 'portfolio_optimization', 'quantum_ml_finance']
SILO_LABEL = {
    'trading_execution': ['Trading', 'Execution'],
    'credit_lending': ['Credit', 'Lending'],
    'fraud_detection': ['Fraud Detection'],
    'derivative_pricing': ['Derivative Pricing', 'Option Pricing'],
    'risk_management': ['Risk Management'],
    'simulation_monte_carlo': ['Monte Carlo', 'Simulation'],
    'portfolio_optimization': ['Portfolio Optimization', 'Portfolio Optimisation'],
    'quantum_ml_finance': ['Quantum ML', 'Quantum Machine Learning'],
}

# Phase 1 taxonomy codes to flag (from shared/config/unified_taxonomy.json)
PD_CODES = [f'PD-{i:02d}' for i in range(1, 11)]
SA_CODES = [f'SA-{i:02d}' for i in range(1, 12)]
TAXO_CODES = PD_CODES + SA_CODES

# Known Phase 1 category labels to check for restatement
P1_LABELS = ['Optimization', 'Machine Learning', 'Simulation', 'Cryptography',
             'Forecasting', 'Risk Analysis', 'Classification', 'Generative Modeling']


def score_silo(silo):
    td = P3_ROOT / 's4_thematic_coding' / silo / 'themes' / 'b2_silo_themes.json'
    d = json.loads(td.read_text(encoding='utf-8'))
    out = d['output']
    desc = out.get('descriptive_themes', [])
    anl = out.get('analytical_themes', [])

    report = {'silo': silo, 'descriptive_count': len(desc), 'analytical_count': len(anl),
              'findings': [], 'flags': {}}

    # ---- C5 anti-anchoring automated checks ----
    silo_keywords = SILO_LABEL[silo]
    c5_keyword_hits = []
    for t in desc + anl:
        label = (t.get('theme_label') or '').lower()
        for kw in silo_keywords:
            # flag ONLY if silo name is the main descriptor (first 3 words)
            first_words = label.split()[:4]
            if kw.lower() in ' '.join(first_words):
                c5_keyword_hits.append((t.get('theme_id'), t.get('theme_label')))
                break
    c5_taxo_hits = []
    for t in desc + anl:
        blob = json.dumps(t).lower()
        for code in TAXO_CODES:
            if code.lower() in blob:
                c5_taxo_hits.append((t.get('theme_id'), code))
                break
    report['flags']['c5_silo_keyword_hits'] = c5_keyword_hits
    report['flags']['c5_phase1_code_hits'] = c5_taxo_hits

    # ---- C1 coherence automated signals ----
    # Flag themes with generic vague labels
    vague_words = ['various', 'different', 'approaches', 'methods', 'techniques',
                   'general', 'miscellaneous', 'other']
    c1_vague = []
    for t in desc + anl:
        label = (t.get('theme_label') or '').lower()
        if any(w in label.split() for w in vague_words):
            c1_vague.append((t.get('theme_id'), t.get('theme_label')))
    report['flags']['c1_vague_labels'] = c1_vague

    # ---- C3 interpretive depth: check analytical themes have substantive interpretation ----
    c3_shallow = []
    for t in anl:
        interp = (t.get('interpretation') or '').strip()
        impl = (t.get('implication') or '').strip()
        if len(interp) < 200 or len(impl) < 80:
            c3_shallow.append((t.get('theme_id'), f'interp={len(interp)}ch impl={len(impl)}ch'))
    report['flags']['c3_short_interpretation'] = c3_shallow

    # ---- C4 counter-evidence validity automated checks ----
    # Load silo paper set
    proj = json.loads((P3_ROOT / 's4_thematic_coding' / silo / 'projection_manifest.json').read_text(encoding='utf-8'))
    silo_pids = {p['paper_id'] for p in proj['papers']}
    c4_out_of_scope = []
    c4_no_ce_count = 0
    c4_generic_ce = []
    for t in anl:
        ce = t.get('counter_evidence')
        if isinstance(ce, list) and ce:
            for entry in ce:
                pid = entry.get('paper_id')
                if pid and pid not in silo_pids:
                    c4_out_of_scope.append((t.get('theme_id'), pid))
                reason = entry.get('reason', '')
                if len(reason) < 40:
                    c4_generic_ce.append((t.get('theme_id'), pid, reason))
        else:
            nce = t.get('no_counter_evidence_reason')
            if nce:
                c4_no_ce_count += 1
                if len(nce) < 60:
                    c4_generic_ce.append((t.get('theme_id'), 'no_ce', nce))
    report['flags']['c4_out_of_scope_ce'] = c4_out_of_scope
    report['flags']['c4_no_ce_used'] = c4_no_ce_count
    report['flags']['c4_short_reasons'] = c4_generic_ce

    # ---- Auto-scoring heuristics ----
    # C1: 5 if 0 vague, 4 if 1 vague, 3 if 2-3, 2 otherwise
    nv = len(c1_vague)
    c1 = 5 if nv == 0 else (4 if nv == 1 else (3 if nv <= 3 else 2))
    # C3: 5 if 0 shallow, 4 if 1 shallow, 3 if 2, lower otherwise
    ns = len(c3_shallow)
    c3 = 5 if ns == 0 else (4 if ns == 1 else (3 if ns == 2 else 2))
    # C4: 5 if no out-of-scope and ≤1 short reason and ≤2 no_ce, else drop
    nc4oos = len(c4_out_of_scope)
    nc4sh = len(c4_generic_ce)
    if nc4oos > 0:
        c4 = 1
    elif nc4sh == 0 and c4_no_ce_count <= 1:
        c4 = 5
    elif nc4sh <= 1 and c4_no_ce_count <= 2:
        c4 = 4
    elif nc4sh <= 3:
        c4 = 3
    else:
        c4 = 2
    # C5: 5 if no keyword or taxonomy hits, 1 if taxonomy hits (critical)
    if len(c5_taxo_hits) > 0:
        c5 = 1
    elif len(c5_keyword_hits) == 0:
        c5 = 5
    elif len(c5_keyword_hits) <= 1:
        c5 = 4
    elif len(c5_keyword_hits) <= 3:
        c5 = 3
    else:
        c5 = 2
    # C2 grounding requires researcher spot-check; default provisional 4
    c2 = 'researcher_check_pending'

    report['auto_scores'] = {'C1': c1, 'C2_provisional': c2, 'C3': c3, 'C4': c4, 'C5': c5}
    report['auto_mean_excl_C2'] = round((c1 + c3 + c4 + c5) / 4, 2)
    # Gate check: mean ≥ 4.0 AND no criterion < 3 (C2 excluded from auto gate)
    non_c2 = [c1, c3, c4, c5]
    report['auto_gate_excl_C2'] = 'PASS' if (report['auto_mean_excl_C2'] >= 4.0 and min(non_c2) >= 3) else 'FAIL'
    return report


reports = [score_silo(s) for s in SILOS]

# Print summary
print(f"{'Silo':25s} {'D':>3} {'A':>3} {'C1':>3} {'C3':>3} {'C4':>3} {'C5':>3} {'Mean':>5} Gate")
print('-' * 70)
for r in reports:
    s = r['auto_scores']
    print(f"{r['silo']:25s} {r['descriptive_count']:>3} {r['analytical_count']:>3} "
          f"{s['C1']:>3} {s['C3']:>3} {s['C4']:>3} {s['C5']:>3} "
          f"{r['auto_mean_excl_C2']:>5} {r['auto_gate_excl_C2']}")

# Detail for flagged silos
print('\n\n=== FLAGS DETAIL ===')
for r in reports:
    flags = r['flags']
    has_issue = (flags['c5_silo_keyword_hits'] or flags['c5_phase1_code_hits']
                 or flags['c1_vague_labels'] or flags['c3_short_interpretation']
                 or flags['c4_out_of_scope_ce'] or flags['c4_no_ce_used'] > 2
                 or len(flags['c4_short_reasons']) > 1)
    if has_issue:
        print(f"\n--- {r['silo']} ---")
        for k, v in flags.items():
            if v and v != 0:
                print(f"  {k}: {v}")

# Write full JSON report
(P3_ROOT / 'docs' / 'B1_B2_RUBRIC_AUTO_SCORES.json').write_text(
    json.dumps(reports, indent=2), encoding='utf-8')
print('\nWrote B1_B2_RUBRIC_AUTO_SCORES.json')
