#!/usr/bin/env python3
"""M1lash original CAPTCHA comedy. Voice-authoritative code animation; no host avatar."""
import json, math, subprocess, wave, os, pathlib, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
R=pathlib.Path(__file__).resolve().parents[2]
OUT=R/"videos"/"pretend_bot3_gpt_ru_v3.mp4"
HERE=pathlib.Path(__file__).resolve().parent
TTS=R/"media"/"tts"/"pretend_bot3_gpt"
JOB=R/"jobs"/"tts"/"pretend_bot3_gpt.json"
W,H,FPS,SR=540,960,24,48000
BG="#101827";WHITE="#F5F7FA";CYAN="#50E5D2";RED="#FF627A";GOLD="#FFD277";BLUE="#668BFA"
F="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SCENES=[
("ВАС ЗАБЛОКИРОВАЛИ","САЙТ РЕШИЛ: Я НЕ ЧЕЛОВЕК","error"),
("ОДНА ГАЛОЧКА","Я НЕ РОБОТ","checkbox"),
("КАПЧА №1","НАЙДИТЕ СВЕТОФОРЫ","captcha"),
("КАПЧА №7","ЭТО ЭКЗАМЕН В МИНИСТЕРСТВО?","captcha"),
("ЗОВУ ИИ","ПРОЙДИ КАПЧУ ЗА МЕНЯ","robot"),
("ГОТОВО","ЗА 0,01 СЕКУНДЫ","robot"),
("НАКОНЕЦ-ТО","САЙТ ПОВЕРИЛ, ЧТО Я...","approved"),
("ОБНАРУЖЕН БОТ","ВАШ ДОСТУП ЗАБЛОКИРОВАН","error"),
("ГЕНИАЛЬНО!","БОТ ДОКАЗАЛ, ЧТО Я НЕ БОТ","loop"),
("РАЗБЛОКИРОВКА","ДОКАЖИТЕ, ЧТО ВЫ ЧЕЛОВЕК","checkbox"),
("ДА ВЫ ИЗДЕВАЕТЕСЬ!","ВСЁ ПО НОВОЙ","loop"),
("M1LASH","ПОДПИСАТЬСЯ","outro"),
]
def ff(*xs):
 return subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",*map(str,xs)],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).stdout
def font(s,b=True):return ImageFont.truetype(FB if b else F,int(s))
def rr(d,xy,fill,r=20,outline=None,w=2):d.rounded_rectangle(tuple(int(v) for v in xy),radius=r,fill=fill,outline=outline,width=w)
def text(d,s,y,fill=WHITE,size=38,max_width=480,x=None):
 size=int(size)
 while size>14 and d.textbbox((0,0),s,font=font(size))[2]>max_width:size-=1
 bb=d.textbbox((0,0),s,font=font(size))
 dx=(W-(bb[2]-bb[0]))/2 if x is None else x
 d.text((dx,y),s,font=font(size),fill=fill)
