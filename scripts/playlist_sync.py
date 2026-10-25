"""Раскладывает свежие ролики канала по плейлистам: 🇷🇺 → RU, 🇺🇸 → EN, нарезки из фильмов/сериалов → «Фильмы».

Нужны переменные окружения (секреты GitHub):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN  — OAuth-доступ к каналу (scope youtube)
  PLAYLIST_RU, PLAYLIST_EN                          — ID плейлистов (из ссылки list=...)
  PLAYLIST_FILMS (необязательно)                    — плейлист для movie-edit нарезок
Movie-edit = ролик в категории «Фильмы и анимация» (categoryId 1); такие идут только в «Фильмы».
Язык ролика: флаг 🇷🇺/🇺🇸 в названии; если флага нет — кириллица = RU, иначе EN.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/youtube/v3"


def http(method, url, data=None, token=None, form=False):
    headers = {}
    body = None
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if data is not None:
        if form:
            body = urllib.parse.urlencode(data).encode()
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        sys.exit(f"HTTP {e.code} {url}\n{e.read().decode()[:500]}")


def token():
    r = http("POST", "https://oauth2.googleapis.com/token", {
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }, form=True)
    return r["access_token"]


def items(pl, tok, limit=200):
    out, page = [], ""
    while len(out) < limit:
        q = {"part": "snippet,contentDetails", "playlistId": pl, "maxResults": 50}
        if page:
            q["pageToken"] = page
        r = http("GET", f"{API}/playlistItems?{urllib.parse.urlencode(q)}", token=tok)
        out += r.get("items", [])
        page = r.get("nextPageToken")
        if not page:
            break
    return out


def lang_of(title):
    if "🇷🇺" in title:
        return "ru"
    if "🇺🇸" in title or "🇬🇧" in title:
        return "en"
    return "ru" if re.search(r"[а-яА-ЯёЁ]", title) else "en"


def main():
    tok = token()
    ch = http("GET", f"{API}/channels?part=contentDetails&mine=true", token=tok)
    uploads = ch["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    targets = {"ru": os.environ["PLAYLIST_RU"], "en": os.environ["PLAYLIST_EN"]}
    if os.environ.get("PLAYLIST_FILMS"):
        targets["films"] = os.environ["PLAYLIST_FILMS"]
    have = {k: {i["contentDetails"]["videoId"] for i in items(pl, tok)} for k, pl in targets.items()}
    added = 0
    ups = items(uploads, tok, limit=100)
    cats = {}
    for i in range(0, len(ups), 50):
        ids = ",".join(u["contentDetails"]["videoId"] for u in ups[i:i + 50])
        for v in http("GET", f"{API}/videos?part=snippet&id={ids}", token=tok).get("items", []):
            cats[v["id"]] = v["snippet"].get("categoryId")
    for it in ups:
        vid = it["contentDetails"]["videoId"]
        title = it["snippet"]["title"]
        lang = "films" if cats.get(vid) == "1" and "films" in targets else lang_of(title)
        if vid in have[lang]:
            continue
        # только Shorts/наши ролики: пропускаем то, что уже лежит в другом языковом плейлисте
        if any(vid in have[k] for k in have if k != lang):
            continue
        http("POST", f"{API}/playlistItems?part=snippet", {
            "snippet": {"playlistId": targets[lang], "resourceId": {"kind": "youtube#video", "videoId": vid}}
        }, token=tok)
        have[lang].add(vid)
        added += 1
        print(f"+ {lang.upper()}  {title}")
    print(f"готово, добавлено: {added}")


if __name__ == "__main__":
    main()
