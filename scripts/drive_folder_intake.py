#!/usr/bin/env python3
"""Private Google Drive folder discovery for future M1lash clip requests.

Read-only scan: NEVER downloads film bodies, transcribes, renders, or publishes.
Listing: private Google Drive files.list using existing OAuth; no public sharing needed.
Statuses "сцена найдена" / "собран" require separate evidence, not filename similarity.
"""
from __future__ import annotations

from clip_lifecycle import needed_requests
import datetime as dt
import json
import os
import re
import subprocess
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "publishing/drive_folder.json"
REQUESTS = ROOT / "publishing/clip_requests.json"
SCAN = ROOT / "publishing/drive_scan.json"
MEDIA_EXT = {".mp4", ".mkv", ".mov", ".avi", ".m4v", ".webm", ".ts"}
ALIASES = {
    "старикам тут не место": ["no country for old men", "nocountryforoldmen"],
    "одержимость": ["whiplash"],
    "из машины": ["ex machina", "exmachina"],
    "стрингер": ["nightcrawler"],
    "интерстеллар": ["interstellar"],
    "бэтмен": ["the batman", "batman"],
    "оппенгеймер": ["oppenheimer"],
    "меню": ["the menu"],
}
TRANSLIT = str.maketrans({
    "а":"a","б":"b","в":"v","г":"g","д":"d","е":"e","ё":"e","ж":"zh",
    "з":"z","и":"i","й":"i","к":"k","л":"l","м":"m","н":"n","о":"o",
    "п":"p","р":"r","с":"s","т":"t","у":"u","ф":"f","х":"h","ц":"ts",
    "ч":"ch","ш":"sh","щ":"shch","ъ":"","ы":"y","ь":"","э":"e","ю":"yu","я":"ya"
})


