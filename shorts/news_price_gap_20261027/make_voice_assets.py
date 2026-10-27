"""M1lash price story audio: use approved Dmitry first, fallback to repository-native narrator for REVIEW ONLY.
Output is not a YouTube release. Requires final manual listening.
"""
import asyncio, json, subprocess, wave, pathlib, os
from dataclasses import dataclass
OUT=pathlib.Path("price_qa"); OUT.mkdir(exist_ok=True)
S=json.load(open("jobs/motion/m1lash_price_gap_20261027_ru.json",encoding="utf8"))["project"]["scenes"][:10]
def call(args): subprocess.run([str(x) for x in args],check=True)
async def dmitry(text,dest):
 import edge_tts
 for attempt in range(7):
  try:
   await edge_tts.Communicate(text,"ru-RU-DmitryNeural",rate="+0%").save(str(dest))
   if dest.stat().st_size<5000: raise RuntimeError("tiny audio")
   return True
  except Exception as exc:
   print("Dmitry retry",attempt,str(exc)[:160],flush=True)
   dest.unlink(missing_ok=True)
   await asyncio.sleep(min(11,2+attempt))
 return False
def native_tts(text,dest):
 raw=dest.with_suffix(".raw.wav")
 last=None
 for v in ["aleksandr-hq","aleksandr","pavel"]:
  try:
   x=subprocess.run(["RHVoice-test","-p",v,"-o",str(raw)],input=text.encode("utf8"),capture_output=True)
   if x.returncode==0 and raw.exists() and raw.stat().st_size>10000:
    call(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",raw,"-ar","24000","-ac","1",dest])
    raw.unlink(missing_ok=True)
    return v
   last=x.stderr.decode("utf8","replace")[:150]
  except Exception as e:last=str(e)
 raise RuntimeError("RHVoice fallback unavailable "+str(last))
async def main():
 ok=[]
 for i,s in enumerate(S):
  good=await dmitry(s["text"],OUT/f"d{i:02}.mp3")
  ok.append(good)
 print("Dmitry successes:",sum(ok),"/",len(S),flush=True)
 mode="ru-RU-DmitryNeural" if all(ok) else "RHVoice channel studio voice (fallback draft)"
 voice=None
 wavs=[]
 for i,s in enumerate(S):
  dst=OUT/f"scene{i:02}.wav"
  if all(ok):
   call(["ffmpeg","-loglevel","error","-y","-i",OUT/f"d{i:02}.mp3","-ar","24000","-ac","1","-sample_fmt","s16",dst])
  else:
   voice=native_tts(s["text"],dst)
  wavs.append(dst)
 durations=[]
 for dst in wavs:
  with wave.open(str(dst),"rb") as w: durations.append(w.getnframes()/w.getframerate())
 # Main voice + 0.20 s of room between scenes, no backing music.
 concat=OUT/"list.txt"
 concat.write_text("".join(f"file 'scene{i:02}.wav'\nfile 'silence.wav'\n" for i in range(len(S))),encoding="utf8")
 call(["ffmpeg","-loglevel","error","-y","-f","lavfi","-i","anullsrc=r=24000:cl=mono","-t","0.2","-c:a","pcm_s16le",OUT/"silence.wav"])
 call(["ffmpeg","-loglevel","error","-y","-f","concat","-safe","0","-i",concat,"-c:a","pcm_s16le",OUT/"speech.wav"])
 metadata={"scene_durations":durations,"pause_seconds":0.2,"tts":mode,"rhvoice_actual":voice,
 "edge_successes":sum(ok),"main_duration":sum(durations)+len(S)*.2,
 "ready_for_release":bool(all(ok)),"reason_if_draft":"Fallback replaces Dmitry and requires owner approval" if not all(ok) else ""}
 (OUT/"voice_report.json").write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding="utf8")
 print("VOICE_REPORT",json.dumps(metadata,ensure_ascii=False),flush=True)
if __name__=="__main__": asyncio.run(main())
