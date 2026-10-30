#!/usr/bin/env python3
"""M1lash: idempotent additive playlist synchronization, no deletions/legacy edits."""
import json
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_direct import RU_ID, token_for, verify_channel
from youtube_stats import iso_seconds

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "publishing" / "playlists.json"
API = "https://www.googleapis.com/youtube/v3"

def call(method, path, token, **kw):
    r = requests.request(method, API + path, headers={"Authorization": "Bearer " + token}, timeout=60, **kw)
    if not r.ok:
        raise RuntimeError("%s %s: HTTP %s %s" % (method, path, r.status_code, r.text[:250]))
    return r.json() if r.text else {}

def pages(path, token, **params):
    result = []
    page = None
    while True:
        query = {**params, "maxResults": 50}
        if page: query["pageToken"] = page
        data = call("GET", path, token, params=query)
        result += data.get("items", [])
        page = data.get("nextPageToken")
        if not page: return result

def category(video, seeds):
    vid = video["id"]
    for key, values in seeds.items():
        if vid in values: return key
    title = video["snippet"].get("title", "").lower()
    seconds = iso_seconds(video["contentDetails"].get("duration", "")) or 0
    if video["snippet"].get("categoryId") == "1":
        return "kino_shorts" if seconds <= 180 else "kino_razbor"
    if "притворись ботом" in title: return "bot_series"
    if any(word in title for word in ("новост", "скандал", "nvidia вложила", "прорыв?!")):
        return "ai_news"
    if any(word in title for word in ("антикитер", "древн", "венер", "лун", "батаре", "самол", "двигател", "компьютеру 2000", "компьютер, которому 2000", "герон")):
        return "science_history"
    if any(word in title for word in ("угадай фильм", "сцена из", "хайзенберг", "чигур", "во все тяжкие", "легeндарная сцена")):
        return "kino_shorts" if seconds <= 180 else "kino_razbor"
    if any(word in title for word in ("нейросет", "ии ", " ии", "робот", "chatgpt", "codex", "агент")):
        return "ai_sketch"
    return "humor"

def main():
    token = token_for("ru")
    verify_channel(token, RU_ID)
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    keys = [k for k, v in cfg.items() if isinstance(v, dict) and "title" in v and "seed" in v]
    existing = {x["snippet"]["title"]: x["id"] for x in pages("/playlists", token, part="snippet", mine="true")}
    for key in keys:
        p = cfg[key]
        if not p.get("id"):
            if p["title"] in existing:
                p["id"] = existing[p["title"]]
                print("FOUND", p["title"], p["id"])
            else:
                made = call("POST", "/playlists", token, params={"part": "snippet,status"},
                            json={"snippet": {"title": p["title"], "description": p["description"], "defaultLanguage": "ru"},
                                  "status": {"privacyStatus": "public"}})
                p["id"] = made["id"]
                print("CREATED", p["title"], p["id"])
            CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    channels = call("GET", "/channels", token, params={"part": "contentDetails", "mine": "true"})
    uploads = channels["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    listed = pages("/playlistItems", token, part="contentDetails", playlistId=uploads)
    upload_ids = list(dict.fromkeys(x["contentDetails"]["videoId"] for x in listed))
    videos = []
    for n in range(0, len(upload_ids), 50):
        result = call("GET", "/videos", token, params={"part": "snippet,contentDetails,status", "id": ",".join(upload_ids[n:n + 50])})
        videos += [v for v in result.get("items", []) if v.get("status", {}).get("privacyStatus") == "public"]
    seeds = {key: set(cfg[key].get("seed", [])) for key in keys}
    wanted = {key: [] for key in keys}
    for v in videos:
        k = category(v, seeds)
        if k in wanted: wanted[k].append(v)
    for key, items in wanted.items():
        playlist_id = cfg[key]["id"]
        have = {x["contentDetails"]["videoId"] for x in pages("/playlistItems", token, part="contentDetails", playlistId=playlist_id)}
        # Oldest first + position 0 => newest videos at the top after insertion.
        for v in sorted((v for v in items if v["id"] not in have), key=lambda i: i["snippet"].get("publishedAt", "")):
            call("POST", "/playlistItems", token, params={"part": "snippet"},
                 json={"snippet": {"playlistId": playlist_id, "position": 0,
                                   "resourceId": {"kind": "youtube#video", "videoId": v["id"]}}})
            print("ADDED", v["id"], "->", cfg[key]["title"])
    print("PLAYLISTS_OK", {k: cfg[k]["id"] for k in keys}, "public uploads scanned:", len(videos))

if __name__ == "__main__":
    main()
