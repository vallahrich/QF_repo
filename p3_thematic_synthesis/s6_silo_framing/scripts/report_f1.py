"""F1 corpus-level acceptance + field-coverage report."""
import json
from collections import Counter
from pathlib import Path

S6 = Path('p3_thematic_synthesis/s6_silo_framing')
RAW = S6 / 'extractions/_raw'
PAPERS = S6 / 'extractions/papers'
INDEX = json.loads((S6 / 'input_index/paper_silo_index.json').read_text(encoding='utf-8'))
LOG = S6 / 'logs/f1_calls.jsonl'

# Per-paper outcome
sanitised = sorted(p.stem for p in PAPERS.glob('*.json'))
raw_present = sorted(p.stem.replace('.raw_response', '') for p in RAW.glob('*.raw_response.txt'))
parse_failed = []
missing_keys = []
for log_path in RAW.glob('*.sanitize_log.json'):
    log = json.loads(log_path.read_text(encoding='utf-8'))
    pid = log['paper_id']
    if log.get('result') == 'rejected_parse_failed':
        parse_failed.append(pid)
    elif log.get('result') == 'rejected_missing_keys':
        missing_keys.append(pid)

# API errors from the audit log
api_errors = []
ok_calls = 0
with LOG.open('r', encoding='utf-8') as f:
    for line in f:
        e = json.loads(line)
        if e.get('status') == 'api_error':
            api_errors.append(e['paper_id'])
        elif e.get('status') == 'ok':
            ok_calls += 1

# Excluded
EXCLUDED = {'4eb84ca51d29'}  # only one actually in the index
total_papers = len(INDEX['papers'])

print('=== F1 CORPUS-LEVEL REPORT ===')
print()
print(f'Index size:                       {total_papers} papers')
print(f'Excluded (proceedings volume):    {len(EXCLUDED)}')
print(f'Targets (after exclusion):        {total_papers - len(EXCLUDED)}')
print()
print('--- API channel ---')
print(f'  ok responses (audit log):       {ok_calls}')
print(f'  api_errors:                     {len(api_errors)}  -> {sorted(set(api_errors))}')
print()
print('--- Sanitiser ---')
print(f'  raw_response files present:     {len(raw_present)}')
print(f'  papers/ structured outputs:     {len(sanitised)} ({100*len(sanitised)/(total_papers - len(EXCLUDED)):.1f}% of targets)')
print(f'  parse_failed:                   {len(parse_failed)}  -> first 5: {parse_failed[:5]}')
print(f'  rejected_missing_keys:          {len(missing_keys)}  -> {missing_keys}')
print()

# Field coverage
field_present = Counter()
field_quote_counts = Counter()
confidence = Counter()
for path in PAPERS.glob('*.json'):
    rec = json.loads(path.read_text(encoding='utf-8'))
    for f in ['problem_statement', 'classical_baseline', 'classical_difficulty', 'business_stakes']:
        if rec.get(f):
            field_present[f] += 1
        n_quotes = len(rec.get(f + '_quotes', []) or [])
        field_quote_counts[f] += n_quotes
    confidence[rec.get('extraction_confidence', '?')] += 1

n = len(sanitised)
print('--- Field coverage (of accepted) ---')
for f in ['problem_statement', 'classical_baseline', 'classical_difficulty', 'business_stakes']:
    pct = 100 * field_present[f] / n if n else 0
    avg_q = field_quote_counts[f] / n if n else 0
    print(f'  {f:<24}: {field_present[f]:>4}/{n} ({pct:>5.1f}%)  avg quotes/paper: {avg_q:.2f}')
print()
print('--- Confidence distribution ---')
for c in ['high', 'medium', 'low']:
    pct = 100 * confidence[c] / n if n else 0
    print(f'  {c:<8}: {confidence[c]:>4} ({pct:>5.1f}%)')
print()

# Per-silo coverage
print('--- Per-silo coverage ---')
print(f"{'silo':<26} {'in_silo':>8} {'sanitised':>10} {'pct':>6}")
for silo, info in sorted(INDEX['by_silo'].items()):
    silo_pids = [p for p in info['paper_ids'] if p not in EXCLUDED]
    have = sum(1 for p in silo_pids if (PAPERS / f'{p}.json').exists())
    pct = 100 * have / len(silo_pids) if silo_pids else 0
    print(f'  {silo:<24}: {len(silo_pids):>6} {have:>10} {pct:>5.1f}%')
