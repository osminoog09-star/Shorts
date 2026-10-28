#!/usr/bin/env python3
"""Actual approved-voice TTS for M1lash Neurooffice S01E01.
No fallback voice, no stretched silence, no synthetic duration reporting.
"""
import argparse, asyncio, hashlib, json, re, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
VOICES={"dima":"ru-RU-DmitryNeural","sveta":"ru-RU-SvetlanaNeural"}
RATE={"dima":"+0%","sveta":"+0%"}
SPEAKER=re.compile(r"^\*\*(ДИМА|СВЕТА):\*\*\s*(.*)$",re.M)
HEAD=re.compile(r"^##\s+Сцена\s+(\d+[Б]?)\.\s+(.+)$",re.M)
INSERT=re.compile(r"^##\s+Вставка\s+после\s+сцены\s+(\d+[Б]?)\s+—\s+(.+)$",re.M)
BREAK=re.compile(r"(?<=[.!?])\s+(?=[А-ЯЁ«])")

def run(*args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError("ffmpeg failed "+p.stderr[-2000:])
 return p.stdout.strip()

def duration(p):
 j=json.loads(run("ffprobe","-v","error","-show_entries","format=duration","-of","json",str(p)))
 return float(j["format"]["duration"])

def parse_blocks(txt,kind):
 rx=HEAD if kind=="core" else INSERT
 heads=list(rx.finditer(txt))
 if not heads:raise RuntimeError("no parsed scenes in "+kind)
 out=[]
 for i,h in enumerate(heads):
  body=txt[h.end():heads[i+1].start() if i+1<len(heads) else len(txt)]
  lines=[]
  for who,t in SPEAKER.findall(body):
   who={"ДИМА":"dima","СВЕТА":"sveta"}[who]
   t=re.sub(r"\s+"," ",t).strip()
   # Per TTS line do not send large paragraphs; retain all exact authored words.
   pieces=BREAK.split(t)
   buf=""
   for part in pieces:
    if buf and len(buf)+len(part)>260:
     lines.append({"speaker":who,"text":buf.strip()});buf=""
    buf+=" "+part
   if buf.strip():lines.append({"speaker":who,"text":buf.strip()})
  out.append({"scene":h.group(1),"title":h.group(2),"kind":kind,"lines":lines})
 return out

def canonical():
 original=(HERE/"EP01_SCRIPT_REFERENCE.md").read_text("utf-8")
 extra=(HERE/"EXTRA_SCENES_V2.md").read_text("utf-8")
 base=parse_blocks(original,"core")
 addon=parse_blocks(extra,"extra")
 ordered=[]
 for s in base:
  ordered.append(s)
  ordered.extend(x for x in addon if x["scene"]==s["scene"])
 lines=[]
 for sc_i,sc in enumerate(ordered):
  for l in sc["lines"]:lines.append({**l,"scene_index":sc_i,"chapter":sc["title"],"stage":sc["kind"]})
 assert len(base)==10,(len(base),[x["scene"] for x in base])
 assert len(addon)==6,len(addon)
 assert all(0<len(l["text"])<=600 for l in lines)
 return ordered,lines

async def synth_one(i,line,edge,sem,out,force):
 who=line["speaker"];voice=VOICES[who];path=out/f"line_{i:04d}_{who}.mp3"
 timing=out/f"line_{i:04d}_{who}.json"
 if not force and path.exists() and path.stat().st_size>2000 and timing.exists():return
 async with sem:
  last=None
  for attempt in range(4):
   try:
    await asyncio.sleep(attempt*2)
    comm=edge.Communicate(line["text"],voice=voice,rate=RATE[who],volume="+0%")
    boundaries=[];audio=[]
    async for chunk in comm.stream():
     if chunk["type"]=="audio":audio.append(chunk["data"])
     elif chunk["type"]=="WordBoundary":
      boundaries.append({"word":chunk["text"],"offset_s":chunk["offset"]/10000000,"duration_s":chunk["duration"]/10000000})
    path.write_bytes(b"".join(audio))
    if path.stat().st_size<2000:raise RuntimeError("empty TTS")
    d=duration(path)
    if d<.17:raise RuntimeError("TTS too short")
    timing.write_text(json.dumps({"voice_id":voice,"engine":"Microsoft Edge TTS",
      "speaker":who,"rate":RATE[who],"text":line["text"],
      "duration_s":d,"words":boundaries},ensure_ascii=False,indent=2),"utf-8")
    return
   except Exception as e:
    last=e
    path.unlink(missing_ok=True);timing.unlink(missing_ok=True)
  raise RuntimeError(f"NO-GO TTS failure at {i} {who}/{voice}: {last}")

async def main():
 import edge_tts
 ap=argparse.ArgumentParser()
 ap.add_argument("--force",action="store_true")
 ap.add_argument("--jobs",type=int,default=2)
 args=ap.parse_args()
 ordered,lines=canonical()
 out=HERE/"production"/"audio";out.mkdir(parents=True,exist_ok=True)
 (out/"SCRIPT_MANIFEST.json").write_text(json.dumps(
  {"status":"SCRIPT_VALIDATED_NOT_FILM","scenes":ordered,"lines":lines},ensure_ascii=False,indent=2),"utf-8")
 sem=asyncio.Semaphore(args.jobs)
 await asyncio.gather(*(synth_one(i,line,edge_tts,sem,out,args.force) for i,line in enumerate(lines)))
 master=out/"NEUROOFFICE_S01E01_DIMA_SVETA.m4a"
 concat=out/"dialogue.ffconcat"
 concat.write_text("ffconcat version 1.0\n"+"".join(
  f"file 'line_{i:04d}_{l['speaker']}.mp3'\n" for i,l in enumerate(lines)))
 run("ffmpeg","-nostdin","-v","error","-y","-f","concat","-safe","0",
     "-i",str(concat),"-ar","48000","-ac","2","-c:a","aac","-b:a","160k",str(master))
 secs=duration(master);pos=0;entries=[]
 for i,l in enumerate(lines):
  p=out/f"line_{i:04d}_{l['speaker']}.mp3"
  metadata=json.loads((out/f"line_{i:04d}_{l['speaker']}.json").read_text("utf-8"))
  d=duration(p)
  entries.append({"index":i,"scene":l["scene_index"],"chapter":l["chapter"],
     "speaker":l["speaker"],"voice_id":VOICES[l["speaker"]],"engine":"Microsoft Edge TTS",
     "source_file":p.name,"start_s":round(pos,3),"end_s":round(pos+d,3),
     "duration_s":round(d,3),"words":[{**w,"at_s":round(pos+w["offset_s"],3)} for w in metadata["words"]],
     "text":l["text"]})
  pos+=d
 audit={"status":"AUDIO_RENDERED_NOT_FILM","spoken_words":sum(len(l["text"].split()) for l in lines),
   "lines":len(lines),"scenes":len(ordered),"voice_ids":VOICES,"audio_duration_s":secs,
   "required_film_min_s":1260,"audio_reaches_21min":secs>=1260,
   "audio_sha256":hashlib.sha256(master.read_bytes()).hexdigest(),"timeline":entries}
 (out/"AUDIO_MANIFEST.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2),"utf-8")
 print(json.dumps({"audio_seconds":secs,"scene_count":len(ordered),
   "spoken_words":audit["spoken_words"],"segments":len(lines),
   "21min_audio":audit["audio_reaches_21min"]},ensure_ascii=False),flush=True)
 # Intentionally no synthetic pauses to force a duration threshold. Renderer checks MP4 duration separately.

if __name__=="__main__":asyncio.run(main())
