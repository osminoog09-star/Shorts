#!/usr/bin/env python3
"""Reusable movie source ASR audio gate via prior GitHub Actions artifact.

Download only specified existing GitHub artifact to RUNNER_TEMP. Never commit
film files or unredacted transcripts. Check whether 3 separated windows actually
contain Russian actor speech. Produces small JSON evidence, not READY video.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlparse

import requests

ROOT=Path(__file__).resolve().parents[2]
JOB=ROOT/"jobs/mediaqa/chigur_004_ru_source.json"
def run(*cmd):
    p=subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=140)
    return p.stdout
def download_artifact(artifact_id:int,path:Path):
    token=os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN missing")
    url="https://api.github.com/repos/osminoog09-star/Shorts/actions/artifacts/"+str(artifact_id)+"/zip"
    with requests.get(url,headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json"},
                      stream=True,timeout=90,allow_redirects=True) as r:
        r.raise_for_status()
        size=0
        with path.open("wb") as out:
            for chunk in r.iter_content(chunk_size=1024*1024):
                size+=len(chunk)
                if size>500_000_000:
                    raise ValueError("Artifact too large for private QA")
                out.write(chunk)
    if not zipfile.is_zipfile(path):
        raise ValueError("Invalid Actions artifact ZIP")
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--job",default=str(JOB))
    opts=a.parse_args()
    job=json.loads(Path(opts.job).read_text(encoding="utf-8"))
    media=job["media_zip_path"]
    if Path(media).is_absolute() or ".." in Path(media).parts:
        raise ValueError("Unsafe media ZIP path")
    out=ROOT/job["report"]
    with tempfile.TemporaryDirectory(dir=os.getenv("RUNNER_TEMP") or None) as t:
        work=Path(t)
        archive=work/"source.zip"
        download_artifact(int(job["artifact_id"]),archive)
        with zipfile.ZipFile(archive) as z:
            info=z.getinfo(media)
            if info.file_size>350_000_000 or info.file_size<100_000:
                raise ValueError("Implausible source size")
            src=work/"movie_source.mp4"
            with z.open(info) as r,src.open("wb") as w:
                import shutil
                shutil.copyfileobj(r,w)
        metadata=json.loads(run("ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,codec_type:stream_tags=language","-of","json",str(src)))
        duration=float(metadata["format"]["duration"])
        from faster_whisper import WhisperModel
        model=WhisperModel("small",device="cpu",compute_type="int8")
        samples=[]
        for idx,start in enumerate(job["windows"]):
            if float(start)+13>duration:
                raise ValueError("Speech sample outside source")
            wav=work/("speech_"+str(idx)+".wav")
            run("ffmpeg","-v","error","-y","-ss",str(start),"-t","15","-i",str(src),"-vn","-ac","1","-ar","16000",str(wav))
            segs,info=model.transcribe(str(wav),beam_size=1,vad_filter=True,condition_on_previous_text=False)
            observed=list(segs)
            meaningful=sum(len(re.findall(r"[А-Яа-яЁё]",s.text)) for s in observed)
            samples.append({"at":start,"language":info.language,"probability":round(float(info.language_probability),3),
                            "segments":len(observed),"russian_characters":meaningful,
                            "speech_seconds":round(sum(max(0,s.end-s.start) for s in observed),2)})
        # A Russian majority, plus one speech-bearing window, is evidence of RU audio.
        confirmed=sum(x["language"]=="ru" and x["probability"]>=.55 and x["speech_seconds"]>=1.5 for x in samples)
        state="PASS" if confirmed>=2 else "REVIEW" if confirmed else "NO_GO"
        report={"stage":"SOURCE_RU_AUDIO_ONLY","id":job["id"],"artifact_id":job["artifact_id"],
                "checked_at":dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                "source_duration":duration,"reported_audio_tags":[x.get("tags",{}) for x in metadata["streams"] if x["codec_type"]=="audio"],
                "samples":samples,"ru_samples":confirmed,"result":state,
                "limits":"NOT final MP4, not Dima closing line, not film license, not visual/copyright QA."}
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"result":state,"samples":samples},ensure_ascii=False))
        if state=="NO_GO":
            raise SystemExit(2)
if __name__=="__main__":
    main()
