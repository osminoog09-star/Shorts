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
  if not(p.exists() and meta.exists() and json.loads(meta.read_text()).get('text')==s['text']):
   for attempt in range(8):
    try:
     events=[]
     with p.open('wb') as f:
      async for x in edge_tts.Communicate(s['text'],'ru-RU-DmitryNeural',rate='+0%',boundary='WordBoundary',receive_timeout=45).stream():
       if x['type']=='audio':f.write(x['data'])
       elif x['type']=='WordBoundary':events.append(x)
     if p.stat().st_size<1000 or not events:raise RuntimeError('Missing voice or word timing')
     meta.write_text(json.dumps(dict(speaker='dima',voice_id='ru-RU-DmitryNeural',engine='edge-tts',rate='+0%',source_file=p.name,words=events,text=s['text']),ensure_ascii=False))
     break
    except Exception:
     p.unlink(missing_ok=True)
     if attempt==7:raise
     await asyncio.sleep(min(45,5*(attempt+1)))
  s['duration']=duration(p);s['audio']=p.name;s['words']=json.loads(meta.read_text())['words']
  print(s['id'],round(s['duration'],2),flush=True)
def short_scenes():
 return [dict(id=i,chapter=c,kind='fact',visual=v,title=t,text=(ROOT/f).read_text().strip(),cta=True) for i,c,v,t,f in [(90,'Самолёт без тяги','plane','ДВИГАТЕЛЬ СТИРАЕМ. ПОЛЁТ?','short_plane.txt'),(91,'Двое суток Венеры','venus','СУТКИ ДЛИННЕЕ ГОДА?','short_venus.txt'),(92,'Кинозагадка','movie','ОНИ ЭТО СДЕЛАЛИ?!','short_movie_private.txt')]]

def assemble():
 scenes=blocks();at=0
 for scene in scenes+short_scenes():
  p=OUT/("voice_%02d.mp3"%scene['id']);meta=json.loads(p.with_suffix('.json').read_text())
  if meta.get('voice_id')!='ru-RU-DmitryNeural' or meta.get('rate')!='+0%' or meta.get('text')!=scene['text'] or not meta.get('words'):raise RuntimeError('Unaccepted narration '+str(p))
  scene.update(audio=p.name,duration=duration(p),words=meta['words'],start=at)
  if scene['id']>=90:
   scene['start']=0;(OUT/f"short_{scene['id']}_timeline.json").write_text(json.dumps(dict(duration=scene['duration']+.18,scenes=[scene]),ensure_ascii=False,indent=2))
  else:at+=scene['duration']+.18
 if at<1260:raise RuntimeError('Longform below 21 minutes; develop content, do not stretch')
 (OUT/'timeline.json').write_text(json.dumps(dict(duration=at,scenes=scenes),ensure_ascii=False,indent=2));print('MEASURED',at,at/60)

async def main():
 import sys
 scenes=blocks();sem=asyncio.Semaphore(1)
 if '--assemble' in sys.argv:assemble();return
 group=next((a.split('=',1)[1] for a in sys.argv if a.startswith('--ids=')),None)
 if group is not None:
  wanted={int(x) for x in group.split(',')};scenes=[s for s in scenes+short_scenes() if s['id'] in wanted]
 if '--smoke' in sys.argv: scenes=scenes[:1]
 results=await asyncio.wait_for(asyncio.gather(*(synth(s,sem) for s in scenes),return_exceptions=True),timeout=1800)
 failures=[dict(scene=s['id'],error=type(e).__name__,detail=str(e)[:300]) for s,e in zip(scenes,results) if isinstance(e,BaseException)]
 (OUT/'voice_status.json').write_text(json.dumps(dict(accepted=[s['id'] for s,e in zip(scenes,results) if not isinstance(e,BaseException)],failed=failures),ensure_ascii=False,indent=2))
 if failures: raise RuntimeError('Exact Dmitry narration incomplete; accepted segments preserved. '+str(failures))
 print('Accepted requested voice batch',flush=True)
if __name__=='__main__':asyncio.run(main())
