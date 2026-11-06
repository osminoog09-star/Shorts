#!/usr/bin/env python3
"""One-time, owner-approved scheduling of EXISTING kino_007 V9c PRIVATE video.

Never uploads or reuploads media. Only edits the privacy/scheduled-release
status of the specific YouTube video previously verified by GitHub Actions.
Designed to run exactly once after owner said 'Ок все' on 2026-11-06.
"""
from __future__ import annotations
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.youtube_direct import API, RU_ID, event_time, token_for, verify_channel

VIDEO_ID = "3YjkmOrxDLA"
EXPECTED_SHA = "0b5fd6b576797877c0a8fcb729304eb9b6830cbf45c6c51a646fa04502b12bb6"
SLOT = "2026-11-06T10:00:00+02:00"
REQUEST_ID = "owner-ok-20261106-kino_007-1000"
RECEIPT = ROOT / "publishing/receipts/kino_007.json"
MANIFEST = ROOT / "publishing/queue/kino_007.json"
INDEX = ROOT / "publishing/queue.json"
SCHEDULE_REQUESTS = ROOT / "publishing/schedule_requests.json"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def record(paths, message):
    subprocess.run(["git","config","user.name","m1lash-kino007-scheduler[bot]"],cwd=ROOT,check=True)
    subprocess.run(["git","config","user.email","kino007-scheduler@users.noreply.github.com"],cwd=ROOT,check=True)
    subprocess.run(["git","add",*[str(p.relative_to(ROOT)) for p in paths]],cwd=ROOT,check=True)
    subprocess.run(["git","commit","-m",message],cwd=ROOT,check=True)
    subprocess.run(["git","pull","--rebase","origin","main"],cwd=ROOT,check=True)
    subprocess.run(["git","push","origin","HEAD:main"],cwd=ROOT,check=True)

def readback(token):
    response = requests.get(API+"/videos",params={"part":"status,snippet","id":VIDEO_ID},
                            headers={"Authorization":"Bearer "+token,"Cache-Control":"no-cache"},timeout=50)
    response.raise_for_status()
    items=response.json().get("items",[])
    if len(items)!=1 or items[0].get("id")!=VIDEO_ID:
        raise RuntimeError("NO-GO: existing YouTube video id not found")
    item=items[0]
    if item.get("snippet",{}).get("channelId")!=RU_ID:
        raise RuntimeError("NO-GO: video not in M1lash RU channel")
    return item["status"]

def preflight():
    manifest = read(MANIFEST)
    receipt = read(RECEIPT)
    index = read(INDEX)
    requests_data = read(SCHEDULE_REQUESTS)
    src = manifest.get("source",{})
    if (manifest.get("channel")!="ru" or src.get("type")!="uploaded"
            or src.get("video_id")!=VIDEO_ID or src.get("sha256")!=EXPECTED_SHA):
        raise RuntimeError("NO-GO: scheduled source differs from owner-reviewed Batman V9c")
    if manifest.get("publish_at")!=SLOT or manifest.get("schedule_request",{}).get("id")!=REQUEST_ID:
        raise RuntimeError("NO-GO: schedule date/request mismatch")
    if (receipt.get("status")!="uploaded" or receipt.get("video_id")!=VIDEO_ID
            or receipt.get("sha256")!=EXPECTED_SHA or receipt.get("source_sha256")!=EXPECTED_SHA
            or receipt.get("channel")!="ru" or receipt.get("publish_at")):
        raise RuntimeError("NO-GO: duplicate or mismatched receipt")
    if (receipt.get("owner_approval",{}).get("message")!="Ок все"
            or receipt["owner_approval"].get("studio_slot")!=SLOT):
        raise RuntimeError("NO-GO: owner approval absent")
    row = next((x for x in index["items"] if x.get("id")=="kino_007"),None)
    if (not row or row.get("status")!="review" or row.get("youtube_id")!=VIDEO_ID
            or row.get("slot") is not None):
        raise RuntimeError("NO-GO: Studio queue entry is no longer PRIVATE review")
    if any(x.get("slot")==SLOT and x.get("id")!="kino_007" for x in index["items"]):
        raise RuntimeError("NO-GO: studio schedule slot collision")
    for k,v in (requests_data.get("requests") or {}).items():
        if k=="kino_007" or v.get("at")==SLOT:
            raise RuntimeError("NO-GO: schedule request already reserved")
    target=event_time(SLOT)
    if target <= dt.datetime.now(dt.timezone.utc)+dt.timedelta(minutes=45):
        raise RuntimeError("NO-GO: selected time is now too near")
    token=token_for("ru")
    verify_channel(token,RU_ID)
    status=readback(token)
    if status.get("privacyStatus")!="private" or status.get("publishAt"):
        raise RuntimeError("NO-GO: video already public/scheduled; do not send another update")
    if status.get("uploadStatus") in ("failed","rejected","deleted"):
        raise RuntimeError("NO-GO: video rejected or unavailable")
    print("KINO007_PREFLIGHT_PASS",VIDEO_ID,"still PRIVATE, no previous schedule",flush=True)
    return token, target, index, requests_data

