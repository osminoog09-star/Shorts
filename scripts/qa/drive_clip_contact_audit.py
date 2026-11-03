#!/usr/bin/env python3
"""Private visual audit for uploaded owner Drive recordings (no GitHub film frames).

Downloads only MP4s from configured owner-controlled Drive folder into runner
tmp, extracts six sample frames per MP4, and uploads ephemeral contact sheets
to the user's private Drive ROOT (not the movie-source folder). Report to repo
contains only codec/duration/dimensions, never movie bytes or image IDs.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.request import Request, urlopen
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from drive_folder_intake import list_folder_authenticated
from drive_scene_probe import fetch_private_film
from drive_oauth_config import resolve_existing_client

FOLDER_CONFIG = ROOT / "publishing/drive_folder.json"
REPORT = ROOT / "reports/research/drive_clip_audit_20261103.json"


def run(*argv, timeout=120):
    p = subprocess.run([str(v) for v in argv], capture_output=True, text=True,
                       timeout=timeout, check=False)
    if p.returncode:
        raise RuntimeError("ffmpeg/ffprobe failed")
    return p.stdout


def summary(path: Path) -> dict:
    data = json.loads(run("ffprobe", "-v", "error",
                          "-show_entries", "format=duration:stream=codec_type,codec_name,width,height",
                          "-of", "json", path))
    streams = data.get("streams", [])
    v = next((x for x in streams if x.get("codec_type") == "video"), {})
    a = next((x for x in streams if x.get("codec_type") == "audio"), {})
    return {"seconds": round(float(data["format"]["duration"]), 1),
            "width": v.get("width"), "height": v.get("height"),
            "video_codec": v.get("codec_name"), "audio_present": bool(a),
            "audio_codec": a.get("codec_name") if a else None}


def contact(video: Path, seconds: float, out: Path) -> None:
    cw, ch = 480, 285
    sheet = Image.new("RGB", (cw * 3, ch * 2), "#142333")
    draw = ImageDraw.Draw(sheet)
    anchors = [0.05, 0.20, 0.36, 0.55, 0.75, 0.92]
    valid = 0
    for i, fraction in enumerate(anchors):
        stamp = max(0.0, min(seconds-0.5, seconds*fraction))
        thumb = out.parent / ("thumb_%02d.jpg" % i)
        try:
            run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                "-ss", f"{stamp:.2f}", "-i", video, "-frames:v", "1",
                "-vf", "scale=468:247:force_original_aspect_ratio=decrease",
                thumb, timeout=120)
            with Image.open(thumb) as frame:
                img=frame.convert("RGB")
                x=i%3*cw+(cw-img.width)//2
                y=i//3*ch+10+(247-img.height)//2
                sheet.paste(img,(x,y))
                valid += 1
        except (OSError, RuntimeError, ValueError):
            pass
        finally:
            thumb.unlink(missing_ok=True)
        at = int(stamp)
        draw.text((i%3*cw+12, i//3*ch+261),
                  f"{at//3600:02d}:{(at//60)%60:02d}:{at%60:02d}", fill="white")
    if valid < 4:
        raise RuntimeError("too few decoded sample frames")
    sheet.save(out, format="JPEG", quality=77, optimize=True)


def upload_private_root(photo: Path, token: str) -> None:
    # The contact sheet remains in personal Drive only; never use the public
    # main repo or Actions artifact as a media storage channel.
    boundary = "m1lash_private_qa_202611"
    metadata = json.dumps({"name": photo.name,
                           "mimeType": "image/jpeg", "parents": ["root"]}).encode()
    raw = photo.read_bytes()
    body = (b"--"+boundary.encode()+b"\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            + metadata + b"\r\n--"+boundary.encode()+b"\r\nContent-Type: image/jpeg\r\n\r\n"
            + raw + b"\r\n--"+boundary.encode()+b"--\r\n")
    req = Request("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id%2Csize",
                  data=body, method="POST",
                  headers={"Authorization":"Bearer "+token,
                           "Content-Type":"multipart/related; boundary="+boundary})
    with urlopen(req, timeout=70) as res:
        created = json.load(res)
    file_id = created.get("id")
    if not file_id:
        raise RuntimeError("contact sheet not stored in Drive")
    check = Request("https://www.googleapis.com/drive/v3/files/"+file_id+"?fields=size",
                    headers={"Authorization":"Bearer "+token})
    with urlopen(check, timeout=40) as res:
        result=json.load(res)
    if int(result.get("size", -1))!=len(raw):
        raise RuntimeError("private Drive contact sheet remote size mismatch")


def main():
    folder = json.loads(FOLDER_CONFIG.read_text(encoding="utf-8"))
    entries = list_folder_authenticated(folder["url"])
    selected = [x for x in entries if re.fullmatch(r"Screen_Recording_\d{8}_\d{6}_Opera\.mp4", x["path"])]
    result = {"checked_at": datetime.now(timezone.utc).isoformat(),
              "note": "PRIVATE Drive contacts only. Frame snapshots are NOT film classification without manual review.",
              "items": []}
    if not selected:
        raise RuntimeError("No screen recording MP4 found in configured private Drive folder")
    auth,_=resolve_existing_client(dict(os.environ))
    token=auth["_GDRIVE_ACCESS_TOKEN"]
    for item in sorted(selected, key=lambda x:x["path"]):
        row={"file":item["path"],"status":"error","film":"unverified"}
        try:
            with tempfile.TemporaryDirectory() as tmp:
                dest=Path(tmp)/"original.mp4"
                size=fetch_private_film(item["url"],dest)
                meta=summary(dest)
                photo=Path(tmp)/("M1lash_QA_"+hashlib.sha256(item["path"].encode()).hexdigest()[:12]+".jpg")
                contact(dest,meta["seconds"],photo)
                upload_private_root(photo,token)
                row.update(meta)
                row["bytes"]=size
                row["contact_name"]=photo.name
                row["status"]="contact_private_drive"
        except Exception as error:
            row["error_class"]=type(error).__name__
        result["items"].append(row)
        REPORT.parent.mkdir(parents=True,exist_ok=True)
        REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print("clip audit:",item["path"],row["status"],round(row.get("seconds",0),1),flush=True)
    if not all(x["status"]=="contact_private_drive" for x in result["items"]):
        raise RuntimeError("Some recordings could not be audited")
    return 0

if __name__=="__main__":
    sys.exit(main())
