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
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
    client_id = safe_line(env.get("YOUTUBE_OAUTH_CLIENT_ID") or env.get("YT_CLIENT_ID", ""), "client_id")
    client_secret = safe_line(env.get("YOUTUBE_OAUTH_CLIENT_SECRET") or env.get("YT_CLIENT_SECRET", ""), "client_secret")
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



def google_oauth_preflight(env: dict[str, str]) -> None:
    """Find the exact failing step without logging or publishing credential material."""
    client = safe_line(env.get("YOUTUBE_OAUTH_CLIENT_ID") or env.get("YT_CLIENT_ID", ""), "client_id")
    secret = safe_line(env.get("YOUTUBE_OAUTH_CLIENT_SECRET") or env.get("YT_CLIENT_SECRET", ""), "client_secret")
    refresh = safe_line(env.get("GDRIVE_REFRESH_TOKEN", ""), "refresh_token")
    payload = urlencode({"client_id": client, "client_secret": secret,
                         "refresh_token": refresh, "grant_type": "refresh_token"}).encode()
    try:
        request = Request("https://oauth2.googleapis.com/token", data=payload, method="POST",
                          headers={"Content-Type": "application/x-www-form-urlencoded"})
        with urlopen(request, timeout=30) as response:
            token = json.load(response).get("access_token")
    except HTTPError as exc:
        # Never serialize HTTP response content, URLs with tokens, or credentials.
        reason = ""
        try:
            reason = json.loads(exc.read(4096)).get("error", "")
        except (ValueError, UnicodeDecodeError):
            pass
        codes = {"invalid_grant": ("refresh_token_rejected", "Google отклонил Drive refresh token (invalid_grant). Нужен новый токен с тем же OAuth-клиентом."),
                 "invalid_client": ("oauth_client_mismatch", "OAuth-клиент не соответствует Drive refresh token. Используй свои OAuth Client ID/Secret."),
                 "unauthorized_client": ("oauth_client_denied", "Google не разрешил этому OAuth-клиенту доступ."),
                 "invalid_scope": ("drive_scope_invalid", "Google отклонил запрошенный Drive scope.")}
        code, message = codes.get(reason, ("oauth_refresh_http_error", f"Не удалось обновить Drive OAuth (HTTP {exc.code})."))
        raise DriveSetupError(code, message) from None
    except (OSError, URLError, ValueError, KeyError, TypeError):
        raise DriveSetupError("oauth_network_error", "Не удалось связаться с Google OAuth для проверки токена.") from None
    if not token:
        raise DriveSetupError("oauth_no_access_token", "Google не выдал access token для Drive.")

    try:
        scope_request = Request("https://oauth2.googleapis.com/tokeninfo?" + urlencode({"access_token": token}))
        with urlopen(scope_request, timeout=30) as response:
            scope_info = json.load(response)
        grants = set(str(scope_info.get("scope", "")).split())
        if not grants.intersection({"https://www.googleapis.com/auth/drive",
                                    "https://www.googleapis.com/auth/drive.file"}):
            raise DriveSetupError("drive_scope_missing", "Токен действителен, но разрешения Google Drive в нём нет.")
        file_request = Request(
            "https://www.googleapis.com/drive/v3/files/" + FOLDER +
            "?fields=id%2CmimeType%2Ccapabilities%28canAddChildren%29&supportsAllDrives=true",
            headers={"Authorization": "Bearer " + token})
        with urlopen(file_request, timeout=30) as response:
            folder = json.load(response)
    except DriveSetupError:
        raise
    except HTTPError as exc:
        codes = {403: ("drive_api_denied", "Google Drive API запретил доступ (HTTP 403): проверь включение Drive API и права аккаунта."),
                 404: ("drive_folder_not_found", "Google Drive не видит выбранную папку (HTTP 404): проверь аккаунт и доступ."),
                 401: ("drive_access_token_denied", "Google Drive отклонил access token (HTTP 401).")}
        code, message = codes.get(exc.code, ("drive_api_http_error", f"Drive API ответил HTTP {exc.code}."))
        raise DriveSetupError(code, message) from None
    except (OSError, URLError, ValueError, KeyError, TypeError):
        raise DriveSetupError("drive_api_network_error", "Не удалось проверить папку через Google Drive API.") from None
    if folder.get("id") != FOLDER or folder.get("mimeType") != "application/vnd.google-apps.folder":
        raise DriveSetupError("drive_folder_invalid", "Google Drive вернул не ту папку.")
    if folder.get("capabilities", {}).get("canAddChildren") is False:
        raise DriveSetupError("drive_folder_read_only", "У аккаунта нет права добавлять файлы в выбранную папку.")


def resolve_existing_client(env: dict[str, str]) -> tuple[dict[str, str], str]:
    """Try existing OAuth client pairs without logging or returning secret material."""
    candidates = [
        ("youtube", env.get("YOUTUBE_OAUTH_CLIENT_ID", ""),
         env.get("YOUTUBE_OAUTH_CLIENT_SECRET", "")),
        ("legacy", env.get("YT_CLIENT_ID", ""), env.get("YT_CLIENT_SECRET", "")),
    ]
    seen: set[tuple[str, str]] = set()
    errors: list[DriveSetupError] = []
    for name, client_id, client_secret in candidates:
        if not client_id or not client_secret or (client_id, client_secret) in seen:
            continue
        seen.add((client_id, client_secret))
        proposed = dict(env)
        proposed["YOUTUBE_OAUTH_CLIENT_ID"] = client_id
        proposed["YOUTUBE_OAUTH_CLIENT_SECRET"] = client_secret
        try:
            google_oauth_preflight(proposed)
            return proposed, name
        except DriveSetupError as exc:
            errors.append(exc)
    if errors:
        if len(errors) == 1:
            raise errors[0]
        codes = ",".join(error.code for error in errors)
        raise DriveSetupError("all_oauth_clients_denied",
                              "Оба сохранённых OAuth-клиента не подошли к Drive-токену (" + codes + ").")
    raise DriveSetupError("missing_credentials", "Нет сохранённых OAuth Client ID/Secret для Google Drive.")


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
        selected_env = dict(os.environ)
        selected_client = "legacy_rclone_config"
        if args.check and not selected_env.get("GDRIVE_RCLONE_CONFIG", "").strip():
            selected_env, selected_client = resolve_existing_client(selected_env)
        save_config(selected_env, args.config)
        if args.check:
            check_access(args.config)
        status.update({
            "oauth_client_source": selected_client if args.check else None,
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
