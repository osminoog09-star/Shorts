#!/usr/bin/env python3
"""Private Denis voice reference transport for Claude's GitHub Actions TTS.

All reference/audio bytes remain in the owner's Google Drive or runner.temp;
public repository stores only file IDs and SHA256 fingerprints. Fail closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import secrets
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fetch_outro import refresh_access_token

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tools/voice/approved.json"
IDS = re.compile(r"[A-Za-z0-9_-]{10,}\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")
JOB_ID = re.compile(r"[a-z][a-z0-9_]{2,48}\Z")
FILES = {
    "reference_wav": ("reference_clean.wav", 256 * 1024, 15 * 1024 * 1024),
    "reference_text": ("ref_text.txt", 20, 64 * 1024),
    "params": ("params.json", 50, 64 * 1024),
}


class VoicePrivateError(RuntimeError):
    pass


def approved(path: Path = MANIFEST) -> dict:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise VoicePrivateError("NO-GO: tools/voice/approved.json недоступен") from exc
    if (obj.get("version") != "denis-qwen3tts-reference-v1"
            or obj.get("speaker") != "denis"
            or obj.get("voice_id") != "denis-qwen3tts-reference-v1"
            or obj.get("engine") != "qwen3-tts-local"
            or obj.get("no_fallback") is not True):
        raise VoicePrivateError("NO-GO: только private Denis reference, никакой чужой голос")
    for field in ("voice_folder_id", "voice_out_folder_id"):
        if not isinstance(obj.get(field), str) or not IDS.fullmatch(obj[field]):
            raise VoicePrivateError("BLOCKED: approved voice Drive folder ID отсутствует")
    for key, (filename, _, _) in FILES.items():
        a = obj.get("assets", {}).get(key, {})
        if (a.get("name") != filename
                or not isinstance(a.get("sha256"), str) or not HEX.fullmatch(a["sha256"])
                or not isinstance(a.get("drive_file_id"), str) or not IDS.fullmatch(a["drive_file_id"])):
            raise VoicePrivateError("NO-GO: approved voice reference metadata испорчены: " + key)
    return obj


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_refs(manifest: Path, dest: Path, env: dict, opener=urlopen) -> list[Path]:
    conf = approved(manifest)
    access = refresh_access_token(env, opener=opener)
    dest.mkdir(parents=True, mode=0o700, exist_ok=True)
    output = []
    with tempfile.TemporaryDirectory(prefix=".voice-stage-", dir=dest) as tmp:
        for key, (filename, minimum, limit) in FILES.items():
            meta = conf["assets"][key]
            url = "https://www.googleapis.com/drive/v3/files/" + meta["drive_file_id"] + "?alt=media"
            request = Request(url, headers={"Authorization": "Bearer " + access})
            path = Path(tmp) / filename
            h, total = hashlib.sha256(), 0
            try:
                with opener(request, timeout=65) as res, path.open("wb") as f:
                    while block := res.read(1024 * 1024):
                        total += len(block)
                        if total > limit:
                            raise VoicePrivateError("NO-GO: reference too large: " + key)
                        h.update(block)
                        f.write(block)
            except HTTPError as exc:
                raise VoicePrivateError(f"BLOCKED: private Drive reference {key} HTTP {exc.code}") from None
            except (URLError, OSError) as exc:
                raise VoicePrivateError("BLOCKED: private voice reference Drive network error") from exc
            if total < minimum or h.hexdigest() != meta["sha256"]:
                raise VoicePrivateError("NO-GO: SHA256 mismatch или неполный private Denis reference: " + key)
            path.chmod(0o600)
            output.append((key, path, dest / filename))
        for key, source, target in output:
            source.replace(target)
            print(f"VOICE PRIVATE FETCH PASS {key} (SHA256 verified, no reference content logged)")
    return [dest / FILES[k][0] for k in FILES]


def verify_refs(manifest: Path, dest: Path) -> None:
    conf = approved(manifest)
    for key, (filename, minimum, maximum) in FILES.items():
        path = dest / filename
        if not path.is_file() or not minimum <= path.stat().st_size <= maximum:
            raise VoicePrivateError("NO-GO: private Denis voice ref missing/invalid: " + key)
        with path.open("rb") as fp:
            h = hashlib.sha256()
            for b in iter(lambda: fp.read(1024 * 1024), b""):
                h.update(b)
        if h.hexdigest() != conf["assets"][key]["sha256"]:
            raise VoicePrivateError("NO-GO: SHA256 mismatch private voice ref: " + key)
        print(f"VOICE PRIVATE VERIFY PASS {key}")


def drive_json(method: str, url: str, access: str, payload: bytes, opener=urlopen) -> dict:
    req = Request(url, data=payload, method=method,
                  headers={"Authorization": "Bearer " + access,
                           "Content-Type": "application/json; charset=utf-8"})
    try:
        with opener(req, timeout=60) as res:
            return json.load(res)
    except HTTPError as exc:
        raise VoicePrivateError(f"BLOCKED: private Drive write HTTP {exc.code}; check owner Drive scope") from None
    except (URLError, ValueError, OSError) as exc:
        raise VoicePrivateError("BLOCKED: private Drive write network/response error") from exc


def make_folder(parent_id: str, name: str, access: str, opener=urlopen) -> str:
    url = "https://www.googleapis.com/drive/v3/files?fields=id,name,parents&supportsAllDrives=true"
    payload = json.dumps({"name": name, "mimeType": "application/vnd.google-apps.folder",
                          "parents": [parent_id]}).encode()
    result = drive_json("POST", url, access, payload, opener=opener)
    file_id = result.get("id", "")
    if not IDS.fullmatch(file_id) or result.get("name") != name:
        raise VoicePrivateError("NO-GO: Google Drive вернул неизвестную папку")
    return file_id


def upload_file(parent: str, path: Path, access: str, opener=urlopen) -> dict:
    if not path.is_file() or path.stat().st_size > 25 * 1024 * 1024:
        raise VoicePrivateError("NO-GO: некорректный TTS файл для private Drive")
    data = path.read_bytes()
    mime = ("audio/wav" if path.suffix == ".wav" else
            "audio/mpeg" if path.suffix == ".mp3" else "application/json")
    boundary = "m1lash" + secrets.token_hex(12)
    meta = json.dumps({"name": path.name, "parents": [parent]}, ensure_ascii=False).encode()
    body = (b"--" + boundary.encode() + b"\r\nContent-Type: application/json; charset=utf-8\r\n\r\n"
            + meta + b"\r\n--" + boundary.encode() + b"\r\nContent-Type: " + mime.encode()
            + b"\r\n\r\n" + data + b"\r\n--" + boundary.encode() + b"--\r\n")
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size,parents"
    req = Request(url, data=body, method="POST",
                  headers={"Authorization": "Bearer " + access,
                           "Content-Type": "multipart/related; boundary=" + boundary})
    try:
        with opener(req, timeout=100) as res:
            obj = json.load(res)
    except HTTPError as exc:
        raise VoicePrivateError(f"BLOCKED: private Drive WAV upload HTTP {exc.code}") from None
    except (URLError, ValueError, OSError) as exc:
        raise VoicePrivateError("BLOCKED: private Drive WAV upload failed") from exc
    if (not isinstance(obj.get("id"), str) or not IDS.fullmatch(obj["id"])
            or obj.get("name") != path.name):
        raise VoicePrivateError("NO-GO: Drive returned invalid uploaded file metadata")
    return {"name": path.name, "id": obj["id"], "sha256": sha_bytes(data), "size": len(data)}


def upload_result(manifest: Path, result_dir: Path, job_id: str, env: dict, opener=urlopen) -> dict:
    if not JOB_ID.fullmatch(job_id):
        raise VoicePrivateError("NO-GO: запрещённый voice job ID")
    conf = approved(manifest)
    src = result_dir / "manifest.json"
    if not src.is_file():
        raise VoicePrivateError("NO-GO: результат TTS без manifest.json")
    data = json.loads(src.read_text(encoding="utf-8"))
    if data.get("job_id") != job_id or data.get("voice_id") != conf["voice_id"]:
        raise VoicePrivateError("NO-GO: TTS manifest does not match verified job/voice ID")
    filelist = [src]
    for item in data.get("utterances", []):
        name = item.get("source_file", "")
        if (not isinstance(name, str) or not re.fullmatch(r"audio/[a-z][a-z0-9_]{1,48}\.wav", name)):
            raise VoicePrivateError("NO-GO: unsafe TTS WAV path")
        wav = result_dir / name
        if not wav.is_file() or sha_bytes(wav.read_bytes()) != item.get("sha256"):
            raise VoicePrivateError("NO-GO: output WAV missing or SHA mismatch")
        filelist.append(wav)
    access = refresh_access_token(env, opener=opener)
    folder_id = make_folder(conf["voice_out_folder_id"], job_id, access, opener=opener)
    receipt = {"job_id": job_id, "folder_id": folder_id,
               "folder_url": "https://drive.google.com/drive/folders/" + folder_id, "files": []}
    for file in filelist:
        info = upload_file(folder_id, file, access, opener=opener)
        receipt["files"].append({**info, "url": "https://drive.google.com/file/d/" + info["id"] + "/view"})
        print(f"VOICE PRIVATE UPLOAD PASS {file.name}: verified sha256 (no audio logged)")
    (result_dir / "drive_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2))
    return receipt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["fetch", "verify", "upload"])
    p.add_argument("--manifest", type=Path, default=MANIFEST)
    p.add_argument("--dest", type=Path, default=Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "m1lash-denis-ref")
    p.add_argument("--result-dir", type=Path)
    p.add_argument("--job-id")
    a = p.parse_args()
    try:
        if a.command == "fetch":
            fetch_refs(a.manifest, a.dest, dict(os.environ))
            verify_refs(a.manifest, a.dest)
        elif a.command == "verify":
            verify_refs(a.manifest, a.dest)
        else:
            if not a.result_dir or not a.job_id:
                raise VoicePrivateError("NO-GO: upload требует --result-dir и --job-id")
            upload_result(a.manifest, a.result_dir, a.job_id, dict(os.environ))
    except VoicePrivateError as exc:
        print("::error::" + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
