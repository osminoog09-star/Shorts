import json
from pathlib import Path
r=Path(__file__).resolve().parent.parent
q=json.loads((r/'shot_plan.json').read_text());d=json.loads((r/'full_data.js').read_text().split('=',1)[1].rstrip(';\n'))
issues=[]
for i,s in enumerate(q):
 if s['end']<=s['start']:issues.append('negative shot duration '+s['id'])
 if i and abs(s['start']-q[i-1]['end'])>.0001:issues.append('gap/overlap '+s['id'])
 if not any(v['id']==s['segmentId'] for v in d['segments']):issues.append('missing audio segment '+s['id'])
# Actual V1 failure times must show the introductory story, never chapter9.
regressions=[]
for t in [22.267,50.533,61.20,88.8,121.95]:
 s=next((s for s in q if s['start']<=t<s['end']),None)
 ok=s is not None and s['chapter']!=9
 regressions.append({'t':t,'shot':s['id'] if s else None,'pass':ok})
 if not ok:issues.append('final intrudes into gap '+str(t))
for s in d['segments']:
 if s['voice_id'] not in ['ru-RU-DmitryNeural','ru-RU-SvetlanaNeural']:issues.append('unapproved voice '+s['id'])
assert q[0]['start']==0
if abs(q[-1]['end']-d['duration'])>.001:issues.append('coverage end mismatch')
result={'pass':not issues,'issues':issues,'shots':len(q),'duration':d['duration'],'regressions':regressions,'voices':sorted(set(s['voice_id'] for s in d['segments']))}
(r/'out/qa/TIMELINE_AUDIT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(bool(issues))
