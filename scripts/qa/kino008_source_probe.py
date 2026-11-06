#!/usr/bin/env python3
"""One-time owner-private Oppenheimer source audit. No film/frames/audio in Git.

Temporary original downloaded with owner Google Drive OAuth and verified folder
membership + expected bytes. Private contact JPEG uploaded to owner's My Drive
root (not broadly shared source folder). Text report contains metadata only.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
import secrets

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from drive_scene_probe import fetch_private_film
from drive_oauth_config import resolve_existing_client

SOURCE_ID = "15jweAqG-x4UgFyCU8jkuZXhAuRJcGIaD"
SOURCE_URL = "https://drive.google.com/file/d/" + SOURCE_ID + "/view"
EXPECTED_SIZE = 836471622
REPORT = ROOT / "reports/research/2026-11-06_KINO_008_OWNER_SOURCE_PROBE.json"

def run(*args, timeout=140):
    p=subprocess.run([str(x) for x in args], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                     text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError("Command failed: "+str(args[0])+" "+p.stderr[-360:])
    return p.stdout

def upload_private_root(src: Path, access: str) -> str:
    """Upload photo to owner's unshared Drive root; strict provider metadata."""
    assert src.suffix==".jpg" and src.stat().st_size<12*1024*1024
    boundary="m1lash"+secrets.token_hex(12)
    meta=json.dumps({"name":src.name,"mimeType":"image/jpeg","parents":["root"]}).encode()
    raw=src.read_bytes()
    part=(b"--"+boundary.encode()+b"\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
         +meta+b"\r\n--"+boundary.encode()+b"\r\nContent-Type: image/jpeg\r\n\r\n"
         +raw+b"\r\n--"+boundary.encode()+b"--\r\n")
    url="https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size,parents"
    req=Request(url,data=part,method="POST",headers={
        "Authorization":"Bearer "+access,
        "Content-Type":"multipart/related; boundary="+boundary})
    with urlopen(req,timeout=90) as r: result=json.load(r)
    if (result.get("name")!=src.name or int(result.get("size",-1))!=len(raw)
            or not result.get("id")):
        raise RuntimeError("Private Drive contact readback invalid")
    return result["id"]

def make_contact(path:Path, seconds:float, output:Path):
    from PIL import Image,ImageDraw,ImageFont
    cols, rows = 5, 8
    cw,ch=320,204
    sheet=Image.new("RGB",(cols*cw,rows*ch),(22,24,35))
    draw=ImageDraw.Draw(sheet)
    positions=[]
    for i in range(cols*rows):
        stamp=max(0,min(seconds-.5,seconds*(i+0.5)/(cols*rows)))
        positions.append(round(stamp,1))
        frame=output.parent/f"thumb_{i:02d}.jpg"
        try:
            run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",
                "%.2f"%stamp,"-i",path,"-frames:v","1",
                "-vf","scale=304:170:force_original_aspect_ratio=decrease",frame,timeout=110)
            with Image.open(frame) as image:
                im=image.convert("RGB")
                left=i%cols*cw+(cw-im.width)//2
                top=i//cols*ch+(176-im.height)//2
                sheet.paste(im,(left,top))
            draw.text((i%cols*cw+9,i//cols*ch+176),
                      f"{int(stamp//60):02d}:{int(stamp%60):02d}",fill=(255,255,255))
        finally:
            frame.unlink(missing_ok=True)
    sheet.save(output,"JPEG",quality=74,optimize=True)
    return positions

def check_languages(path:Path,dur:float,temp:Path):
    from faster_whisper import WhisperModel
    w=WhisperModel("tiny",device="cpu",compute_type="int8",cpu_threads=2,
                   num_workers=1)
    results=[]
    for i,frac in enumerate([.07,.29,.5,.71,.93]):
        start=dur*frac
        audio=temp/f"lang{i}.wav"
        run("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",
            "%.1f"%start,"-t","20","-i",path,"-ac","1","-ar",
            "16000","-vn",audio,timeout=140)
        _,info=w.transcribe(str(audio),beam_size=2, vad_filter=False,
                            condition_on_previous_text=False)
        results.append({"sample_t":round(start,1),"lang":info.language,
                        "probability":round(float(info.language_probability),2)})
        audio.unlink(missing_ok=True)
    return results

def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    result={"film":"Оппенгеймер (2023)", "source_kind":"owner_screen_recording_excerpt",
            "source_id":SOURCE_ID,"source_filename":"Screen_Recording_20261103_124519_Opera.mp4",
            "status":"error","created_at":datetime.now(timezone.utc).isoformat(),
            "contents_private":True,"youtube_status":"not_uploaded",
            "note":"Review source audio and visual content before film selection. No movie frames/voice in repo."}
    try:
        with tempfile.TemporaryDirectory(prefix="kino008-owner-",dir=os.environ.get("RUNNER_TEMP") or None) as tmp:
            temp=Path(tmp)
            path=temp/"owner_source.mp4"
            size=fetch_private_film(SOURCE_URL,path)
            if size != EXPECTED_SIZE or path.stat().st_size != EXPECTED_SIZE:
                raise RuntimeError("NO-GO: owner source byte count changed")
            digest=hashlib.file_digest(path.open("rb"),"sha256").hexdigest()
            probe=json.loads(run("ffprobe","-v","error","-show_entries",
                                 "format=duration:stream=codec_type,codec_name,width,height",
                                 "-of","json",path))
            duration=float(probe["format"]["duration"])
            if not 600<duration<4000: raise RuntimeError("source unexpected duration")
            videos=[v for v in probe["streams"] if v["codec_type"]=="video"]
            audios=[v for v in probe["streams"] if v["codec_type"]=="audio"]
            if not videos or not audios: raise RuntimeError("Video/audio track missing")
            contact=temp/"KINO008_OPPENHEIMER_PRIVATE_40FRAME_QA.jpg"
            times=make_contact(path,duration,contact)
            env,_=resolve_existing_client(dict(os.environ))
            contact_id=upload_private_root(contact,env["_GDRIVE_ACCESS_TOKEN"])
            langs=check_languages(path,duration,temp)
            is_ru=sum(v["lang"]=="ru" and v["probability"]>=.56 for v in langs)>=3
            result.update(status="source_verified_ru" if is_ru else "blocked_audio_language",
                          size_bytes=size,sha256=digest,duration_s=round(duration,2),
                          video_width=videos[0].get("width"),video_height=videos[0].get("height"),
                          video_codec=videos[0].get("codec_name"),audio_codec=audios[0].get("codec_name"),
                          contact_drive_file_id=contact_id,contact_image_times=times,
                          languages=langs,ru_audio_verified=is_ru,scene_verified=False)
            print("KINO008_SOURCE_SHA256",digest,"SIZE",size,flush=True)
            print("KINO008_SOURCE_PROBE",result["status"],"duration",duration,
                  "contact_id",contact_id,"languages",langs,flush=True)
    except Exception as exc:
        result["status"]="error"
        result["error_class"]=type(exc).__name__
        result["error_message"]=str(exc)[:240]
        print("KINO008_SOURCE_FAIL",type(exc).__name__,str(exc)[:180],flush=True)
        raise
    finally:
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