def dur_audio():
 j=json.loads(JOB.read_text(encoding="utf-8"))
 assert len(j["lines"])==len(SCENES),"TTS lines do not match animation sections"
 tracks=[];manifest=[];starts=[];duration=0
 for i,l in enumerate(j["lines"]):
  mp3=TTS/(l["id"]+".mp3");md=TTS/(l["id"]+".json")
  if not mp3.exists() or not md.exists():raise RuntimeError("Missing approved speech "+str(mp3))
  m=json.loads(md.read_text(encoding="utf-8"))
  assert m["text"]==l["text"] and m["voice_id"]==l.get("voice",j["voice"])
  assert m["voice_id"] in ("ru-RU-DmitryNeural","ru-RU-SvetlanaNeural")
  assert m["engine"] in ("edge-tts","azure-speech")
  pcm=np.frombuffer(ff("-i",mp3,"-ar",SR,"-ac","1","-f","f32le","pipe:1"),dtype="<f4").copy()
  nz=np.where(np.abs(pcm)>.002)[0]
  if len(nz):pcm=pcm[max(0,nz[0]-int(.03*SR)):min(len(pcm),nz[-1]+int(.15*SR))]
  pad=.17 if i<11 else .55
  # Additional pause before reveal and punchline
  if i in (0,3,7,10):pad=.3
  starts.append(duration)
  duration+=(len(pcm)/SR)+pad
  tracks.append((pcm,pad))
  manifest.append({"id":l["id"],"speaker":m.get("speaker"),"voice_id":m["voice_id"],"engine":m["engine"],"rate":m.get("rate"),"source_file":str(mp3),"start":round(starts[-1],3),"duration":round(len(pcm)/SR,3)})
 n=round(duration*SR);a=np.zeros(n,dtype=np.float32)
 for s,(pcm,pad) in zip(starts,tracks):
  v=round(s*SR);a[v:v+len(pcm)]=pcm
 peak=np.max(np.abs(a))
 if peak<.005:raise RuntimeError("Voice is silent")
 a=a/peak*.77
 bg=np.zeros(n,dtype=np.float32)
 pitches=[196,247,294,220,262,330,294,247]
 for k in range(math.ceil(duration/.43)):
  st=round(k*.43*SR);z=np.arange(min(round(.26*SR),n-st),dtype=np.float32)/SR
  q=np.sin(2*np.pi*pitches[k%len(pitches)]*z)+.25*np.sin(2*np.pi*2*pitches[k%len(pitches)]*z)
  bg[st:st+len(z)]+=.042*q*np.exp(-14*z)
 for i,s in enumerate(starts):
  if i not in (0,4,5,7,10,11):continue
  st=round(s*SR);z=np.arange(min(round(.2*SR),n-st),dtype=np.float32)/SR
  bg[st:st+len(z)]+=.07*np.sin(2*np.pi*(600-240*z)*z)*np.exp(-20*z)
 # Smooth mix with a music fade during speech; voice itself is always dominant.
 out=np.clip(a+bg,-.96,.96)
 wavepath=HERE/"voice_mix.wav"
 with wave.open(str(wavepath),"wb") as w:
  w.setparams((1,2,SR,0,"NONE","not compressed"))
  w.writeframes((out*32767).astype("<i2").tobytes())
 (HERE/"voice_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 return wavepath,starts,duration,manifest
def ground(d,t):
 d.rectangle((0,0,W,H),fill=BG)
 for x in range(-60,W+100,48):
  xx=x+int((t*7)%48)
  d.line((xx,0,xx,H),fill="#1C2A3A",width=1)
 for y in range(-50,H+70,48):
  yy=y+int((t*10)%48)
  d.line((0,yy,W,yy),fill="#1C2A3A",width=1)
 for k in range(18):
  x=(k*177+21*math.sin(t*.7+k))%W;y=(k*213+8*t*(1+k%3))%H
  d.ellipse((x,y,x+2,y+2),fill="#366075")
def panel(d):
 rr(d,(26,195,514,715),"#E7F0F2",30)
def checkbox(d,t):
 panel(d)
 text(d,"ПОДТВЕРЖДЕНИЕ",239,"#233648",31,438)
 text(d,"входа в аккаунт",291,"#61778A",21,430)
 rr(d,(75,355,466,460),"#CEDAE4",17)
 rr(d,(104,377,155,428),"#FFFFFF",7,"#8298AA",3)
 text(d,"Я не робот",386,"#22364A",26,350,x=181)
 # cursor moves decisively to checkbox
 pp=min(1,t/1.3);xx=260-112*pp;yy=510-110*pp
 d.polygon([(xx,yy),(xx+26,yy+12),(xx+12,yy+17),(xx+16,yy+31)],fill=RED)
 if t>1.45:
  d.text((112,380),"✓",font=font(34),fill="#24A995")
 rr(d,(75,559,465,621),"#D1E0E9",13)
 text(d,"ЗАЩИТА ОТ БОТОВ",575,"#526A7D",24,360)
def traffic(d,x,y,c,active):
 rr(d,(x,y,x+138,y+106),"#B9D6D7",8)
 d.rectangle((x,y+61,x+138,y+106),fill="#91AF9D")
 d.polygon([(x+20,y+106),(x+62,y+55),(x+81,y+55),(x+119,y+106)],fill="#6C919E")
 d.line((x+70,y+32,x+70,y+92),fill="#426374",width=5)
 rr(d,(x+57,y+9,x+83,y+64),"#152D3C",7)
 for j,fill in enumerate((RED,GOLD,CYAN)):
  d.ellipse((x+66,y+17+j*14,x+74,y+25+j*14),fill=fill)
 if active:
  rr(d,(x+1,y+1,x+137,y+105),None,8,CYAN,4)
  d.text((x+9,y+7),"✓",font=font(18),fill=CYAN)
def captcha(d,t,retry):
 panel(d)
 rr(d,(39,208,501,326),BLUE,17)
 d.text((60,221),"ПРОВЕРКА",font=font(29),fill=WHITE)
 d.text((60,259),"Выберите все квадраты",font=font(19),fill=WHITE)
 d.text((60,282),"со светофорами",font=font(22),fill=WHITE)
 for i in range(9):
  row,col=divmod(i,3);traffic(d,61+col*143,337+row*113,i,i in (0,2,4,6) and (t>.7))
 rr(d,(348,679,479,710),BLUE,8)
 d.text((352,685),"ПРОВЕРИТЬ",font=font(16),fill=WHITE)
 if retry:
  # Keep the retry alert strictly above the subtitle safe zone (y >= 760).
  rr(d,(48,721,492,755),RED,10)
  text(d,"ОПЯТЬ НЕВЕРНО",726,BG,23,400)
def robot(d,t,yes=False):
 rr(d,(30,215,510,720),"#1C3447",29,CYAN,4)
 text(d,"ИИ-ПОМОЩНИК",253,CYAN,31,430)
 cy=410+8*math.sin(t*4)
 d.line((273,cy-12,273,cy-43),fill=CYAN,width=6)
 d.ellipse((264,cy-55,282,cy-37),fill=GOLD)
 rr(d,(187,cy,358,cy+185),"#112438",34,CYAN,5)
 rr(d,(214,cy+43,330,cy+111),"#27485B",18)
 for x in (247,299):d.ellipse((x-11,cy+70,x+11,cy+90),fill=CYAN)
 d.arc((235,cy+86,307,cy+147),10,170,fill=WHITE,width=5)
 d.arc((98,cy+64,204,cy+213),211,345,fill=BLUE,width=7)
 d.arc((333,cy+64,450,cy+213),190,326,fill=BLUE,width=7)
 rr(d,(85,645,455,705),("#244E48" if yes else BLUE),17)
 text(d,"✓ ГОТОВО ЗА 0,01 С" if yes else "РЕШИТЬ КАПЧУ",660,WHITE,28,335)
def error(d,t,first=False):
 shake=int(7*(1-min(1,t))*math.sin(t*42))
 rr(d,(33+shake,222,507+shake,727),"#352733",26,RED,5)
 d.polygon([(270,292),(365,490),(177,490)],fill=RED)
 text(d,"!",363,BG,78,180)
 text(d,"ОШИБКА 403" if not first else "БЛОКИРОВКА",536,WHITE,37,436)
 text(d,"ОБНАРУЖЕН БОТ" if not first else "ТЫ НЕ ЧЕЛОВЕК",594,RED,34,440)
 rr(d,(77,662,460,707),"#71384C",12)
 text(d,"ДОСТУП ЗАПРЕЩЁН",671,WHITE,23,350)
def loop(d,t):
 rr(d,(37,214,505,725),"#203747",29,CYAN,3)
 labs=["ЧЕЛОВЕК","БОТ","КАПЧА"]
 for k,v in enumerate(labs):
  a=t*.8+k*2*math.pi/3
  x=270+142*math.cos(a);y=479+142*math.sin(a)
  rr(d,(x-77,y-49,x+77,y+49),BLUE if k==0 else "#364C60",19)
  txt=font(18);width=d.textbbox((0,0),v,font=txt)[2]
  d.text((x-width/2,y-11),v,font=txt,fill=WHITE)
 d.arc((133,332,408,635),0,335,fill=CYAN,width=9)
def outro(d,t):
 rr(d,(40,218,500,727),"#1B2C40",30,CYAN,3)
 text(d,"M1LASH",315,WHITE,85,438)
 text(d,"СПАСИБО ЗА ПРОСМОТР!",432,"#BDD3DE",23,420)
 pulse=5*math.sin(t*5)
 rr(d,(90-pulse,525,450+pulse,618),RED,20)
 text(d,"ПОДПИСАТЬСЯ",541,BG,37,330)
 text(d,"♥  ЛАЙК",654,CYAN,24,280)
def draw(i,t,progress):
 im=Image.new("RGB",(W,H));d=ImageDraw.Draw(im)
 ground(d,t)
 rr(d,(24,22,516,103),"#1D2E42",17,"#365268",2)
 d.ellipse((42,47,57,62),fill=CYAN)
 d.text((70,43),"M1LASH  /  ПРИТВОРИСЬ БОТОМ",font=font(18),fill=WHITE)
 d.text((427,78),"03 / 03",font=font(12),fill="#A3B7C9")
 rr(d,(26,118,514,126),"#31465B",4)
 rr(d,(26,118,26+488*progress,126),CYAN,4)
 title,subtitle,mode=SCENES[i]
 text(d,title,153,RED if i in (0,7,10) else CYAN,34,496)
 if mode=="checkbox":checkbox(d,t)
 elif mode=="captcha":captcha(d,t,i==3)
 elif mode=="robot":robot(d,t,i==5)
 elif mode=="approved":
  robot(d,t,True)
 elif mode=="error":error(d,t,i==0)
 elif mode=="loop":loop(d,t)
 else:outro(d,t)
 if mode!="outro":
  rr(d,(25,760,515,855),"#0B1322",22)
  text(d,subtitle,784,WHITE,27,457)
  rr(d,(28,878,512,926),"#1D2E41",11)
  d.text((49,891),"ДИМА" if i not in (2,5,7,9) else "СИСТЕМА",font=font(17),fill=CYAN if i not in (2,5,7,9) else GOLD)
 else:text(d,"КАПЧА ТЕБЯ ТОЖЕ БЕСИТ?",824,WHITE,24,488)
 return im
def main():
 OUT.parent.mkdir(parents=True,exist_ok=True)
 wav,starts,total,manifest=dur_audio()
 # Most important gate: the full approved speech including CTA determines video duration.
 frames=math.ceil(total*FPS)
 cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(wav),"-vf","scale=1080:1920:flags=lanczos,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","20","-c:a","aac","-b:a","160k","-ar","48000","-shortest","-movflags","+faststart",str(OUT)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 try:
  for n in range(frames):
   now=n/FPS
   i=max(0,min(11,int(np.searchsorted(starts,now,side="right")-1)))
   im=draw(i,now-starts[i],now/total)
   p.stdin.write(im.tobytes())
  p.stdin.close();err=p.stderr.read();code=p.wait()
  if code:raise RuntimeError(err.decode(errors="replace")[-2000:])
 except Exception:
  p.kill();raise
 probe=json.loads(ffprobe(OUT))
 vd=float(probe["format"]["duration"])
 result={"status":"RENDERED_REVIEW_PENDING","seconds":round(vd,2),"voices":sorted(set(v["voice_id"] for v in manifest)),"resolution":"1080x1920","voice_count":len(manifest),"script":"S6-D25","file":str(OUT)}
 (HERE/"QA.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
 print(json.dumps(result,ensure_ascii=False))
def ffprobe(p):
 return subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(p)])
if __name__=="__main__":main()
