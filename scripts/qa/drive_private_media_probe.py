#!/usr/bin/env python3
"""Read-only Drive API media probe using the existing owner OAuth.

Reads at most 1024 bytes from one existing video file; no names, IDs, URLs,
credentials or file contents are printed/stored. Does not alter Drive or Git.
"""
import json
import os
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from scripts.drive_folder_intake import list_folder_authenticated
from scripts.drive_scene_probe import drive_id
from scripts.drive_oauth_config import resolve_existing_client, DriveSetupError

FOLDER_CONFIG = Path("publishing/drive_folder.json")


def main():
    folder = json.loads(FOLDER_CONFIG.read_text(encoding="utf-8"))["url"]
    entries = list_folder_authenticated(folder)
    video = next((e for e in entries if Path(e["path"]).suffix.lower() == ".mp4"), None)
    if not video:
        print("private_media_probe: no existing MP4 to test; not verified")
        return 1
    try:
        creds, _ = resolve_existing_client(dict(os.environ))
        token = creds["_GDRIVE_ACCESS_TOKEN"]
        req = Request(
            "https://www.googleapis.com/drive/v3/files/" + drive_id(video["url"]) +
            "?alt=media&supportsAllDrives=true",
            headers={"Authorization": "Bearer " + token, "Range": "bytes=0-1023"})
        with urlopen(req, timeout=60) as response:
            data = response.read(1024)
            status = response.status
    except DriveSetupError as exc:
        print("private_media_probe: oauth error", exc.code)
        return 1
    except HTTPError as exc:
        print("private_media_probe: API rejected read HTTP", exc.code)
        return 1
    except (OSError, URLError, KeyError, ValueError):
        print("private_media_probe: network or metadata error")
        return 1
    if not data or status not in (200,206):
        print("private_media_probe: unexpected response")
        return 1
    print("private_media_probe: private authenticated media READ OK; max_bytes=1024; no upload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
