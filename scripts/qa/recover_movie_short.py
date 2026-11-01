#!/usr/bin/env python3
"""Recover existing private movie Short from previously downloaded Actions artifact.

Never writes copyrighted source or final movie media into Git. Only the Actions
review artifact gets the rebuilt MP4. All outputs remain PRIVATE, not READY.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

import requests

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "recovery-output"
MAX_BYTES = 550_000_000

def cmd(args, *, timeout=1200):
    print("RUN:", " ".join(map(str, args[:6])), flush=True)
    return subprocess.run([str(x) for x in args], check=True, timeout=timeout)

def fetch_artifact(artifact: int, output: Path) -> None:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN absent")
    url = f"https://api.github.com/repos/osminoog09-star/Shorts/actions/artifacts/{artifact}/zip"
    with requests.get(url, headers={"Authorization": f"Bearer {token}",
                                   "Accept": "application/vnd.github+json"},
                      stream=True, allow_redirects=True, timeout=(20,120)) as response:
        response.raise_for_status()
        count = 0
        with output.open("wb") as file:
            for chunk in response.iter_content(1024 * 1024):
                if not chunk:
                    continue
                count += len(chunk)
                if count > MAX_BYTES:
                    raise RuntimeError("Source artifact size exceeds limit")
                file.write(chunk)
    if not zipfile.is_zipfile(output):
        raise RuntimeError("Actions source artifact is not ZIP")

async def synthesize(text: str, target: Path) -> None:
    import edge_tts
    # This is the studio's approved main narrator, not a synthetic actor dub.
    tts = edge_tts.Communicate(text=text, voice="ru-RU-DmitryNeural", rate="+4%")
    await tts.save(str(target))

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("job", type=Path)
    args = ap.parse_args()
    job = json.loads(args.job.read_text(encoding="utf-8"))
    if job.get("id") != "004" or job.get("mode") != "rebuild_004_v46":
        raise ValueError("This recovery revision currently supports only Short 004")
    target = job["media_in_zip"]
    if Path(target).is_absolute() or ".." in Path(target).parts:
        raise ValueError("Unsafe movie media path")
    OUTPUT.mkdir(exist_ok=True)
    report = {"id":job["id"],"source_artifact_id":int(job["source_artifact_id"]),
              "voice":"ru-RU-DmitryNeural","outro":"approved vertical rev4",
              "status":"NOT_VERIFIED"}
    with tempfile.TemporaryDirectory(dir=os.getenv("RUNNER_TEMP") or None) as td:
        scratch = Path(td)
        archive = scratch / "source.zip"
        source = scratch / "source.mp4"
        fetch_artifact(report["source_artifact_id"], archive)
        with zipfile.ZipFile(archive) as z:
            entry = z.getinfo(target)
            if entry.file_size < 100_000 or entry.file_size > 350_000_000:
                raise ValueError("Suspicious source size")
            with z.open(entry) as original, source.open("wb") as copied:
                shutil.copyfileobj(original,copied)
        cmd(["ffprobe","-v","error","-show_entries",
             "format=duration:stream=codec_type,width,height","-of","json",source],timeout=30)
        title = scratch / "004_dima_title.mp3"
        awaitable = synthesize(job["spoken_title"],title)
        asyncio.run(awaitable)
        if title.stat().st_size < 3_000:
            raise RuntimeError("Dima TTS too small")
        # Build exactly from studio's reproducible 004 safe-zone edit.
        cmd(["python3",ROOT/"scripts/qa/rebuild_004_clean_ru_safe_v46.py",
             source,"--out-dir",OUTPUT,"--title",title],timeout=2300)
        final = OUTPUT / "004_V46_OFFICIAL_PRIVATE.mp4"
        cmd(["ffmpeg","-v","error","-xerror","-i",final,"-f","null","-"],timeout=240)
        out = subprocess.check_output(
            ["ffprobe","-v","error","-show_format","-show_streams",
             "-of","json",str(final)], text=True)
        metadata = json.loads(out)
        video = next(x for x in metadata["streams"] if x["codec_type"] == "video")
        audio = next(x for x in metadata["streams"] if x["codec_type"] == "audio")
        time = float(metadata["format"]["duration"])
        if (video["width"],video["height"]) != (1080,1920) or not 32<=time<=59:
            raise RuntimeError("Wrong short dimensions or duration")
        if video["codec_name"]!="h264" or audio["codec_name"]!="aac":
            raise RuntimeError("Wrong codecs")
        qa_file = Path(str(final) + ".qa.json")
        qa = json.loads(qa_file.read_text(encoding="utf-8"))
        if qa.get("problems") or not qa.get("decode_ok"):
            raise RuntimeError("Official assembler did not PASS")
        report.update({"status":"TECHNICALLY_PASS_VISUAL_REVIEW_REQUIRED",
                       "duration_seconds":round(time,3),
                       "h264_aac":True,"check_qa":qa,
                       "sha256":hashlib.sha256(final.read_bytes()).hexdigest(),
                       "source_bytes_not_committed":True,
                       "upload":"NEVER",
                       "caveats":"Listen to final RU/Dima speech, visually check all subtitles, copyright claims."})
    (OUTPUT/"004_recovery_report.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"duration_seconds":report["duration_seconds"]},ensure_ascii=False))

if __name__=="__main__":
    main()
