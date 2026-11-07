#!/usr/bin/env python3
"""One-off playlist cleanup from reports/youtube/channel_audit.json (Claude, 07.11.2026, Денис: «приведи канал в порядок»).
Only playlist MEMBERSHIP changes: no video is deleted, hidden or edited; no playlist is deleted. Idempotent."""
import sys
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import youtube_direct as yd  # noqa: E402

NEWS_OLD, FILMS_OLD = "PLfmef1R-EinQ", "PLQTlKCepQASo"
KINO, GAMES, AI_SKETCH, FILMS = "PLIVjPUG-C-Xc", "PLLncmzxjs43Q", "PLW88AiB_GiWg", "PLIjIaTAj2CdA"
REMOVE = [  # (playlist, video, why)
    (NEWS_OLD, "F5-BqfTnA_w", "наука (самолёт) — не новости"),
    (NEWS_OLD, "4PYRNmbopwo", "наука (Венера) — не новости"),
    (NEWS_OLD, "OpMT1DWymCA", "наука (батарея) — не новости"),
    (KINO, "1As0yonBV9Q", "Roblox-квест — не кино"),
    (FILMS_OLD, "1As0yonBV9Q", "Roblox-квест — не кино"),
]
ADD = [
    (GAMES, "1As0yonBV9Q", "Roblox — в «Мои игровые проекты»"),
    (AI_SKETCH, "bEdC0uFDvl4", "кофемашина вышла 07.11 — ИИ-скетч"),
]


def items(token, pl):
    out, tok = [], None
    while True:
        r = requests.get(yd.API + "/playlistItems", params={"part": "id,contentDetails", "playlistId": pl, "maxResults": 50, **({"pageToken": tok} if tok else {})},
                         headers={"Authorization": "Bearer " + token}, timeout=40)
        r.raise_for_status(); j = r.json(); out += j.get("items", []); tok = j.get("nextPageToken")
        if not tok: return out


def main():
    token = yd.token_for("ru"); H = {"Authorization": "Bearer " + token}
    for pl, vid, why in REMOVE:
        for it in items(token, pl):
            if it["contentDetails"]["videoId"] == vid:
                r = requests.delete(yd.API + "/playlistItems", params={"id": it["id"]}, headers=H, timeout=40)
                print("REMOVED" if r.ok else f"FAIL {r.status_code}", pl, vid, why)
    for pl, vid, why in ADD:
        if any(it["contentDetails"]["videoId"] == vid for it in items(token, pl)):
            print("ALREADY", pl, vid); continue
        r = requests.post(yd.API + "/playlistItems", params={"part": "snippet"}, headers=H, timeout=40,
                          json={"snippet": {"playlistId": pl, "position": 0, "resourceId": {"kind": "youtube#video", "videoId": vid}}})
        print("ADDED" if r.ok else f"FAIL {r.status_code} {r.text[:200]}", pl, vid, why)


if __name__ == "__main__":
    main()
