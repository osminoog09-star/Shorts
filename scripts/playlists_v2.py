#!/usr/bin/env python3
"""Create the M1lash playlists if missing and sort film videos into them (read/write playlists only)."""
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from youtube_direct import RU_ID, token_for, verify_channel  # noqa: E402
from youtube_stats import iso_seconds  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CFG = ROOT / "publishing" / "playlists.json"
API = "https://www.googleapis.com/youtube/v3"


def call(method, path, tok, **kw):
    r = requests.request(method, API + path, headers={"Authorization": "Bearer " + tok}, timeout=60, **kw)
    if not r.ok:
        raise RuntimeError("%s %s -> HTTP %s %s" % (method, path, r.status_code, r.text[:200]))
    return r.json() if r.text else {}


def main():
    tok = token_for("ru")
    verify_channel(tok, RU_ID)
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    for key in ("kino_shorts", "kino_razbor"):
        p = cfg[key]
        if not p.get("id"):
            made = call("POST", "/playlists", tok, params={"part": "snippet,status"},
                        json={"snippet": {"title": p["title"], "description": p["description"], "defaultLanguage": "ru"},
                              "status": {"privacyStatus": "public"}})
            p["id"] = made["id"]
            print("CREATED", p["title"], p["id"])
    CFG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ch = call("GET", "/channels", tok, params={"part": "contentDetails", "mine": "true"})
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    def members(pl):
        ids, page = set(), None
        while True:
            q = {"part": "contentDetails", "playlistId": pl, "maxResults": 50}
            if page:
                q["pageToken"] = page
            r = call("GET", "/playlistItems", tok, params=q)
            ids |= {x["contentDetails"]["videoId"] for x in r.get("items", [])}
            page = r.get("nextPageToken")
            if not page:
                return ids
    all_ids = sorted(members(uploads))
    want = {"kino_shorts": set(cfg["kino_shorts"]["seed"]), "kino_razbor": set(cfg["kino_razbor"]["seed"])}
    for i in range(0, len(all_ids), 50):
        r = call("GET", "/videos", tok, params={"part": "snippet,contentDetails", "id": ",".join(all_ids[i:i + 50])})
        for v in r.get("items", []):
            if v["snippet"].get("categoryId") == "1":
                dur = iso_seconds(v["contentDetails"].get("duration")) or 0
                want["kino_shorts" if dur <= 180 else "kino_razbor"].add(v["id"])
    for key, vids in want.items():
        pl = cfg[key]["id"]
        have = members(pl)
        for vid in sorted(vids - have):
            call("POST", "/playlistItems", tok, params={"part": "snippet"},
                 json={"snippet": {"playlistId": pl, "resourceId": {"kind": "youtube#video", "videoId": vid}}})
            print("ADDED", vid, "->", cfg[key]["title"])
    print("PLAYLISTS_OK", {k: cfg[k]["id"] for k in want})


if __name__ == "__main__":
    main()
