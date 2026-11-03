#!/usr/bin/env python3
"""One-time, owner-approved PRIVATE upload of exactly four already-reviewed Shorts.

This is only an event adapter: all YouTube mutations go through youtube_direct.py.
No publish_at, no schedule, no automatic retries. A persisted reservation protects
every attempted upload; on an uncertain outcome, stop and inspect Studio manually.
"""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import requests

from youtube_direct import RU_ID, token_for, verify_channel

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "publishing/private_upload_requests/next_four_20261103.json"
APPROVED = {
    "ai_vacation_202611": ("videos/ai_vacation_202611_v1.mp4",
        "3de6317eaf5226e67c48058a046e7921928a53e7506a235bb9fe7bf8e551ed20", 7104859),
    "ai_fridge_202611": ("videos/ai_fridge_202611_v1.mp4",
        "d7b63b2f05c6fbbc2c363cefa32be1f9a5d762a3c6deaccc49364f1981908825", 6612146),
    "science_orbit_202611": ("videos/science_orbit_202611_v1.mp4",
        "80f5f4044885a4e139f8c32049dc7494f362e85bbe37b84e5d32a0454f5656ee", 7832183),
    "science_mirror_202611": ("videos/science_mirror_202611_v1.mp4",
        "b9bfb516fc14f16af3d065645fcd0f0501653afba624fd874cdd3336f342a5cd", 6739411),
}
UPLOAD = ROOT / "scripts/youtube_direct.py"
QUEUE = ROOT / "publishing/queue.json"
RECEIPTS = ROOT / "publishing/receipts"


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True)


def commit_receipt(id_, label):
    path = f"publishing/receipts/{id_}.json"
    run("git", "add", "--", path)
    run("git", "commit", "-m", f"youtube: {label} {id_}")
    # Rebase before pushing, including competing metadata-only commits, never
    # silently force-push or auto-repeat a YouTube mutation.
    run("git", "pull", "--rebase", "origin", "main")
    run("git", "push", "origin", "HEAD:main")


def source_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as src:
        for buf in iter(lambda: src.read(2 * 1024 * 1024), b""):
            h.update(buf)
    return h.hexdigest()


def check_request():
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    if set(request) != {"action", "private_only", "owner_approval_date", "items"}:
        raise RuntimeError("Request has unknown fields; do not upload")
    if (request["action"] != "private_upload_once" or request["private_only"] is not True
            or request["owner_approval_date"] != "2026-11-03"):
        raise RuntimeError("Owner approval or PRIVATE-only gate missing")
    received = request["items"]
    if not isinstance(received, list) or len(received) != len(APPROVED):
        raise RuntimeError("Request must include exactly four reviewed Shorts")
    expected = [{"id": id_, "manifest": f"publishing/queue/{id_}.json",
                 "sha256": APPROVED[id_][1]} for id_ in APPROVED]
    if received != expected:
        raise RuntimeError("Manifest/ID/hash differs from 4 approved immutable MP4s")
    queue = {x["id"]: x for x in json.loads(QUEUE.read_text(encoding="utf-8"))["items"]}
    for id_, (rel, digest, size) in APPROVED.items():
        manifest_path = ROOT / f"publishing/queue/{id_}.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        source = manifest.get("source", {})
        meta = manifest.get("metadata", {})
        approval = manifest.get("provenance", {})
        item = queue.get(id_, {})
        if ((RECEIPTS / (id_ + ".json")).exists() or item.get("youtube_id")
                or item.get("status") != "draft" or item.get("slot")):
            raise RuntimeError(f"{id_}: already exists, scheduled or reserved: NO RETRY")
        if (manifest.get("channel") != "ru" or manifest.get("publish_at")
                or source != {"type": "repo", "path": rel, "sha256": digest}
                or meta.get("type") != "short"
                or not meta.get("title", "").endswith("#shorts")
                or meta.get("made_for_kids") is not False
                or approval.get("owner_audio_approved") is not True
                or item.get("owner_audio_approved") is not True
                or approval.get("no_schedule_authorized") is not True):
            raise RuntimeError(f"{id_}: manifest/owner approval does not match")
        path = ROOT / rel
        if not path.is_file() or path.stat().st_size != size:
            raise RuntimeError(f"{id_}: original MP4 missing or size changed")
        if source_sha(path) != digest:
            raise RuntimeError(f"{id_}: original MP4 SHA256 differs, NO-GO")
    print("STRICT_BATCH_PREFLIGHT_OK: four approved immutable MP4s; PRIVATE only", flush=True)


