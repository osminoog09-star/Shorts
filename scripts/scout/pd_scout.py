#!/usr/bin/env python3
"""Скаут материала M1lash (решение Дениса 06.11.2026: «сами ищут материал для кино-Shorts»).

Ищет ЗАКОННЫЕ бесплатные фильмы — общественное достояние (Public Domain Mark / CC0) и Creative Commons
BY/BY-SA — в Internet Archive и среди открытых фильмов Blender Studio. Лицензия проверяется по метаданным
самого источника (licenseurl), без неё фильм не берётся. Пиратские сайты, торренты, YouTube, DRM — никогда.

Результат: reports/scout/library.json — кандидаты с прямой ссылкой на MP4 (её принимает movie-short.yml
как `url`), лицензией и доказательством (ссылка на страницу с лицензией). Уже занятые фильмы
(publishing/film_projects.json) пропускаются.

usage: python scripts/scout/pd_scout.py [--rows 60] [--out reports/scout/library.json]
Работает в GitHub Actions (material-scout.yml); из песочницы archive.org может быть недоступен.
"""
import argparse, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UA = {"User-Agent": "M1lash-Studio-scout/1.0 (+https://github.com/osminoog09-star/Shorts)"}
# не для канала: взрослое, сборники-«грайндхаус», нарезки — скаут их не предлагает
SKIP = re.compile(r"nudist|naked|nude|sex|erotic|grindhouse|double feature|public domain movies|compilation|trailer", re.I)
OK_LICENSE = re.compile(r"creativecommons\.org/(publicdomain/(mark|zero)/|licenses/by(-sa)?/)", re.I)
MAX_BYTES = 1_800_000_000

# Открытые фильмы Blender Studio — CC BY (https://studio.blender.org/films/), прямые MP4 с download.blender.org
BLENDER = [
    {"title": "Sintel (2010)", "url": "https://download.blender.org/durian/movies/Sintel.2010.1080p.mkv", "page": "https://durian.blender.org/"},
    {"title": "Tears of Steel (2012)", "url": "https://download.blender.org/demo/movies/ToS/tears_of_steel_1080p.mov", "page": "https://mango.blender.org/"},
    {"title": "Big Buck Bunny (2008)", "url": "https://download.blender.org/peach/bigbuckbunny_movies/big_buck_bunny_1080p_h264.mov", "page": "https://peach.blender.org/"},
]


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return json.loads(r.read())
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(3 * (i + 1))


def reachable(url):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status == 200
    except Exception:
        return False


def used_films():
    try:
        d = json.loads((ROOT / "publishing" / "film_projects.json").read_text(encoding="utf-8"))
        return {re.sub(r"\W+", "", x.get("film", "").lower()) for x in d.get("items", [])}
    except Exception:
        return set()


def search(query, rows):
    q = urllib.parse.urlencode({"q": query, "fl[]": ["identifier", "title", "year", "downloads", "licenseurl", "language", "runtime"],
                                "sort[]": "downloads desc", "rows": rows, "output": "json"}, doseq=True)
    d = get("https://archive.org/advancedsearch.php?" + q)
    if "response" not in d:
        raise RuntimeError(str(d)[:300])
    return d["response"]["docs"]


def best_mp4(ident):
    meta = get("https://archive.org/metadata/" + urllib.parse.quote(ident))
    lic = (meta.get("metadata") or {}).get("licenseurl", "")
    files = [f for f in meta.get("files", []) if f.get("name", "").lower().endswith(".mp4") and f.get("source") != "metadata"]
    files = [f for f in files if 50_000_000 < int(f.get("size", 0) or 0) < MAX_BYTES]
    if not files:
        return None, lic
    f = max(files, key=lambda x: int(x.get("size", 0)))  # самый качественный в пределах лимита
    return {"name": f["name"], "bytes": int(f["size"]),
            "url": "https://archive.org/download/" + urllib.parse.quote(ident) + "/" + urllib.parse.quote(f["name"])}, lic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=int, default=60)
    ap.add_argument("--out", default="reports/scout/library.json")
    a = ap.parse_args()
    used, out, seen = used_films(), [], set()
    queries = [
        # лицензию фильтруем по метаданным каждого фильма (ведущие * в поиске archive.org не работают)
        ('collection:(feature_films) AND mediatype:(movies)', "any"),
        ('mediatype:(movies) AND (language:(Russian) OR language:(rus)) AND (collection:(feature_films) OR collection:(moviesandfilms))', "ru"),
    ]
    for q, tag in queries:
        try:
            docs = search(q, a.rows)
        except Exception as e:
            print("search failed:", tag, e, file=sys.stderr); continue
        for d in docs:
            ident = d["identifier"]
            key = re.sub(r"\W+", "", str(d.get("title", "")).lower())
            if ident in seen or key in used or SKIP.search(str(d.get('title', ''))):
                continue
            seen.add(ident)
            try:
                mp4, lic = best_mp4(ident)
            except Exception as e:
                print("meta failed:", ident, e, file=sys.stderr); continue
            if not mp4 or not OK_LICENSE.search(lic or ""):
                continue  # нет MP4 или лицензия не подтверждена источником — не берём
            lang = d.get("language")
            out.append({"source": "internet_archive", "id": ident, "title": d.get("title"), "year": d.get("year"),
                        "language": lang if isinstance(lang, str) else ", ".join(lang or []),
                        "russian_audio": tag == "ru", "downloads": d.get("downloads"), "license": lic,
                        "proof": "https://archive.org/details/" + ident, **mp4})
            time.sleep(0.5)
    for b in BLENDER:
        if not reachable(b["url"]):
            print("blender: недоступно, пропуск", b["url"], file=sys.stderr); continue
        out.append({"source": "blender_studio", "id": re.sub(r"\W+", "_", b["title"].lower()).strip("_"), "title": b["title"],
                    "language": "English", "russian_audio": False, "license": "https://creativecommons.org/licenses/by/3.0/",
                    "proof": b["page"], "url": b["url"]})
    p = ROOT / a.out
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"t": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "count": len(out),
                             "rule": "только PD/CC по метаданным источника; ru-аудио помечено; занятые фильмы исключены",
                             "items": out}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"scout: {len(out)} кандидатов ({sum(1 for x in out if x['russian_audio'])} с русским звуком) → {a.out}")


if __name__ == "__main__":
    main()
