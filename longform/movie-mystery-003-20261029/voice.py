import asyncio,json,subprocess,os,re
from pathlib import Path
import edge_tts
R=Path(__file__).resolve().parent;B=R/'build';B.mkdir(exist_ok=True)
async def main():
 text=(R/'script_private.txt').read_text().strip();spoken=text.replace('«','').replace('»','') if os.environ.get('CLEAN_PUNCTUATION')=='1'else text;p=B/'voice_92.mp3';words=[]
 for attempt in range(5):
  try:
   words=[]
   with p.open('wb')as f:
    async for c in edge_tts.Communicate(spoken,'ru-RU-DmitryNeural',rate='+0%',boundary='WordBoundary',receive_timeout=45).stream():
     if c['type']=='audio':f.write(c['data'])
     elif c['type']=='WordBoundary':words.append(c)
   assert words and p.stat().st_size>1000;break
  except Exception:
   p.unlink(missing_ok=True)
   print('Exact voice retry',attempt+1,flush=True)
   if attempt==4:
    try:
     await edge_tts.Communicate('Привет, это Дима.','ru-RU-DmitryNeural',rate='+0%').save(str(B/'diagnostic_only.mp3'))
     print('SMOKE_SUCCEEDED_FULL_TEXT_FAILED',flush=True)
    except Exception as e:print('SMOKE_FAILED',type(e).__name__,str(e),flush=True)
    raise
   await asyncio.sleep(min(40,5*(attempt+1)))
 meta=dict(speaker='dima',voice_id='ru-RU-DmitryNeural',engine='edge-tts',rate='+0%',source_file=p.name,text=text,engine_input_text=spoken,words=words)
 p.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
 duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]))
 s=dict(id=92,title='ОНА НЕ ЗАБЫЛА',chapter='Кинозагадка',kind='fact',visual='movie',text=text,audio=p.name,duration=duration,words=words,start=0,cta=True)
 (B/'timeline.json').write_text(json.dumps(dict(scenes=[])))
 (B/'short_92_timeline.json').write_text(json.dumps(dict(duration=duration+.18,scenes=[s]),ensure_ascii=False,indent=2))
 print('Accepted exact Dima narration',duration,flush=True)
if __name__=='__main__':asyncio.run(main())
