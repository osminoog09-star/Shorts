"""Revision 2: one complete 10–15 minute timeline, plus two portrait timelines."""
import json,shutil,wave
from pathlib import Path
R=Path(__file__).resolve().parent
s=json.loads((R/'timeline.json').read_text());assert len(s)==22
base=sum(x['dur'] for x in s);tail=json.loads((R/'timeline-ending.json').read_text())[0]
shutil.copy2(R/'out/speech_ending.wav',R/'audio/22.wav')
with wave.open(str(R/'audio/22.wav')) as w:speech=w.getnframes()/w.getframerate()
tail.update(index=22,start=base,file='audio/22.wav',speech=speech)
s.append(tail);(R/'timeline.json').write_text(json.dumps(s,ensure_ascii=False,indent=2));dur=sum(x['dur'] for x in s);assert 600<=dur<=900,dur
manifest=json.loads((R/'native.json').read_text());tasks=[]
for name,n,frames in [('main',32,round(dur*30))]+[(x['name'],4,x['frames']) for x in manifest if x['name']!='ending']:
 for i in range(n):tasks.append({'clip':name,'part':i,'parts':n,'frames':frames})
(R/'v2_matrix.json').write_text(json.dumps({'include':tasks}));print('Revision 2 master:',dur,'seconds;',len(tasks),'frame jobs')
