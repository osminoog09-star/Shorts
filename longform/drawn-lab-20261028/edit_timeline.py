from pathlib import Path
import json
B=Path(__file__).resolve().parent/'build';p=B/'timeline.json';d=json.loads(p.read_text());at=0
d['scenes']=[s for s in d['scenes']if s['id']not in{28,29,30}]
for s in d['scenes']:s['start']=at;at+=s['duration']+.18
if at<1260:raise RuntimeError('Editorial cut below 21 minutes')
d.update(duration=at,editorial_exclusions=[28,29,30],reason='Remove repeated recap, notes and generic app warning; retain the full diagnostic decision tree')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2));print('MEASURED_EDITORIAL_CUT',at,at/60)
