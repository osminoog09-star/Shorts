from pathlib import Path
import json
R=Path(__file__).resolve().parent;B=R/'build';p=B/'timeline.json';d=json.loads(p.read_text());excluded={5,16,30};kept=[s for s in d['scenes']if s['id']not in excluded];at=0
for s in kept:s['start']=at;at+=s['duration']+.18
if at<1260:raise RuntimeError('Editorial cut below 21 minutes')
d.update(scenes=kept,duration=at,editorial_exclusions=sorted(excluded),reason='Remove repeated explanatory examples; preserve every retained sentence and natural voice speed')
p.write_text(json.dumps(d,ensure_ascii=False,indent=2));print('EDITORIAL_RUNTIME',at,at/60)
