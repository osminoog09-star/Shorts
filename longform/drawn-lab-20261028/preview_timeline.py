from pathlib import Path
import json
from voice import blocks,short_scenes,duration,OUT
wanted={0,2,28,31,90}
scenes=[]
for s in blocks()+short_scenes():
 if s['id']not in wanted:continue
 p=OUT/f"voice_{s['id']:02d}.mp3";m=json.loads(p.with_suffix('.json').read_text());s.update(audio=p.name,duration=duration(p),words=m['words'],start=0)
 if s['id']<90:scenes.append(s)
 else:(OUT/f"short_{s['id']}_timeline.json").write_text(json.dumps(dict(duration=s['duration']+.18,scenes=[s]),ensure_ascii=False))
(OUT/'timeline.json').write_text(json.dumps(dict(duration=sum(s['duration']+.18 for s in scenes),scenes=scenes),ensure_ascii=False))
