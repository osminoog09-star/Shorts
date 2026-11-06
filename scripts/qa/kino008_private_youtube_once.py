#!/usr/bin/env python3
"""KINO008 private owner-review upload, exactly once; never schedule or reupload.

Source remains in owner-private Drive; Git stores SHA, metadata and YouTube ID
only. Reservation receipt is PUSHED before POST to avoid duplicates on failure.
"""
from __future__ import annotations
import hashlib,json,os,re,subprocess,sys,tempfile
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen
import requests

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from youtube_direct import API,RU_ID,token_for,verify_channel,youtube_upload
from fetch_outro import refresh_access_token
REPORT=ROOT/"reports/research/2026-11-06_KINO_008_FINAL_V1_PRIVATE_QA.json"
RECEIPT=ROOT/"publishing/receipts/kino_008.json"
MANIFEST=ROOT/"publishing/queue/kino_008.json"
INDEX=ROOT/"publishing/queue.json"
META={
 "type":"short",
 "title":"Они нажали кнопку — и даже ЗВУК исчез… 😨 #shorts",
 "description":"Обратный отсчёт закончился. Но самая страшная часть началась потом.\nТы угадал фильм до последней секунды? Напиши, когда понял!\n\nSong: Laeko - DONT WANNA KNOW!!!\nMusic provided by NoCopyrightSounds\nFree Download/Stream: http://ncs.io/dontwannaknow\nWatch: https://ncs.lnk.to/dontwannaknowAT/youtube\n\n#shorts #кино #угадайфильм #фильмы #эпичнаясцена #сценаизфильма #m1lash",
 "tags":["кино","угадай фильм","эпичная сцена","обратный отсчёт","сильная сцена","кинозагадка","movie short","russian dub","shorts","m1lash"],
 "category_id":"1","made_for_kids":False,"contains_synthetic_media":True,
 "default_language":"ru","default_audio_language":"ru"
}
def now():return datetime.now(timezone.utc).isoformat()
def write(p,o):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def push(files,message):
 subprocess.run(["git","config","user.name","kino008-private[bot]"],cwd=ROOT,check=True)
 subprocess.run(["git","config","user.email","kino008-private@users.noreply.github.com"],cwd=ROOT,check=True)
 subprocess.run(["git","add",*[str(p.relative_to(ROOT)) for p in files]],cwd=ROOT,check=True)
 if subprocess.run(["git","diff","--cached","--quiet"],cwd=ROOT).returncode==0:return
 subprocess.run(["git","commit","-m",message],cwd=ROOT,check=True)
 subprocess.run(["git","pull","--rebase","origin","main"],cwd=ROOT,check=True)
 subprocess.run(["git","push","origin","HEAD:main"],cwd=ROOT,check=True)
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()
def get_movie(report,dest,token):
 id=report["private_final_drive_file_id"];size=int(report["final_size_bytes"])
 if not re.fullmatch("[A-Za-z0-9_-]{10,}",id) or not 1000000<size<150000000:
  raise RuntimeError("invalid private Drive ID/size")
 base="https://www.googleapis.com/drive/v3/files/"+id
 with urlopen(Request(base+"?fields=id,size,mimeType,parents",
                      headers={"Authorization":"Bearer "+token}),timeout=45) as r:
  m=json.load(r)
 if m.get("id")!=id or int(m.get("size",-1))!=size or m.get("mimeType")!="video/mp4":
  raise RuntimeError("private final metadata mismatch")
 count=0
 with urlopen(Request(base+"?alt=media",headers={"Authorization":"Bearer "+token}),
              timeout=240) as r,dest.open("wb") as f:
  while True:
   b=r.read(4*1024*1024)
   if not b:break
   count+=len(b)
   if count>size:raise RuntimeError("private final oversize")
   f.write(b)
 if count!=size or sha(dest)!=report["final_sha256"]:
  dest.unlink(missing_ok=True)
  raise RuntimeError("final private movie byte/hash mismatch")
