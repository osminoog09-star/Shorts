from pathlib import Path
import json,textwrap
R=Path(__file__).resolve().parent.parent;m=json.loads((R/'out/M1lash_News_20261029_Dima_Sveta_MIX_manifest.json').read_text());ss=[];seen=set();srt=[]
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
for i,a in enumerate(m['segments']):
 first=a['chapter'] not in seen;seen.add(a['chapter']);cues=[];p=R/'lipsync'/(a['id']+'.json');trim=a.get('editorial_trim_start',0)
 if p.exists():
  vis=json.loads(p.read_text())['visemes'];offset=round(trim*30);vis=vis[offset:];last=None
  for f,v in enumerate(vis):
   if v!=last:
    if cues:cues[-1]['end']=f/30
    cues.append(dict(start=f/30,end=(f+1)/30,value=v));last=v
  if cues:cues[-1]['end']=len(vis)/30
 ss.append(dict(a,index=i,first=first,cues=cues,pose='point' if first else 'talk'))
 for w in a['words']:
  start=a['start']+w['start'];end=min(a['end'],a['start']+w['end']);txt='\n'.join(textwrap.wrap(w['w'],width=65))
  srt.append(f'{len(srt)+1}\n{stamp(start)} --> {stamp(end)}\n{txt}\n')
(R/'full_data.js').write_text('window.NEWS_DATA='+json.dumps(dict(segments=ss,duration=m['duration'],timing_status='ACTUAL_AUDIO'),ensure_ascii=False)+';')
(R/'out/M1lash_News_RU.srt').write_text('\n'.join(srt));(R/'narration_RELEASE.md').write_text('\n\n'.join(a['text'] for a in m['segments']))
chapters=[]
for a in ss:
 if a['first']:
  sec=int(a['start']);chapters.append(f'{sec//60:02d}:{sec%60:02d} '+['Технологии и ответственность','Cloudflare: чужой ответ','Amazon: счётчик и результат','Harmonic: доказать, а не угадать','Serve: ужин на колёсах','Opera: локальный ИИ','Apple: творческие инструменты','Firefox: наблюдение страниц','DART и Hera: проверка результата','Твой выбор'][a['chapter']])
(R/'out/CHAPTERS.txt').write_text('\n'.join(chapters));print('actual duration',m['duration'],'clips',len(ss),'sentence captions',len(srt))
