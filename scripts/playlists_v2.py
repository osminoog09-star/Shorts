#!/usr/bin/env python3
"""Non-destructive idempotent YouTube playlist sync for the M1lash channel.

Only adds confirmed PUBLIC videos to their primary thematic playlist; does not
remove/hide videos, change video metadata or touch old Shorts RU/ENG playlists.
Existing playlists and their IDs remain untouched. New entries go to position 0.
"""
import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_direct import RU_ID, token_for, verify_channel  # noqa: E402
from youtube_stats import iso_seconds  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "publishing" / "playlists.json"
API = "https://www.googleapis.com/youtube/v3"
GROUPS = ("kino_shorts", "kino_razbor", "pretend_bot", "ai_news",
          "ai_sketches", "science_history", "humor")
UA = requests.Session()


def call(method, path, token, **kw):
    resp = UA.request(method, API + path,
                      headers={"Authorization": "Bearer " + token},
                      timeout=60, **kw)
    if not resp.ok:
        raise RuntimeError(f"{method} {path} -> HTTP {resp.status_code}: {resp.text[:200]}")
    return resp.json() if resp.content else {}


def list_items(token, playlist_id):
    """Return video IDs already in a playlist; read-only."""
    ids, page = set(), None
    while True:
        params = {"part": "contentDetails", "playlistId": playlist_id, "maxResults": 50}
        if page:
            params["pageToken"] = page
        data = call("GET", "/playlistItems", token, params=params)
        ids.update(item.get("contentDetails", {}).get("videoId")
                   for item in data.get("items", [])
                   if item.get("contentDetails", {}).get("videoId"))
        page = data.get("nextPageToken")
        if not page:
            return ids


def uploaded_ids(token):
    channel = call("GET", "/channels", token,
                   params={"part": "contentDetails", "mine": "true"})
    uploads = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    return sorted(list_items(token, uploads))


def all_public_videos(token, ids):
    result = {}
    for i in range(0, len(ids), 50):
        data = call("GET", "/videos", token,
                    params={"part": "snippet,status,contentDetails",
                            "id": ",".join(ids[i:i + 50])})
        for item in data.get("items", []):
            if item.get("status", {}).get("privacyStatus") == "public":
                result[item["id"]] = item
    return result


def choose(video, seeds):
    vid = video["id"]
    for key in GROUPS:
        if vid in seeds[key]:
            return key
    snippet = video["snippet"]
    title = (snippet.get("title") or "").casefold()
    seconds = iso_seconds(video.get("contentDetails", {}).get("duration")) or 0

    if "притворись ботом" in title:
        return "pretend_bot"
    # YouTube category 1 is the main category for film clips and film essays.
    if str(snippet.get("categoryId")) == "1":
        return "kino_shorts" if seconds <= 180 else "kino_razbor"
    if re.search(r"новост|недел[юие]|скандал|запрет|прорыв|искусственн.*интеллект", title):
        return "ai_news"
    if re.search(r"луна|венер|антикитер|древн|герон|истори|самол[её]т|батаре|физик|наук|двигател", title):
        return "science_history"
    if re.search(r"\bии\b|нейросет|нейросетк|робот|кодекс|chatgpt|попросил|капч", title):
        return "ai_sketches"
    return "humor"


def main():
    token = token_for("ru")
    verify_channel(token, RU_ID)
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    for key in GROUPS:
        if key not in cfg:
            raise RuntimeError(f"Missing group: {key}")
    # Only our seven managed playlist IDs; old Shorts RU/ENG never enumerated.
    for key in GROUPS:
        entry = cfg[key]
        if not entry.get("id"):
            result = call("POST", "/playlists", token,
                          params={"part": "snippet,status"},
                          json={"snippet": {"title": entry["title"],
                                            "description": entry["description"],
                                            "defaultLanguage": "ru"},
                                "status": {"privacyStatus": "public"}})
            entry["id"] = result["id"]
            # Persist each successful creation immediately to avoid duplicates on retry.
            CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
            print("CREATED", key, entry["id"])

    public = all_public_videos(token, uploaded_ids(token))
    seeds = {k: set(cfg[k].get("seed", [])) for k in GROUPS}
    # Hard-coded seeds must not cause duplicate assignment between our new groups.
    overlaps = [(v, a, b) for i, a in enumerate(GROUPS)
                for b in GROUPS[i + 1:] for v in seeds[a] & seeds[b]]
    if overlaps:
        raise RuntimeError(f"Overlapping playlist seeds: {overlaps}")
    desired = {k: [] for k in GROUPS}
    for video in public.values():
        key = choose(video, seeds)
        desired[key].append(video)

    for key in GROUPS:
        playlist_id = cfg[key]["id"]
        existing = list_items(token, playlist_id)
        missing = [v for v in desired[key] if v["id"] not in existing]
        # Insert oldest first at position=0 => newest ends at the top.
        missing.sort(key=lambda v: (v["snippet"].get("publishedAt", ""), v["id"]))
        for video in missing:
            call("POST", "/playlistItems", token,
                 params={"part": "snippet"},
                 json={"snippet": {
                     "playlistId": playlist_id,
                     "position": 0,
                     "resourceId": {"kind": "youtube#video", "videoId": video["id"]}
                 }})
            print("ADDED", video["id"], "->", key)
        print("PLAYLIST", key, "existing", len(existing), "new", len(missing))
    print("PLAYLISTS_OK", {k: cfg[k]["id"] for k in GROUPS})


if __name__ == "__main__":
    main()
