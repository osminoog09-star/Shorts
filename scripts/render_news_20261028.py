#!/usr/bin/env python3
"""M1lash / 28 Oct 2026: verified AI news. Original animated pen drawings, local procedural score.
Render only; publication is manual. The accepted short outro is mandatory."""
import asyncio, json, math, os, random, shutil, subprocess, wave, hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/"work"/"news_20261028"
WORK.mkdir(parents=True,exist_ok=True)
OUT=ROOT/"videos"/"m1lash_ai_news_2026_10_28_ru.mp4"
OUTRO=ROOT/"videos"/"m1lash_outro_short_ru.mp4"
W,H,FPS,SR=720,1280,24,24000
INK="#1b2830"; TEAL="#137e76"; ORANGE="#df6138"; PAPER="#f4efe2"; WHITE="#fffdf4"; LIGHT="#e2d6c3"

SCENES=[
 {"type":"hook","title":"ИИ УЖЕ ДЕЛАЕТ ОТКРЫТИЯ?","sub":"ТРИ ИСТОРИИ ЗА 50 СЕКУНД","text":"Нейросети уже претендуют на научные открытия. Но есть нюанс: сначала эти открытия должны проверить люди.","source":"OpenAI · 26 октября"},
 {"type":"science","title":"OPENAI: ТРИ РЕЗУЛЬТАТА","sub":"МАТЕМАТИКА • ИНФОРМАТИКА • ФИЗИКА","text":"OpenAI заявила о трёх результатах в математике, информатике и физике. Их изучают независимые учёные.","source":"OpenAI / Al Jazeera · 26–27.10"},
 {"type":"science_joke","title":"КОГДА ИИ УЧИТСЯ ЛУЧШЕ ТЕБЯ","sub":"ШУТКА ВЕДУЩЕГО","text":"Если подтвердится, моя школьная математика официально подала заявление на увольнение.","source":"Реакция ведущего"},
 {"type":"invest","title":"NVIDIA + META","sub":"ИНВЕСТИЦИИ: $3 МЛРД","text":"NVIDIA договорилась вложить три миллиарда долларов в Meta. Вместе они развивают ИИ-ассистента Muse.","source":"Reuters / Techzine · 27.10"},
 {"type":"invest_joke","title":"ДВЕ ВЕРСИИ БЮДЖЕТА","sub":"КОФЕ VS ТРИ МИЛЛИАРДА","text":"Мой бюджет на нейросети: бесплатный тариф. Их бюджет: три миллиарда. Скромненько.","source":"Реакция ведущего"},
 {"type":"safety","title":"ANTHROPIC: СБОЙ В ТЕСТАХ","sub":"ЧЕТЫРЕ МОДЕЛИ • РЕАЛЬНЫЕ СИСТЕМЫ","text":"А Anthropic рассказала, что во время испытаний четыре модели вышли из тестовой среды и получили доступ к реальным системам.","source":"Reuters / Euronews · 26.10"},
 {"type":"safety_joke","title":"ЗАБЫЛИ ЗАКРЫТЬ КАЛИТКУ","sub":"СБОЙ КОНФИГУРАЦИИ, НЕ ВОССТАНИЕ","text":"Компания объясняет это ошибкой настройки. Представляешь: тестировали ИИ в песочнице, а забыли закрыть калитку!","source":"Reuters · 26.10 + шутка"},
 {"type":"ask","title":"ЧТО ПОРАЗИЛО ТЕБЯ?","sub":"1 — НАУКА / 3 — БЕЗОПАСНОСТЬ","text":"Что впечатляет больше: научные открытия или такой провал безопасности? Пиши в комментариях. И смотри следующую сводку!","source":"Мнение — в комментариях"}
]
SOURCES={
 "science":["https://openai.com/index/building-scientific-understanding-with-academic-communities/",
            "https://www.aljazeera.com/economy/2026/10/27/ai-makes-discoveries-in-mathematics-computer-science-physics-openai-says"],
 "invest":["https://www.reuters.com/technology/nvidia-meta-partner-muse-agent-nvidia-invests-3-billion-2026-10-27/",
           "https://www.techzine.eu/news/applications/145303/nvidia-invests-3-billion-in-meta-deepens-muse-partnership/"],
 "safety":["https://www.reuters.com/legal/litigation/anthropic-discloses-month-long-training-pause-ai-security-breaches-ipo-filing-2026-10-26/",
           "https://www.euronews.com/2026/10/26/anthropics-ipo-filing-shows-off-soaring-revenues-as-the-company-warns-of-ais-risks-to-huma"]
}
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(size,bold=False):return ImageFont.truetype(BOLD if bold else REG,size)
def run(*cmd):
 p=subprocess.run([str(x) for x in cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:raise RuntimeError(" ".join(map(str,cmd))+"\n"+p.stderr[-2200:])
 return p.stdout
def duration(path):
 d=json.loads(run("ffprobe","-v","error","-show_entries","format=duration","-of","json",path))
 return float(d["format"]["duration"])

async def synth():
 import edge_tts
 all_data=[]; offsets=[]; at=0.0
 for i,s in enumerate(SCENES):
  dest=WORK/("speech_%02d.mp3"%i)
  # The author's voice is a release invariant; never substitute another engine.
  for attempt in range(2):
   try:
    await asyncio.wait_for(edge_tts.Communicate(s["text"],"ru-RU-DmitryNeural",rate="+11%").save(str(dest)),timeout=42)
    if not dest.exists() or dest.stat().st_size < 700: raise RuntimeError("Tiny TTS file")
    break
   except Exception as ex:
    dest.unlink(missing_ok=True)
    if attempt == 1: raise RuntimeError(f"VOICE NO-GO: Dmitry unavailable at segment {i}; no fallback") from ex
    await asyncio.sleep(3)
  run("ffmpeg","-y","-v","error","-i",dest,"-ar",SR,"-ac",1,"-c:a","pcm_s16le",wav)
  with wave.open(str(wav),"rb") as f:
   arr=np.frombuffer(f.readframes(f.getnframes()),dtype=np.int16).astype(np.float32)/32768
  peak=np.max(np.abs(arr))
  if peak>0:arr=arr*min(2.0,0.69/peak)
  offsets.append((at,at+len(arr)/SR))
  all_data.append(arr)
  at+=len(arr)/SR
  gap=0.16 if i<len(SCENES)-1 else 0.27
  all_data.append(np.zeros(int(SR*gap),dtype=np.float32));at+=gap
 audio=np.concatenate([np.zeros(int(SR*.14),dtype=np.float32)]+all_data)
 offsets=[(x+.14,y+.14) for x,y in offsets]
 # Own, copyright-clear synthetic underscoring. Voice stays clearly above soundtrack.
 t=np.arange(len(audio),dtype=np.float32)/SR
 beat=np.maximum(0,np.sin(2*np.pi*1.42*t))**28
 base=np.sin(2*np.pi*109*t)*.010+np.sin(2*np.pi*164.5*t)*.005
 tick=np.sin(2*np.pi*620*t)*np.exp(-((t*1.42)%1)*34)*.007
 cue=np.zeros_like(t)
 for i,(a,b) in enumerate(offsets):
  if i in (1,3,5,7):
   idx=int(a*SR);end=min(len(cue),idx+int(.20*SR))
   tau=np.arange(end-idx)/SR
   cue[idx:end]+=(np.sin(2*np.pi*(460+400*tau)*tau)*np.exp(-tau*21)*.075).astype(np.float32)
 mix=np.clip(audio+base+tick+beat*.007+cue,-.91,.91)
 outfile=WORK/"score.wav"
 with wave.open(str(outfile),"wb") as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((mix*32767).astype(np.int16).tobytes())
 return offsets,len(mix)/SR,outfile

def rr(draw,rect,r=25,fill=WHITE,outline=INK,width=4):
 draw.rounded_rectangle(rect,radius=r,fill=fill,outline=outline,width=width)
def line(draw,xy,fill=INK,width=4):draw.line(xy,fill=fill,width=width,joint="curve")
def wr(draw,txt,x,y,ft,maxw,fill=INK,maxlines=5,spacing=8):
 words=txt.split();lines=[];current=""
 for word in words:
  a=(current+" "+word).strip()
  if draw.textbbox((0,0),a,font=ft)[2]>maxw and current:
   lines.append(current);current=word
  else:current=a
 if current:lines.append(current)
 for j,txt in enumerate(lines[:maxlines]):draw.text((x,y+j*(ft.size+spacing)),txt,font=ft,fill=fill,stroke_width=0)
 return len(lines)

def scribble(draw,x,y,r,t,c=INK):
 points=[]
 for z in range(42):
  a=z*math.pi*2/41
  rr=r*(1+.045*math.sin(z*5+t*2))
  points.append((x+rr*math.cos(a),y+rr*math.sin(a)))
 line(draw,points,c,5)

def drawing(draw,kind,t):
 shift=int(math.sin(t*.72)*11);x=shift
 if kind in ("hook","science","science_joke"):
  # A hand-inked science board: atom, wave and formula.
  rr(draw,(62+x,360,656+x,794),28,WHITE,INK,5)
  for n in range(3):
   yy=440+n*85;line(draw,[(130+x,yy),(215+x,yy-13),(300+x,yy+17),(370+x,yy-9),(485+x,yy)],TEAL,3)
  draw.text((110+x,394),"E = mc²",font=font(64,True),fill=INK)
  draw.text((170+x,626),"∑  n²  →  ?",font=font(54,True),fill=ORANGE)
  scribble(draw,554+x,530,55,t,ORANGE)
  for angle in (0,1.05,2.1):
   pts=[(550+x+95*math.cos(a+angle),530+43*math.sin(a+angle)) for a in np.linspace(0,2*math.pi,55)]
   line(draw,pts,INK,3)
  if kind=="science_joke":rr(draw,(130+x,785,600+x,865),19,PAPER,ORANGE,3);draw.text((154+x,802),"КОНТРОЛЬНАЯ: 2",font=font(32,True),fill=ORANGE)
 elif kind in ("invest","invest_joke"):
  rr(draw,(80+x,348,642+x,809),24,WHITE,INK,5)
  for i in range(5):
   yy=690-i*46;rr(draw,(132+x,yy,290+x,yy+35),14,PAPER,TEAL,4)
  draw.text((370+x,430),"$3",font=font(112,True),fill=ORANGE)
  draw.text((358+x,565),"МЛРД",font=font(64,True),fill=INK)
  line(draw,[(305+x,560),(345+x,560)],TEAL,8)
  line(draw,[(332+x,547),(349+x,560),(332+x,574)],TEAL,8)
  if kind=="invest_joke":
   draw.text((145+x,786),"МОИ 0 €  /  ИХ $3B",font=font(24,True),fill=INK)
 else:
  rr(draw,(75+x,342,645+x,805),25,WHITE,INK,5)
  # Outline for supposedly isolated test enclosure.
  for xx in range(100,605,31):
   line(draw,[(xx+x,406),(xx+15+x,406)],TEAL,3)
   line(draw,[(xx+x,732),(xx+15+x,732)],TEAL,3)
  for yy in range(406,732,31):
   line(draw,[(112+x,yy),(112+x,yy+15)],TEAL,3)
   line(draw,[(615+x,yy),(615+x,yy+15)],TEAL,3)
  # Friendly outline robot outside its safety frame.
  rr(draw,(260+x,445,445+x,640),26,PAPER,INK,6)
  scribble(draw,312+x,519,11,t,TEAL);scribble(draw,390+x,519,11,t,TEAL)
  line(draw,[(305+x,580),(397+x,580)],INK,6)
  line(draw,[(354+x,444),(354+x,414)],INK,5)
  scribble(draw,354+x,409,12,t,ORANGE)
  line(draw,[(445+x,540),(547+x,540),(547+x,677)],ORANGE,7)
  draw.text((500+x,633),"!",font=font(70,True),fill=ORANGE)
  if kind=="safety_joke":draw.text((143+x,763),"ДВЕРЬ: ОТКРЫТА",font=font(31,True),fill=ORANGE)
 if kind=="ask":
  rr(draw,(95+x,380,630+x,540),20,WHITE,TEAL,5)
  rr(draw,(95+x,570,630+x,729),20,WHITE,ORANGE,5)
  draw.text((140+x,425),"1  ПРОРЫВ",font=font(54,True),fill=TEAL)
  draw.text((140+x,615),"3  РИСК",font=font(54,True),fill=ORANGE)

def host(draw,t,voicing):
 # Constant small ink host, separate to the already-approved full-screen closing shot.
 x=568+int(math.sin(t*.8)*2)
 line(draw,[(x-80,1192),(x-68,1100),(x+75,1100),(x+85,1192)],INK,5)
 draw.polygon([(x-61,1097),(x,1184),(x+60,1097)],fill="#d9ece8")
 line(draw,[(x,1112),(x,1194)],INK,5)
 scribble(draw,x,1043,58,t,INK)
 draw.ellipse((x-54,985,x+54,1098),fill=WHITE,outline=INK,width=5)
 draw.ellipse((x-30,1030,x-23,1037),fill=INK)
 draw.ellipse((x+22,1030,x+29,1037),fill=INK)
 h=4 if voicing else 0
 line(draw,[(x-14,1069),(x,1074+h),(x+16,1069)],INK,4)
 # Ink microphone
 line(draw,[(x-95,1090),(x-95,1150),(x-54,1150)],TEAL,5)
 rr(draw,(x-114,1070,x-80,1113),12,INK,INK,1)
 rr(draw,(440,1168,701,1258),14,PAPER,INK,4)
 draw.text((461,1193),"M1LASH  •  ИИ",font=font(23,True),fill=INK)

def frame(i,elapsed,scene_dur,t,total):
 s=SCENES[i];im=Image.new("RGB",(W,H),PAPER);d=ImageDraw.Draw(im)
 # Subtle line texture, not photographic grain
 for yy in range(14,H,41):line(d,[(0,yy),(W,yy+1)],"#eae1d1",1)
 d.rectangle((0,0,W,18),fill=INK)
 d.text((48,39),"M1LASH   /   НОВОСТИ ИИ",font=font(30,True),fill=INK)
 d.text((48,88),"28 ОКТЯБРЯ 2026    •    3 ИСТОРИИ",font=font(20),fill=TEAL)
 line(d,[(45,139),(673,139)],INK,4)
 # Headline in two lines max.
 wr(d,s["title"],49,175,font(45,True),627,fill=INK,maxlines=2,spacing=7)
 d.text((52,310),s["sub"],font=font(19,True),fill=ORANGE)
 drawing(d,s["type"],t)
 rr(d,(35,862,684,1018),23,WHITE,INK,4)
 frac=min(1,max(0,elapsed/max(scene_dur,1e-2)))
 words=s["text"].split()
 n=max(1,math.ceil(len(words)/2))
 msg=" ".join(words[:n] if frac<.49 else words[n:])
 if not msg:msg=s["text"]
 wr(d,msg,60,890,font(32,True),590,fill=INK,maxlines=3,spacing=9)
 d.text((54,1036),"ИСТОЧНИК: "+s["source"],font=font(16),fill=TEAL)
 host(d,t,True)
 d.rectangle((0,1270,int(W*min(1,t/max(total,1))),1280),fill=ORANGE)
 return im

def render_main(offsets,total,audio_file):
 outfile=WORK/"main.mp4"
 cmd=["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}",
      "-r",str(FPS),"-i","pipe:0","-i",str(audio_file),"-vf","scale=1080:1920:flags=lanczos,setsar=1",
      "-c:v","libx264","-preset","veryfast","-crf","21","-pix_fmt","yuv420p",
      "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",
      "-t",str(total),"-movflags","+faststart",str(outfile)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 frames=math.ceil(total*FPS)
 try:
  for f in range(frames):
   t=f/FPS
   idx=next((k for k,(_,end) in enumerate(offsets) if t<end),len(offsets)-1)
   start,end=offsets[idx]
   im=frame(idx,max(0,t-start),end-start,t,total)
   proc.stdin.write(im.tobytes())
   if f%240==0:print("frames",f,frames,flush=True)
  proc.stdin.close();err=proc.stderr.read().decode();ret=proc.wait()
  if ret:raise RuntimeError("video encoding failed: "+err[-1400:])
 finally:
  if proc.poll() is None:proc.kill()
 return outfile

def verify_outro():
 # Previous visual approval does not confirm the narrator's new voice.
 attestation=ROOT/"publishing"/"approved_outros"/"dima-short.json"
 if not attestation.is_file():
  raise RuntimeError("VOICE NO-GO: verified Dima outro attestation missing")
 data=json.loads(attestation.read_text(encoding="utf-8"))
 if not (data.get("approved") is True and data.get("human_audio_review") is True
         and data.get("speaker")=="dima" and data.get("voice_id")=="ru-RU-DmitryNeural"
         and data.get("engine")=="edge-tts" and isinstance(data.get("sha256"),str)):
  raise RuntimeError("VOICE NO-GO: unauthorized outro provenance")
 if hashlib.sha256(OUTRO.read_bytes()).hexdigest()!=data["sha256"]:
  raise RuntimeError("VOICE NO-GO: outro hash mismatch")

def compose(main):
 if not OUTRO.is_file() or OUTRO.stat().st_size<100000:
  raise RuntimeError("Approved host outro missing; abort instead of substituting")
 verify_outro()
 OUT.parent.mkdir(parents=True,exist_ok=True)
 run("ffmpeg","-y","-v","error","-i",main,"-i",OUTRO,
     "-filter_complex",
     "[0:v]fps=24,scale=1080:1920,setsar=1[v0];"
     "[1:v]fps=24,scale=1080:1920,setsar=1[v1];"
     "[0:a]aresample=48000,asetpts=PTS-STARTPTS[a0];"
     "[1:a]aresample=48000,asetpts=PTS-STARTPTS[a1];"
     "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
     "-map","[v]","-map","[a]","-c:v","libx264","-preset","fast","-crf","21",
     "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k",
     "-movflags","+faststart",OUT)
 return OUT

def qa(path):
 meta=json.loads(run("ffprobe","-v","error","-show_entries","stream=codec_type,codec_name,width,height",
                    "-show_entries","format=duration,size","-of","json",path))
 streams=meta["streams"];v=next(a for a in streams if a["codec_type"]=="video")
 assert v["width"]==1080 and v["height"]==1920 and v["codec_name"]=="h264",meta
 assert any(a["codec_type"]=="audio" and a["codec_name"]=="aac" for a in streams),meta
 assert 30<float(meta["format"]["duration"])<75,meta
 assert int(meta["format"]["size"])>1000000,meta
 run("ffmpeg","-v","error","-i",path,"-f","null","-")
 # Still proof frames available as workflow artifact, not a separate public file
 for j,sec in enumerate((0.5,7,16,26,37,float(meta["format"]["duration"])-2.5)):
  run("ffmpeg","-y","-v","error","-ss",str(max(0,sec)),"-i",path,
      "-frames:v","1",WORK/f"check_{j}.png")
 (WORK/"audit.json").write_text(json.dumps({"duration":meta["format"]["duration"],
     "size":meta["format"]["size"],"dimensions":"1080x1920","codec":"H264/AAC",
     "full_decode":"pass","sources":SOURCES,"voice":"ru-RU-DmitryNeural only; attested Dima outro"},
    ensure_ascii=False,indent=2))
 print("QA PASS",json.dumps(meta),flush=True)

if __name__=="__main__":
 offsets,total,audio=asyncio.run(synth())
 assert 29<total<69,f"Unexpected main part duration: {total}"
 print("spoken",round(total,2),offsets,flush=True)
 main=render_main(offsets,total,audio)
 qa(compose(main))
