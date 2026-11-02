#!/usr/bin/env python3
"""M1lash legacy movie Shorts recovery: previously obtained RU source, official builder.
Triggered by jobs/motion/movie_review_*.json. Private QA, NEVER YouTube upload.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

import requests

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"motion-output"

def run(args):
    print("EXEC", " ".join(str(x) for x in args[:5]),flush=True)
    subprocess.run([str(x) for x in args],check=True)

def restore(artifact_id, member, destination):
    url=f"https://api.github.com/repos/osminoog09-star/Shorts/actions/artifacts/{artifact_id}/zip"
    token=os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing Actions GITHUB_TOKEN")
    with requests.get(url,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json"},
                      stream=True,timeout=120) as res:
        res.raise_for_status()
        archive=destination.parent/"source_archive.zip"
        size=0
        with archive.open("wb") as out:
            for chunk in res.iter_content(chunk_size=1048576):
                size+=len(chunk)
                if size>150_000_000:raise ValueError("Source artifact limit exceeded")
                out.write(chunk)
    with zipfile.ZipFile(archive) as z:
        info=z.getinfo(member)
        if info.file_size>130_000_000 or info.file_size<1_000_000:
            raise ValueError("Unexpected source file size")
        with z.open(info) as inp,destination.open("wb") as out:
            shutil.copyfileobj(inp,out)
    print("RESTORED source",destination.stat().st_size,flush=True)

def trim(src, parts, output):
    if not parts:
        shutil.copyfile(src,output)
        return
    # Encode selected story windows with synchronized audio and fresh timestamp origin.
    f=[]
    for n,(start,end) in enumerate(parts):
        if end<=start:raise ValueError("invalid timeline")
        f.extend((f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS,fps=30[v{n}]",
                  f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,aresample=48000[a{n}]"))
    links="".join(f"[v{n}][a{n}]" for n in range(len(parts)))
    f.append(links+f"concat=n={len(parts)}:v=1:a=1[v][a]")
    run(["ffmpeg","-hide_banner","-v","error","-y","-i",src,
         "-filter_complex",";".join(f),
         "-map","[v]","-map","[a]","-c:v","libx264",
         "-preset","veryfast","-crf","19","-pix_fmt","yuv420p","-r","30",
         "-c:a","aac","-b:a","224k","-ar","48000","-ac","2",output])

def main():
    filename=os.getenv("M1LASH_JOB_PATH","")
    f=Path(filename)
    if f.parent.as_posix()!="jobs/motion" or not f.name.startswith("movie_review_") or f.suffix!=".json":
        raise ValueError("invalid review spec path")
    job=json.loads(f.read_text(encoding="utf-8"))
    ident=job["id"]
    if ident not in {"001","002","003","005","006"}:raise ValueError("unexpected film ID")
    out_id="kino_"+ident+"_"+job.get("edition","v47")
    output=ROOT/"videos"/(out_id+".mp4")
    if str(output.relative_to(ROOT))!=job["output"]:raise ValueError("output path mismatch")
    root=Path(os.environ.get("RUNNER_TEMP") or "/tmp")
    with tempfile.TemporaryDirectory(prefix="m1lash_movie_") as td:
        work=Path(td)
        source=work/"ru_movie.mp4"
        restore(int(job["artifact_id"]),job["member"],source)
        source_for_edit=work/"sequence.mp4"
        trim(source,job.get("segments"),source_for_edit)
        args=[sys.executable,ROOT/"scripts/movie_short.py","--src",source_for_edit,
              "--id",out_id,"--start","0","--title",job["public_hook"],
              "--film",job["film"],"--lang","ru","--question",job["question"]]
        if job.get("editorial_profile"):
            args.extend(["--editorial-profile",job["editorial_profile"]])
        if job.get("on_screen_hook"):
            args.extend(["--on-screen-hook", job["on_screen_hook"]])
        run(args)
        if not output.exists():raise RuntimeError("No master MP4 from studio builder")
        ART.mkdir(exist_ok=True)
        qa_json=ROOT/"reports/qa"/out_id/"qa.json"
        sheet=ROOT/"reports/research/qa"/(out_id+"_look.jpg")
        if not qa_json.is_file() or not sheet.is_file():
            raise RuntimeError("Missing official QA or contact sheet")
        shutil.copy(qa_json,ART/(out_id+"_qa.json"))
        shutil.copy(sheet,ART/(out_id+"_look.jpg"))
        print("PRIVATE REVIEW BUILT",output,output.stat().st_size,flush=True)
if __name__=="__main__":main()
