#!/usr/bin/env python3
"""One-time PRIVATE YouTube review upload of kino_007 V9c.

The file never enters the public repository. An ephemeral RSA key stays only
inside this GitHub Actions runner; a URL encrypted to its public key is handed
off via a non-secret public envelope. SHA256 pins the exact owner-reviewed MP4.
No public/scheduled publication and no automatic retry.
"""
from __future__ import annotations
import base64
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.youtube_direct import API, RU_ID, token_for, verify_channel, youtube_upload

PROJECT = "kino_007"
EXPECTED_SHA = "0b5fd6b576797877c0a8fcb729304eb9b6830cbf45c6c51a646fa04502b12bb6"
EXPECTED_SIZE = 21455659
MEDIA_UUID = "b888fa74-f101-4888-83a8-6e70f186ab7e"
DATA_DIR = ROOT / "publishing" / "private_upload_requests"
PUB = DATA_DIR / (PROJECT + "_v9c_ephemeral_public.pem")
ENVELOPE = DATA_DIR / (PROJECT + "_v9c_envelope.json")
RECEIPT = ROOT / "publishing" / "receipts" / (PROJECT + ".json")
MANIFEST = ROOT / "publishing" / "queue" / (PROJECT + ".json")
INDEX = ROOT / "publishing" / "queue.json"
API_URL = "https://api.github.com/repos/osminoog09-star/Shorts/contents/" + str(ENVELOPE.relative_to(ROOT))

DESCRIPTION = (
    "Он считал их командой. Но последний ответ перевернул весь разговор.\n"
    "Ты угадал фильм до развязки? Напиши секунду!\n\n"
    "Song: Laeko - DONT WANNA KNOW!!!\n"
    "Music provided by NoCopyrightSounds\n"
    "Free Download/Stream: http://ncs.io/dontwannaknow\n"
    "Watch: https://ncs.lnk.to/dontwannaknowAT/youtube\n\n"
    "#shorts #кино #угадайфильм #фильмы #кинокадры #сценаизфильма #m1lash"
)
METADATA = {
    "type": "short",
    "title": "Он думал, что они КОМАНДА… Но услышал ЭТО 😳 #shorts",
    "description": DESCRIPTION,
    "tags": [
        "кино", "угадай фильм", "сцена из фильма",
        "напряженный диалог", "киношортс", "сильная сцена",
        "movie short", "russian dub", "shorts", "m1lash"
    ],
    "category_id": "1",
    "made_for_kids": False,
    "contains_synthetic_media": True,
    "default_language": "ru",
    "default_audio_language": "ru",
}

def now():
    return datetime.now(timezone.utc).isoformat()

def put_json(path: Path, content: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def record(paths, message):
    subprocess.run(["git", "config", "user.name", "m1lash-kino007-private[bot]"], cwd=ROOT, check=True)
    subprocess.run(["git", "config", "user.email", "kino007-private@users.noreply.github.com"], cwd=ROOT, check=True)
    subprocess.run(["git", "add", *[str(p.relative_to(ROOT)) for p in paths]], cwd=ROOT, check=True)
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if diff.returncode == 0:
        return
    subprocess.run(["git", "commit", "-m", message], cwd=ROOT, check=True)
    subprocess.run(["git", "pull", "--rebase", "origin", "main"], cwd=ROOT, check=True)
    subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT, check=True)

def input_url(private_key, token: str) -> str:
    headers = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
    }
    print("KINO007_WAITING_FOR_ENCRYPTED_ENVELOPE", flush=True)
    for attempt in range(48):
        resp = requests.get(API_URL, params={"ref": "main"}, headers=headers, timeout=30)
        if resp.ok:
            content = resp.json().get("content", "")
            envelope = json.loads(base64.b64decode(content).decode("utf-8"))
            if envelope.get("id") != PROJECT or envelope.get("sha256") != EXPECTED_SHA:
                raise RuntimeError("NO-GO: encrypted envelope identity/SHA mismatch")
            raw = base64.b64decode(envelope["ciphertext_b64"], validate=True)
            plain = private_key.decrypt(raw, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()),
                                                         algorithm=hashes.SHA256(), label=None))
            url = plain.decode("utf-8")
            parsed = urlsplit(url)
            if (parsed.scheme != "https"
                    or parsed.hostname != "d2ol7oe51mr4n9.cloudfront.net"
                    or not parsed.path.endswith("/" + MEDIA_UUID + ".mp4")
                    or parsed.username or parsed.password or parsed.query or parsed.fragment):
                raise RuntimeError("NO-GO: unsafe video URL origin/path")
            print("KINO007_ENCRYPTED_URL_ACCEPTED", flush=True)
            return url
        if resp.status_code != 404:
            raise RuntimeError("Envelope API HTTP " + str(resp.status_code))
        time.sleep(10)
    raise RuntimeError("NO-GO: encrypted handoff timed out; no YouTube upload")

