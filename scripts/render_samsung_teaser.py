#!/usr/bin/env python3
"""Render a vertical Samsung teaser from verified neural speech assets."""
import json, subprocess, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"videos"/"samsung_teaser_ru.mp4"
TMP=ROOT/"build"/"samsung"
TMP.mkdir(parents=True,exist_ok=True)
job=json.loads((ROOT/"jobs/tts/samsung_teaser.json").read_text())
font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
texts=["SAMSUNG\nПО ВСЕМУ МИРУ?","ЕВРОПА\nГЕРМАНИЯ · ФРАНЦИЯ · БЕЛЬГИЯ","КАРТА МИРА\nНЕ ВСЁ ТАК ПРОСТО","МАГАЗИН ≠ ЗАПРЕТ","ПРОВЕРЯЕМ ФАКТЫ\nБЕЗ ВЫДУМОК","100+ СТРАН\nПОЛНЫЙ ВЫПУСК — M1LASH"]
colors=[(9,19,34),(12,32,49),(12,18,37),(31,19,43),(9,32,39),(9,19,34)]
dur=[]
for line in job["lines"]:
 p=ROOT/"media/tts/samsung_teaser"/(line["id"]+".mp3")
 if not p.exists() and line["id"]=="s06":
  p=ROOT/"media/tts/samsung_teaser_s06/s06.mp3"
 if not p.exists() or p.stat().st_size<1000: raise RuntimeError(f"Missing verified neural audio {p}")
 d=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(p)]))
 dur.append((p,d+0.22))
w,h=1080,1920
f1=ImageFont.truetype(font,86);f2=ImageFont.truetype(regular,35)
for i,(p,d) in enumerate(dur):
 im=Image.new("RGB",(w,h),colors[i]);dr=ImageDraw.Draw(im)
 for k in range(0,20):
  x=(k*71+i*97)%w
  dr.line((x,0,x-200,h),fill=(24,49,69),width=2)
 dr.rounded_rectangle((64,260,1016,1650),radius=50,outline=(45,171,205),width=5)
 dr.text((90,105),"M1LASH  /  ТЕХНОЛОГИИ",font=f2,fill=(126,219,240))
 y=690
 for line in texts[i].split("\\n"):
  box=dr.textbbox((0,0),line,font=f1)
  dr.text(((w-(box[2]-box[0]))/2,y),line,font=f1,fill=(241,249,255),stroke_width=1)
  y+=135
 dr.text((90,1490),f"0{i+1} / 06",font=f2,fill=(126,219,240))
 im.save(TMP/f"scene{i}.png")
parts=[]
for i,(p,d) in enumerate(dur):
 seg=TMP/f"seg{i}.mp4"
 subprocess.run(["ffmpeg","-y","-loglevel","error","-loop","1","-framerate","30","-i",str(TMP/f"scene{i}.png"),"-i",str(p),"-vf","format=yuv420p","-af","apad=pad_dur=0.22","-t",str(d),"-c:v","libx264","-preset","veryfast","-crf","21","-r","30","-c:a","aac","-b:a","160k","-ar","48000","-shortest",str(seg)],check=True)
 parts.append(seg)
lst=TMP/"concat.txt"
lst.write_text("".join(f"file '{p.resolve()}'\\n" for p in parts))
OUT.parent.mkdir(exist_ok=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),"-c","copy",str(OUT)],check=True)
subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(OUT),"-f","null","-"],check=True)
print(OUT)
