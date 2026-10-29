#!/usr/bin/env python3
"""M1lash media preflight. Uses local FFmpeg/ffprobe; no API keys or paid tools.

Checks metadata, complete decode, audio-tail silence and diagnostic black/freeze windows.
It does NOT claim artistic approval. Use --strict to fail hard gates.
"""
import argparse, json, re, shutil, subprocess, hashlib
from pathlib import Path

def call(cmd,timeout=900):
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=timeout)
    return p.returncode,p.stdout,p.stderr

def probe(path):
    rc,out,err=call(["ffprobe","-v","error","-show_entries",
      "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate,duration",
      "-of","json",str(path)])
    if rc:raise RuntimeError("ffprobe failed: "+err[-500:])
    return json.loads(out)

def analyze(path, seconds=35, target_silence=3.0, profile='auto'):
    if profile not in ('auto','short','long'): raise ValueError('Invalid profile')
    path=Path(path); metadata=probe(path); duration=float(metadata["format"]["duration"])
    streams=metadata["streams"]; videos=[s for s in streams if s["codec_type"]=="video"]
    audios=[s for s in streams if s["codec_type"]=="audio"]
    findings=[]; checks={}
    checks["video_present"]=bool(videos);checks["audio_present"]=bool(audios)
    if not videos: findings.append({"severity":"P0","issue":"no video stream"})
    if not audios: findings.append({"severity":"P0","issue":"no audio stream"})
    checks["resolution"]=f'{videos[0].get("width")}x{videos[0].get("height")}' if videos else None
    if videos:
        w,h=videos[0].get("width",0),videos[0].get("height",0)
        kind=profile if profile!='auto' else ('short' if h>w else 'long')
        checks["profile"]=kind
        min_w,min_h=(1080,1920) if kind=='short' else (1920,1080)
        if (h<=w if kind=='short' else w<=h):
            findings.append({"severity":"P0","issue":f"wrong orientation for {kind}"})
        if w<min_w or h<min_h:
            findings.append({"severity":"P1","issue":f"below {kind} target: {w}x{h} vs {min_w}x{min_h}"})

    checks["streams"]= [{"type":s["codec_type"],"duration":s.get("duration"),"codec":s.get("codec_name")} for s in streams]
    for s in streams:
        if "duration" in s:
            delta=abs(float(s["duration"])-duration)
            if delta>.5:findings.append({"severity":"P0","issue":f'stream duration mismatch {s["codec_type"]}: {delta:.3f}s'})
    # Real decoder pass: technical success is separate from viewing.
    rc,_,err=call(["ffmpeg","-nostdin","-v","error","-xerror","-i",str(path),"-map","0:v:0",
       "-map","0:a:0?","-f","null","-"],timeout=2400)
    checks["decode_pass"]=rc==0
    if rc:findings.append({"severity":"P0","issue":"full decode failed","detail":err[-700:]})
    if audios:
        start=max(0,duration-seconds)
        rc,_,err=call(["ffmpeg","-nostdin","-hide_banner","-ss",str(start),"-i",str(path),
          "-af","silencedetect=noise=-42dB:d=0.5","-vn","-f","null","-"],timeout=120)
        events=[]
        for m in re.finditer(r"silence_start:\s*([\d.]+)|silence_end:\s*([\d.]+)\s*\|\s*silence_duration:\s*([\d.]+)",err):
            if m.group(1) is not None:events.append(("start",float(m.group(1))))
            else:events.append(("end",float(m.group(2))))
        checks["tail_silence_events"]=events
        # Last-start without last-end means silence reaches end of stream.
        if events and events[-1][0]=="start" and (duration-start-events[-1][1])>=target_silence:
            findings.append({"severity":"P0","issue":"unintended long silence at end","seconds":round(duration-start-events[-1][1],2)})
    # Diagnostics for reviewer; black/freeze output alone never means defective.
    start=max(0,duration-seconds)
    rc,_,err=call(["ffmpeg","-nostdin","-hide_banner","-ss",str(start),"-i",str(path),
      "-vf","blackdetect=d=0.5:pix_th=0.08,freezedetect=n=-60dB:d=2.0","-an","-f","null","-"],timeout=160)
    checks["tail_black_events"]=re.findall(r"black_start:[^\n]+",err)[-12:]
    checks["tail_freeze_events"]=re.findall(r"freeze_(?:start|end):[^\n]+",err)[-12:]
    with path.open("rb") as src:
        sha=hashlib.file_digest(src,"sha256").hexdigest()
    checks["sha256"]=sha
    checks["duration_seconds"]=round(duration,3)
    checks["qa_scope"]="metadata, full technical decode and automated tail diagnostics; HUMAN artistic review still required"
    return {"file":str(path),"checks":checks,"issues":findings,
            "technical_pass":not any(x["severity"]=="P0" for x in findings)}

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("input");p.add_argument("--json-out");p.add_argument("--strict",action="store_true");p.add_argument("--profile",choices=["auto","short","long"],default="auto")
    a=p.parse_args()
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):raise SystemExit("FFmpeg and ffprobe required")
    result=analyze(a.input,profile=a.profile)
    out=json.dumps(result,ensure_ascii=False,indent=2)
    if a.json_out:Path(a.json_out).write_text(out,encoding="utf-8")
    print(out)
    if a.strict and not result["technical_pass"]:raise SystemExit(2)