def main():
 if RECEIPT.exists() or MANIFEST.exists():
  raise RuntimeError("NO-GO: previous kino008 receipt/manifest; NEVER retry automatically")
 report=json.loads(REPORT.read_text(encoding="utf8"))
 if (report.get("status")!="ready_for_private_youtube_review_upload" or
     report.get("official_check_result")!="returncode_0_official_check" or
     report.get("manual_contact_review")!="GPT_VISUAL_PASS_FINAL_CONTACT" or
     report.get("youtube_upload") is not False or
     not re.fullmatch("[0-9a-f]{64}",report.get("final_sha256",""))):
  raise RuntimeError("NO-GO: approved FINAL video QA/readback not present")
 index=json.loads(INDEX.read_text(encoding="utf8"))
 row=next((x for x in index["items"] if x.get("id")=="kino_008"),None)
 if row is None or row.get("status")!="draft" or row.get("youtube_id") or row.get("slot"):
  raise RuntimeError("NO-GO: queue not in clean preupload draft state")
 with tempfile.TemporaryDirectory(prefix="kino008-once-") as t:
  file=Path(t)/"kino_008.mp4"
  access=refresh_access_token(dict(os.environ))
  get_movie(report,file,access)
  youtube_token=token_for("ru")
  verify_channel(youtube_token,RU_ID)
  info={"channel":"ru","source":{"sha256":report["final_sha256"]},
        "metadata":META,"publish_at":None}
  receipt={"status":"reserved","id":"kino_008","action":"one_time_private_only",
           "expected_sha256":report["final_sha256"],
           "size_bytes":report["final_size_bytes"],
           "reserved_at":now(),"never_retry_automatically":True,"publish_at":None}
  write(RECEIPT,receipt)
  push([RECEIPT],"youtube(kino008): reserve no-retry PRIVATE upload before YouTube POST")
  print("KINO008_PRIVATE_UPLOAD_RESERVED",flush=True)
  video_id=youtube_upload(file,info,None,youtube_token)
 receipt.update(status="uploaded",video_id=video_id,uploaded_at=now(),
                youtube_url="https://www.youtube.com/watch?v="+video_id)
 write(RECEIPT,receipt)
 write(MANIFEST,{"channel":"ru",
   "source":{"type":"uploaded","video_id":video_id,"sha256":report["final_sha256"]},
   "metadata":META,"publish_at":None,
   "provenance":{"qa_report":str(REPORT.relative_to(ROOT)),
                 "owner_review":"PRIVATE_ONLY_PUBLISH_DATE_NOT_APPROVED"}})
 row.update(status="review",youtube_id=video_id,slot=None,
            review_version="KINO008_V2_BODY_DENIS_V7_QA_PASS",
            private_review_url="https://studio.youtube.com/video/"+video_id+"/edit",
            note="Owner chooses date via M1lash Studio. Private verified YouTube ID. NO automated publication.")
 write(INDEX,index)
 push([RECEIPT,MANIFEST,INDEX],"youtube(kino008): record PRIVATE video and owner Studio review WITHOUT date")
 print("KINO008_PRIVATE_ID_SAVED",video_id,flush=True)
 resp=requests.get(API+"/videos",params={"part":"status","id":video_id},
                   headers={"Authorization":"Bearer "+youtube_token},timeout=45)
 resp.raise_for_status()
 items=resp.json().get("items",[])
 status=items[0].get("status",{}) if len(items)==1 and items[0].get("id")==video_id else {}
 if status.get("privacyStatus")!="private" or status.get("publishAt"):
  raise RuntimeError("NO-GO: video is not PRIVATE or has a date")
 print("KINO008_YOUTUBE_PRIVATE_GET_PASS",video_id,"NO_PUBLISH_DATE",flush=True)
if __name__=="__main__":
 try:main()
 except Exception as e:
  print("KINO008_NO_GO",type(e).__name__,str(e)[:240],file=sys.stderr)
  raise SystemExit(2)
