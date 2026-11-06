#!/usr/bin/env python3
"""Compose and run strict full QA for Kino008; save final MOVIE only in owner-private Drive.
No YouTube upload in this stage, no film/speaker WAV bytes in public Git.
"""
from __future__ import annotations
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime,timezone
from pathlib import Path
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
sys.path.insert(0,str(ROOT/"scripts"/"qa"))
from fetch_outro import refresh_access_token
from kino008_body_render import private_upload_small,private_upload_mp4

BODY_ID="1uhX70_jxQkj-3L7IxKWkd9YaG30AfR8n"
BODY_SHA="1b57063ee69df5f57662478b73a494b7a0cef6b2f86b885fe0d512066b6d0def"
BODY_SIZE=23932719
VOICE=[
 ("prefix","1zp0U0aafppatW7LlRiQWGGjL2iGOt9A1",
  "d5cca0b08718311b712a2545c241596c5f86c5b1399ab6f8d25d7fa7020e231e",69164),
 ("name","1si_sUTncpojiYOPccGpc_py1NTfOVCR_",
  "4febf29941426fb34c51e639a1d6459611205feb652e9d9730d806790dadd2b8",88364),
]
REPORT=ROOT/"reports/research/2026-11-06_KINO_008_FINAL_V1_PRIVATE_QA.json"
PUBLIC={
    "title":"Они нажали кнопку — и даже ЗВУК исчез… 😨 #shorts",
    "description":(
       "Обратный отсчёт закончился. Но самая страшная часть началась потом.\n"
       "Ты угадал фильм до последней секунды? Напиши, когда понял!\n\n"
       "Song: Laeko - DONT WANNA KNOW!!!\n"
       "Music provided by NoCopyrightSounds\n"
       "Free Download/Stream: http://ncs.io/dontwannaknow\n"
       "Watch: https://ncs.lnk.to/dontwannaknowAT/youtube\n\n"
       "#shorts #кино #угадайфильм #фильмы #эпичнаясцена #сценаизфильма #m1lash"),
    "tags":["кино","угадай фильм","эпичная сцена","обратный отсчёт","сильная сцена",
            "кинозагадка","movie short","russian dub","shorts","m1lash"],
    "hashtags":["#shorts","#кино","#угадайфильм","#фильмы"],
    "pinned_comment":"На какой секунде понял, что произойдёт, и узнал фильм до финала?",
    "thumbnail_text":"И ТУТ ОНИ НАЖАЛИ...",
    "public_filename":"m1lash_movie_mystery_008_ru.mp4",
    "captions":["ОНИ НАЖАЛИ КНОПКУ","ДО ДЕТОНАЦИИ","А ПОТОМ..."],
    "chapters":[],
    "end_card_text":"Подпишись! Спасибо за лайк!"
}

def cmd(*args,timeout=500):
    p=subprocess.run([str(a) for a in args],text=True,stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,timeout=timeout)
    if p.returncode:
        raise RuntimeError("Command "+str(args[0])+" failed "+p.stderr[-1100:])
    return p.stdout,p.stderr

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def fetch_exact(file_id,expected_sha,expected_size,path,token):
    assert re.fullmatch(r"[A-Za-z0-9_-]{10,}",file_id)
    url="https://www.googleapis.com/drive/v3/files/"+file_id
    meta_req=Request(url+"?fields=id,size,mimeType,parents",headers={"Authorization":"Bearer "+token})
    with urlopen(meta_req,timeout=60) as res:meta=json.load(res)
    if meta.get("id")!=file_id or int(meta.get("size",-1))!=expected_size:
        raise RuntimeError("PRIVATE DRIVE FILE SIZE/ID MISMATCH")
    if "video/" not in meta.get("mimeType","") and "audio/" not in meta.get("mimeType",""):
        raise RuntimeError("PRIVATE DRIVE UNSUPPORTED MIME")
    req=Request(url+"?alt=media",headers={"Authorization":"Bearer "+token})
    total=0;hash_obj=hashlib.sha256()
    with urlopen(req,timeout=250) as res,path.open("wb") as dest:
        while True:
            b=res.read(4*1024*1024)
            if not b:break
            total+=len(b)
            if total>expected_size:raise RuntimeError("PRIVATE DRIVE oversize")
            hash_obj.update(b);dest.write(b)
    if total!=expected_size or hash_obj.hexdigest()!=expected_sha:
        path.unlink(missing_ok=True)
        raise RuntimeError("PRIVATE DRIVE SHA256 MISMATCH")
    return {"id":file_id,"bytes":total,"sha256":expected_sha}

