#!/usr/bin/env python3
"""Safe, per-channel YouTube uploader for reviewed M1lash videos.

No background process. 'check' never uploads; 'reserve' persists a guard before
'send'. Only the GitHub Actions workflow should run 'send' after reservation.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "publishing" / "queue"
CHANNELS = ROOT / "publishing" / "channels.json"
RECEIPTS = ROOT / "publishing" / "receipts"
TZ = ZoneInfo("Europe/Tallinn")
API = "https://www.googleapis.com/youtube/v3"
RU_ID = "UC919eyHbOIgjsnH8z70pmZw"


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(path)


def manifest_path(value):
    path = (ROOT / value).resolve()
    if path.parent != QUEUE.resolve() or not re.fullmatch(r"[a-zA-Z0-9_-]+\.json", path.name):
        raise ValueError("Manifest must be a file directly under publishing/queue/*.json")
    if not path.is_file():
        raise ValueError("Manifest not found")
    return path


def receipt_path(path):
    return RECEIPTS / path.name


def event_time(value):
    instant = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("publish_at must include an explicit UTC offset (Europe/Tallinn)")
    local = instant.astimezone(TZ)
    if local.utcoffset() != instant.utcoffset():
        raise ValueError("publish_at offset must match Tallinn daylight-saving time")
    return instant.astimezone(dt.timezone.utc)


def validate(data, channel_map, check_future=True):
    if not isinstance(data, dict):
        raise ValueError("Manifest must be an object")
    lang = data.get("channel")
    if lang not in ("ru", "en"):
        raise ValueError("channel must be ru or en")
    ids = [v for v in channel_map.values() if v]
    if len(ids) != len(set(ids)):
        raise ValueError("RU and EN must use different YouTube channel IDs")
    channel_id = channel_map.get(lang)
    if not isinstance(channel_id, str) or not re.fullmatch(r"UC[A-Za-z0-9_-]{22}", channel_id):
        raise ValueError("YouTube channel ID not configured for " + lang)
    if lang == "ru" and channel_id != RU_ID:
        raise ValueError("RU channel differs from connected M1lash channel")
    source = data.get("source", {})
    if source.get("type") == "repo":
        relative = source.get("path", "")
        relative_path = Path(relative)
        if (not isinstance(relative, str) or relative_path.is_absolute()
                or ".." in relative_path.parts or relative_path.suffix.lower() != ".mp4"
                or not (relative.startswith("videos/") or relative.startswith("longform/"))):
            raise ValueError("Invalid repository MP4 path")
        file_path = (ROOT / relative).resolve()
        if not file_path.is_relative_to(ROOT) or not file_path.is_file():
            raise ValueError("Source MP4 absent from checkout")
    elif source.get("type") == "release":
        for field in ("tag", "asset"):
            value = source.get(field, "")
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,180}", value):
                raise ValueError("Invalid release " + field)
        if not source["asset"].lower().endswith(".mp4"):
            raise ValueError("Release asset must be an MP4")
    else:
        raise ValueError("Source must be repo or release")
    digest = source.get("sha256")
    if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest)):
        raise ValueError("sha256 must be 64 hex digits")
    meta = data.get("metadata", {})
    if not isinstance(meta, dict):
        raise ValueError("metadata must be an object")
    title = meta.get("title", "")
    description = meta.get("description", "")
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 100:
        raise ValueError("Video title must be 1..100 characters")
    if not isinstance(description, str) or len(description) > 5000:
        raise ValueError("Description too long or invalid")
    if meta.get("type") not in ("short", "long"):
        raise ValueError("metadata.type must be short or long")
    if not isinstance(meta.get("made_for_kids"), bool):
        raise ValueError("made_for_kids must be explicitly true or false")
    if not isinstance(meta.get("contains_synthetic_media"), bool):
        raise ValueError("contains_synthetic_media must be explicitly true or false")
    tags = meta.get("tags", [])
    if not isinstance(tags, list) or len(tags) > 30 or any(not isinstance(t, str) or len(t) > 80 for t in tags):
        raise ValueError("tags must be up to 30 short strings")
    category = str(meta.get("category_id", "24"))
    if not category.isdigit():
        raise ValueError("category_id must be numeric")
    publish_at = event_time(data.get("publish_at", ""))
    if check_future and publish_at < dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=45):
        raise ValueError("Publishing requires at least 45 minutes of lead time")
    return lang, channel_id, publish_at


def validate_queue(current_path, current, channel_map):
    channel, _, when = validate(current, channel_map)
    today = when.astimezone(TZ).date()
    shorts = []
    for other_path in QUEUE.glob("*.json"):
        if other_path.resolve() == current_path.resolve():
            continue
        other = load_json(other_path)
        if other.get("channel") != channel:
            continue
        other_when = event_time(other["publish_at"])
        if abs((other_when - when).total_seconds()) < 60:
            raise ValueError("Collision: another queued video has the same publication time")
        if other.get("metadata", {}).get("type") == "short" and other_when.astimezone(TZ).date() == today:
            shorts.append(other_when)
    if current.get("metadata", {}).get("type") == "short":
        if len(shorts) >= 2:
            raise ValueError("No more than two Shorts per day on this channel")
        if any(abs((other - when).total_seconds()) < 6 * 3600 for other in shorts):
            raise ValueError("Shorts on same channel must be at least six hours apart")


def token_for(lang):
    client_id = os.environ.get("YOUTUBE_OAUTH_CLIENT_ID") or os.environ.get("YT_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_OAUTH_CLIENT_SECRET") or os.environ.get("YT_CLIENT_SECRET")
    refresh = os.environ.get("YOUTUBE_REFRESH_TOKEN_" + lang.upper())
    if lang == "ru":
        refresh = refresh or os.environ.get("YT_REFRESH_TOKEN")
    if not all((client_id, client_secret, refresh)):
        raise RuntimeError("YouTube OAuth secrets are missing for " + lang + "; see publishing/README.md")
    response = requests.post("https://oauth2.googleapis.com/token",
                             data={"client_id": client_id, "client_secret": client_secret,
                                   "refresh_token": refresh, "grant_type": "refresh_token"}, timeout=40)
    if not response.ok:
        raise RuntimeError("OAuth token refresh failed (HTTP %s)" % response.status_code)
    return response.json()["access_token"]


def verify_channel(token, channel_id):
    response = requests.get(API + "/channels",
                            params={"part": "id,snippet", "mine": "true"},
                            headers={"Authorization": "Bearer " + token}, timeout=40)
    if not response.ok:
        raise RuntimeError("YouTube channel verification failed (HTTP %s)" % response.status_code)
    items = response.json().get("items", [])
    if channel_id not in {item.get("id") for item in items}:
        raise RuntimeError("OAuth token belongs to the wrong YouTube channel; upload blocked")


def youtube_upload(video_path, data, publish_at, token):
    video_path = Path(video_path)
    if not video_path.is_file() or video_path.suffix.lower() != ".mp4" or video_path.stat().st_size < 1000:
        raise ValueError("MP4 file missing or empty")
    expected_sha = data["source"].get("sha256")
    if expected_sha:
        sha = hashlib.sha256()
        with video_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                sha.update(chunk)
        if sha.hexdigest().lower() != expected_sha.lower():
            raise ValueError("MP4 SHA-256 mismatch; refusing upload")
    meta = data["metadata"]
    payload = {
        "snippet": {
            "title": meta["title"], "description": meta["description"],
            "tags": meta.get("tags", []), "categoryId": str(meta.get("category_id", "24")),
            "defaultLanguage": data["channel"]
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_at.isoformat().replace("+00:00", "Z"),
            "selfDeclaredMadeForKids": meta["made_for_kids"],
            "containsSyntheticMedia": meta["contains_synthetic_media"]
        }
    }
    size = video_path.stat().st_size
    response = requests.post("https://www.googleapis.com/upload/youtube/v3/videos",
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": "Bearer " + token, "X-Upload-Content-Length": str(size),
                 "X-Upload-Content-Type": "video/mp4"},
        json=payload, timeout=60)
    if response.status_code not in (200, 201) or "Location" not in response.headers:
        raise RuntimeError("YouTube initialization failed (HTTP %s); do not auto-retry" % response.status_code)
    session = response.headers["Location"]
    parsed = urlparse(session)
    if parsed.scheme != "https" or parsed.hostname not in ("www.googleapis.com", "youtube.googleapis.com"):
        raise RuntimeError("Invalid YouTube resumable session host")
    with video_path.open("rb") as stream:
        uploaded = requests.put(session, data=stream,
                                headers={"Content-Length": str(size), "Content-Type": "video/mp4"},
                                timeout=1200, allow_redirects=False)
    if not uploaded.ok:
        raise RuntimeError("YouTube upload outcome uncertain (HTTP %s): inspect channel before retry" % uploaded.status_code)
    result = uploaded.json()
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", str(result.get("id", ""))):
        raise RuntimeError("YouTube returned no valid video ID; inspect channel before retry")
    return result["id"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["check", "reserve", "send"])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--video-file", default="")
    args = parser.parse_args()
    file = manifest_path(args.manifest)
    data = load_json(file)
    channels = load_json(CHANNELS)
    channel, expected_id, publish_at = validate(data, channels)
    validate_queue(file, data, channels)
    receipt = receipt_path(file)
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    if args.operation == "check":
        if receipt.exists():
            raise ValueError("Previously reserved/uploaded: " + str(receipt.relative_to(ROOT)))
        print("CHECK OK: channel=%s, publish_at=%s, mode=PRIVATE until scheduled release" %
              (channel, publish_at.isoformat()))
        print("Metricool appointments are NOT visible here: inspect its existing queue during migration.")
        return
    if args.operation == "reserve":
        if receipt.exists():
            raise ValueError("Receipt already exists; manual reconciliation required")
        atomic_json(receipt, {"status": "reserved", "manifest": str(file.relative_to(ROOT)),
                              "manifest_sha256": digest, "channel": channel,
                              "publish_at_utc": publish_at.isoformat(),
                              "note": "A reserved attempt must NEVER be automatically retried."})
        print("RESERVED " + str(receipt.relative_to(ROOT)))
        return
    if not receipt.exists():
        raise ValueError("No reservation receipt: run reserve and persist it BEFORE uploading")
    prior = load_json(receipt)
    if prior.get("status") != "reserved" or prior.get("manifest_sha256") != digest:
        raise ValueError("Receipt state/hash mismatch: manual intervention required")
    if not args.video_file:
        raise ValueError("--video-file required for send")
    # Upload outcome may remain uncertain after a network error. Do not re-run 'send'.
    # The workflow writes a durable reservation commit before reaching this point.
    token = token_for(channel)
    verify_channel(token, expected_id)
    vid = youtube_upload(args.video_file, data, publish_at, token)
    atomic_json(receipt, {**prior, "status": "uploaded", "video_id": vid,
                          "video_url": "https://youtu.be/" + vid})
    print("YOUTUBE_UPLOAD_OK https://youtu.be/" + vid)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, KeyError, json.JSONDecodeError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        sys.exit(1)
