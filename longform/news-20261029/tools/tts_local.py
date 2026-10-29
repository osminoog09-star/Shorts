import asyncio,os,json,subprocess,sys,ssl
from pathlib import Path
import certifi
certifi.where=lambda:'/etc/ssl/certs/ca-certificates.crt'
import edge_tts
ROOT=Path(__file__).resolve().parent.parent
async def synth(line,attempts=15):
 p=ROOT/'audio'/(line['id']+'.mp3');meta=p.with_suffix('.json');voice=line['voice'];text=line['text']
 if p.exists() and p.stat().st_size>1000 and meta.exists():return True
 for attempt in range(attempts):
  try:
   words=[]
   com=edge_tts.Communicate(text,voice,rate='+0%',proxy=os.environ.get('HTTPS_PROXY'),boundary='SentenceBoundary')
   async with asyncio.timeout(35):
    with p.open('wb') as f:
     async for ch in com.stream():
      if ch['type']=='audio':f.write(ch['data'])
      elif ch['type'] in ('WordBoundary','SentenceBoundary'):words.append(dict(w=ch['text'],start=ch['offset']/1e7,end=(ch['offset']+ch['duration'])/1e7))
   assert p.stat().st_size>1000
   duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
   meta.write_text(json.dumps(dict(line,speaker='sveta' if 'Svetlana' in voice else 'dima',voice_id=voice,engine='edge-tts',rate='+0%',source_file=str(p),duration=duration,words=words),ensure_ascii=False,indent=2))
   print('OK',line['id'],round(duration,2),flush=True);return True
  except Exception as e:
   p.unlink(missing_ok=True);print('RETRY',line['id'],attempt+1,type(e).__name__,flush=True)
   await asyncio.sleep(min(12,2+attempt*2))
 return False
async def main():
 job=json.loads((ROOT/'tts_job.json').read_text());lines=job['lines']
 if '--probe' in sys.argv:
  lines=[dict(id='probe_dima',voice='ru-RU-DmitryNeural',text='Привет, это Дима.'),dict(id='probe_sveta',voice='ru-RU-SvetlanaNeural',text='Привет, проверка.'),lines[0]]
 sem=asyncio.Semaphore(8)
 async def one(l):
  async with sem:return await synth(l)
 rs=await asyncio.gather(*(one(l) for l in lines));print('RESULT',sum(rs),'/',len(rs),flush=True)
 if not all(rs):sys.exit(1)
if __name__=='__main__':asyncio.run(main())
