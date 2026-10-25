"""Retry missing narration with a disposable context prelude, trimmed by word boundaries."""
import asyncio,json,subprocess
from pathlib import Path
import edge_tts,edge_tts.communicate as ec
ec._SSL_CTX.load_verify_locations('/etc/ssl/certs/ca-certificates.crt')
B=Path(__file__).resolve().parent;R=B.parents[1];j=json.loads((R/'jobs/tts/research_codex.json').read_text());out=R/'media/tts/research_codex';sem=asyncio.Semaphore(2)
async def one(l):
 async with sem:
  p=out/(l['id']+'.mp3');m=p.with_suffix('.json')
  if p.exists() and m.exists():return
  for attempt,prefix in enumerate(['Продолжаем исследование. ','Разберёмся подробно. ','Проверяем факты. ','Вот что выяснилось. ']):
   try:
    words=[];data=bytearray()
    com=edge_tts.Communicate(prefix+l['text'],j['voice'],rate='+8%',boundary='WordBoundary')
    async for ch in com.stream():
     if ch['type']=='audio':data.extend(ch['data'])
     elif ch['type']=='WordBoundary':words.append({'w':ch['text'],'start':ch['offset']/1e7,'end':(ch['offset']+ch['duration'])/1e7})
    skip=len(prefix.split());assert len(words)>skip
    start=max(0,words[skip]['start']-.035);tmp=p.with_suffix('.context.mp3');tmp.write_bytes(data)
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(start),'-i',str(tmp),'-c:a','libmp3lame','-b:a','128k',str(p)],check=True)
    for w in words[skip:]:w['start']-=start;w['end']-=start
    m.write_text(json.dumps({'text':l['text'],'words':words[skip:],'trimmed_context':True},ensure_ascii=False,indent=2));tmp.unlink();print('REPAIRED',l['id'],flush=True);return
   except Exception as ex:print('context retry',l['id'],attempt,type(ex).__name__,flush=True);await asyncio.sleep(3)
  print('CONTEXT FAILED',l['id'],flush=True)
async def main():
 wanted={'research_privacy_2','research_privacy_4','research_truth_0','research_truth_1','research_truth_3','research_business_3','research_business_4','research_business_5'}
 await asyncio.gather(*(one(l) for l in j['lines'] if l['id'] in wanted))
asyncio.run(main())
