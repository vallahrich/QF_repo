"""Validate + persist a silo's B2 output."""
import json, sys
from p3_thematic_synthesis.scripts.b1_b2_lib import (
    aggregate_b1, extract_json, validate_b2, persist_b2, P3_ROOT, size_sensitive_cap
)
silo = sys.argv[1]
themes_dir = P3_ROOT / 's4_thematic_coding' / silo / 'themes'
raw = (themes_dir / 'b2.raw_response.txt').read_text(encoding='utf-8')
meta = json.loads((themes_dir / 'b2.meta.json').read_text(encoding='utf-8'))
rendered_prompt = (themes_dir / 'b2.prompt.txt').read_text(encoding='utf-8')
agg = aggregate_b1(silo)
silo_pids = set(agg['silo_paper_ids'])
b1_ids = {t['theme_id'] for t in agg['themes']}
max_a = size_sensitive_cap(len(agg['themes']))
parsed = extract_json(raw)
ok, errors = validate_b2(parsed, silo, silo_pids, b1_ids, max_a)
n_d = len(parsed.get('descriptive_themes', [])) if isinstance(parsed, dict) else -1
n_a = len(parsed.get('analytical_themes', [])) if isinstance(parsed, dict) else -1
print(f'{silo:30s} d={n_d} a={n_a} max_a={max_a} pass={ok} errors={len(errors)}')
for e in errors[:20]:
    print('  -', e)
if ok:
    out = persist_b2(silo, parsed, meta, rendered_prompt, raw, meta.get('model', 'claude-opus-4.6'), 'passed')
    print('  -> persisted', out.name)
