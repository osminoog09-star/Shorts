#!/usr/bin/env python3
"""Upload a finished PRIVATE review file (MP4 with Denis voice, QA json) into owner-private Drive
voice_out/<folder> for the owner to watch. Never public Git, never YouTube. Reuses voice_private_io auth.
usage: python scripts/drive_private_upload.py --folder <name> FILE [FILE...]
Prints only the folder URL and per-file SHA-256 (no secrets)."""
import argparse, hashlib, json, os, re, secrets, sys
from pathlib import Path
from urllib.request import Request, urlopen
sys.path.insert(0, str(Path(__file__).resolve().parent))
import voice_private_io as vp

MIME = {".mp4": "video/mp4", ".mp3": "audio/mpeg", ".json": "application/json", ".jpg": "image/jpeg", ".png": "image/png", ".wav": "audio/wav"}


def upload(parent, path, access):
    size = path.stat().st_size
    if size > 400 * 1024 * 1024:
        raise SystemExit("NO-GO: file too large")
    meta = json.dumps({"name": path.name, "parents": [parent]}).encode()
    init = Request("https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&fields=id,name,size",
                   data=meta, method="POST", headers={"Authorization": "Bearer " + access,
                   "Content-Type": "application/json; charset=utf-8",
                   "X-Upload-Content-Type": MIME.get(path.suffix, "application/octet-stream"),
                   "X-Upload-Content-Length": str(size)})
    with urlopen(init, timeout=60) as r:
        loc = r.headers["Location"]
    req = Request(loc, data=path.read_bytes(), method="PUT",
                  headers={"Content-Type": MIME.get(path.suffix, "application/octet-stream")})
    with urlopen(req, timeout=600) as r:
        obj = json.load(r)
    return {"name": path.name, "id": obj["id"], "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "url": "https://drive.google.com/file/d/" + obj["id"] + "/view"}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--folder", required=True); ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9_-]{2,60}", a.folder):
        raise SystemExit("NO-GO: folder name")
    conf = vp.approved(vp.MANIFEST)
    access = vp.refresh_access_token(dict(os.environ))
    fid = vp.make_folder(conf["voice_out_folder_id"], a.folder, access)
    rec = {"folder_url": "https://drive.google.com/drive/folders/" + fid, "files": [upload(fid, Path(f), access) for f in a.files]}
    print(json.dumps(rec, ensure_ascii=False, indent=1))
    Path("drive_review_receipt.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
