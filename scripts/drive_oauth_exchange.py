#!/usr/bin/env python3
"""Secure Google Drive authorization-code exchange in GitHub Actions.

Consumes a *temporary* OAuth authorization code stored in GitHub Secrets,
exchanges it for a Drive refresh token, checks Drive folder ownership/write,
and seals the refresh token to the repository's Actions Secrets public key.
Only encrypted_value/key_id/nonce/status are written to GitHub; never a token.
"""
from __future__ import annotations
import base64
from datetime import datetime, timezone
from http.client import HTTPException
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.drive_oauth_config import DriveSetupError, google_oauth_preflight

OUT = Path("publishing/drive_oauth_exchange.json")
REDIRECT_URI = "https://developers.google.com/oauthplayground"


def exchange_code(env: dict[str, str]) -> dict:
    code = (env.get("GDRIVE_AUTH_CODE") or "").strip()
    nonce = env.get("AUTH_NONCE", "")
    public_key = env.get("AUTH_PUBLIC_KEY", "")
    key_id = env.get("AUTH_KEY_ID", "")
    expected_client = env.get("AUTH_CLIENT_ID", "")
    if not re.fullmatch(r"[0-9a-f]{32}", nonce):
        raise DriveSetupError("invalid_nonce", "Неверный идентификатор подключения.")
    if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", key_id):
        raise DriveSetupError("invalid_key_id", "Неверный идентификатор шифрования GitHub.")
    if not 16 <= len(code) <= 2000 or any(c in code for c in "\r\n\0"):
        raise DriveSetupError("missing_auth_code", "Нужен свежий одноразовый Authorization code от Google.")
    clients = [
        (env.get("YOUTUBE_OAUTH_CLIENT_ID"), env.get("YOUTUBE_OAUTH_CLIENT_SECRET")),
        (env.get("YT_CLIENT_ID"), env.get("YT_CLIENT_SECRET"))
    ]
    matched = next(((client, secret) for client, secret in clients
                    if client and secret and client == expected_client), None)
    if not matched:
        raise DriveSetupError("oauth_client_changed", "OAuth Client ID на сайте устарел. Обнови страницу.")
    client_id, client_secret = matched
    try:
        from nacl.public import PublicKey, SealedBox
        recipient = PublicKey(base64.b64decode(public_key, validate=True))
    except (ValueError, TypeError, ImportError) as exc:
        raise DriveSetupError("invalid_public_key", "Не удалось проверить открытый ключ GitHub.") from None
    payload = urlencode({
        "code": code, "client_id": client_id, "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI, "grant_type": "authorization_code"
    }).encode()
    try:
        req = Request("https://oauth2.googleapis.com/token", data=payload,
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      method="POST")
        with urlopen(req, timeout=30) as response:
            data = json.load(response)
    except HTTPError as exc:
        try:
            reason = json.loads(exc.read(2048)).get("error", "")
        except (ValueError, UnicodeDecodeError):
            reason = ""
        codes = {
            "invalid_grant": ("auth_code_invalid", "Код Google истёк, использован или выдан другому OAuth-клиенту. Начни вход заново."),
            "unauthorized_client": ("oauth_client_denied", "Google запретил авторизацию для существующего OAuth-клиента."),
            "invalid_client": ("invalid_client", "Существующий Google OAuth Client ID/Secret не принят Google."),
        }
        error, message = codes.get(reason, ("oauth_exchange_failed", "Google отказал в обмене кода (HTTP " + str(exc.code) + ")."))
        raise DriveSetupError(error, message) from None
    except (OSError, URLError, ValueError, HTTPException):
        raise DriveSetupError("oauth_network_error", "Google OAuth не ответил.") from None
    refresh = data.get("refresh_token", "")
    if not refresh:
        raise DriveSetupError("refresh_token_missing", "Google не выдал refresh token. Начни заново с подтверждением согласия.")
    # Actual check against Google's own Drive API BEFORE we store a long-lived credential.
    candidate = dict(env)
    candidate["YOUTUBE_OAUTH_CLIENT_ID"] = client_id
    candidate["YOUTUBE_OAUTH_CLIENT_SECRET"] = client_secret
    candidate["GDRIVE_REFRESH_TOKEN"] = refresh
    google_oauth_preflight(candidate)
    sealed = SealedBox(recipient).encrypt(refresh.encode("utf-8"))
    return {
        "status": "ready", "nonce": nonce, "key_id": key_id,
        "encrypted_value": base64.b64encode(sealed).decode("ascii"),
        "checked_at": datetime.now(timezone.utc).isoformat()
    }


def main() -> int:
    status = {"status": "error", "nonce": os.getenv("AUTH_NONCE", ""),
              "checked_at": datetime.now(timezone.utc).isoformat()}
    try:
        status = exchange_code(dict(os.environ))
        code = 0
    except DriveSetupError as exc:
        status["error_code"] = exc.code
        status["message"] = str(exc)
        code = 1
    except Exception:
        status["error_code"] = "unexpected_error"
        status["message"] = "Неожиданная ошибка при подключении Google."
        code = 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(status, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Google Drive code exchange:", status["status"], status.get("error_code", "encrypted_ready"))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