def download_exact(url: str, target: Path):
    digest = hashlib.sha256()
    received = 0
    with requests.get(url, stream=True, timeout=(30, 180), allow_redirects=False) as r:
        r.raise_for_status()
        if r.status_code != 200:
            raise RuntimeError("NO-GO: unexpected video response/redirect")
        with target.open("wb") as f:
            for chunk in r.iter_content(chunk_size=4 * 1024 * 1024):
                if not chunk:
                    continue
                received += len(chunk)
                if received > EXPECTED_SIZE:
                    raise RuntimeError("NO-GO: video larger than expected")
                digest.update(chunk)
                f.write(chunk)
    if received != EXPECTED_SIZE or digest.hexdigest() != EXPECTED_SHA:
        target.unlink(missing_ok=True)
        raise RuntimeError("NO-GO: video size/SHA mismatch")
    print("KINO007_PRIVATE_BINARY_SHA_PASS", received, flush=True)

def main():
    if RECEIPT.exists() or MANIFEST.exists():
        raise RuntimeError("NO-GO: existing receipt or upload manifest. NEVER auto-retry.")
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    row = next((v for v in index["items"] if v.get("id") == PROJECT), None)
    if row is None or row.get("youtube_id") or row.get("slot") or row.get("status") != "draft":
        raise RuntimeError("NO-GO: main queue not draft/private")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        raise RuntimeError("GITHUB_TOKEN absent")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PUB.write_bytes(key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ))
    record([PUB], "youtube(kino007): publish one-time ephemeral encryption public key")
    url = input_url(key, token)
    with tempfile.TemporaryDirectory(prefix="m1lash-kino007-") as temporary:
        path = Path(temporary) / "kino_007_v9c.mp4"
        download_exact(url, path)
        yt_token = token_for("ru")
        verify_channel(yt_token, RU_ID)
        manifest = {"channel": "ru",
                    "source": {"sha256": EXPECTED_SHA},
                    "metadata": METADATA,
                    "publish_at": None}
        receipt = {"status": "reserved", "action": "upload_private_once",
                   "id": PROJECT, "sha256": EXPECTED_SHA,
                   "size_bytes": EXPECTED_SIZE, "reserved_at": now(),
                   "publish_at": None, "never_retry_automatically": True}
        put_json(RECEIPT, receipt)
        record([RECEIPT], "youtube(kino007): reserve one-time PRIVATE review upload")
        print("KINO007_UPLOAD_RESERVED", flush=True)
        video_id = youtube_upload(path, manifest, None, yt_token)
    receipt.update(status="uploaded", video_id=video_id,
                   youtube_url="https://www.youtube.com/watch?v=" + video_id,
                   uploaded_at=now())
    put_json(RECEIPT, receipt)
    manifest["source"] = {"type": "uploaded", "video_id": video_id, "sha256": EXPECTED_SHA}
    manifest["provenance"] = {"upload_method": "encrypted_ephemeral_handoff_sha256_once",
                              "owner_review": "PRIVATE_ONLY_NOT_APPROVED_FOR_RELEASE"}
    put_json(MANIFEST, manifest)
    row.update(status="review", youtube_id=video_id,
               review_version="V9c_PRIVATE_YOUTUBE_REVIEW",
               private_review_url="https://studio.youtube.com/video/" + video_id + "/edit",
               note="06.11 V9c exact-SHA upload to YouTube PRIVATE without date; owner must watch/listen and approve separate publishing decision.")
    put_json(INDEX, index)
    record([RECEIPT, MANIFEST, INDEX], "youtube(kino007): record exact V9c PRIVATE video ID; no publish date")
    check = requests.get(API + "/videos", params={"part": "status", "id": video_id},
                         headers={"Authorization": "Bearer " + yt_token}, timeout=40)
    check.raise_for_status()
    items = check.json().get("items", [])
    status = items[0].get("status", {}) if len(items) == 1 and items[0].get("id") == video_id else {}
    if status.get("privacyStatus") != "private" or status.get("publishAt"):
        raise RuntimeError("NO-GO: YouTube PRIVATE/no date readback failed")
    print("KINO007_YOUTUBE_PRIVATE_READBACK_PASS", video_id, flush=True)
    # Cleanup public encrypted handshake after verified upload. No private key
    # or unencrypted URL was ever committed.
    PUB.unlink(missing_ok=True)
    ENVELOPE.unlink(missing_ok=True)
    record([PUB, ENVELOPE], "youtube(kino007): clean up public ephemeral handoff records")
    print("KINO007_DONE_PRIVATE_REVIEW_ONLY", flush=True)

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("KINO007_PRIVATE_UPLOAD_STOP:", type(exc).__name__, str(exc)[:160], file=sys.stderr)
        raise SystemExit(2)
