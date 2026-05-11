"""Sanitize + validate + persist B1 outputs.

Policy:
1. Drop any support_code_id not present in that paper's A1 codes (hallucinated code IDs).
2. If a paper's support_code_ids entry becomes empty after drop, drop that paper from supporting_papers.
3. If supporting_papers drops below min (3), reject the theme.
4. Re-validate and persist; record sanitization in audit log.
"""
import json, sys
from p3_thematic_synthesis.scripts.b1_b2_lib import (
    compute_batches, extract_json, validate_b1, persist_b1, load_index, P3_ROOT
)

SILO_CODES = {
    'credit_lending': 'CL', 'derivative_pricing': 'DP', 'fraud_detection': 'FD',
    'portfolio_optimization': 'PO', 'quantum_ml_finance': 'QML',
    'risk_management': 'RM', 'simulation_monte_carlo': 'SMC', 'trading_execution': 'TE',
}
MIN_PAPERS = 3

silo = sys.argv[1]
code = SILO_CODES[silo]
themes_dir = P3_ROOT / 's4_thematic_coding' / silo / 'themes'
raw = (themes_dir / 'b1_batch_01.raw_response.txt').read_text(encoding='utf-8')
meta = json.loads((themes_dir / 'b1_batch_01.meta.json').read_text(encoding='utf-8'))
rendered = (themes_dir / 'b1_batch_01.prompt.txt').read_text(encoding='utf-8')
batches = compute_batches(silo, papers_per_batch=1000)
batch_pids = batches[0]['paper_ids']
parsed = extract_json(raw)
idx = load_index(silo)

# Build per-paper valid code set
paper_codes: dict[str, set[str]] = {}
for pid, info in idx['papers'].items():
    paper_codes[pid] = {c['code_id'] for c in info.get('codes', [])}

sanitized = []
san_log = []
dropped_themes = []
for theme in parsed:
    tid = theme.get('theme_id', '?')
    sp = list(theme.get('supporting_papers') or [])
    sci = dict(theme.get('support_code_ids') or {})
    dropped_codes = []
    dropped_papers = []
    new_sci = {}
    new_sp = []
    for pid in sp:
        if pid not in paper_codes:
            dropped_papers.append((pid, 'paper_not_in_index'))
            continue
        valid = [c for c in (sci.get(pid) or []) if c in paper_codes[pid]]
        invalid = [c for c in (sci.get(pid) or []) if c not in paper_codes[pid]]
        if invalid:
            dropped_codes.append({'paper_id': pid, 'dropped': invalid})
        if valid:
            new_sci[pid] = valid
            new_sp.append(pid)
        else:
            dropped_papers.append((pid, 'all_codes_invalid'))
    if len(new_sp) >= MIN_PAPERS:
        t2 = dict(theme)
        t2['supporting_papers'] = new_sp
        t2['support_code_ids'] = new_sci
        sanitized.append(t2)
        if dropped_codes or dropped_papers:
            san_log.append({
                'theme_id': tid,
                'original_support_count': len(sp),
                'final_support_count': len(new_sp),
                'dropped_codes': dropped_codes,
                'dropped_papers': dropped_papers,
            })
    else:
        dropped_themes.append({'theme_id': tid, 'reason': f'supporting_papers fell below {MIN_PAPERS} after sanitization',
                               'original_support_count': len(sp), 'final_support_count': len(new_sp)})

print(f'{silo}: in={len(parsed)} sanitized={len(sanitized)} dropped_themes={len(dropped_themes)}')
print(f'  themes with edits: {len(san_log)}')
for e in san_log[:5]:
    print('  -', e['theme_id'], 'dropped_codes=', len(e['dropped_codes']), 'dropped_papers=', len(e['dropped_papers']))
for e in dropped_themes:
    print('  DROP', e)

ok, errors = validate_b1(sanitized, batch_pids, code, 1, MIN_PAPERS, idx, silo)
print(f'post-sanitize validation: pass={ok} errors={len(errors)}')
for e in errors[:10]:
    print('  -', e)

if ok:
    # Persist the SANITIZED output, also save sanitization log
    out = persist_b1(silo, 1, sanitized, meta, rendered, raw, meta.get('model', 'claude-opus-4.6-1m'), 'passed_after_sanitize')
    san_path = themes_dir / 'b1_batch_01.sanitize_log.json'
    san_path.write_text(json.dumps({
        'silo': silo,
        'themes_in': len(parsed),
        'themes_out': len(sanitized),
        'themes_dropped': dropped_themes,
        'edits': san_log,
    }, indent=2), encoding='utf-8')
    print(f'  -> persisted {out.name}')
    print(f'  -> sanitize log {san_path.name}')
else:
    print('  !! still failing after sanitize; manual intervention needed')
