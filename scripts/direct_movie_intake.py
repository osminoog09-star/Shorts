#!/usr/bin/env python3
"""Server-only intake of rights-cleared, directly downloadable MP4 features.

Allowed public origins only. No player extraction, CAPTCHA/DRM handling, cookies,
authorization headers, proxies, or uploads to the repository. The owner must
have the right to download/reuse the supplied source.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import ipaddress
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
from urllib.parse import unquote, urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

from hdrezka_intake import IntakeError, upload_to_drive, verify_video

STATUS = Path("publishing/direct_movie_status.json")
MAX_BYTES = 6_500_000_000
ALLOWED_HOSTS = {"archive.org", "download.blender.org", "github.com", "release-assets.githubusercontent.com"}
QUALITY = {"720p": 720, "1080p": 1080}


def safe_source(url: str) -> str:
    if not isinstance(url, str) or not 16 <= len(url) <= 800:
        raise IntakeError("invalid_url", "Нужна прямая HTTPS-ссылка на MP4.")
    try:
        parsed = urlsplit(url.strip())
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        raise IntakeError("invalid_url", "Некорректная ссылка.") from None
    if (parsed.scheme != "https" or parsed.username or parsed.password
            or parsed.query or parsed.fragment or port not in (None, 443)
            or (host not in ALLOWED_HOSTS and not host.endswith(".archive.org"))
            or not unquote(parsed.path).lower().endswith(".mp4")):
        raise IntakeError("source_not_supported",
                          "Только прямые публичные MP4 с Archive.org, Blender или GitHub Releases. Страницы плееров и защищённые потоки не поддерживаются.")
    return url.strip()


def check_public_dns(url: str) -> None:
    host = urlsplit(url).hostname or ""
    try:
        addrs = socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        if not addrs:
            raise ValueError("no addresses")
        for address in addrs:
            ip = ipaddress.ip_address(address[4][0])
            if not ip.is_global:
                raise ValueError("non-public destination")
    except (OSError, ValueError):
        raise IntakeError("source_network_denied",
                          "Источник не имеет доступного публичного адреса.") from None


class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # The library follows no redirects beyond our same public-origin allowlist.
        safe_source(newurl)
        check_public_dns(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def open_movie(url: str, inspect_only: bool = False):
    safe_source(url)
    check_public_dns(url)
    req = Request(url, headers={
        "User-Agent": "M1lashStudio/1.0 (+private licensed media transfer)",
        **({"Range": "bytes=0-4095"} if inspect_only else {}),
    })
    return build_opener(RestrictedRedirect()).open(req, timeout=70)


def require_mp4_header(chunk: bytes) -> None:
    if len(chunk) < 12 or chunk[4:8] != b"ftyp":
        raise IntakeError("not_mp4", "По ссылке пришёл не MP4-файл (возможно HTML, реклама или защита).")


def safe_name(url: str) -> str:
    tail = unquote(urlsplit(url).path.split("/")[-1])
    name = re.sub(r"[^a-zA-Z0-9_-]", "-", tail[:-4])[:68].strip("-") or "movie"
    return name + "_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".mp4"


def transfer(url: str, output_dir: Path, max_bytes: int = MAX_BYTES) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    dest = output_dir / safe_name(url)
    size = 0
    try:
        with open_movie(url) as response, dest.open("wb") as out:
            announced = response.headers.get("Content-Length")
            if announced and int(announced) > max_bytes:
                raise IntakeError("file_too_large", "Исходник превышает лимит временной обработки 6,5 ГБ.")
            first = response.read(65536)
            require_mp4_header(first)
            out.write(first)
            size = len(first)
            while True:
                data = response.read(2 * 1024 * 1024)
                if not data:
                    break
                size += len(data)
                if size > max_bytes:
                    raise IntakeError("file_too_large", "Файл превышает лимит 6,5 ГБ.")
                out.write(data)
    except IntakeError:
        dest.unlink(missing_ok=True)
        raise
    except (OSError, ValueError, TimeoutError):
        dest.unlink(missing_ok=True)
        raise IntakeError("direct_download_failed",
                          "Не удалось скачать публичный MP4 на сервере.") from None
    if size < 20 * 1024 * 1024:
        dest.unlink(missing_ok=True)
        raise IntakeError("not_full_movie", "Файл слишком мал для полного фильма.")
    return dest


def confirm_drive_file(dest: Path, config: str) -> None:
    try:
        result = subprocess.run(
            ["rclone", "--config", config, "lsjson", "m1lash:" + dest.name, "--files-only"],
            capture_output=True, text=True, timeout=120, check=False
        )
        if result.returncode:
            raise ValueError("rclone failed")
        listing = json.loads(result.stdout)
        if (not isinstance(listing, list) or
                not any(x.get("Name") == dest.name and x.get("Size") == dest.stat().st_size
                        for x in listing if isinstance(x, dict))):
            raise ValueError("remote size mismatch")
    except (OSError, ValueError, TypeError, subprocess.TimeoutExpired):
        raise IntakeError("drive_verify_failed",
                          "Отправка завершилась, но размер MP4 в Google Drive подтвердить не удалось.") from None


def job(url: str, mode: str, quality: str, folder: str, config: str, output_dir: Path) -> dict:
    url = safe_source(url)
    if quality not in QUALITY:
        raise IntakeError("invalid_quality", "Нужно выбрать 720p или 1080p.")
    if mode not in ("inspect", "download"):
        raise IntakeError("invalid_mode", "Неизвестный режим.")
    if mode == "inspect":
        try:
            with open_movie(url, inspect_only=True) as response:
                require_mp4_header(response.read(4096))
                size = response.headers.get("Content-Length")
                # Range responses may show only the range length: never report
                # a verified full size, resolution, soundtrack or duration here.
                return {"reachable": True, "note": "MP4 отвечает; качество и длительность проверятся после загрузки."}
        except IntakeError:
            raise
        except (OSError, ValueError, TimeoutError):
            raise IntakeError("source_unavailable", "Сервер не смог открыть прямой MP4.") from None
    if not config or not Path(config).is_file():
        raise IntakeError("drive_not_connected", "Google Drive OAuth не настроен.")
    dest = transfer(url, output_dir)
    try:
        info = verify_video(dest, QUALITY[quality])
        upload_to_drive(dest, folder, config)
        confirm_drive_file(dest, config)
        return {**info, "drive_uploaded": True}
    finally:
        dest.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=os.environ.get("DIRECT_MOVIE_URL", ""))
    parser.add_argument("--mode", choices=["inspect", "download"], default=os.environ.get("DIRECT_MOVIE_MODE", "inspect"))
    parser.add_argument("--quality", choices=["720p", "1080p"], default=os.environ.get("DIRECT_MOVIE_QUALITY", "1080p"))
    parser.add_argument("--folder-id", default=os.environ.get("GDRIVE_FOLDER_ID", ""))
    parser.add_argument("--config-file", default=os.environ.get("GDRIVE_RCLONE_CONFIG_PATH", ""))
    parser.add_argument("--output-dir", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "m1lash_direct")
    parser.add_argument("--status", type=Path, default=STATUS)
    args = parser.parse_args()
    status = {"checked_at": datetime.now(timezone.utc).isoformat(), "mode": args.mode,
              "status": "error", "drive_uploaded": False}
    try:
        status.update(job(args.url, args.mode, args.quality, args.folder_id,
                          args.config_file, args.output_dir))
        status["status"] = "ok"
        result_code = 0
    except IntakeError as err:
        status.update(error_code=err.code, message=str(err))
        result_code = 1
    except Exception:
        status.update(error_code="unexpected_error", message="Серверная ошибка импорта.")
        result_code = 1
    args.status.parent.mkdir(parents=True, exist_ok=True)
    args.status.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Direct movie intake:", status["status"], status.get("error_code", args.mode))
    return result_code


if __name__ == "__main__":
    sys.exit(main())
