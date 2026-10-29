#!/usr/bin/env python3
"""Diagnostic probe: distinguish Microsoft voice, text, and runner/network failures."""
import asyncio, json, pathlib, traceback
import edge_tts
OUT=pathlib.Path("work/serve_20261029");OUT.mkdir(parents=True,exist_ok=True)
async def main():
 result={"edge_tts_version":getattr(edge_tts,"__version__","unknown"),"probes":[]}
 try:
  voices=await asyncio.wait_for(edge_tts.list_voices(),timeout=15)
  result["dmitry_listed"]=any(v.get("ShortName")=="ru-RU-DmitryNeural" for v in voices)
 except Exception as e:
  result["voice_list_error"]=f"{type(e).__name__}: {e}"
 for voice,text in [("ru-RU-DmitryNeural","Привет, это Дима."),("ru-RU-DmitryNeural","Представь: за едой приезжает не курьер, а маленький робот на колёсах."),("ru-RU-SvetlanaNeural","Привет, проверка.")]:
  path=OUT/("probe_"+str(len(result["probes"]))+".mp3")
  p={"voice":voice,"text":text}
  try:
   await asyncio.wait_for(edge_tts.Communicate(text,voice).save(str(path)),timeout=30)
   p["bytes"]=path.stat().st_size
   p["ok"]=p["bytes"]>1000
  except Exception as e:
   p["ok"]=False;p["error"]=f"{type(e).__name__}: {e}"
  result["probes"].append(p)
  print(json.dumps(p,ensure_ascii=False),flush=True)
 (OUT/"tts_diagnostics.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
 if not any(p["ok"] and p["voice"]=="ru-RU-DmitryNeural" for p in result["probes"]):
  print("NO-GO: Dmitry voice failed. Inspect diagnostics, do not substitute.",flush=True)
if __name__=="__main__":asyncio.run(main())
