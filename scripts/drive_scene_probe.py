#!/usr/bin/env python3
"""ASR preflight for ONE public Drive movie, grouped requests; never publishes.

Creates only approximate timing candidates. Russian soundtrack and real scene
must still pass human visual/audio QA before any private Short assembly.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "publishing/drive_scan.json"
REQUESTS = ROOT / "publishing/clip_requests.json"
STATE = ROOT / "publishing/scene_candidates.json"


def hint_range(s):
    # M1lash source briefs use HH:MM, e.g. 00:28 is minute 28.
    times = re.findall(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", s or "")
    values = [int(h) * 3600 + int(m) * 60 for h, m in times if int(m) < 60]
    if len(values) >= 2:
        return min(values[:2]), max(values[:2])
    if values:
        return max(0, values[0] - 180), values[0] + 180
    return 0, 300


def drive_id(url):
    u = urlparse(url)
    if u.scheme != "https" or u.hostname != "drive.google.com" or u.username or u.password:
        raise ValueError("Not a Google Drive file URL")
    ids = parse_qs(u.query).get("id", []) if u.path == "/uc" else []
    if not ids:
        match = re.fullmatch(r"/file/d/([A-Za-z0-9_-]{10,})/view/?", u.path)
        if match and not u.query:
            ids = [match.group(1)]
    if len(ids) != 1 or not re.fullmatch(r"[A-Za-z0-9_-]{10,}", ids[0]):
        raise ValueError("Invalid Google Drive ID")
    return ids[0]


def fetch_private_film(url, dest, credentials=None):
    """Download only the selected private Drive file. Never log bearer tokens."""
    from drive_oauth_config import resolve_existing_client, DriveSetupError
    token_env = dict(credentials if credentials is not None else os.environ)
    if not token_env.get("GDRIVE_REFRESH_TOKEN"):
        raise RuntimeError("Нужен уже подключённый Google Drive OAuth в GitHub Secrets.")
    try:
        verified, _ = resolve_existing_client(token_env)
    except DriveSetupError as exc:
        raise RuntimeError("Google Drive OAuth отказал: " + exc.code) from None
    token = verified.get("_GDRIVE_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("Google OAuth не выдал токен для чтения фильма.")
    file_id = drive_id(url)
    request = Request(
        "https://www.googleapis.com/drive/v3/files/" + file_id + "?alt=media&supportsAllDrives=true",
        headers={"Authorization":"Bearer " + token})
    max_size = 6_500_000_000
    written = 0
    try:
        with urlopen(request, timeout=120) as response, open(dest, "wb") as out:
            length = response.headers.get("Content-Length")
            if length and int(length) > max_size:
                raise RuntimeError("Фильм превышает лимит 6,5 ГБ на временном runner.")
            while True:
                chunk = response.read(8 * 1024 * 1024)
                if not chunk:
                    break
                written += len(chunk)
                if written > max_size:
                    raise RuntimeError("Фильм превышает лимит 6,5 ГБ.")
                out.write(chunk)
    except HTTPError as exc:
        raise RuntimeError("Google Drive не дал прочитать файл (HTTP " + str(exc.code) + ").") from None
    except (OSError, URLError, ValueError):
        raise RuntimeError("Не получилось временно скачать файл из закрытого Drive.") from None
    if written < 1_000_000:
        raise RuntimeError("Файл слишком мал для киноисходника.")
    return written


def cmd(*args, timeout=120):
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    if p.returncode:
        raise RuntimeError("Command failed: " + str(args[0]) + " " + p.stderr[-400:])
    return p.stdout


def pending():
    scan = json.loads(SCAN.read_text(encoding="utf-8"))
    reqs = {x["id"]: x for x in json.loads(REQUESTS.read_text(encoding="utf-8"))["items"]}
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"items": {}}
    if scan.get("status") != "ok":
        return [], state
    groups = {}
    for row in scan.get("items", []):
        rid = row.get("id")
        if row.get("status") != "фильм найден" or not row.get("file_url") or rid not in reqs:
            continue
        previous = state.get("items", {}).get(rid, {})
        if previous.get("file_url") == row["file_url"] and previous.get("status") in ("candidate", "error"):
            continue
        groups.setdefault(row["file_url"], []).append(reqs[rid])
    return list(groups.items()), state


def analyze(url, reqs, directory):
    from faster_whisper import WhisperModel

    film = directory / "movie.bin"
    fetch_private_film(url, film)
    if not 1_000_000 <= film.stat().st_size <= 6_500_000_000:
        raise ValueError("Movie size outside temp runner safety bounds")
    duration = float(cmd("ffprobe", "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=nw=1:nk=1", str(film)).strip())
    if duration < 60 or duration > 18000:
        raise ValueError("Invalid film duration")
    model = WhisperModel("small", device="cpu", compute_type="int8")
    langs = []
    for i, fraction in enumerate((0.2, 0.5, 0.8)):
        wav = directory / ("lang_" + str(i) + ".wav")
        cmd("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss",
            str(max(0, duration * fraction - 20)), "-t", "40", "-i", str(film),
            "-vn", "-ac", "1", "-ar", "16000", str(wav), timeout=120)
        _, info = model.transcribe(str(wav), beam_size=1, vad_filter=True)
        langs.append({"language": info.language, "probability": round(info.language_probability, 2)})
        wav.unlink(missing_ok=True)
    if sum(x["language"] == "ru" and x["probability"] >= 0.55 for x in langs) < 2:
        raise ValueError("Russian dub not verified in 2/3 sampled audio windows")
    segments, _ = model.transcribe(str(film), language="ru", beam_size=1,
                                    vad_filter=True, condition_on_previous_text=False)
    transcript = [{"start": s.start, "end": s.end, "text": s.text} for s in segments]
    sha = hashlib.sha256()
    with open(film, "rb") as f:
        for piece in iter(lambda: f.read(8 * 1024 * 1024), b""):
            sha.update(piece)
    # Transcript cache remains in ephemeral Actions workspace ONLY, never commit.
    (directory / ("asr_" + sha.hexdigest()[:16] + ".json")).write_text(
        json.dumps(transcript, ensure_ascii=False), encoding="utf-8")
    items = {}
    for req in reqs:
        start, end = hint_range(req.get("minute", ""))
        start, end = max(0, start), min(duration, end)
        # Approximate audio-based candidate; never prove the on-screen action.
        scored = []
        for i in range(12):
            center = start + (i + 0.5) * max(1, end - start) / 12
            a, b = max(0, center - 22), min(duration, center + 22)
            speech = sum(max(0, min(b, seg["end"]) - max(a, seg["start"])) for seg in transcript)
            score = (44 - speech if "тишин" in req.get("scene", "").lower() else speech)
            scored.append({"start": round(a, 1), "end": round(b, 1),
                           "speech_seconds": round(speech, 1), "score": round(score, 2)})
        candidates = sorted(scored, key=lambda r: -r["score"])[:3]
        items[req["id"]] = {"status": "candidate", "film": req.get("film"),
                            "file_url": url, "file_sha256": sha.hexdigest(),
                            "language_samples": langs, "candidates": candidates,
                            "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                            "note": "Only approximate ASR candidate: VISUAL/AUDIO QA needed; NOT scene_found"}
    film.unlink(missing_ok=True)
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list-pending", action="store_true")
    args = ap.parse_args()
    groups, state = pending()
    if args.list_pending:
        print(json.dumps({"pending": len(groups), "ids": [r["id"] for _, reqs in groups for r in reqs]}))
        return
    if not groups:
        print("No new movie to probe")
        return
    url, reqs = groups[0]  # one film / all requests about it
    with tempfile.TemporaryDirectory(dir=os.environ.get("RUNNER_TEMP") or None) as temp:
        try:
            new = analyze(url, reqs, Path(temp))
            state.setdefault("items", {}).update(new)
        except Exception as exc:
            for r in reqs:
                state.setdefault("items", {})[r["id"]] = {
                    "status": "error", "film": r.get("film"), "file_url": url,
                    "error": str(exc)[:400], "checked_at": dt.datetime.now(dt.timezone.utc).isoformat()
                }
            state["updated"] = dt.datetime.now(dt.timezone.utc).isoformat()
            STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            raise
    state["updated"] = dt.datetime.now(dt.timezone.utc).isoformat()
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Audio candidates written for", [r["id"] for r in reqs])


if __name__ == "__main__":
    main()
