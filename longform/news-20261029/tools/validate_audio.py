from pathlib import Path
import json,re,subprocess
R=Path(__file__).resolve().parent.parent
job=json.loads((R/'tts_job.json').read_text())
def norm(t):return ''.join(re.findall(r'[\w]+',t.lower())).replace('ё','е')
report=[]
for l in job['lines']:
 p=R/'audio'/(l['id']+'.mp3');m=p.with_suffix('.json');reason=[]
 if not p.exists() or not m.exists():reason=['missing']
 else:
  try:
   meta=json.loads(m.read_text());duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],stderr=subprocess.DEVNULL))
   if meta.get('voice_id')!=l['voice']:reason.append('voice mismatch')
   if meta.get('text')!=l['text']:reason.append('text mismatch')
   observed=norm(' '.join(w['w'] for w in meta.get('words',[])));expected=norm(l['text'])
   if observed!=expected:reason.append(f'incomplete metadata text {len(observed)}/{len(expected)}')
   if abs(duration-meta.get('duration',0))>.1:reason.append('duration changed')
   if meta.get('words') and meta['words'][-1]['end']>duration+.25:reason.append('audio truncated')
  except Exception as e:reason.append(type(e).__name__)
 report.append(dict(id=l['id'],ok=not reason,reasons=reason))
(R/'out'/'AUDIO_GATE.json').write_text(json.dumps(report,indent=2))
print('PASS',sum(x['ok'] for x in report),'/',len(report));print([x for x in report if not x['ok'] and x['reasons']!=['missing']])
