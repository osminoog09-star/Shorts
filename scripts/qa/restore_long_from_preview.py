#!/usr/bin/env python3
"""Restore the full-resolution movie picture while borrowing ONLY graphics windows
from a smaller editorial preview. Keeps the base movie/audio outside these windows.
This does not turn PIL/vector graphics into native 3D. Never commit movie files.
Usage: python scripts/qa/restore_long_from_preview.py \
  --base master1080.mp4 --preview art720.mp4 --ranges new_graphics_ranges.json \
  --output final_private.mp4
"""
import argparse
import json
import subprocess
from pathlib import Path

def probe_duration(filename):
    p = subprocess.run(["ffprobe","-v","error","-show_entries",
        "format=duration","-of","default=nw=1:nk=1",str(filename)],
        capture_output=True,text=True,check=True)
    return float(p.stdout.strip())

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for arg in ("base","preview","ranges","output"):
        ap.add_argument("--"+arg,required=True,type=Path)
    ap.add_argument("--crf",type=int,default=18)
    ap.add_argument("--preset",default="superfast")
    args=ap.parse_args()
    for f in (args.base,args.preview,args.ranges):
        if not f.is_file(): ap.error("File missing: "+str(f))
    if args.output.resolve() in (args.base.resolve(),args.preview.resolve()):
        ap.error("Output must be different from inputs")
    data=json.loads(args.ranges.read_text(encoding="utf-8"))
    runs=data.get("runs",[])
    if not runs: ap.error("No graphics windows")
    base_d=probe_duration(args.base)
    preview_d=probe_duration(args.preview)
    if abs(base_d-preview_d)>0.10:
        ap.error(f"Master/preview timing mismatch: {base_d} vs {preview_d}")
    previous_end=0
    expressions=[]
    for run in runs:
        s,e,*_=run
        s=float(s);e=float(e)
        if s<previous_end or e<=s or e>base_d+0.1:
            ap.error("Invalid or overlapping graphics intervals")
        previous_end=e
        expressions.append(f"between(t,{s:.5f},{e-0.00001:.5f})")
    enable="+".join(expressions)
    fc=("[1:v]scale=1920:1080:flags=lanczos,setsar=1[art];"
       "[0:v][art]overlay=0:0:enable='"+enable+
       "':shortest=1:format=auto[video]")
    command=["ffmpeg","-hide_banner","-nostdin","-y","-i",str(args.base),
       "-i",str(args.preview),"-filter_complex",fc,
       "-map","[video]","-map","0:a:0","-c:v","libx264",
       "-preset",args.preset,"-crf",str(args.crf),"-pix_fmt","yuv420p",
       "-r","30","-c:a","copy","-movflags","+faststart",str(args.output)]
    subprocess.run(command,check=True)
    print("PRIVATE REVIEW ONLY — confirm audio bitstream hash and run check.py/look.py before release.")

if __name__=="__main__":
    main()
