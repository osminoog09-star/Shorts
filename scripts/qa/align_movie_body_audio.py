#!/usr/bin/env python3
"""Align body AAC ending to video before attaching original studio outro.

Body VIDEO stream-copied, body AUDIO may be padded and encoded. Does not edit
the official outro. Never cut dialogue or claim release readiness on its own.
"""
import argparse,json,subprocess
from pathlib import Path
def duration(path):
    raw=subprocess.check_output(["ffprobe","-v","error","-show_entries","stream=codec_type,duration","-of","json",str(path)])
    return {s["codec_type"]:float(s["duration"]) for s in json.loads(raw)["streams"] if s.get("duration")}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path);p.add_argument("output",type=Path)
    p.add_argument("--end-gap",type=float,default=.050)
    a=p.parse_args()
    if not a.source.is_file() or a.source.resolve()==a.output.resolve():p.error("Bad input or output")
    if not .025<=a.end_gap<=.150:p.error("gap must be 0.025..0.150")
    d=duration(a.source);stop=d["video"]-a.end_gap
    if stop<=d["audio"]-.01:p.error("Cannot cut original speech; edit at a word boundary first")
    a.output.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(["ffmpeg","-hide_banner","-nostdin","-v","error","-y","-i",str(a.source),
        "-map","0:v:0","-map","0:a:0","-c:v","copy",
        "-af",f"apad=whole_dur={stop:.6f},atrim=end={stop:.6f},asetpts=PTS-STARTPTS",
        "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",str(a.output)],check=True)
    after=duration(a.output)
    if abs(after["video"]-d["video"])>.005 or abs(after["audio"]-stop)>.03:
        raise RuntimeError("Bad stream duration "+str(after))
    print(json.dumps({"input":d,"output":after,"target_gap":a.end_gap}))
if __name__=="__main__":main()
