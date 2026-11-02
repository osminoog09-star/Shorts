#!/usr/bin/env python3
"""M1lash private movie intake via a third-party HDRezka CLI.

Only handles explicitly requested HTTPS film-page URLs, no DRM/CAPTCHA bypass.
Never writes a movie, source URL, credentials or actor dialogue to git.
Result JSON contains only status/quality, safe for a PUBLIC repository.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit

ALLOWED_HOSTS = {"rezka.ag", "hdrezka.ag"}
QUALITY = {"720p": 720, "1080p": 1080}
DEFAULT_STATUS = Path("publishing/hdrezka_status.json")


class IntakeError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def validate_source(value: str) -> str:
    if not 16 <= len(value) <= 600:
        raise IntakeError("invalid_url", "Нужна ссылка на страницу фильма.")
    try:
        u = urlsplit(value)
        host = (u.hostname or "").lower()
        port = u.port
    except ValueError as exc:
        raise IntakeError("invalid_url", "Недопустимый URL.") from exc
    if (
        u.scheme != "https"
        or host not in ALLOWED_HOSTS
        or u.username or u.password
        or port not in (None, 443)
        or not re.fullmatch(r"/(?:films|series|cartoons|animation|anime)/[A-Za-z0-9_/-]+\.html/?", u.path)
        or u.query or u.fragment
    ):
        raise IntakeError("invalid_url", "Допускаются только HTTPS-страницы фильмов rezka.ag/hdrezka.ag.")
    return value


def parse_qualities(info: str) -> dict[str, str]:
    """Only return ordinary vs premium options; no stream URLs."""
    found: dict[str, str] = {}
    for line in info.splitlines():
        m = re.match(r"^\s{2,}(720p|1080p)(?:\s+Ultra)?\b(?::|\s|$)", line, re.I)
        if m:
            quality = m.group(1).lower()
            status = "premium" if "(premium)" in line.lower() else "available"
            if quality not in found or status == "available":
                found[quality] = status
    return found


def run_process(argv: list[str], timeout: int) -> str:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, errors="replace", timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise IntakeError("source_unavailable", "Источник не ответил или загрузчик недоступен.") from exc
    if p.returncode != 0:
        raise IntakeError("source_unavailable", "Плеер не открылся из GitHub Actions (возможно, блокировка запросов).")
    return p.stdout + "\n" + p.stderr


def inspect(url: str, translation: str) -> dict[str, str]:
    cmd = ["hdrezka-dl", "--no-antibot-solver", "--info"]
    if translation:
        cmd.extend(["--translation", translation])
    cmd.append(url)
    qualities = parse_qualities(run_process(cmd, 240))
    if not qualities:
        raise IntakeError("source_unavailable", "Не удалось определить доступные качества.")
    return qualities


def verify_video(path: Path, expected_height: int) -> dict[str, int]:
    if not path.is_file() or path.stat().st_size < 20 * 1024 * 1024:
        raise IntakeError("download_failed", "Фильм не был скачан полностью или получен короткий фрагмент.")
    raw = run_process(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)],
        60,
    )
    try:
        data = json.loads(raw)
        stream = data["streams"][0]
        height = int(stream["height"])
        width = int(stream["width"])
        duration = float(data["format"]["duration"])
    except (ValueError, IndexError, KeyError, TypeError) as exc:
        raise IntakeError("invalid_video", "Полученный файл не прошёл проверку видео.") from exc
    if height < expected_height or width < int(expected_height * 1.2):
        raise IntakeError("low_resolution", "Полученный файл ниже запрошенного разрешения.")
    if duration < 20 * 60:
        raise IntakeError("short_video", "Вместо полного фильма получен короткий фрагмент.")
    return {"height": height, "width": width, "duration_minutes": round(duration / 60)}


def safe_output_name(url: str, quality: str) -> str:
    tail = urlsplit(url).path.split("/")[-1].removesuffix(".html")
    tail = re.sub(r"[^a-zA-Z0-9_-]", "-", tail)[:70].strip("-")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{tail or 'film'}_{quality}_{ts}.mp4"


def upload_to_drive(source: Path, folder_id: str, config_file: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9_-]{12,100}", folder_id):
        raise IntakeError("drive_not_connected", "Не указана проверенная папка Drive.")
    if not config_file or not Path(config_file).is_file():
        raise IntakeError("drive_not_connected", "Требуется секрет GDRIVE_RCLONE_CONFIG.")
    env = os.environ.copy()
    env["RCLONE_CONFIG_M1LASH_ROOT_FOLDER_ID"] = folder_id
    try:
        p = subprocess.run(
            ["rclone", "--config", config_file, "copyto", str(source), "m1lash:" + source.name,
             "--no-traverse", "--retries", "2"],
            env=env, capture_output=True, text=True, timeout=3600, check=False
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise IntakeError("drive_failed", "Загрузка в Google Drive не завершилась.") from exc
    if p.returncode:
        raise IntakeError("drive_failed", "Google Drive не принял файл; проверь OAuth и свободное место.")


def job(url: str, quality: str, mode: str, translation: str, folder: str, config_file: str, output_dir: Path) -> dict:
    validate_source(url)
    if quality not in QUALITY:
        raise IntakeError("invalid_quality", "Допустимые варианты: 720p и 1080p.")
    if len(translation) > 80 or "\n" in translation or "\r" in translation:
        raise IntakeError("invalid_translation", "Слишком длинное название озвучки.")
    options = inspect(url, translation)
    result: dict = {"available": options}
    if mode == "inspect":
        return result
    if mode != "download":
        raise IntakeError("invalid_mode", "Неизвестный режим.")
    if options.get(quality) != "available":
        raise IntakeError("quality_unavailable", "Выбранное качество отсутствует или доступно только в Premium.")
    if not config_file or not Path(config_file).exists():
        raise IntakeError("drive_not_connected", "Google Drive OAuth пока не подключён к GitHub.")
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / safe_output_name(url, quality)
    cmd = ["hdrezka-dl", "--no-antibot-solver", "--quality", quality]
    if translation:
        cmd.extend(["--translation", translation])
    cmd.extend([url, str(dest)])
    run_process(cmd, 5400)
    result.update(verify_video(dest, QUALITY[quality]))
    upload_to_drive(dest, folder, config_file)
    result["drive_uploaded"] = True
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("MOVIE_URL", ""))
    parser.add_argument("--quality", choices=sorted(QUALITY), default=os.environ.get("MOVIE_QUALITY", "1080p"))
    parser.add_argument("--mode", choices=["inspect", "download"], default=os.environ.get("MOVIE_MODE", "inspect"))
    parser.add_argument("--translation", default=os.environ.get("MOVIE_TRANSLATION", ""))
    parser.add_argument("--folder-id", default=os.environ.get("GDRIVE_FOLDER_ID", ""))
    parser.add_argument("--config-file", default=os.environ.get("GDRIVE_RCLONE_CONFIG_PATH", ""))
    parser.add_argument("--output-dir", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "m1lash_media")
    parser.add_argument("--status", type=Path, default=DEFAULT_STATUS)
    args = parser.parse_args()
    result = {"checked_at": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
              "requested_quality": args.quality, "status": "error", "drive_uploaded": False}
    code = 0
    try:
        result.update(job(args.url, args.quality, args.mode, args.translation,
                          args.folder_id, args.config_file, args.output_dir))
        result["status"] = "ok"
    except IntakeError as exc:
        result["error_code"] = exc.code
        result["message"] = str(exc)
        code = 1
    except Exception:
        result["error_code"] = "unexpected_error"
        result["message"] = "Неожиданная ошибка загрузчика. Проверь Actions."
        code = 1
    args.status.parent.mkdir(parents=True, exist_ok=True)
    args.status.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Media intake: {result['status']} ({result.get('error_code', args.mode)})")
    return code


if __name__ == "__main__":
    sys.exit(main())
