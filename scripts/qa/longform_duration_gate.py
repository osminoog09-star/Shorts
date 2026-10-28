#!/usr/bin/env python3
"""M1lash longform release technical gate: every new full video must run >=21:00."""
import argparse
import json
import subprocess
from pathlib import Path

MIN_SECONDS=1260.0

def validate(probe):
    issues=[]
    try:
        seconds=float(probe["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        return {"pass":False,"issues":["missing duration"]}
    streams=probe.get("streams",[])
    video=next((x for x in streams if x.get("codec_type")=="video"),None)
    audio=next((x for x in streams if x.get("codec_type")=="audio"),None)
    if seconds<MIN_SECONDS: issues.append("under 21:00 minimum")
    if not video: issues.append("video absent")
    else:
        w,h=video.get("width",0),video.get("height",0)
        if w<1920 or h<1080 or w<=h:
            issues.append("full film must be landscape >=1920x1080")
    if not audio: issues.append("audio absent")
    for name,s in (("video",video),("audio",audio)):
        if s and s.get("duration") not in (None,"","N/A"):
            try:
                if abs(float(s["duration"])-seconds)>2:
                    issues.append(name+" stream duration differs >2s")
            except (ValueError,TypeError):issues.append(name+" stream has invalid duration")
    return {"pass":not issues,"seconds":round(seconds,3),"minimum_seconds":MIN_SECONDS,
            "issues":issues,"limitations":"technical duration/streams check; not story, artistic, rights or audio-content validation"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("movie")
    p.add_argument("--report")
    a=p.parse_args()
    movie=Path(a.movie)
    if not movie.is_file() or movie.suffix.lower()!=".mp4":
        raise SystemExit("NO-GO: final MP4 missing")
    out=subprocess.run(["ffprobe","-v","error","-show_entries",
       "format=duration:stream=codec_type,duration,width,height","-of","json",str(movie)],
       capture_output=True,text=True,timeout=45)
    if out.returncode:raise SystemExit("NO-GO: ffprobe failure")
    result=validate(json.loads(out.stdout))
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if a.report:Path(a.report).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    if not result["pass"]:raise SystemExit(2)
if __name__=="__main__":main()
