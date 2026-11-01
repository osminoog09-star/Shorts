#!/usr/bin/env python3
"""Recreate approved 004 RU-safe M1lash private master entirely from existing Actions media.
No film/MP4 source is committed to Git. Render via shared motion-render.yml only.
"""
from __future__ import annotations
import asyncio
import hashlib
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
ART.mkdir(exist_ok=True)
SOURCE_ARTIFACT=13070096727
SOURCE_PATH="originals/machina_ava_ru_blackout_ok_candidate.mp4"
MP4_NAME="004_V47_OFFICIAL_PRIVATE.mp4"
CHECK=ROOT/"skills/ext/ffmpeg-skill/scripts/check.py"
LOOK=ROOT/"skills/ext/ffmpeg-skill/scripts/look.py"

def call(args,**kwargs):
    print("+", " ".join(str(x) for x in args[:6]),flush=True)
    return subprocess.run([str(x) for x in args],check=True,**kwargs)

def artifact(zip_path):
    token=os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN unavailable")
    url=f"https://api.github.com/repos/osminoog09-star/Shorts/actions/artifacts/{SOURCE_ARTIFACT}/zip"
    resp=requests.get(url,headers={"Authorization":f"Bearer {token}","Accept":"application/vnd.github+json"},timeout=120)
    resp.raise_for_status()
    if len(resp.content)>300_000_000:raise ValueError("artifact too large")
    zip_path.write_bytes(resp.content)

async def voice(out):
    from edge_tts import Communicate
    await Communicate("Это был фильм… Из машины.","ru-RU-DmitryNeural",rate="+8%").save(str(out))
    if out.stat().st_size<8000:raise RuntimeError("Dima TTS empty")

def main():
    with tempfile.TemporaryDirectory(prefix="m1lash_004_",dir=os.getenv("RUNNER_TEMP") or None) as tmp:
        work=Path(tmp)
        zpath=work/"source.zip"
        artifact(zpath)
        with zipfile.ZipFile(zpath) as z:
            info=z.getinfo(SOURCE_PATH)
            if not 8_000_000<=info.file_size<=80_000_000:raise RuntimeError("Unexpected RU movie source file size")
            source=work/"source.mp4"
            with z.open(info) as fin,source.open("wb") as out:
                shutil.copyfileobj(fin,out)
        intro=work/"dima_004_title.mp3"
        asyncio.run(voice(intro))
        out_dir=work/"render"
        call([sys.executable, ROOT/"scripts/qa/rebuild_004_clean_ru_safe_v46.py",source,
              "--out-dir",out_dir,"--title",intro])
        final=out_dir/"004_V46_OFFICIAL_PRIVATE.mp4"
        if not final.exists():raise RuntimeError("missing rebuilt master")
        target=ROOT/"videos"/MP4_NAME
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(final,target)
        call(["ffmpeg","-v","error","-xerror","-i",target,"-f","null","-"],stdout=subprocess.DEVNULL)
        probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_type,width,height,avg_frame_rate","-of","json",target]))
        duration=float(probe["format"]["duration"])
        videos=[a for a in probe["streams"] if a["codec_type"]=="video"]
        if not (40<=duration<=46 and videos and videos[0]["width"]==1080 and videos[0]["height"]==1920):
            raise RuntimeError(f"bad final master metadata: {probe}")
        # Independently verify the FINAL title audio with Russian ASR, not only title source metadata.
        call(["ffmpeg","-v","error","-y","-ss",f"{max(0,duration-4.8):.3f}","-i",target,
              "-vn","-ac","1","-ar","16000","-t","4.8",work/"title.wav"])
        from faster_whisper import WhisperModel
        model=WhisperModel("small",device="cpu",compute_type="int8")
        segs,info=model.transcribe(str(work/"title.wav"),language="ru",beam_size=3,condition_on_previous_text=False)
        phrases=" ".join(s.text for s in segs).casefold()
        word_ok="машин" in phrases
        asr={"text":phrases,"language":info.language,"key_phrase_ok":word_ok}
        qa={"id":"004","version":"V47","source_artifact":SOURCE_ARTIFACT,
            "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "master_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "master_seconds":duration,
            "dima_voice":"ru-RU-DmitryNeural","title_asr":asr,
            "final_recreated":True,"rights":"not_verified",
            "status":"PRIVATE_REVIEW_NOT_PUBLISHED"}
        (ART/"004_V47_metadata.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
        if not word_ok:raise RuntimeError("FINAL title RU ASR mismatch: "+phrases)
        shutil.copy(out_dir/"004_V46_final_look.jpg",ART/"004_V47_final_look.jpg")
        print("PRIVATE MASTER",target,"seconds",duration,"ASR",phrases,flush=True)

if __name__=="__main__":main()
