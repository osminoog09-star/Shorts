#!/usr/bin/env python3
"""Deep 245s Trinity scene owner-private audit, never export movie pixels to public Git."""
from __future__ import annotations
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,re,subprocess,sys,tempfile,secrets
from urllib.request import Request,urlopen

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from drive_scene_probe import fetch_private_film
from drive_oauth_config import resolve_existing_client

SOURCE_URL="https://drive.google.com/file/d/15jweAqG-x4UgFyCU8jkuZXhAuRJcGIaD/view"
SOURCE_SHA="a784b456047834339c4cc908d638f03d3b032917ca6b51aa948cf59312e656e1"
START=900.0
DURATION=245.0
REPORT=ROOT/"reports/research/2026-11-06_KINO_008_TRINITY_PRIVATE_TIMELINE.json"

def cmd(*args,timeout=140):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=timeout)
 if p.returncode:
  raise RuntimeError("ffmpeg/probe failure "+p.stderr[-230:])
 return p.stdout,p.stderr

def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(8*1024*1024),b""):h.update(b)
 return h.hexdigest()

def private_upload(path,token,mime):
 assert path.stat().st_size<=12*1024*1024
 border="m1lash"+secrets.token_hex(12)
 meta=json.dumps({"name":path.name,"mimeType":mime,"parents":["root"]},ensure_ascii=False).encode()
 raw=path.read_bytes()
 body=(b"--"+border.encode()+b"\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
       +meta+b"\r\n--"+border.encode()+b"\r\nContent-Type: "+mime.encode()+b"\r\n\r\n"
       +raw+b"\r\n--"+border.encode()+b"--\r\n")
 req=Request("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size",
              data=body,method="POST",headers={"Authorization":"Bearer "+token,
                                                "Content-Type":"multipart/related; boundary="+border})
 with urlopen(req,timeout=95) as r:info=json.load(r)
 if info.get("name")!=path.name or int(info.get("size",-1))!=len(raw) or not info.get("id"):
  raise RuntimeError("Private Drive result mismatch")
 return info["id"]

def contact(film,output,directory):
 from PIL import Image,ImageDraw
 cols,rows=6,10
 cw,ch=298,200
 sheet=Image.new("RGB",(cols*cw,rows*ch),(12,14,25))
 pen=ImageDraw.Draw(sheet)
 stamps=[]
 for i in range(cols*rows):
  t=START+(i+.5)*DURATION/(cols*rows)
  p=directory/f"frame_{i:02d}.jpg"
  try:
   cmd("ffmpeg","-v","error","-y","-ss",round(t,2),"-i",film,
       "-frames:v","1","-vf","scale=282:158:force_original_aspect_ratio=decrease",p,timeout=120)
   with Image.open(p) as img:
    im=img.convert("RGB")
    x=(i%cols)*cw+(cw-im.width)//2
    y=(i//cols)*ch+(173-im.height)//2
    sheet.paste(im,(x,y))
   pen.text(((i%cols)*cw+9,(i//cols)*ch+173),f"{int(t//60):02d}:{int(t%60):02d}",fill=(255,255,255))
   stamps.append(round(t,2))
  finally:p.unlink(missing_ok=True)
 sheet.save(output,"JPEG",quality=74,optimize=True)
 return stamps

def sound_and_asr(film,folder):
 from faster_whisper import WhisperModel
 wav=folder/"trinity_window.wav"
 cmd("ffmpeg","-v","error","-y","-ss",START,"-t",DURATION,
     "-i",film,"-ac","1","-ar","16000","-c:a","pcm_s16le","-vn",wav,timeout=300)
 model=WhisperModel("small",device="cpu",compute_type="int8",
                    cpu_threads=2,num_workers=1)
 segments, info=model.transcribe(str(wav),language="ru",beam_size=3,
                                 word_timestamps=True,vad_filter=True,
                                 condition_on_previous_text=False)
 lines=[]
 for seg in segments:
  words=[{"start_abs":round(START+w.start,2),"end_abs":round(START+w.end,2),
          "text":w.word.strip()} for w in (seg.words or []) if w.word.strip()]
  lines.append({"start_abs":round(START+seg.start,2),"end_abs":round(START+seg.end,2),
                "text":seg.text.strip(),"words":words})
 wav.unlink(missing_ok=True)
 return lines

def silences(film):
 _,err=cmd("ffmpeg","-hide_banner","-v","info","-ss",START,"-t",DURATION,
           "-i",film,"-vn","-af","silencedetect=noise=-34dB:d=0.5",
           "-f","null","-",timeout=360)
 starts=[float(x) for x in re.findall(r"silence_start:\\s*([\\d.]+)",err)]
 ends=[float(x) for x in re.findall(r"silence_end:\\s*([\\d.]+)",err)]
 return [{"from_abs":round(START+s,2),"to_abs":round(START+e,2)}
         for s,e in zip(starts,ends) if e-s>.75]

def main():
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 state={"checked_at":datetime.now(timezone.utc).isoformat(),"status":"error",
        "range_start":START,"range_end":START+DURATION,"youtube_upload":False,
        "note":"Private transcription and contact in owner Drive only, not public repo."}
 try:
  with tempfile.TemporaryDirectory(prefix="kino008-trinity-",dir=os.environ.get("RUNNER_TEMP") or None) as tmp:
   d=Path(tmp)
   film=d/"owner_original.mp4"
   bytes_received=fetch_private_film(SOURCE_URL,film)
   if bytes_received!=836471622 or sha(film)!=SOURCE_SHA:
    raise RuntimeError("Source SHA/size mismatch")
   auth,_=resolve_existing_client(dict(os.environ))
   token=auth["_GDRIVE_ACCESS_TOKEN"]
   image=d/"KINO008_TRINITY_DENSE_PRIVATE_60FRAMES.jpg"
   stamps=contact(film,image,d)
   image_id=private_upload(image,token,"image/jpeg")
   print("KINO008_PRIVATE_CONTACT_READY",image_id,len(stamps),flush=True)
   lines=sound_and_asr(film,d)
   private_text=d/"KINO008_TRINITY_PRIVATE_ASR_RU.json"
   private_text.write_text(json.dumps({"start":START,"end":START+DURATION,
       "language":"ru","segments":lines},ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
   text_id=private_upload(private_text,token,"application/json")
   intervals=silences(film)
   # Public report has only words to locate timing, no copyrighted dialogue.
   keywords=re.compile(r"взрыв|бомб|испытан|секунд|минут|готов|отсч|ноль|мир|время|пуск|свет|солнц|гроз",re.I)
   hits=[{"at":q["start_abs"],"keyword_count":len(keywords.findall(q["text"]))}
         for q in lines if keywords.search(q["text"])]
   state.update(status="ru_scene_asr_private_ready",
    source_sha256=SOURCE_SHA,contact_file_id=image_id,asr_file_id=text_id,
    contact_times=stamps,asr_segments=len(lines),
    speech_first_at=lines[0]["start_abs"] if lines else None,
    silence_intervals=intervals[:40],keyword_windows=hits[:30])
   print("KINO008_PRIVATE_ASR_READY",text_id,"segments",len(lines),
         "silences",intervals[:8],"keyword_windows",hits[:15],flush=True)
 except Exception as exc:
  state["status"]="error";state["error_class"]=type(exc).__name__
  state["error_message"]=str(exc)[:200]
  print("KINO008_TRINITY_AUDIT_FAIL",type(exc).__name__,str(exc)[:180],flush=True)
  raise
 finally:
  REPORT.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":main()
