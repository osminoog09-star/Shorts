#!/usr/bin/env python3
"""Chigur V21 bounded-memory editor. No movie sources or assets in the repo.

Execute with local private V20 master, 28 locally rendered graphics MP4s, and
V21_GRAPHICS_WINDOWS_PRIVATE.json adjacent to V21_GRAPHICS_ONLY_AUTHOR_CAPTIONS.ass.
Works sequentially (max two video decoders), copying original AAC unchanged.
This code does NOT make unlicensed sources available and never uploads anything.
"""
from __future__ import annotations
import argparse, json, subprocess, hashlib
from pathlib import Path

FPS=30
def run(argv):
    return subprocess.run(argv,check=True)
def probe(f):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,width,nb_frames","-of","json",str(f)],text=True))
def count(f):
    p=probe(f)
    return int(next(x["nb_frames"] for x in p["streams"] if x["codec_type"]=="video"))
def timecode(s):
    centis=round(s*100);h,centis=divmod(centis,360000);m,centis=divmod(centis,6000);sec,centis=divmod(centis,100)
    return f"{h}:{m:02d}:{sec:02d}.{centis:02d}"
def secs(t):
    p=t.split(":");return int(p[0])*3600+int(p[1])*60+float(p[2])
def caption_slice(source,a,b,target):
    header=[];texts=[]
    for line in source.read_text(encoding="utf8").splitlines():
        if not line.startswith("Dialogue: "):header.append(line);continue
        p=line[len("Dialogue: "):].split(",",9)
        if len(p)<10:continue
        start,end=secs(p[1]),secs(p[2]); lo=max(start,a/FPS);hi=min(end,b/FPS)
        if hi-lo>.11:
            p[1],p[2]=timecode(lo-a/FPS),timecode(hi-a/FPS)
            texts.append("Dialogue: "+",".join(p))
    target.write_text("\n".join(header+texts)+"\n",encoding="utf8")
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--baseline",required=True)
    ap.add_argument("--graphics",required=True)
    ap.add_argument("--map",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--work",required=True)
    ap.add_argument("--crf",type=int,default=19)
    ap.add_argument("--preview-frames",type=int,default=0)
    a=ap.parse_args()
    src=Path(a.baseline);arts=Path(a.graphics);mapping=Path(a.map)
    out=Path(a.output);work=Path(a.work);work.mkdir(parents=True,exist_ok=True);out.parent.mkdir(parents=True,exist_ok=True)
    edits=json.loads(mapping.read_text(encoding="utf8"))["windows"]
    if len(edits)!=28:raise ValueError("Expected 28 graphics windows")
    meta=probe(src);n_total=count(src)
    if int(next(x["width"] for x in meta["streams"] if x["codec_type"]=="video"))!=1920:raise ValueError("1080p baseline required")
    # Fail closed if a proposed graphics window would cover a verified actor clip.
    # Read physical segment durations; nominal editorial timestamps can drift.
    timeline_file=mapping.parent/"V20_EDITORIAL_TIMELINE_PRIVATE.json"
    if not timeline_file.exists():raise FileNotFoundError(timeline_file)
    parts=json.loads(timeline_file.read_text(encoding="utf8"))["parts"]
    film_windows=[];cursor=0.0
    for part in parts:
        segment=mapping.parent/"segments"/(part["id"]+".mp4")
        if not segment.exists():raise FileNotFoundError(segment)
        duration=float(probe(segment)["format"]["duration"])
        if part["id"].startswith("film_"):
            film_windows.append((cursor,cursor+duration,part["id"]))
        cursor+=duration
    for shot in edits:
        for start,end,film_id in film_windows:
            if shot["start_sec"]<end+.05 and shot["end_sec"]>start-.05:
                raise RuntimeError("Graphic would cover original film dialogue "+film_id)
    spans=[];previous=0;spid=0
    for shot in edits:
        left,right=round(shot["start_sec"]*FPS),round(shot["end_sec"]*FPS)
        if left<=previous or right<=left or right>n_total:raise ValueError("Window intersects prior range")
        video=arts/(shot["id"]+"_3D_ONLY.mp4")
        if not video.exists():raise FileNotFoundError(video)
        if float(probe(video)["format"]["duration"])+.20<shot["seconds"]:raise ValueError("short 3D "+shot["id"])
        if left>previous:spans.append((spid,previous,left,None));spid+=1
        spans.append((spid,left,right,shot["id"]));spid+=1;previous=right
    if previous<n_total:spans.append((spid,previous,n_total,None))
    if sum(r-l for _,l,r,_ in spans)!=n_total:raise AssertionError("frame gaps")
    captions=mapping.parent/"V21_GRAPHICS_ONLY_AUTHOR_CAPTIONS.ass"
    if not captions.exists():raise FileNotFoundError(captions)
    files=[];done=0
    for index,left,right,shot_id in spans:
        if a.preview_frames and done>=a.preview_frames:break
        frames=min(right-left,a.preview_frames-done) if a.preview_frames else right-left
        f=work/f"span_{index:02d}.mp4"
        if not (f.exists() and count(f)==frames):
            cmd=["ffmpeg","-hide_banner","-nostdin","-y","-v","error","-ss",f"{left/FPS:.9f}","-i",str(src)]
            if shot_id:
                cmd+=["-i",str(arts/(shot_id+"_3D_ONLY.mp4"))]
                subtitles=work/f"captions_{index:02d}.ass"
                caption_slice(captions,left,left+frames,subtitles)
                cmd+=["-filter_complex",
                   f"[0:v]fps=30,setpts=PTS-STARTPTS[b];[1:v]fps=30,setpts=PTS-STARTPTS[g];"
                   f"[b][g]overlay=0:0:shortest=0:repeatlast=0:eof_action=pass,ass={subtitles}[v]",
                   "-map","[v]"]
            else:cmd+=["-vf","fps=30"]
            cmd+=["-frames:v",str(frames),"-an","-c:v","libx264","-preset","veryfast",
                  "-crf",str(a.crf),"-pix_fmt","yuv420p","-r","30","-g","60","-bf","0",str(f)]
            run(cmd)
            if count(f)!=frames:raise RuntimeError("frame count changed "+str(f))
        files.append(f);done+=frames
        print("SPAN",index,shot_id or "original",frames,flush=True)
    if not a.preview_frames and done!=n_total:raise AssertionError("incomplete timeline")
    listing=work/"concat.txt"
    listing.write_text("".join(f"file '{str(f)}'\n" for f in files))
    cmd=["ffmpeg","-hide_banner","-nostdin","-y","-v","error","-f","concat","-safe","0","-i",str(listing)]
    if not a.preview_frames:cmd+=["-i",str(src),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","copy"]
    else:cmd+=["-map","0:v:0","-c:v","copy","-an"]
    cmd+=["-movflags","+faststart",str(out)]
    run(cmd)
    if count(out)!=done:raise AssertionError(f"final frames {count(out)} != {done}")
    run(["ffmpeg","-v","error","-xerror","-i",str(out),"-f","null","-"])
    print("VIDEO_FULL_DECODE_PASS",out,done,"sha256",hashlib.sha256(out.read_bytes()).hexdigest(),flush=True)
if __name__=="__main__":main()
