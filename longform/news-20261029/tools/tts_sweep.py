import asyncio,os,json,subprocess,re,shutil
from pathlib import Path
import certifi
certifi.where=lambda:'/etc/ssl/certs/ca-certificates.crt'
import edge_tts
R=Path(__file__).resolve().parent.parent;D=R/'audio_verified';D.mkdir(exist_ok=True)
lines=json.loads((R/'tts_job.json').read_text())['lines']
def norm(t):return ''.join(re.findall(r'\w+',t.lower())).replace('ё','е')
def good(d,l):
 p=d/(l['id']+'.mp3');m=p.with_suffix('.json')
 try:
  x=json.loads(m.read_text());dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],stderr=subprocess.DEVNULL));return x['voice_id']==l['voice'] and x['text']==l['text'] and norm(' '.join(w['w'] for w in x['words']))==norm(l['text']) and abs(dur-x['duration'])<.1 and x['words'][-1]['end']<=dur+.25
 except:return False
async def one(l):
 if good(D,l):return
 if good(R/'audio',l):
  for ext in ['.mp3','.json']:shutil.copyfile(R/'audio'/(l['id']+ext),D/(l['id']+ext))
  return
 p=D/(l['id']+'.part.mp3');words=[]
 try:
  com=edge_tts.Communicate(l['text'],l['voice'],rate='+0%',proxy=os.environ.get('HTTPS_PROXY'))
  async with asyncio.timeout(55):
   with p.open('wb') as f:
    async for c in com.stream():
     if c['type']=='audio':f.write(c['data'])
     elif c['type'] in ('WordBoundary','SentenceBoundary'):words.append({'w':c['text'],'start':c['offset']/1e7,'end':(c['offset']+c['duration'])/1e7})
  dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],stderr=subprocess.DEVNULL))
  if norm(' '.join(w['w'] for w in words))!=norm(l['text']) or words[-1]['end']>dur+.25:raise ValueError(f'incomplete speech text={len(norm(" ".join(w["w"] for w in words)))}/{len(norm(l["text"]))} end={words[-1]["end"] if words else 0} duration={dur}')
  final=D/(l['id']+'.mp3');p.replace(final);meta=dict(l,speaker='sveta' if 'Svetlana' in l['voice'] else 'dima',voice_id=l['voice'],engine='edge-tts',rate='+0%',source_file=str(final),duration=dur,words=words)
  final.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));print('VERIFIED',l['id'],round(dur,2),flush=True)
 except Exception as e:p.unlink(missing_ok=True);print('MISS',l['id'],type(e).__name__,str(e)[:150],flush=True)
async def main():
 for sweep in range(4):
  missing=[l for l in lines if not good(D,l)];sem=asyncio.Semaphore(4)
  async def run(l):
   async with sem:await one(l)
  await asyncio.gather(*(run(l) for l in missing))
  print('SWEEP',sweep,'GOOD',sum(good(D,l) for l in lines),'/',len(lines),flush=True)
asyncio.run(main())
