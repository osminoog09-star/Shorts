import asyncio,json,hashlib,time
from pathlib import Path
import edge_tts,edge_tts.communicate as ec
ec._SSL_CTX.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
B=Path(__file__).resolve().parent;j=json.loads((B/'script.json').read_text());out=B/'audio';out.mkdir(exist_ok=True)
sem=asyncio.Semaphore(4)
async def one(s):
 async with sem:
  p=out/(s['id']+'.mp3');m=p.with_suffix('.json');h=hashlib.sha256(s['text'].encode()).hexdigest()
  if p.exists() and m.exists() and json.loads(m.read_text()).get('hash')==h:return True
  for attempt,rate in enumerate(['+8%','+10%','+6%','+12%']):
   try:
    data=bytearray();words=[];com=edge_tts.Communicate(s['text'],'ru-RU-DmitryNeural',rate=rate,boundary='WordBoundary')
    async for ch in com.stream():
     if ch['type']=='audio':data.extend(ch['data'])
     elif ch['type']=='WordBoundary':words.append({'w':ch['text'],'start':ch['offset']/1e7,'end':(ch['offset']+ch['duration'])/1e7})
    if len(data)<1000 or not words:raise ValueError('missing speech or alignment')
    p.write_bytes(data);m.write_text(json.dumps({'id':s['id'],'text':s['text'],'hash':h,'voice':'ru-RU-DmitryNeural','rate':rate,'words':words},ensure_ascii=False,indent=2));print('OK',s['id'],len(data),flush=True);return True
   except Exception as ex:print('retry',s['id'],attempt,type(ex).__name__,flush=True);await asyncio.sleep(3+attempt*2)
  return False
async def main():
 results=await asyncio.gather(*(one(s) for s in j['scenes']+j['short']));failed=[s['id'] for s,r in zip(j['scenes']+j['short'],results) if not r];(B/'TTS_STATUS.json').write_text(json.dumps({'failed':failed,'voice':'Dmitry','credits':0},indent=2));print('FAILED',failed,flush=True)
asyncio.run(main())
