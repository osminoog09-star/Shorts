#!/usr/bin/env python3
"""Exactly-once PRIVATE M1lash Chigur upload from owner's private Google Drive.
This is a narrow owner-authorized recovery workflow, not a publication scheduler.
No private film, Qwen WAV, OAuth token or owner reference is committed to public Git.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.drive_oauth_config import resolve_existing_client
from scripts.youtube_direct import token_for, verify_channel, youtube_upload, RU_ID

SOURCE_ID = "1ysQ5mnSmtxv8xnjAq4uMt3DV6FZnVvVs"
SOURCE_NAME = "M1lash_Chigur_DENIS_V7_QA_APPROVED_PRIVATE_FINAL_10m58.mp4"
SOURCE_SHA = "d9278386aa2eb2b55b56d91a849820a5c24c9c4a739305d7953b3fd4f6a347c7"
SOURCE_SIZE = 80725337
REQUEST = ROOT / "longform/chigur/chigur_private_upload_request.json"
RECEIPT = ROOT / "publishing/receipts/chigur_long_denis_v7.json"
QUEUE = ROOT / "publishing/queue/chigur_long_denis_v7.json"


def record(paths, message):
    subprocess.run(["git", "config", "user.name", "chigur-review-upload[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "chigur-review-upload@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "add", *[str(p.relative_to(ROOT)) for p in paths]], cwd=ROOT, check=True)
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, check=True)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def download_from_owner_drive(path):
    env, _ = resolve_existing_client(dict(os.environ))
    auth = {"Authorization": "Bearer " + env["_GDRIVE_ACCESS_TOKEN"]}
    url = "https://www.googleapis.com/drive/v3/files/" + SOURCE_ID
    response = requests.get(url, params={"fields": "id,name,mimeType,size,trashed"}, headers=auth, timeout=60)
    response.raise_for_status()
    meta = response.json()
    if not (meta.get("id") == SOURCE_ID and meta.get("name") == SOURCE_NAME
            and meta.get("mimeType") == "video/mp4"
            and int(meta.get("size", -1)) == SOURCE_SIZE
            and not meta.get("trashed")):
        raise RuntimeError("NO-GO: Drive identity/size/mime mismatch")
    digest = hashlib.sha256()
    count = 0
    with requests.get(url, params={"alt": "media"}, headers=auth,
                      stream=True, timeout=(40, 180)) as response:
        response.raise_for_status()
        with path.open("wb") as output:
            for block in response.iter_content(chunk_size=4 * 1024 * 1024):
                if not block:
                    continue
                count += len(block)
                if count > SOURCE_SIZE:
                    raise RuntimeError("NO-GO: Drive media oversized")
                output.write(block)
                digest.update(block)
    if count != SOURCE_SIZE or digest.hexdigest() != SOURCE_SHA:
        path.unlink(missing_ok=True)
        raise RuntimeError("NO-GO: Drive media SHA-256 mismatch")
    print("Exact private Drive video SHA and byte count verified", flush=True)


def main():
    req = json.loads(REQUEST.read_text(encoding="utf-8"))
    if not (req.get("action") == "upload_private_once" and req.get("channel") == "ru"
            and req.get("drive_file_id") == SOURCE_ID
            and req.get("sha256") == SOURCE_SHA
            and req.get("size_bytes") == SOURCE_SIZE
            and req.get("visibility") == "private"
            and req.get("publish_at") is None):
        raise RuntimeError("NO-GO: private owner request mismatch")
    if RECEIPT.exists() or QUEUE.exists():
        raise RuntimeError("NO-GO: video already reserved/uploaded: NEVER retry automatically")
    token = token_for("ru")
    verify_channel(token, RU_ID)
    target = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / SOURCE_NAME
    download_from_owner_drive(target)
    metadata = req["metadata"]
    if (metadata.get("type") != "long"
            or metadata.get("made_for_kids") is not False
            or metadata.get("contains_synthetic_media") is not True):
        raise RuntimeError("NO-GO: review metadata mismatch")
    payload = {"channel": "ru", "source": {"sha256": SOURCE_SHA}, "metadata": metadata}
    receipt = {
        "status": "reserved", "action": "upload_private_once",
        "source": "owner_google_drive_private", "drive_file_id": SOURCE_ID,
        "sha256": SOURCE_SHA, "size_bytes": SOURCE_SIZE,
        "reserved_at": datetime.now(timezone.utc).isoformat(),
        "publish_at": None, "never_retry_automatically": True
    }
    save(RECEIPT, receipt)
    record([RECEIPT], "youtube: reserve exact-SHA PRIVATE Chigur upload (no date)")
    print("PRIVATE_UPLOAD_RESERVED", flush=True)
    video_id = youtube_upload(target, payload, None, token)
    receipt.update(
        status="uploaded", video_id=video_id,
        youtube_url="https://www.youtube.com/watch?v=" + video_id,
        uploaded_at=datetime.now(timezone.utc).isoformat()
    )
    save(RECEIPT, receipt)
    save(QUEUE, {
        "channel": "ru",
        "source": {"type": "uploaded", "video_id": video_id, "sha256": SOURCE_SHA},
        "metadata": metadata, "publish_at": None,
        "provenance": {"upload_method": "private_drive_sha256_once",
                       "owner_review": "private_only", "drive_file_id": SOURCE_ID}
    })
    record([RECEIPT, QUEUE], "youtube: record PRIVATE Chigur Denis-v7 upload; no publish date")
    print("YOUTUBE_PRIVATE_VIDEO_ID", video_id, "NO_PUBLISH_DATE", flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        # Avoid logging API tokens, redirect URLs or response payloads.
        print("CHIGUR_UPLOAD_FAIL_SAFE", type(err).__name__, str(err)[:160], file=sys.stderr)
        raise SystemExit(2)
