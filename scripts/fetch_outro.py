#!/usr/bin/env python3
"""Fetch the two OWNER-approved Denis v7 outros from private Google Drive.

Fail closed: no public URLs, no alternative voice, no old Dima asset. Only
GDRIVE_REFRESH_TOKEN and an existing OAuth client are used; never print secrets.
The local files are installed only AFTER BOTH SHA-256 checks succeed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
APPROVED = ROOT / "tools" / "outro" / "approved.json"
TARGETS = {
    "vertical": "media/outro/m1lash_outro_denis_v7_vertical.mp4",
    "horizontal": "media/outro/m1lash_outro_denis_v7_horizontal.mp4",
}
MAX_BYTES = 50 * 1024 * 1024
DRIVE_FILE_ID = re.compile(r"[A-Za-z0-9_-]{10,}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class OutroError(RuntimeError):
    """Redacted error safe to display in CI logs."""


def read_approved(path: Path) -> dict[str, dict[str, str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise OutroError("Невозможно прочитать tools/outro/approved.json") from exc
    if (data.get("version") != "denis-v7-voice10"
            or data.get("speaker") != "denis"
            or data.get("no_fallback_to_old_dima") is not True):
        raise OutroError("NO-GO: утверждение Denis v7 отсутствует или изменено; fallback запрещён")
    assets = data.get("assets")
    if not isinstance(assets, dict):
        raise OutroError("NO-GO: в approved.json отсутствуют assets")
    result = {}
    for label, safe_path in TARGETS.items():
        entry = assets.get(label)
        if not isinstance(entry, dict) or entry.get("path") != safe_path:
            raise OutroError(f"NO-GO: путь approved {label} не совпадает с ожидаемым Denis v7")
        expected, file_id = entry.get("sha256", ""), entry.get("drive_file_id", "")
        if not isinstance(expected, str) or not SHA256.fullmatch(expected):
            raise OutroError(f"NO-GO: некорректный SHA256 approved {label}")
        if not isinstance(file_id, str) or not DRIVE_FILE_ID.fullmatch(file_id):
            raise OutroError(f"BLOCKED: нет приватного Google Drive file ID для {label}")
        result[label] = {"path": safe_path, "sha256": expected, "drive_file_id": file_id}
    return result


def refresh_access_token(env: dict[str, str], opener=urlopen) -> str:
    refresh = env.get("GDRIVE_REFRESH_TOKEN", "").strip()
    if not refresh:
        raise OutroError("BLOCKED: отсутствует GitHub Secret GDRIVE_REFRESH_TOKEN")
    pairs = [
        (env.get("YOUTUBE_OAUTH_CLIENT_ID", ""), env.get("YOUTUBE_OAUTH_CLIENT_SECRET", "")),
        (env.get("YT_CLIENT_ID", ""), env.get("YT_CLIENT_SECRET", "")),
    ]
    pairs = [(a.strip(), b.strip()) for a, b in pairs if a and b]
    if not pairs:
        raise OutroError("BLOCKED: нет OAuth Client ID/Secret для Google Drive")
    for client_id, secret in dict.fromkeys(pairs):
        payload = urlencode({"client_id": client_id, "client_secret": secret,
                             "refresh_token": refresh, "grant_type": "refresh_token"}).encode()
        request = Request("https://oauth2.googleapis.com/token", data=payload,
                          headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        try:
            with opener(request, timeout=30) as res:
                response = json.load(res)
                token = response.get("access_token", "")
                if isinstance(token, str) and token:
                    return token
        except HTTPError as exc:
            if exc.code in (400, 401, 403):
                continue  # try a second existing client, no token or response body in logs
            raise OutroError(f"Google OAuth временно отказал: HTTP {exc.code}") from None
        except (URLError, OSError, ValueError, TypeError) as exc:
            raise OutroError("Не удалось получить access token Google Drive (сеть/ответ)") from exc
    raise OutroError("BLOCKED: Google отклонил Drive OAuth refresh token или выбранный Client ID/Secret")


def download_one(file_id: str, bearer: str, destination: Path, opener=urlopen) -> tuple[str, int]:
    url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&supportsAllDrives=true"
    request = Request(url, headers={"Authorization": "Bearer " + bearer})
    digest, size = hashlib.sha256(), 0
    try:
        with opener(request, timeout=60) as res, destination.open("wb") as out:
            while block := res.read(1024 * 1024):
                size += len(block)
                if size > MAX_BYTES:
                    raise OutroError("NO-GO: Drive asset больше защитного лимита 50MiB")
                digest.update(block)
                out.write(block)
    except HTTPError as exc:
        raise OutroError(f"BLOCKED: Google Drive download HTTP {exc.code}; проверить Drive OAuth scope и права") from None
    except (URLError, OSError) as exc:
        raise OutroError("BLOCKED: Google Drive media недоступно (сеть/доступ)") from exc
    if size < 1024:
        raise OutroError("NO-GO: Google Drive вернул пустую/неполную концовку")
    return digest.hexdigest(), size


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_existing(manifest: Path, root: Path) -> None:
    for label, asset in read_approved(manifest).items():
        file = root / asset["path"]
        if not file.is_file() or sha256_file(file) != asset["sha256"]:
            raise OutroError(f"NO-GO: {label} SHA256 не совпадает с approved.json; запрещена замена на старого Диму")
        print(f"VERIFY PASS {label}: {file.relative_to(root)} SHA256={asset['sha256']}")


def fetch_all(manifest: Path, root: Path, env: dict[str, str], opener=urlopen) -> None:
    assets = read_approved(manifest)
    token = refresh_access_token(env, opener=opener)
    target = root / "media" / "outro"
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    # Stage both files before touching approved paths. A failed/mismatched file
    # never installs a partial pair, and CI must stop nonzero before assembly.
    with tempfile.TemporaryDirectory(prefix=".denis-v7-stage-", dir=target) as tmp:
        stage = Path(tmp)
        checked = []
        for label, asset in assets.items():
            tmp_path = stage / (label + ".mp4")
            actual, count = download_one(asset["drive_file_id"], token, tmp_path, opener=opener)
            if actual != asset["sha256"]:
                raise OutroError(f"NO-GO: SHA256 несовпадение Google Drive {label}; запрещено использовать изменённую концовку")
            tmp_path.chmod(0o600)
            checked.append((label, tmp_path, root / asset["path"], count))
        for label, src, dst, count in checked:
            src.replace(dst)
            print(f"FETCH PASS {label}: {dst.relative_to(root)} {count} bytes; approved SHA256 verified")
    verify_existing(manifest, root)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=APPROVED)
    p.add_argument("--root", type=Path, default=ROOT)
    p.add_argument("--verify-only", action="store_true", help="offline check of both already downloaded files")
    args = p.parse_args(argv)
    try:
        if args.verify_only:
            verify_existing(args.manifest, args.root)
        else:
            fetch_all(args.manifest, args.root, dict(os.environ))
    except OutroError as exc:
        print("::error::" + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
