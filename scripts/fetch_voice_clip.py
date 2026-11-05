#!/usr/bin/env python3
"""Fetch only a signed/ASR-gated Denis voice WAV from owner-private voice_out.

The Drive folder and sibling manifest must prove speaker/voice_id and WAV SHA.
No public share links, no Dima/other speaker, no embedding/reference downloads.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fetch_outro import refresh_access_token
from voice_private_io import approved

RID=re.compile(r"[A-Za-z0-9_-]{10,}\Z")
HEX=re.compile(r"[0-9a-f]{64}\Z")
BASE="https://www.googleapis.com/drive/v3"
LIMIT=25*1024*1024
class VoiceClipError(RuntimeError):pass

def fetch_json(url: str, token: str, opener=urlopen) -> dict:
    try:
        with opener(Request(url,headers={"Authorization":"Bearer "+token}),timeout=35) as r:
            obj=json.load(r)
    except HTTPError as e:
        raise VoiceClipError(f"BLOCKED: Google Drive voice metadata HTTP {e.code}") from None
    except (URLError,ValueError,OSError) as e:
        raise VoiceClipError("BLOCKED: Google Drive voice metadata inaccessible") from e
    if not isinstance(obj,dict):raise VoiceClipError("NO-GO: Google Drive malformed metadata")
    return obj

def download_clip(file_id: str, expected_sha: str, target: Path, env: dict, opener=urlopen) -> None:
    if not RID.fullmatch(file_id) or not HEX.fullmatch(expected_sha):
        raise VoiceClipError("NO-GO: voice Drive file ID / SHA256 must be explicit")
    conf=approved()
    token=refresh_access_token(env,opener=opener)
    info=fetch_json(f"{BASE}/files/{file_id}?fields=id,name,mimeType,parents,size",token,opener)
    if info.get("id")!=file_id or info.get("mimeType") not in ("audio/x-wav","audio/wav","audio/wave","application/octet-stream"):
        raise VoiceClipError("NO-GO: only private WAV file is permitted")
    parents=info.get("parents",[])
    if not isinstance(parents,list) or len(parents)!=1 or not RID.fullmatch(parents[0]):
        raise VoiceClipError("NO-GO: voice WAV lacks an owner-private job folder")
    parent=parents[0]
    meta=fetch_json(f"{BASE}/files/{parent}?fields=id,name,mimeType,parents",token,opener)
    if (meta.get("id")!=parent or meta.get("mimeType")!="application/vnd.google-apps.folder"
            or conf["voice_out_folder_id"] not in meta.get("parents",[])):
        raise VoiceClipError("NO-GO: audio is outside M1lash/_studio/voice_out/<job_id>/")
    # Only use WAV backed by one of our Qwen3-TTS generated manifests with ASR evidence.
    q=urlencode({"q":f"'{parent}' in parents and name = 'manifest.json' and trashed = false",
                 "fields":"files(id,name,mimeType),nextPageToken","pageSize":"10"})
    listings=fetch_json(f"{BASE}/files?{q}",token,opener)
    manifests=listings.get("files",[])
    if len(manifests)!=1 or not RID.fullmatch(manifests[0].get("id","")):
        raise VoiceClipError("NO-GO: private voice_out folder does not have a unique manifest")
    manifest=fetch_json(f"{BASE}/files/{manifests[0]['id']}?alt=media",token,opener)
    if manifest.get("speaker")!="denis" or manifest.get("voice_id")!=conf["voice_id"] or manifest.get("engine")!="qwen3-tts-local":
        raise VoiceClipError("NO-GO: voice manifest is not verified Denis Qwen3")
    matched=[row for row in manifest.get("utterances",[])
             if row.get("source_file")=="audio/"+info.get("name","")
             and row.get("sha256")==expected_sha and row.get("asr_similarity",0)>=0.80]
    if len(matched)!=1:
        raise VoiceClipError("NO-GO: WAV does not match a verified Denis utterance/ASR manifest")
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix=".denis-title-stage-",delete=False) as f:
        partial=Path(f.name)
        h,total=hashlib.sha256(),0
        try:
            req=Request(f"{BASE}/files/{file_id}?alt=media",headers={"Authorization":"Bearer "+token})
            with opener(req,timeout=75) as response:
                while block:=response.read(1024*1024):
                    total+=len(block)
                    if total>LIMIT:raise VoiceClipError("NO-GO: voice WAV too big")
                    h.update(block);f.write(block)
        except HTTPError as e:
            raise VoiceClipError(f"BLOCKED: Drive WAV HTTP {e.code}") from None
        except (URLError,OSError) as e:
            raise VoiceClipError("BLOCKED: failed to download private voice WAV") from e
    try:
        if total<8000 or h.hexdigest()!=expected_sha:
            raise VoiceClipError("NO-GO: SHA256 mismatch on private generated Denis WAV")
        p=subprocess.run(["ffprobe","-v","error","-show_entries","stream=codec_type,codec_name:format=duration",
                          "-of","json",str(partial)],capture_output=True,text=True,timeout=30)
        if p.returncode:
            raise VoiceClipError("NO-GO: downloaded voice is not decodable")
        data=json.loads(p.stdout)
        streams=data.get("streams",[])
        dur=float(data.get("format",{}).get("duration",0))
        if len(streams)!=1 or streams[0].get("codec_type")!="audio" or not 0.5<=dur<=45:
            raise VoiceClipError("NO-GO: unexpected voice audio streams/duration")
        partial.replace(target)
        print(f"VOICE CLIP VERIFIED: {info['name']} sha256={expected_sha} (Denis, ASR manifest, private Drive)")
    finally:partial.unlink(missing_ok=True)

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--file-id",required=True)
    p.add_argument("--sha256",required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    try:
        temp=Path(os.environ.get("RUNNER_TEMP","/tmp")).resolve()
        if not str(a.out.resolve()).startswith(str(temp)+os.sep):
            raise VoiceClipError("NO-GO: private voice must stay under RUNNER_TEMP")
        download_clip(a.file_id,a.sha256,a.out,dict(os.environ))
    except VoiceClipError as e:
        print("::error::"+str(e),file=sys.stderr)
        return 1
    return 0
if __name__=="__main__":
    raise SystemExit(main())
