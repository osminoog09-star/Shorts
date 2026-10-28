import asyncio,json,os,wave,subprocess
from pathlib import Path
import edge_tts
import edge_tts.communicate as ec
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'build';OUT.mkdir(exist_ok=True)
if os.environ.get('CODEX_PROXY_CERT'):ec._SSL_CTX.load_verify_locations(os.environ['CODEX_PROXY_CERT'])
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
def blocks():
 result=[]
 for i,b in enumerate((ROOT/'script.txt').read_text().strip().split('\n\n')):
  head,text=b.split('\n',1);chapter,kind,visual,title=head.split('|')
  result.append(dict(id=i,chapter=chapter,kind=kind,visual=visual,title=title,text=text.strip()))
 return result
async def synth(s,sem):
 async with sem:
  p=OUT/f"voice_{s['id']:02d}.mp3"; meta=p.with_suffix('.json')
  if not(p.exists() and meta.exists()):
   for attempt in range(3):
    try:
     events=[]
     with p.open('wb') as f:
      async for x in edge_tts.Communicate(s['text'],'ru-RU-DmitryNeural',rate='+0%',boundary='WordBoundary',receive_timeout=20).stream():
       if x['type']=='audio':f.write(x['data'])
       elif x['type']=='WordBoundary':events.append(x)
     if p.stat().st_size<1000 or not events:raise RuntimeError('Missing voice or word timing')
     meta.write_text(json.dumps(dict(speaker='dima',voice_id='ru-RU-DmitryNeural',engine='edge-tts',rate='+0%',source_file=p.name,words=events,text=s['text']),ensure_ascii=False))
     break
    except Exception:
     p.unlink(missing_ok=True)
     if attempt==2:raise
     await asyncio.sleep(2*(attempt+1))
  s['duration']=duration(p);s['audio']=p.name;s['words']=json.loads(meta.read_text())['words']
  print(s['id'],round(s['duration'],2),flush=True)
async def main():
 import sys
 scenes=blocks();sem=asyncio.Semaphore(2)
 if '--smoke' in sys.argv: scenes=scenes[:1]
 await asyncio.wait_for(asyncio.gather(*(synth(s,sem) for s in scenes)),timeout=1500)
 at=0
 for s in scenes:s['start']=at;at+=s['duration']+.18
 (OUT/'timeline.json').write_text(json.dumps(dict(duration=at,scenes=scenes),ensure_ascii=False,indent=2))
 print('MEASURED',at,at/60,flush=True)
 if '--smoke' not in sys.argv:
  short=dict(id=90,chapter='Чужой контекст',kind='fact',visual='leak',title='ЭТО НЕ ГАЛЛЮЦИНАЦИЯ?',text=(ROOT/'short.txt').read_text().strip(),cta=True)
  await asyncio.wait_for(synth(short,sem),timeout=180)
  short['start']=0
  (OUT/'short_timeline.json').write_text(json.dumps(dict(duration=short['duration']+.18,scenes=[short]),ensure_ascii=False,indent=2))
asyncio.run(main())
