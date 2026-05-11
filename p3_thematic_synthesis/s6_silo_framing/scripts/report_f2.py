"""F2 corpus-level acceptance + paper-id verification report."""
import json
from pathlib import Path

S6 = Path('p3_thematic_synthesis/s6_silo_framing')
BRIEFS = S6 / 'briefs'

print('=== F2 BRIEFS REPORT ===\n')

ID_FIELDS = [
    'problem_statement_supporting_paper_ids',
    'classical_baseline_supporting_paper_ids',
    'classical_difficulty_supporting_paper_ids',
    'business_stakes_supporting_paper_ids',
]

hdr = f"{'silo':<26} {'records':>7} {'P':>4} {'B':>4} {'D':>4} {'S':>4} {'silence':>7} {'brief_chars':>11}"
print(hdr)
print('-' * 80)

for d in sorted(BRIEFS.iterdir()):
    if not d.is_dir():
        continue
    bp = d / 'f2_silo_brief.json'
    if not bp.exists():
        print(f'{d.name:<26} MISSING BRIEF')
        continue
    brief = json.loads(bp.read_text(encoding='utf-8'))
    n_records = brief['coverage_stats']['n_papers_in_silo_with_f1']
    counts = [len(brief.get(f, [])) for f in ID_FIELDS]
    silence_n = len(brief.get('silo_silence_flags', []))
    brief_text = brief.get('draft_finance_brief', '')
    has_stakes = '*' if brief.get('synthesised_business_stakes') else '-'
    print(f'{d.name:<26} {n_records:>7} {counts[0]:>4} {counts[1]:>4} {counts[2]:>4} {counts[3]:>4}{has_stakes} {silence_n:>7} {len(brief_text):>11}')

# Sanitiser drops
print('\n--- Sanitiser drops (hallucinated paper IDs) ---')
total_drops = 0
for d in sorted(BRIEFS.iterdir()):
    if not d.is_dir():
        continue
    log_path = d / 'f2.sanitize_log.json'
    if not log_path.exists():
        continue
    log = json.loads(log_path.read_text(encoding='utf-8'))
    actions = log.get('supporting_paper_actions', [])
    if not actions:
        print(f'  {d.name:<26} no drops')
        continue
    for a in actions:
        n_dropped = len(a.get('dropped_ids', []))
        total_drops += n_dropped
        print(f"  {d.name:<26} {a.get('field')}: dropped {n_dropped} (kept {a.get('kept_count')})")
        if a.get('dropped_ids'):
            print(f"      dropped_ids: {a['dropped_ids']}")
print(f'\nTotal hallucinated paper IDs dropped: {total_drops}')

print('\n--- Brief lengths (target 200-400 words = ~1300-2700 chars) ---')
for d in sorted(BRIEFS.iterdir()):
    if not d.is_dir():
        continue
    bp = d / 'f2_silo_brief.json'
    if not bp.exists():
        continue
    brief = json.loads(bp.read_text(encoding='utf-8'))
    text = brief.get('draft_finance_brief', '')
    words = len(text.split())
    print(f'  {d.name:<26} {words} words ({len(text)} chars)')
