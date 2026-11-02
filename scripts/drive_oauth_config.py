#!/usr/bin/env python3
"""Create a private rclone Drive remote from a Google OAuth refresh token.

Never print tokens, client secret, or the generated config.
Legacy GDRIVE_RCLONE_CONFIG is supported. A shared Drive folder URL is NOT OAuth.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess

FOLDER = "1ANvcXlUj0wBv1CG5U0bBQGdH-32OyaAi"
STATUS = Path("publishing/drive_auth_status.json")


class DriveSetupError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def safe_line(value: str, field: str) -> str:
    if not value or len(value) > 4096 or any(ch in value for ch in "\r\n\x00"):
        raise DriveSetupError("missing_credentials", "Не настроены корректные OAuth-данные для Google Drive.")
    if field == "client_id" and not value.endswith(".apps.googleusercontent.com"):
        raise DriveSetupError("invalid_client", "Google OAuth Client ID имеет неверный формат.")
    return value


def make_config(env: dict[str, str]) -> str:
    legacy = env.get("GDRIVE_RCLONE_CONFIG", "").strip()
    if legacy:
        if not re.search(r"(?m)^\[m1lash\]\s*$", legacy):
            raise DriveSetupError("bad_config", "В конфигурации rclone нет раздела [m1lash].")
        return legacy + "\n"
    refresh = safe_line(env.get("GDRIVE_REFRESH_TOKEN", ""), "refresh_token")
    client_id = safe_line(env.get("YOUTUBE_OAUTH_CLIENT_ID", ""), "client_id")
    client_secret = safe_line(env.get("YOUTUBE_OAUTH_CLIENT_SECRET", ""), "client_secret")
    token = json.dumps({
        "access_token": "",
        "token_type": "Bearer",
        "refresh_token": refresh,
        "expiry": "2000-01-01T00:00:00Z",
    }, separators=(",", ":"))
    return (
        "[m1lash]\n"
        "type = drive\n"
        f"client_id = {client_id}\n"
        f"client_secret = {client_secret}\n"
        "scope = drive\n"
        f"root_folder_id = {FOLDER}\n"
        f"token = {token}\n"
    )


def save_config(env: dict[str, str], path: Path) -> None:
    contents = make_config(env)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as out:
        out.write(contents)
    path.chmod(0o600)


def check_access(path: Path) -> None:
    try:
        result = subprocess.run(
            ["rclone", "--config", str(path), "lsf", "m1lash:", "--max-depth", "1",
             "--contimeout", "15s", "--timeout", "45s", "--retries", "1"],
            capture_output=True, text=True, timeout=90, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DriveSetupError("drive_check_failed", "Не удалось подключиться к Google Drive.") from exc
    if result.returncode:
        raise DriveSetupError("oauth_or_folder_denied", "Google отклонил OAuth или доступ к папке. Проверь Drive API, scope и Google-аккаунт.")


def write_status(status: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--status", type=Path, default=STATUS)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    status = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "status": "error", "connected": False,
    }
    try:
        save_config(os.environ, args.config)
        if args.check:
            check_access(args.config)
        status.update({
            "status": "ok", "connected": True if args.check else False,
            "message": "Google Drive подключён" if args.check else "OAuth-конфигурация создана",
        })
        code = 0
    except DriveSetupError as err:
        status.update(error_code=err.code, message=str(err))
        code = 1
    except Exception:
        status.update(error_code="unexpected_error", message="Не удалось проверить Google Drive.")
        code = 1
    write_status(status, args.status)
    print("Drive setup:", status["status"], status.get("error_code", "ok"))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
