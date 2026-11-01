#!/usr/bin/env python3
"""Precision story edits to close independently detected dead-air gaps in film Shorts.

Reuses only the already approved RU source from existing Actions artifacts.
No long-movie downloads, no publication, no replacement of approved M1lash outro.
Actual silent windows rejected by scripts/movie_short.py V47 (01.11).
Cuts are mapped to original source timeline, not to already-cut V45 bodies.
"""
import argparse,json,subprocess
from pathlib import Path

# Absolute film SOURCE times in seconds, measured/reviewed on the archived MP4.
# 001: keep gun reveal action around 147+; shorten only quiet hesitation.
# 002: start at the meaningful exchange, preserve final refusal after 202s.
# 005: preserve confrontation and concluding line, remove long 41–50s gap.
PARTS={
 "001":[(128.0,145.4),(147.1,160.0)],
 "002":[(174.0,199.0),(202.4,209.0)],
 "005":[(17.0,41.0),(50.0,58.0)],
}
def main():
 p=argparse.ArgumentParser();p.add_argument("--id",required=True,choices=sorted(PARTS))
 p.add_argument("--src",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
 a=p.parse_args()
 if not a.src.is_file():raise FileNotFoundError(a.src)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 src_d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(a.src)]))
 parts=PARTS[a.id]
 if any(x<0 or y<=x or y>src_d for x,y in parts):raise ValueError("Source time range out of bounds")
 filters=[]
 for i,(start,end) in enumerate(parts):
  filters.extend([f"[0:v]trim=start={start:.6f}:end={end:.6f},setpts=PTS-STARTPTS,fps=30,setsar=1[v{i}]",
                  f"[0:a]atrim=start={start:.6f}:end={end:.6f},asetpts=PTS-STARTPTS,aresample=48000[a{i}]"])
 names="".join(f"[v{i}][a{i}]" for i in range(len(parts)))
 filters.append(names+f"concat=n={len(parts)}:v=1:a=1[v][a]")
 subprocess.run(["ffmpeg","-hide_banner","-nostdin","-y","-v","warning",
  "-i",str(a.src),"-filter_complex",";".join(filters),"-map","[v]","-map","[a]",
  "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","30",
  "-c:a","aac","-b:a","224k","-ar","48000","-ac","2",
  "-movflags","+faststart",str(a.out)],check=True,timeout=500)
 d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",str(a.out)]))
 expected=sum(y-x for x,y in parts)
 if abs(d-expected)>.12:raise RuntimeError(f"Duration {d} vs {expected}")
 subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(a.out),"-f","null","-"],check=True,timeout=250)
 print(json.dumps({"id":a.id,"source_seconds":src_d,"story_s":round(d,3),"segments":parts,"full_decode":"PASS"}),flush=True)
if __name__=="__main__":main()