def make_title(folder):
    import wave
    pcm=[]
    for name,_,_,_ in VOICE:
        with wave.open(str(folder/(name+".wav")),"rb") as w:
            if (w.getframerate(),w.getnchannels(),w.getsampwidth())!=(24000,1,2):
                raise RuntimeError("DENIS VOICE unexpected WAV format")
            pcm.append(w.readframes(w.getnframes()))
    out=folder/"title_denis.wav"
    with wave.open(str(out),"wb") as w:
        w.setframerate(24000);w.setnchannels(1);w.setsampwidth(2)
        w.writeframes(pcm[0] + b"\x00"*(24000*2//8) + pcm[1])
    return out

def write_release_json(directory):
    d={
      "internal":{"project_id":"kino_008","film_title":"Оппенгеймер",
                  "film_title_aliases":["Oppenheimer","Оппенгеймер (2023)"],
                  "film_rights_verified":False},
      "public":PUBLIC,
      "outro":{"cta_voice_id":"denis-qwen3tts-reference-v1",
               "last_title_voice_id":"denis-qwen3tts-reference-v1",
               "cta_text":"Подпишись, и спасибо всем, кто досмотрел и поставил лайк.",
               "spoken_lines":["Подпишись, и спасибо всем, кто досмотрел и поставил лайк.",
                               "Это был фильм.","Оппенгеймер"],
               "title_visible_on_screen":False,"lip_sync_verified":False},
      "video":{"width":1080,"height":1920,"full_bleed":True,
               "dialogue_language":"ru","music_license_verified":False,
               "music_ducking":True,"visual_qa_done":False,
               "audio_qa_done":False},
      "publication":{"publish_ready":False}}
    p=directory/"mystery_release.json"
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return p

def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    status={"status":"error","started_at":datetime.now(timezone.utc).isoformat(),
            "film":"Оппенгеймер (2023)","project":"kino_008",
            "body_sha256":BODY_SHA,"voice_v2_run_id":42147263572,
            "youtube_upload":False,"privacy":"owner_private_Drive",
            "public_publication":False}
    try:
      with tempfile.TemporaryDirectory(prefix="m1lash-kino008-final-",dir=os.getenv("RUNNER_TEMP") or None) as temporary:
        directory=Path(temporary)
        auth=refresh_access_token(dict(os.environ))
        body=directory/"body_v2.mp4"
        fetch_exact(BODY_ID,BODY_SHA,BODY_SIZE,body,auth)
        for name,id,sha,n in VOICE:
            fetch_exact(id,sha,n,directory/(name+".wav"),auth)
        title=make_title(directory)
        title_secs=float(cmd("ffprobe","-v","error","-show_entries","format=duration",
                           "-of","csv=p=0",title)[0].strip())
        assert 2.0<title_secs<7.0, "DENIS title duration unexpected"
        release=write_release_json(directory)
        cmd("python3",ROOT/"tools/movie_edit/validate_mystery.py",release,timeout=40)
        # Original approved outro is sha-verified by tools/assemble_with_outro.py;
        # fetched by caller CI beforehand, not stored in public repository.
        output=directory/"M1lash_KINO008_TRINITY_FINAL_PRIVATE_V1.mp4"
        cmd("python3",ROOT/"tools/assemble_with_outro.py",
            body,"-o",output,"--title",title,"--preset","fast","--crf","18",
            "--body-lufs","-15.0","--max-seconds","59",timeout=2000)
        _,decode_errors=cmd("ffmpeg","-hide_banner","-v","error","-xerror",
                            "-i",output,"-f","null","-",timeout=700)
        if decode_errors.strip():raise RuntimeError("FINAL FULL DECODE noisy errors")
        check_out,check_err=cmd("python3",ROOT/"skills/ext/ffmpeg-skill/scripts/check.py",output,
                     "--platform","shorts","--content",timeout=1500)
        # Official checker returns nonzero on failures (cmd already enforces it).
        contact=directory/"M1lash_KINO008_FINAL_CONTACT_20_PRIVATE.png"
        cmd("python3",ROOT/"skills/ext/ffmpeg-skill/scripts/look.py",output,
            "--safe","shorts","--tiles","4x5","--no-timecode","-o",contact,timeout=500)
        if not contact.is_file() or contact.stat().st_size<50000:
            raise RuntimeError("OFFICIAL LOOK contact not saved")
        info=json.loads(cmd("ffprobe","-v","error","-show_entries",
            "stream=codec_type,width,height,r_frame_rate:format=duration,size",
            "-of","json",output,timeout=60)[0])
        duration=float(info["format"]["duration"]);total=int(info["format"]["size"])
        if not 35.0<=duration<=59.0:raise RuntimeError("FINAL duration invalid")
        streams=info["streams"]
        if not any(s.get("codec_type")=="video" and s.get("width")==1080 and
                   s.get("height")==1920 for s in streams):
            raise RuntimeError("FINAL invalid 1080x1920 video")
        if not any(s.get("codec_type")=="audio" for s in streams):
            raise RuntimeError("FINAL audio missing")
        # Output belongs only to owner private Drive root, NOT a public repo or media CDN.
        from PIL import Image
        jpg=directory/"M1lash_KINO008_FINAL_CONTACT_20_PRIVATE.jpg"
        Image.open(contact).convert("RGB").save(jpg,"JPEG",quality=80,optimize=True)
        photo_id=private_upload_small(jpg,auth,"image/jpeg")
        drive_id=private_upload_mp4(output,auth)
        status.update(status="ready_for_private_youtube_review_upload",
             completed_at=datetime.now(timezone.utc).isoformat(),
             final_sha256=digest(output),final_size_bytes=total,
             final_duration_s=round(duration,3),title_duration_s=round(title_secs,3),
             private_final_drive_file_id=drive_id,
             private_contact_drive_file_id=photo_id,
             official_check_result="returncode_0_official_check",
             official_look_result="20-frame private contact generated",
             manual_contact_review="pending_after_export",
             owner_audio_hearing="pending",
             video_source_rights="not_granted_by_studio",
             music_license="outro NCS approved credit; film soundtrack remains owner risk")
        print("KINO008_FINAL_QA_PASS",status["final_sha256"],
              "duration",status["final_duration_s"],"bytes",total,
              "DRIVE_FINAL",drive_id,"DRIVE_CONTACT",photo_id,flush=True)
    except Exception as exc:
      status.update(status="error",failure_class=type(exc).__name__,
                    failure=str(exc)[:300])
      print("KINO008_FINAL_QA_NO_GO",type(exc).__name__,str(exc)[:300],flush=True)
      raise
    finally:
      REPORT.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":main()
