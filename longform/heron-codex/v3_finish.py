"""Assemble V3 longform from genuine narrated scenes; NO publishing."""
import json
import subprocess
from pathlib import Path

R=Path(__file__).resolve().parent
O=R/"out"
O.mkdir(exist_ok=True)
S=json.loads((R/"timeline.json").read_text(encoding="utf-8"))
assert len(S)==44
D=sum(s["dur"] for s in S)
assert 1260<=D<=1800, f"NO-GO: V3 {D:.2f}s"
# Existing author-owned background music and Foley; no copyrighted recordings.
scope={"__file__":str(R/"compose.py")}
exec((R/"compose.py").read_text(encoding="utf-8").split("chunks=sorted")[0],scope)
shards=R/"v3_shards"
parts=sorted(shards.glob("main_*.mp4"))
assert len(parts)==64, f"NO-GO: incomplete V3 render: {len(parts)}/64"
listing=O/"v3_concat.txt"
listing.write_text("".join("file '"+str(p.resolve())+"'\n" for p in parts))
dst=O/"heron_ancient_automation_v3_21plus_ru.mp4"
subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",str(listing),
                "-i",str(O/"mix.wav"),"-map","0:v:0","-map","1:a:0",
                "-vf","scale=in_range=pc:out_range=tv,format=yuv420p",
                "-c:v","libx264","-preset","medium","-crf","21","-pix_fmt","yuv420p",
                "-r","30","-c:a","aac","-b:a","160k","-af","loudnorm=I=-16:TP=-3:LRA=9",
                "-t",str(D),"-movflags","+faststart",str(dst)],check=True)
subprocess.run(["python3","scripts/qa/longform_duration_gate.py",str(dst),
                "--report",str(O/"heron_v3_duration_gate.json")],check=True)
# Automated decode catches truncated files. Artistic review still required.
subprocess.run(["ffmpeg","-v","error","-i",str(dst),"-f","null","-"],check=True)
chapters=[{"time":f"{int(s['start'])//60:02}:{int(s['start'])%60:02}","title":s["title"]}
          for i,s in enumerate(S) if i==0 or i%4==0]
(O/"heron_v3_metadata.json").write_text(json.dumps({
    "version":"V3","status":"REVIEW_REQUIRED_NOT_PUBLISHED",
    "duration_sec":D,"narrator":"ru-RU-DmitryNeural",
    "source_video":dst.name,"chapters":chapters,
    "duration_gate":"passed","continuous_video_decode":"passed",
    "full_audio_listen":"not_performed",
    "visual_quality_review":"pending",
    "youtube_studio_duplicate_check":"pending",
    "metricool_account_limit_resolution":"pending"},ensure_ascii=False,indent=2),encoding="utf-8")
print("V3 technical gate and decode passed:",dst,D,"seconds")
