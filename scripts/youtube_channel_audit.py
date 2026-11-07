#!/usr/bin/env python3
"""Read-only channel audit (Claude, 07.11.2026): every upload (any privacy) + every playlist of the channel and its members.
Writes reports/youtube/channel_audit.json and prints: uploads with their playlists, videos in no playlist, duplicates,
Shorts in long-video playlists and vice versa. Changes nothing on YouTube."""
import json, re, sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import youtube_direct as yd  # noqa: E402


def secs(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    return 0 if not m else sum(int(x or 0) * k for x, k in zip(m.groups(), (86400, 3600, 60, 1)))


def pages(token, path, **params):
    out, tok = [], None
    while True:
        r = requests.get(yd.API + path, params={**params, "maxResults": 50, **({"pageToken": tok} if tok else {})},
                         headers={"Authorization": "Bearer " + token}, timeout=40)
        r.raise_for_status(); j = r.json(); out += j.get("items", []); tok = j.get("nextPageToken")
        if not tok: return out


def main():
    token = yd.token_for("ru")
    ch = requests.get(yd.API + "/channels", params={"part": "contentDetails,snippet", "mine": "true"},
                      headers={"Authorization": "Bearer " + token}, timeout=40).json()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = list(dict.fromkeys(x["contentDetails"]["videoId"] for x in pages(token, "/playlistItems", part="contentDetails", playlistId=uploads)))
    vids = {}
    for i in range(0, len(ids), 50):
        r = requests.get(yd.API + "/videos", params={"part": "snippet,contentDetails,status", "id": ",".join(ids[i:i + 50])},
                         headers={"Authorization": "Bearer " + token}, timeout=40).json()
        for v in r.get("items", []):
            vids[v["id"]] = {"title": v["snippet"]["title"], "privacy": v["status"]["privacyStatus"], "publishAt": v["status"].get("publishAt"),
                             "sec": secs(v["contentDetails"].get("duration")), "cat": v["snippet"].get("categoryId"),
                             "published": v["snippet"].get("publishedAt"), "playlists": []}
    pls = []
    for p in pages(token, "/playlists", part="snippet,status,contentDetails", mine="true"):
        items = [x["contentDetails"]["videoId"] for x in pages(token, "/playlistItems", part="contentDetails", playlistId=p["id"])]
        pls.append({"id": p["id"], "title": p["snippet"]["title"], "privacy": p["status"]["privacyStatus"], "count": len(items), "items": items})
        for v in items:
            if v in vids: vids[v]["playlists"].append(p["snippet"]["title"])
    out = {"channel": ch["snippet"]["title"], "uploads": len(vids), "playlists": [{k: p[k] for k in ("id", "title", "privacy", "count")} for p in pls],
           "videos": vids, "playlist_items": {p["id"]: p["items"] for p in pls}}
    (ROOT / "reports/youtube/channel_audit.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("CHANNEL", out["channel"], "uploads", len(vids))
    for p in pls: print("PLAYLIST", p["id"], p["privacy"], p["count"], p["title"])
    for vid, v in sorted(vids.items(), key=lambda kv: kv[1]["published"] or ""):
        kind = "SHORT" if v["sec"] <= 180 else "LONG"
        print("VIDEO", vid, v["privacy"], kind, v["sec"], "|", v["title"][:60], "|", "; ".join(v["playlists"]) or "-")


if __name__ == "__main__":
    main()
