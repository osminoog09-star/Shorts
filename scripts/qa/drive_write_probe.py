#!/usr/bin/env python3
"""Write/read/delete a tiny private test object in Drive root, NEVER movie folder.

Uses the exact OAuth secrets from GitHub Actions. Does not output tokens,
file IDs, object names, HTTP bodies, or owner account identifiers.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.drive_oauth_config import resolve_existing_client, DriveSetupError

ROOT_API = "https://www.googleapis.com/drive/v3/files"
BINARY_API = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id%2Csize"
BODY = b"M1lash-private-Drive-write-probe"


def run() -> int:
    try:
        creds, _ = resolve_existing_client(dict(os.environ))
        token = creds["_GDRIVE_ACCESS_TOKEN"]
    except (KeyError, DriveSetupError) as err:
        print("drive_write_probe: OAuth unavailable", getattr(err, "code", "missing"))
        return 1
    auth = {"Authorization": "Bearer " + token}
    boundary = "m1lash_source_probe_2026"
    name = "m1lash-temporary-writecheck-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + ".txt"
    metadata = json.dumps({"name": name, "mimeType": "text/plain", "parents":["root"]}).encode("utf-8")
    data = (b"--" + boundary.encode() + b"\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
            + metadata + b"\r\n--" + boundary.encode()
            + b"\r\nContent-Type: text/plain\r\n\r\n" + BODY
            + b"\r\n--" + boundary.encode() + b"--\r\n")
    file_id = None
    cleanup_ok = False
    result_ok = False
    try:
        req = Request(BINARY_API, method="POST", data=data,
                      headers={**auth, "Content-Type": "multipart/related; boundary=" + boundary})
        with urlopen(req, timeout=50) as resp:
            meta = json.load(resp)
        file_id = meta.get("id")
        if not isinstance(file_id, str) or not file_id:
            raise ValueError("upload no ID")
        check = Request(ROOT_API + "/" + file_id + "?fields=id%2Csize", headers=auth)
        with urlopen(check, timeout=30) as resp:
            remote = json.load(resp)
        result_ok = remote.get("id") == file_id and int(remote.get("size", -1)) == len(BODY)
    except (OSError, ValueError, TypeError, URLError, HTTPError):
        result_ok = False
    finally:
        if file_id:
            try:
                deletion = Request(ROOT_API + "/" + file_id, method="DELETE", headers=auth)
                with urlopen(deletion, timeout=40) as response:
                    cleanup_ok = response.status in (200, 204)
            except (OSError, URLError, HTTPError):
                cleanup_ok = False
    if result_ok and cleanup_ok:
        print("drive_write_probe: create/read/exact-size/delete OK; movie folder unchanged")
        return 0
    print("drive_write_probe: verification_or_cleanup_failed; uploaded=", bool(file_id),
          " cleanup_ok=", cleanup_ok)
    return 1


if __name__ == "__main__":
    sys.exit(run())
