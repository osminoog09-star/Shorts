#!/usr/bin/env python3
"""Synthesize only approved Dima as one continuous take; retry transient Edge issue."""
import asyncio, json, importlib.metadata, random
from pathlib import Path
import edge_tts
D=Path("shorts/genie4_20261028/production.json")
P=Path("work/genie4/final_voice");P.mkdir(parents=True,exist_ok=True)
shots=json.loads(D.read_text(encoding="utf8"))["shots"]
text=" ".join(s["text"] for s in shots)
async def main():
 print("version",importlib.metadata.version("edge-tts"),"chars",len(text),flush=True)
 for attempt in range(1,15):
  file=P/"dima_full.mp3"; words=[]
  try:
   c=edge_tts.Communicate(text,voice="ru-RU-DmitryNeural",rate="+0%")
   n=0
   with file.open("wb") as f:
    async for chunk in c.stream():
     if chunk["type"]=="audio":f.write(chunk["data"]);n+=len(chunk["data"])
     if chunk["type"]=="WordBoundary":words.append(dict(w=chunk["text"],start=chunk["offset"]/1e7,end=(chunk["offset"]+chunk["duration"])/1e7))
   if n<40000 or len(words)<80:
    raise ValueError(f"incomplete audio n={n}, word count={len(words)}")
   md={"voice_id":"ru-RU-DmitryNeural","engine":"edge-tts","rate":"+0%","text":text,"shot_texts":[s["text"] for s in shots],"words":words,"bytes":n,"is_dima":True}
   (P/"voice_manifest.json").write_text(json.dumps(md,ensure_ascii=False,indent=2))
   print("SUCCESS",n,len(words),flush=True)
   return
  except Exception as e:
   file.unlink(missing_ok=True)
   print("NOAUDIO",attempt,type(e).__name__,str(e)[:220],flush=True)
   if attempt==14:raise RuntimeError("NO-GO approved Dima unavailable after 14 bounded attempts") from e
   await asyncio.sleep(5+attempt*2)
asyncio.run(main())