def api_verify_private(id_, video_id):
    access = token_for("ru")
    verify_channel(access, RU_ID)
    for attempt in range(5):
        response = requests.get("https://www.googleapis.com/youtube/v3/videos",
            params={"part": "status,snippet", "id": video_id},
            headers={"Authorization": "Bearer " + access, "Cache-Control": "no-cache"},
            timeout=40)
        if response.ok:
            items = response.json().get("items", [])
            if len(items) == 1 and items[0].get("id") == video_id:
                status = items[0].get("status", {})
                if status.get("privacyStatus") == "private" and not status.get("publishAt"):
                    print(f"{id_}: YouTube status confirmed PRIVATE, no publishAt", flush=True)
                    return dt.datetime.now(dt.timezone.utc).isoformat()
                raise RuntimeError(f"{id_}: YouTube status not PRIVATE or unexpected publishAt; manual inspection")
        if attempt < 4:
            time.sleep(2 ** attempt)
    raise RuntimeError(f"{id_}: YouTube readback unavailable; no retry of upload")


def main():
    if os.environ.get("GITHUB_REPOSITORY") != "osminoog09-star/Shorts":
        raise RuntimeError("Only the approved Shorts repository may run this")
    check_request()
    run("git", "config", "user.name", "m1lash-youtube-private-bot")
    run("git", "config", "user.email", "m1lash-youtube-private-bot@users.noreply.github.com")
    # precheck all manifests before attempting even the first upload
    for id_ in APPROVED:
        run(sys.executable, UPLOAD, "check", "--manifest", f"publishing/queue/{id_}.json")
    for id_, (rel, digest, size) in APPROVED.items():
        manifest = f"publishing/queue/{id_}.json"
        video = rel
        # Reconcile other agents' commits while no local changes are pending.
        run("git", "pull", "--ff-only", "origin", "main")
        if (RECEIPTS / (id_ + ".json")).exists():
            raise RuntimeError(f"{id_}: receipt exists; do not retry")
        run(sys.executable, UPLOAD, "preflight", "--manifest", manifest,
            "--video-file", video)
        # Reservation must be durable BEFORE the YouTube upload begins.
        run(sys.executable, UPLOAD, "reserve", "--manifest", manifest)
        commit_receipt(id_, "reserve private upload")
        # No automatic retry after this line; a network failure may have uploaded it.
        run(sys.executable, UPLOAD, "send", "--manifest", manifest,
            "--video-file", video)
        receipt_path = RECEIPTS / (id_ + ".json")
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        video_id = receipt["video_id"]
        if not (receipt.get("status") == "uploaded" and len(video_id) == 11):
            raise RuntimeError(f"{id_}: send returned without valid uploaded ID")
        # Write ID to Git first, before any optional readback that might fail.
        commit_receipt(id_, "record private video ID")
        verified_at = api_verify_private(id_, video_id)
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        receipt.update({"privacy_status": "private", "channel_id": RU_ID,
                        "private_verified_at": verified_at,
                        "source_sha256": digest, "upload_method": "youtube-direct",
                        "owner_audio_approved": True, "publish_at_utc": None})
        receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        commit_receipt(id_, "verify private-only YouTube upload")
        print(f"PRIVATE_UPLOAD_CONFIRMED {id_} https://studio.youtube.com/video/{video_id}/edit", flush=True)
    print("ALL_FOUR_PRIVATE_UPLOADS_CONFIRMED_NO_SCHEDULE", flush=True)


if __name__ == "__main__":
    main()
