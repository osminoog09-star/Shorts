import json
from pathlib import Path
r=Path(__file__).resolve().parent.parent
p=json.loads((r/'shot_plan.json').read_text())
assert all(x['end']>x['start'] for x in p)
assert all(abs(p[i]['start']-p[i-1]['end'])<0.001 for i in range(1,len(p)))
(r/'shot_plan.js').write_text('window.SHOT_PLAN='+json.dumps(p,ensure_ascii=False)+';')