def compact(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower().replace("ё", "е")
    return re.sub(r"[^a-zа-я0-9]+", "", s)


def variants(film: str) -> list[str]:
    title = re.sub(r"\s*\(\d{4}\)\s*$", "", film).strip()
    normalized = compact(title)
    variants = [normalized, compact(title.lower().translate(TRANSLIT))]
    for key, values in ALIASES.items():
        if compact(key) == normalized:
            variants.extend(compact(v) for v in values)
    return [x for x in dict.fromkeys(variants) if len(x) >= 5]


def score(film: str, filename: str) -> int:
    name = compact(Path(filename).stem)
    year = re.search(r"\((\d{4})\)", film)
    found = [v for v in variants(film) if v in name]
    if not found:
        return 0
    result = max(90 if len(v) >= 8 else 75 for v in found)
    if year and year.group(1) in name:
        result += 9
    # Trailer/sample fragments must never auto-match a whole feature film.
    if any(x in name for x in ("trailer", "трейлер", "тизер", "teaser", "sample", "fragment", "фрагмент")):
        result -= 40
    return result


def folder_url(raw: str) -> str:
    u = urlparse(raw.strip())
    if u.scheme != "https" or u.hostname != "drive.google.com" or u.username or u.password:
        raise ValueError("Ожидается https://drive.google.com/drive/folders/ID")
    m = re.fullmatch(r"/drive/(?:u/\d+/)?folders/([A-Za-z0-9_-]{10,})/?", u.path)
    if not m:
        raise ValueError("Нужна ссылка именно на ПАПКУ Google Drive")
    return "https://drive.google.com/drive/folders/" + m.group(1)


def list_folder_authenticated(raw_url: str, credentials: dict[str, str] | None = None) -> list[dict]:
    """Read metadata from the owner's *private* Drive folder via existing OAuth.

    No film bytes, cookies or credentials are ever written to disk or logs.
    A public sharing setting is not required.
    """
    from drive_oauth_config import FOLDER, DriveSetupError, resolve_existing_client
    url = folder_url(raw_url)
    folder_id = url.rsplit("/", 1)[-1]
    # One known owner-controlled folder, no arbitrary Drive resource enumeration.
    if folder_id != FOLDER:
        raise RuntimeError("Папка не совпадает с настроенной личной папкой M1lash.")
    env = dict(credentials if credentials is not None else os.environ)
    if not env.get("GDRIVE_REFRESH_TOKEN"):
        raise RuntimeError("GitHub Secret GDRIVE_REFRESH_TOKEN отсутствует: приватное сканирование невозможно.")
    try:
        verified, _ = resolve_existing_client(env)
    except DriveSetupError as exc:
        raise RuntimeError("Приватный Drive недоступен (" + exc.code + ").") from None
    access_token = verified.get("_GDRIVE_ACCESS_TOKEN")
    if not access_token:
        raise RuntimeError("Google OAuth не выдал access token для списка файлов.")
    files: list[dict] = []
    page_token = ""
    for _ in range(20):
        params = {
            "q": "'" + folder_id + "' in parents and trashed = false",
            "fields": "nextPageToken,files(id,name,mimeType,size)",
            "pageSize": "1000", "supportsAllDrives": "true",
            "includeItemsFromAllDrives": "true"
        }
        if page_token:
            params["pageToken"] = page_token
        request = Request(
            "https://www.googleapis.com/drive/v3/files?" + urlencode(params),
            headers={"Authorization": "Bearer " + access_token})
        try:
            with urlopen(request, timeout=40) as response:
                payload = json.load(response)
        except HTTPError as exc:
            raise RuntimeError("Google Drive API отклонил приватный список (HTTP " + str(exc.code) + ").") from None
        except (URLError, OSError, ValueError):
            raise RuntimeError("Google Drive API не вернул список файлов.") from None
        if not isinstance(payload, dict) or not isinstance(payload.get("files"), list):
            raise RuntimeError("Google Drive API вернул неправильный список.")
        for entry in payload["files"]:
            file_id = entry.get("id", "")
            name = entry.get("name", "")
            if not re.fullmatch(r"[A-Za-z0-9_-]{10,}", file_id) or not isinstance(name, str):
                continue
            if entry.get("mimeType") == "application/vnd.google-apps.folder":
                continue
            files.append({"path": name, "url": "https://drive.google.com/file/d/" + file_id + "/view"})
        page_token = payload.get("nextPageToken", "")
        if not page_token:
            return files
    raise RuntimeError("Google Drive вернул слишком много страниц; сканирование остановлено.")



def summarize(entries: list[dict], requests: list[dict]) -> dict:
    films = list(dict.fromkeys(r["film"] for r in requests if r.get("film") and r["film"] != "Свой клип"))
    video = [e for e in entries if Path(e["path"]).suffix.lower() in MEDIA_EXT]
    matches = {}
    for film in films:
        candidates = sorted([(score(film, e["path"]), e) for e in video],
                            key=lambda t: t[0], reverse=True)
        good = [(s, e) for s, e in candidates if s >= 85]
        if len(good) == 1:
            s, e = good[0]
            matches[film] = {"status": "фильм найден", "filename": e["path"], "file_url": e["url"],
                             "confidence": s}
        elif len(good) > 1:
            confirmed = {r.get("match_confirmed_filename") for r in requests if r.get("film") == film}
            selected = [e for _, e in good if e["path"] in confirmed]
            if len(selected) == 1:
                e = selected[0]
                matches[film] = {"status": "фильм найден", "filename": e["path"], "file_url": e["url"],
                                 "confidence": 100}
            else:
                matches[film] = {"status": "нужно подтвердить фильм", "candidates": [e["path"] for _, e in good[:5]]}
        else:
            matches[film] = {"status": "нет фильма в папке"}
    items = []
    for r in requests:
        film = r.get("film", "")
        m = matches.get(film, {"status": "нужен файл"})
        # A manually verified scene remains verified until its source changes.
        verified = r.get("scene_verified") if isinstance(r.get("scene_verified"), dict) else None
        status = m["status"]
        if verified and status == "фильм найден" and verified.get("file_url") == m.get("file_url"):
            if verified.get("checked") is True and isinstance(verified.get("start"), (float, int)):
                status = "сцена найдена"
        items.append({"id": r.get("id"), "film": film, "status": status,
                      "filename": m.get("filename"), "file_url": m.get("file_url"),
                      "candidates": m.get("candidates", []),
                      "scene_start": verified.get("start") if verified and status == "сцена найдена" else None})
    return {"status": "ok", "file_count": len(entries), "video_files": len(video),
            "required_film_count": len(films), "matched_film_count": sum(m["status"] == "фильм найден" for m in matches.values()),
            "missing": [k for k, v in matches.items() if v["status"] != "фильм найден"], "items": items}


def main() -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    request = needed_requests(json.loads(REQUESTS.read_text(encoding="utf-8"))["items"], ROOT)
    ts = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    if not config.get("scan_enabled") or not config.get("url"):
        summary = {"status": "not_configured", "scanned_at": ts, "file_count": 0,
                   "video_files": 0, "required_film_count": len({r["film"] for r in request}),
                   "matched_film_count": 0, "missing": [], "items": [],
                   "message": "Папка ещё не задана. Старые 7 роликов повторно скачивать не нужно."}
    else:
        try:
            entries = list_folder_authenticated(config["url"])
            summary = summarize(entries, request)
            summary["scanned_at"] = ts
            summary["message"] = "Только поиск файлов. ASR/монтаж не запускались."
        except (ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
            summary = {"status": "error", "scanned_at": ts,
                       "message": str(exc)[:480], "items": []}
    SCAN.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Drive scan: {summary['status']} {summary.get('file_count', 0)} files; {summary.get('matched_film_count', 0)} matched")
    if summary["status"] == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
