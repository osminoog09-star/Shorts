#!/usr/bin/env python3
"""Ежечасный «пульс» канала: счётчики Data API (подписчики, просмотры свежих роликов). Только чтение.

YouTube Analytics обновляется с задержкой 1–2 дня, поэтому почасово берём только живые счётчики
videos.list / channels.list (≈3 единицы квоты в час). Хранится в ветке pulse-data (не засоряет main):
pulse.json = {"snapshots": [{"t", "subs", "views", "videos": {id: views}}], "recent": [{id,title,published}]},
последние 72 часа. Сайт студии берёт его в motion-pages.yml.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.youtube_direct import token_for  # noqa: E402

API = "https://www.googleapis.com/youtube/v3/"


def get(s, path, **params):
    r = s.get(API + path, params=params, timeout=30)
    if not r.ok:
        sys.exit(f"pulse: Data API HTTP {r.status_code} (no secrets logged)")
    return r.json()


def main(out):
    s = requests.Session()
    s.headers["Authorization"] = "Bearer " + token_for("ru")
    ch = get(s, "channels", part="statistics,contentDetails", mine="true")["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    items = get(s, "playlistItems", part="contentDetails,snippet", playlistId=uploads, maxResults=10)["items"]
    ids = [i["contentDetails"]["videoId"] for i in items]
    vids = get(s, "videos", part="statistics,status,snippet", id=",".join(ids))["items"]
    public = [v for v in vids if v["status"]["privacyStatus"] == "public"]
    path = Path(out)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {"snapshots": []}
    st = ch["statistics"]
    data["snapshots"].append({"t": datetime.now(timezone.utc).isoformat(timespec="minutes"),
                              "subs": int(st.get("subscriberCount", 0)), "views": int(st.get("viewCount", 0)),
                              "videos": {v["id"]: int(v["statistics"].get("viewCount", 0)) for v in public}})
    data["snapshots"] = data["snapshots"][-72:]
    data["recent"] = [{"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"],
                       "likes": int(v["statistics"].get("likeCount", 0)),
                       "comments": int(v["statistics"].get("commentCount", 0))} for v in public]
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    print("pulse:", st.get("subscriberCount"), "subs,", len(public), "recent public videos")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "pulse.json")
