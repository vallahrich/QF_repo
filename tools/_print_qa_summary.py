"""Print verdict_summary for all 7 frameworks (audit utility)."""
import json
from pathlib import Path

root = Path('p3_thematic_synthesis/quantum_advantage')
files = {
    'Ronnow':       root / 'ronnow/results/ronnow_results.json',
    'Hoefler':      root / 'hoefler_assessment/results/hoefler_results.json',
    'Babbush':      root / 'babbush_2021/results/babbush_results.json',
    'Beverland':    root / 'beverland_2022/results/beverland_results.json',
    'Chakrabarti':  root / 'chakrabarti_2021/results/chakrabarti_results.json',
    'Dalzell':      root / 'dalzell_2023/results/dalzell_results.json',
    'StilckFranca': root / 'stilck_franca_2021/results/stilck_franca_results.json',
}
for name, fp in files.items():
    d = json.loads(fp.read_text(encoding='utf-8'))
    summary = d.get('verdict_summary', {})
    total = d.get('total_experiments', '?')
    print(f'{name:14s} total={total:>5}  {summary}')
