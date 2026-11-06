#!/usr/bin/env python3
"""Kino008 Oppenheimer Trinity: original owner recording => private MOVIE BODY.

Never commit movie pixels, soundtrack or credentials to public Git. All media
and QA contact stay in owner-restricted Google Drive root. No YouTube API here.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,tempfile,secrets,datetime,re
from pathlib import Path
from urllib.request import Request,urlopen
import requests

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from drive_scene_probe import fetch_private_film
from drive_oauth_config import resolve_existing_client

SOURCE_URL="https://drive.google.com/file/d/15jweAqG-x4UgFyCU8jkuZXhAuRJcGIaD/view"
SOURCE_SHA="a784b456047834339c4cc908d638f03d3b032917ca6b51aa948cf59312e656e1"
REPORT=ROOT/"reports/research/2026-11-06_KINO_008_BODY_V2_PRIVATE_QA.json"

# t in owner's private 40min screen recording; 12 shots in 32.8s body.
# Source frame 1258x1080, actual movie area letterboxed y≈300..840;
# manual focus center x in source coords, verified against owner-private 60f contact.
SHOTS=[
 ("cold_flash",1019.70,1.15,620),
 ("ru_countdown",1006.10,2.85,610,905.12),
 ("arm_controls",945.00,2.35,635),
 ("timer",970.90,2.75,660),
 ("tower",987.10,2.65,625),
 ("faces_preflash",1000.20,2.35,610),
 ("blinding_flash",1021.05,2.90,620),
 ("fire_rises",1034.00,3.45,640),
 ("inferno",1055.70,3.00,620),
 ("silent_reaction",1069.00,2.70,700),
 ("delayed_rumble",1100.20,2.90,605),
 ("aftermath",1110.25,3.55,610),
]
TOTAL=sum(s[2] for s in SHOTS)
WORDS=[
 (0.0,1.15,"ОНИ НАЖАЛИ КНОПКУ..."),
 (1.20,2.70,"90 СЕКУНД"),
 (2.70,4.00,"ДО ДЕТОНАЦИИ"),
 (5.6,7.65,"ОБРАТНОГО ПУТИ НЕТ"),
 (11.4,13.8,"НИКТО НЕ ЗНАЛ..."),
 (13.9,15.6,"ЧТО БУДЕТ ДАЛЬШЕ"),
 (21.0,23.0,"СНАЧАЛА — ТИШИНА"),
 (27.0,29.0,"А ПОТОМ...")
]

def shell(*args,timeout=180):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True,timeout=timeout)
 if p.returncode:
  raise RuntimeError("Command "+str(args[0])+" failed "+p.stderr[-480:])
 return p.stdout,p.stderr

def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for b in iter(lambda:f.read(4*1024*1024),b""):h.update(b)
 return h.hexdigest()

def private_upload_small(path,token,mime):
 raw=path.read_bytes()
 if len(raw)>12*1024*1024: raise RuntimeError("contact too large")
 bound="m1lash"+secrets.token_hex(12)
 meta=json.dumps({"name":path.name,"mimeType":mime,"parents":["root"]}).encode()
 payload=(b"--"+bound.encode()+b"\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n"
          +meta+b"\r\n--"+bound.encode()+b"\r\nContent-Type: "+mime.encode()+b"\r\n\r\n"
          +raw+b"\r\n--"+bound.encode()+b"--\r\n")
 req=Request("https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,size",
  data=payload,method="POST",headers={"Authorization":"Bearer "+token,
                                      "Content-Type":"multipart/related; boundary="+bound})
 with urlopen(req,timeout=100) as res:meta=json.load(res)
 if meta.get("name")!=path.name or int(meta.get("size",-1))!=len(raw):raise RuntimeError("Private contact size mismatch")
 return meta["id"]

def private_upload_mp4(path,token):
 size=path.stat().st_size
 if not (1_000_000<size<200_000_000):raise RuntimeError("private movie body unexpected size")
 with requests.Session() as s:
  init=s.post("https://www.googleapis.com/upload/drive/v3/files",
    params={"uploadType":"resumable","fields":"id,name,size,mimeType,parents"},
    headers={"Authorization":"Bearer "+token,"Content-Type":"application/json; charset=UTF-8",
      "X-Upload-Content-Type":"video/mp4","X-Upload-Content-Length":str(size)},
    json={"name":path.name,"mimeType":"video/mp4","parents":["root"]},timeout=65)
  if init.status_code not in (200,201) or not init.headers.get("Location"):
   raise RuntimeError("Private Drive video session init HTTP "+str(init.status_code))
  with path.open("rb") as f:
   uploaded=s.put(init.headers["Location"],data=f,headers={"Content-Type":"video/mp4",
                            "Content-Length":str(size)},timeout=500)
  if not uploaded.ok:raise RuntimeError("Private Drive upload outcome unknown HTTP "+str(uploaded.status_code))
  obj=uploaded.json()
  if obj.get("name")!=path.name or int(obj.get("size",-1))!=size or obj.get("mimeType")!="video/mp4":
   raise RuntimeError("Google Drive returned mismatched private body")
  return obj["id"]

def ass_ts(t):
 h=int(t//3600);m=int((t%3600)//60);s=t%60
 return f"{h}:{m:02d}:{s:05.2f}"
def make_subs(path):
 header="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,DejaVu Sans,71,&H00FFFFFF,&H00FFFFFF,&H00000000,&H56000000,1,0,0,0,100,100,0,0,1,7,3,2,64,64,480,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
 lines=[]
 for st,en,txt in WORDS:
  lines.append(f"Dialogue: 0,{ass_ts(st)},{ass_ts(en)},Sub,,0,0,0,,{{\\fad(90,90)}}{txt}")
 path.write_text(header+"\n".join(lines)+"\n",encoding="utf-8")

def make_contact(body,output,temp):
 from PIL import Image,ImageDraw
 cols,rows=4,4;cw,ch=248,440
 sheet=Image.new("RGB",(cols*cw,rows*ch),(20,24,31));draw=ImageDraw.Draw(sheet)
 for i in range(cols*rows):
  sec=(i+.5)*TOTAL/(cols*rows);p=temp/f"look_{i:02d}.jpg"
  try:
   shell("ffmpeg","-hide_banner","-v","error","-ss",round(sec,3),
          "-i",body,"-frames:v","1","-q:v","3","-y",p,timeout=65)
   with Image.open(p) as img:
    image=img.convert("RGB");image.thumbnail((cw-8,ch-22))
    sheet.paste(image,((i%cols)*cw+(cw-image.width)//2,(i//cols)*ch+2))
   draw.text(((i%cols)*cw+10,(i//cols)*ch+ch-19),f"{sec:.1f}s",fill="white")
  finally:p.unlink(missing_ok=True)
 sheet.save(output,"JPEG",quality=70,optimize=True)

def main():
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 result={"status":"error","created_at":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "source_sha256":SOURCE_SHA,"youtube_id":None,"youtube_upload":False,
         "segment_plan":[{"name":row[0],"source_start_s":row[1],"duration_s":row[2],"focus_x":row[3],"audio_source_s":row[4] if len(row)>4 else row[1]} for row in SHOTS],
         "expected_body_duration_s":round(TOTAL,3)}
 try:
  with tempfile.TemporaryDirectory(prefix="kino008-edit-",dir=os.environ.get("RUNNER_TEMP") or None) as tmp:
   d=Path(tmp)
   source=d/"owner.mp4"
   got=fetch_private_film(SOURCE_URL,source)
   if got!=836471622 or digest(source)!=SOURCE_SHA:raise RuntimeError("Owner source changed")
   clips=[]
   for i,row in enumerate(SHOTS):
    name,start,dur,cx = row[:4]
    voice_src = row[4] if len(row)>4 else None
    clip=d/f"clip{i:02d}.mp4"
    x=max(0,min(1258-304,int(cx-304/2)))
    vf=f"crop=304:540:{x}:290,scale=1080:1920:flags=lanczos,fps=30,setsar=1,format=yuv420p"
    af=f"aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,afade=t=in:st=0:d=0.035,afade=t=out:st={max(0,dur-.075):.3f}:d=0.075"
    input_args=["-ss",start,"-i",source]
    if voice_src is not None:
     input_args+=["-ss",voice_src,"-i",source]
    shell("ffmpeg","-hide_banner","-v","error","-y",*input_args,
          "-t",dur,"-map","0:v:0","-map","1:a:0" if voice_src is not None else "0:a:0",
          "-vf",vf,"-af",af,"-c:v","libx264","-preset","veryfast",
          "-crf","18","-pix_fmt","yuv420p","-r","30","-c:a","aac",
          "-ar","48000","-ac","2","-b:a","192k",clip,timeout=300)
    clips.append(clip)
    print("KINO008_SHOT",i+1,name,"source",start,"seconds",dur,"bytes",clip.stat().st_size,flush=True)
   concat=d/"list.txt"
   concat.write_text("".join(f"file '{x}'\n" for x in clips),encoding="utf-8")
   joint=d/"concat.mp4"
   shell("ffmpeg","-hide_banner","-v","error","-y","-f","concat",
         "-safe","0","-i",concat,"-c","copy",joint,timeout=150)
   captions=d/"captions.ass"
   make_subs(captions)
   body=d/"M1lash_KINO008_TRINITY_PRIVATE_BODY_V2.mp4"
   shell("ffmpeg","-hide_banner","-v","error","-y","-i",joint,
         "-vf",f"ass={captions.as_posix()}:shaping=complex","-c:v","libx264",
         "-preset","veryfast","-crf","18","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-ar","48000","-ac","2",
         "-movflags","+faststart",body,timeout=380)
   stdout,_=shell("ffprobe","-v","error","-show_entries",
                  "format=duration:stream=codec_type,width,height",
                  "-of","json",body,timeout=50)
   probe=json.loads(stdout)
   duration=float(probe["format"]["duration"])
   if abs(duration-TOTAL)>1.0 or duration>45:
    raise RuntimeError("KINO008 body duration mismatch")
   shell("ffmpeg","-hide_banner","-v","error","-xerror",
         "-i",body,"-f","null","-",timeout=360)
   contact=d/"M1lash_KINO008_PRIVATE_BODY_V2_CONTACT_16.jpg"
   make_contact(body,contact,d)
   env,_=resolve_existing_client(dict(os.environ))
   token=env["_GDRIVE_ACCESS_TOKEN"]
   image_id=private_upload_small(contact,token,"image/jpeg")
   video_id=private_upload_mp4(body,token)
   result.update(status="private_body_rendered_qa_pending",
                 duration_s=round(duration,3),sha256=digest(body),
                 size_bytes=body.stat().st_size,private_body_drive_id=video_id,
                 private_contact_drive_id=image_id,full_decode_ok=True,
                 subtitle_cues=len(WORDS),ffprobe=probe)
   print("KINO008_PRIVATE_BODY",video_id,"CONTACT",image_id,"SHA256",result["sha256"],
         "DURATION",duration,flush=True)
 except Exception as exc:
  result.update(status="error",error_class=type(exc).__name__,error_message=str(exc)[:200])
  print("KINO008_BODY_FAILURE",type(exc).__name__,str(exc)[:180],flush=True)
  raise
 finally:
  REPORT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":main()