def main():
    token,target,index,requests_data = preflight()
    # Existing shared uploader: validate queue, update only status of uploaded
    # video, verify YouTube videos.list GET on success, persist receipt locally.
    subprocess.run([sys.executable,"scripts/youtube_direct.py","schedule",
                    "--manifest","publishing/queue/kino_007.json",
                    "--expected-publish-at",SLOT,
                    "--expected-request-id",REQUEST_ID],cwd=ROOT,check=True)
    verified = readback(token)
    expected_utc=target.isoformat().replace("+00:00","Z")
    actual=verified.get("publishAt")
    if (verified.get("privacyStatus")!="private" or not actual or
        dt.datetime.fromisoformat(actual.replace('Z','+00:00')).astimezone(dt.timezone.utc)!=target):
        raise RuntimeError("NO-GO: YouTube GET after schedule mismatches approved date")
    print("KINO007_YOUTUBE_SCHEDULE_GET_PASS",VIDEO_ID,actual,flush=True)
    receipt=read(RECEIPT)
    if receipt.get("status")!="scheduled" or receipt.get("publish_at_utc")!=expected_utc:
        raise RuntimeError("NO-GO: shared scheduler receipt mismatch")
    receipt["publish_at"]=SLOT
    receipt["owner_approval_message"]="Ок все"
    save(RECEIPT,receipt)
    row=next(x for x in index["items"] if x.get("id")=="kino_007")
    row.update(status="scheduled",slot=SLOT,review_version="V9c_YOUTUBE_SCHEDULED",
               youtube_id=VIDEO_ID,youtube_url="https://youtu.be/"+VIDEO_ID,
               note="OWNER OK 06.11; YouTube GET verified PRIVATE scheduled for 2026-11-06 10:00 Tallinn. Exact V9c binary, no reupload. Content ID not independently cleared; rights risk acknowledged.")
    save(INDEX,index)
    requests_data.setdefault("requests",{})["kino_007"]={
        "at":SLOT,"kind":"short","title":row["title"],"video_id":VIDEO_ID,
        "request_id":REQUEST_ID,"requested_at":"2026-11-06T00:51:56Z",
        "origin":"owner_chat_ok_20261106","confirmed_by":"youtube_videos_list_GET"
    }
    save(SCHEDULE_REQUESTS,requests_data)
    record([RECEIPT,INDEX,SCHEDULE_REQUESTS],
           "youtube(kino007): confirm owner-approved Batman V9c 06 Nov 10:00 Tallinn schedule by YouTube GET")
    print("KINO007_SCHEDULED_CONFIRMED",VIDEO_ID,SLOT,flush=True)

if __name__=="__main__":
    try: main()
    except Exception as exc:
        print("KINO007_SCHEDULE_STOP:",type(exc).__name__,str(exc)[:200],file=sys.stderr)
        raise SystemExit(2)
