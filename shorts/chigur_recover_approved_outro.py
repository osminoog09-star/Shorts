#!/usr/bin/env python3
"""Recover exact, already-approved horizontal M1lash outro from GitHub checkout.

This is a PRIVATE production asset handoff through existing motion-render workflow.
It does not create/edit an outro or publish a video.
"""
from pathlib import Path
from shutil import copy2
import hashlib,json,subprocess,os
root=Path(__file__).resolve().parents[1]
src=root/"media/outro/m1lash_outro_v1_horizontal.mp4"
out=root/"motion-output"
out.mkdir(exist_ok=True)
if not src.is_file() or src.stat().st_size<100000:raise RuntimeError("Approved horizontal outro is missing")
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,codec_name,width,height","-of","json",str(src)]))
if abs(float(probe["format"]["duration"])-6.6)>.18:raise RuntimeError("Outro length changed")
vs=[x for x in probe["streams"] if x["codec_type"]=="video"]
au=[x for x in probe["streams"] if x["codec_type"]=="audio"]
if not (len(vs)==1 and len(au)==1 and vs[0]["width"]==1920 and vs[0]["height"]==1080):
    raise RuntimeError("Approved horizontal outro profile changed")
subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(src),"-f","null","-"],check=True)
copy2(src,out/src.name)
copy2(root/"tools/assemble_with_outro.py",out/"assemble_with_outro.py")
(out/"horizontal_outro_manifest.json").write_text(json.dumps({
 "source":str(src.relative_to(root)),"size":src.stat().st_size,
 "sha256":hashlib.sha256(src.read_bytes()).hexdigest(),"duration":probe["format"]["duration"],
 "source_note":"Exact approved file from public repo checkout; no sound edits",
 "github_run_id":os.getenv("GITHUB_RUN_ID","unknown")
},ensure_ascii=False,indent=2)+"\n")
print("EXACT_APPROVED_OUTRO_EXPORTED",src.stat().st_size,flush=True)
