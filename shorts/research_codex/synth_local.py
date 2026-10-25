"""Same approved Dmitry voice, local session only; trust the host CA bundle."""
import asyncio,json,sys
from pathlib import Path
import edge_tts,edge_tts.communicate as ec
# Keep certificate verification enabled, adding this runtime's supplied CA certificates.
ec._SSL_CTX.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
B=Path(__file__).resolve().parent;R=B.parents[1]
job=json.loads((R/'jobs/tts/research_codex.json').read_text())
out=R/'media/tts/research_codex';out.mkdir(parents=True,exist_ok=True)
sem=asyncio.Semaphore(3)
async def one(ln):
 async with sem:
  p=out/(ln['id']+'.mp3');m=p.with_suffix('.json')
  if p.exists() and p.stat().st_size>1000 and m.exists():return
  for trial in range(6):
   try:
    com=edge_tts.Communicate(ln['text'],job['voice'],rate=['+8%','+10%','+12%','+6%','+0%','+15%'][trial],boundary='WordBoundary')
    words=[];data=bytearray()
    async for ch in com.stream():
     if ch['type']=='audio':data.extend(ch['data'])
     elif ch['type']=='WordBoundary':words.append({'w':ch['text'],'start':ch['offset']/1e7,'end':(ch['offset']+ch['duration'])/1e7})
    if len(data)<1000:raise ValueError('empty narration')
    p.write_bytes(data);m.write_text(json.dumps({'text':ln['text'],'words':words},ensure_ascii=False,indent=2))
    print('OK',ln['id'],len(data),flush=True);return
   except Exception as ex:
    print('retry',ln['id'],trial,type(ex).__name__,flush=True)
    await asyncio.sleep(2+trial*2)
  print('FAILED',ln['id'],flush=True)
async def main():await asyncio.gather(*(one(l) for l in job['lines']))
if __name__=='__main__':asyncio.run(main())
