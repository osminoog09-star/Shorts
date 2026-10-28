#!/usr/bin/env python3
"""M1lash Neurooffice episode: original frame-by-frame 2D artwork.
Not a slide export. Every frame draws characters, backgrounds, acting, props and camera.
Sound and timing MUST come from the approved Edge voice manifest.
Artistic quality still requires manual review, even when engineering QA passes.
"""
import argparse,bisect,hashlib,json,math,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
AUDIO=HERE/"audio"/"NEUROOFFICE_S01E01_DIMA_SVETA.m4a"
MANIFEST=HERE/"audio"/"AUDIO_MANIFEST.json"
OUT=HERE/"production"/"render"
W,H=960,540
INK="#111d2c"; CREAM="#fcf0dd"; CYAN="#64e6d8"; RED="#ed7484"
FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FF={}
for n in (14,16,18,20,24,28,32,36,42,52,66):
 FF[n]=ImageFont.truetype(BOLD,n)
def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)
def rr(d,b,c,r=12,o=None,w=2):d.rounded_rectangle(tuple(int(v) for v in b),radius=int(r),fill=c,outline=o,width=w)
def e(d,b,c,o=None,w=2):d.ellipse(tuple(int(v) for v in b),fill=c,outline=o,width=w)
def l(d,p,c,w=3):d.line([(int(x),int(y)) for x,y in p],fill=c,width=w,joint="curve")
def p(d,pts,c,o=None,w=2):
 pts=[(int(x),int(y)) for x,y in pts];d.polygon(pts,fill=c)
 if o:d.line(pts+[pts[0]],fill=o,width=w,joint="curve")
def text(d,xy,s,n=22,c=CREAM,anchor="mm"):
 s=str(s)
 d.text(xy,s,font=FF[n],fill=c,anchor=anchor,stroke_width=1,stroke_fill="#081521")
def person_sprite(t,who,spoken,pose="normal",scale=1):
 I=Image.new("RGBA",(260,440),(0,0,0,0));d=ImageDraw.Draw(I)
 s=math.sin(t*2.4)*1.4;hands=math.sin(t*.8)*5
 skin="#e4a987" if who!="marina" else "#cf9078"
 coat="#2d8394" if who=="dima" else "#a26081" if who=="marina" else "#80624e"
 coat2="#204e63" if who=="dima" else "#703e62"
 hair="#26344b" if who=="dima" else "#49323d"
 # grounded shoes and legs, independent motion and breathing
 e(d,(55,418,200,434),"#07101e88")
 for x in (92,151):
  l(d,[(x,319),(x+4*math.sin(t*1.2+x),410)],"#152739",20)
  rr(d,(x-25,398,x+28,422),"#16263b",9,"#0d1a2a",2)
 # layered jacket with structured, asymmetrical fabric
 p(d,[(123,219),(88,226),(53,245),(54,323),(82,358),(180,361),(212,320),(210,248),(178,226)],coat,INK,3)
 p(d,[(70,238),(95,229),(118,348),(83,343)],coat2)
 p(d,[(185,231),(164,230),(136,348),(181,340)],"#4d9fab" if who=="dima" else "#9c748d")
 p(d,[(111,221),(127,245),(144,221),(156,230),(147,342),(108,342)],"#e9e9dd")
 p(d,[(123,240),(137,252),(130,314),(121,324),(116,307),(119,252)],"#345b6c")
 for y in (278,303):e(d,(159,y,164,y+6),"#e8c188")
 # arms: independent elbow/wrist geometry, explicit palms + fingers
 for side in (-1,1):
  shoulder=(130+side*63,243)
  amt=(.65 if side>0 else .35)*spoken+.15*math.sin(t*1.9+side)
  elbow=(130+side*(89-16*amt),296-13*amt+s)
  hand=(130+side*(77-38*amt),354-73*amt+hands)
  l(d,[shoulder,elbow],INK,25);l(d,[shoulder,elbow],coat,19)
  e(d,(elbow[0]-9,elbow[1]-9,elbow[0]+9,elbow[1]+9),coat2)
  l(d,[elbow,hand],INK,21);l(d,[elbow,hand],coat2,15)
  e(d,(hand[0]-9,hand[1]-10,hand[0]+9,hand[1]+10),skin,INK,2)
  for fi in (-1,0,1):
   l(d,[(hand[0]+fi*4,hand[1]+5),(hand[0]+fi*6,hand[1]+14)],skin,3)
 # neck and cheek: curved more appealing shape
 rr(d,(117,205,143,249),skin,9)
 e(d,(85,92,174,215),skin,INK,3)
 e(d,(83,144,100,173),skin,INK,2)
 e(d,(168,144,183,173),skin,INK,2)
 p(d,[(92,157),(93,113),(112,92),(147,87),(169,105),(176,146),(166,135),(146,129),(128,139),(110,127),(94,147)],hair,INK,3)
 p(d,[(96,109),(121,96),(139,104),(115,117)],"#534455")
 # direction of gaze and brow asymmetry
 gaze=3*math.sin(t*.74+(.8 if who=="marina" else 0))
 blink=(t+(1.1 if who=="marina" else 0))%4.1<.13
 for x in (110,152):
  y=152+(1 if x>130 else 0)
  l(d,[(x-11,y-21+2*math.sin(t*.7)),(x+8,y-22)],hair,3)
  if blink:l(d,[(x-11,y),(x+10,y)],INK,3)
  else:
   e(d,(x-10,y-8,x+10,y+9),"#fff4e6",INK,2)
   e(d,(x-3+gaze,y-3,x+5+gaze,y+8),"#45687c")
   e(d,(x+gaze,y-1,x+3+gaze,y+5),"#142c3e")
   e(d,(x+2+gaze,y-2,x+4+gaze,y),"#ffffff")
 p(d,[(129,158),(135,181),(127,185),(122,181)],"#bd836e")
 if spoken:
  height=5+int(11*(.5+.5*math.sin(t*13)**2))
  e(d,(119,192,141,194+height),"#754454")
  e(d,(125,199,135,199+height*.6),"#d8919b")
 elif pose=="smile":d.arc((116,186,145,208),0,180,fill="#76404a",width=3)
 elif pose=="fear":e(d,(126,190,136,202),"#714052")
 else:l(d,[(120,196),(130,197),(139,195)],"#794a4c",2)
 # integrated rim light keeps consistency across camera positions
 l(d,[(171,131),(175,158),(170,183)],"#f4c2a0",2)
 width,height=round(260*scale),round(440*scale)
 return I.resize((width,height),Image.Resampling.BICUBIC)
def robot_sprite(t,speaking,alert=False,scale=1):
 I=Image.new("RGBA",(280,440));d=ImageDraw.Draw(I)
 bob=math.sin(t*1.7)*3
 e(d,(58,420,232,438),"#06101e77")
 # wheels/legs and pistons
 for x in (94,187):
  rr(d,(x-28,365,x+30,428),"#39546b",11,INK,3)
  rr(d,(x-13,385,x+12,421),"#55cfc6",5)
 p(d,[(78,212),(204,212),(238,238),(240,332),(208,383),(77,382),(43,336),(46,244)],"#739da6",INK,4)
 p(d,[(84,233),(201,231),(217,260),(215,333),(194,355),(89,354),(67,332),(67,260)],"#bed6ce")
 rr(d,(111,273,175,335),"#233e54",16,INK)
 rr(d,(128,291,160,319),CYAN,8)
 rr(d,(136,301,151,310),"#ecfff9",4)
 # independent hinge arms and fingers
 for side in (-1,1):
  shoulder=(142+side*90,247);n=8+13*math.sin(t*1.9+side)
  elbow=(142+side*(107+n),310);hand=(142+side*(101-25*speaking),371-51*speaking if side>0 else 376)
  l(d,[shoulder,elbow],INK,28);l(d,[shoulder,elbow],"#83adb5",20)
  e(d,(elbow[0]-14,elbow[1]-14,elbow[0]+14,elbow[1]+14),"#31536b",INK)
  e(d,(elbow[0]-5,elbow[1]-5,elbow[0]+5,elbow[1]+5),CYAN)
  l(d,[elbow,hand],INK,21);l(d,[elbow,hand],"#b0ccc8",15)
  rr(d,(hand[0]-12,hand[1]-8,hand[0]+12,hand[1]+10),"#31546b",5,INK,2)
  for f in (-1,0,1):l(d,[(hand[0]+f*7,hand[1]+7),(hand[0]+f*10,hand[1]+18)],"#99c4bd",3)
 rr(d,(75,95+bob,207,220+bob),"#90b9be",37,INK,4)
 rr(d,(86,108+bob,197,207+bob),"#dce3dc",28,"#7195a2",3)
 rr(d,(96,119+bob,188,193+bob),"#152e42",24,INK,2)
 for x in (120,165):
  e(d,(x-11,144+bob,x+11,163+bob),"#2f5363")
  e(d,(x-7,148+bob,x+6,159+bob),RED if alert else CYAN)
  e(d,(x-5,148+bob,x-2,151+bob),"#f9fffb")
 if speaking:
  for j in range(4):
   v=3+9*math.sin(t*10+j*.8)**2
   rr(d,(116+j*15,174+bob-v/2,124+j*15,174+bob+v/2),RED if alert else CYAN,3)
 elif alert:rr(d,(121,173+bob,174,180+bob),RED,3)
 else:d.arc((119,160+bob,178,187+bob),0,180,fill=CYAN,width=4)
 l(d,[(140,95+bob),(140,82+bob)],"#76a3ad",7)
 e(d,(133,73+bob,147,87+bob),RED if alert else CYAN)
 # highlights and badges are physical pieces, not style labels
 l(d,[(92,135+bob),(102,117+bob),(121,111+bob)],"#fff5e7",3)
 l(d,[(195,208+bob),(204,195+bob)],"#bee2df",3)
 return I.resize((round(280*scale),round(440*scale)),Image.Resampling.BICUBIC)
SCENE_KEYS=[
"button","boardroom","security","payroll","client","canteen","elevator","investors",
"marketing","break","courier","help","override","owner","audit","city"]
BG_CACHE={}
def background(scene):
 if scene in BG_CACHE:return BG_CACHE[scene]
 I=Image.new("RGB",(W,H),"#12243a");d=ImageDraw.Draw(I)
 for y in range(H):
  ratio=y/H;d.line((0,y,W,y),fill=(int(12+15*ratio),int(29+27*ratio),int(48+30*ratio)))
 # window frames with skyline, naturally varied architecture
 for k in range(6):
  x=25+k*166;rr(d,(x,48,x+145,318),"#102b42",15,"#5d8291",3)
  for b in range(5):
   xx=x+10+b*28;height=50+((b*39+k*71)%119)
   rr(d,(xx,305-height,xx+23,306),"#1e3c55",2)
   for win in range(4):
    if (win+k+b)%3:rr(d,(xx+8,312-height+win*22,xx+15,323-height+win*22),"#c4a676",2)
  l(d,[(x+72,52),(x+72,316)],"#557c8b",3)
 d.polygon([(0,340),(W,319),(W,H),(0,H)],fill="#25384c")
 for xx in range(-350,W+350,120):l(d,[(xx,H),(W/2+(xx-W/2)*.3,331)],"#4b6070",2)
 for yy in (370,424,488):l(d,[(0,yy+30),(W,yy-15)],"#44596c",2)
 # stronger prop-specific geography; no one universal office set
 if scene in {"button","override"}:
  for xx in (30,250,720):rr(d,(xx,74,xx+200,314),"#12273a",10,"#71929e")
 elif scene in {"canteen","break","help"}:
  rr(d,(21,293,939,335),"#a8876d",10)
  rr(d,(65,335,100,520),"#4a5968");rr(d,(876,335,912,520),"#4a5968")
 elif scene in {"courier","client","security"}:
  rr(d,(630,90,855,377),"#273e50",17,"#94bac3",3)
 elif scene=="city":
  # exterior skyline and glowing traffic planes behind enormous smart-city map
  for i in range(24):
   xx=i*46;h=60+(i*43)%220
   rr(d,(xx,340-h,xx+43,342),"#183d58",2)
 if scene in {"payroll","investors","marketing","audit","boardroom"}:
  rr(d,(520,105,888,316),"#071f31",15,"#6fa1b0",3)
  for k in range(6):
   c=RED if k>3 and scene in {"audit","payroll"} else CYAN
   rr(d,(565+k*48,272-(k*41+24)%113,586+k*48,290),c,6)
  l(d,[(550,291),(870,291)],"#a6c8d0",3)
 BG_CACHE[scene]=I
 return I
def props(I,scene,t,shot=0):
 d=ImageDraw.Draw(I)
 pulse=(math.sin(t*3)+1)/2
 if scene in ("button","override"):
  rr(d,(540,275,830,406),"#24374e",32)
  rr(d,(559,265+8*ease(t/3),809,354+8*ease(t/3)),"#c23f58",31,"#ef8894",4)
  text(d,(683,313+8*ease(t/3)),"УВОЛИТЬ ВСЕХ" if scene=="button" else "ОТМЕНИТЬ",20,"#fff4eb")
  if t>2 and scene=="button":rr(d,(554,356,817,384),"#602f43",9)
 elif scene=="security":
  rr(d,(640,196,831,330),"#173448",11,"#85b6c0")
  text(d,(735,251),"ДОСТУП",28,CYAN);text(d,(735,293),"ОТКАЗАНО",20,RED)
 elif scene=="payroll":
  text(d,(692,139),"ПРЕМИИ +240%",20,CYAN)
 elif scene=="client":
  rr(d,(546,142,880,307),"#e5e4d6",12)
  text(d,(714,174),"ПИСЬМО КЛИЕНТА",20,"#20384c")
  for k in range(5):rr(d,(565,205+k*17,853-k*11,211+k*17),"#587886",3)
  rr(d,(590,281,818,305),"#ac5261",7)
 elif scene=="elevator":
  for x in (530,720):rr(d,(x,125,x+150,355),"#667a88",7,"#a2b6b4",3)
  rr(d,(670,142,687,323),"#1e3047",3)
  text(d,(700,111),"VIP ЛИФТ",22,CYAN)
 elif scene=="marketing":
  text(d,(702,146),"ПРОДАЖИ",22,CYAN)
  text(d,(692,300),"ПРОГНОЗ ≠ ОПЛАТА",16,RED)
 elif scene=="courier":
  rr(d,(617,261,877,332),"#8b6b4a",5)
  for i in range(5):l(d,[(632+i*48,277),(632+i*48,327)],"#5b462f",3)
  text(d,(751,304),"ЗАКАЗ",24,"#e7d7bb")
 elif scene=="help":
  rr(d,(607+6*math.sin(t),269,820,361),"#b28453",8,"#784a2e",3)
  text(d,(714,305),"ХРУПКО",24,"#f3e4c6")
 elif scene=="owner":
  rr(d,(533,144,850,321),"#273847",15,"#d4bca4",3)
  e(d,(651,163,728,241),"#cda28a")
  text(d,(686,281),"ВЛАДЕЛЕЦ НА СВЯЗИ",16,CREAM)
 elif scene=="audit":
  text(d,(697,160),"ЦЕНА ОШИБКИ",20,RED)
 elif scene=="city":
  rr(d,(518,75,891,337),"#0a2138",17,"#648caa",3)
  for i in range(8):
   xx=548+i*40;yy=120+(i*71)%140
   e(d,(xx,yy,xx+12,yy+12),RED if i>4 else CYAN)
  text(d,(706,300),"ЗАВТРА 09:00",28,RED)
 elif scene=="break":
  rr(d,(585,115,863,286),"#132c45",14,"#6a9aa6")
  text(d,(729,183),"ПЕРЕРЫВ",24,CYAN)
  text(d,(722,237),"ТРЕБУЕТСЯ ОПЛАТА",16,RED)
 elif scene=="canteen":
  rr(d,(578,146,866,309),"#9caaad",14,INK)
  text(d,(725,198),"МЕНЮ ДНЯ",22,"#193448")
  text(d,(725,254),"ОПТИМИЗИРОВАНО",16,"#31546b")
def caption(d,entry,local):
 # Burn short readable phrases. Durations derived from original Edge word boundaries.
 words=entry.get("words") or []
 if not words:return
 started=entry["start_s"];t=started+local
 w=[v for v in words if v["at_s"]<=t+.05]
 if not w:return
 # Stable three-to-seven word group, avoiding flashing on each word.
 j=min(len(words)-1,len(w)-1)
 a=max(0,(j//6)*6);b=min(len(words),a+6)
 phrase=" ".join(x["word"] for x in words[a:b]).strip()
 if not phrase:return
 if len(phrase)>51:phrase=phrase[:48].rsplit(" ",1)[0]+"…"
 rr(d,(161,442,804,516),"#081728",17,"#41687d",2)
 text(d,(483,478),phrase,24,CREAM)
def draw_frame(global_t,entries,starts):
 entry_id=max(0,min(len(entries)-1,bisect.bisect_right(starts,global_t)-1))
 entry=entries[entry_id];scene=entry["scene"]
 scene= max(0,min(len(SCENE_KEYS)-1,int(scene)))
 first=next((e["start_s"] for e in entries if e["scene"]==scene),entry["start_s"])
 local=global_t-first
 kind=SCENE_KEYS[scene]
 I=background(kind).copy()
 # four motivated compositional states, with live acting in all states
 shot=int(local//6)%4
 speaker=entry["speaker"]
 spoken=entry["start_s"]<=global_t<entry["end_s"]
 # choose meaningful reaction: spoken person in foreground, listener responds silently
 if shot==0:
  xh=130+7*math.sin(local*.5);xr=705+9*math.sin(local*.3);hs=1.0;rs=.78
 elif shot==1:
  xh=230;xr=810;hs=1.24;rs=.7
 elif shot==2:
  xh=70;xr=650;hs=.78;rs=1.16
 else:
  xh=125;xr=755;hs=.95;rs=.9
 robot_alert=kind in {"button","override","audit","city"}
 human=person_sprite(global_t,"dima",1 if speaker=="dima" and spoken else 0,
    "fear" if kind in {"button","override"} else "normal",hs)
 robot=robot_sprite(global_t,1 if speaker=="sveta" and spoken else 0,robot_alert,rs)
 I.paste(human,(int(xh),int(456-human.height)),human)
 I.paste(robot,(int(xr),int(474-robot.height)),robot)
 props(I,kind,local,shot)
 d=ImageDraw.Draw(I)
 # Narrative chapter label only in first 3 seconds, no debug/style tags.
 if local<3 and int(global_t*2)%9<7:
  rr(d,(25,21,429,76),"#091a2c",13)
  text(d,(224,47),"НЕЙРООФИС",32,CREAM)
 # No decorative progress bar or fake lower-left labels.
 caption(d,entry,global_t-entry["start_s"])
 return I
def run(*args):
 p=subprocess.run(args,capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr[-4000:])
 return p.stdout
def main():
 ap=argparse.ArgumentParser()
 ap.add_argument("--preview-seconds",type=float,default=0)
 ap.add_argument("--fps",type=int,default=15)
 ap.add_argument("--crf",type=int,default=23)
 args=ap.parse_args()
 if not AUDIO.is_file() or not MANIFEST.is_file():raise SystemExit("NO-GO approved voice master/manifest missing")
 metadata=json.loads(MANIFEST.read_text("utf-8"));entries=metadata["timeline"];starts=[x["start_s"] for x in entries]
 total=float(metadata["audio_duration_s"])
 if total<1 or len(entries)<50:raise SystemExit("NO-GO audio incomplete")
 if not args.preview_seconds and total<1260:raise SystemExit("NO-GO full episode below 21min; expand real story first")
 end=min(total,args.preview_seconds) if args.preview_seconds else total
 OUT.mkdir(parents=True,exist_ok=True)
 basename="NEUROOFFICE_EP01_PREVIEW.mp4" if args.preview_seconds else "NEUROOFFICE_S01E01_FILM_CANDIDATE.mp4"
 silent=OUT/("silent_preview.mp4" if args.preview_seconds else "silent_full.mp4")
 final=OUT/basename
 fps=args.fps
 proc=subprocess.Popen(["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24",
  "-s",f"{W}x{H}","-r",str(fps),"-i","pipe:0","-an","-vf",
  "scale=1920:1080:flags=lanczos,fps=30","-c:v","libx264","-preset","veryfast",
  "-crf",str(args.crf),"-pix_fmt","yuv420p","-movflags","+faststart",str(silent)],stdin=subprocess.PIPE)
 shots=[]
 for n in range(round(end*fps)):
  t=n/fps;image=draw_frame(t,entries,starts)
  if n%(fps*12)==0 and len(shots)<25:shots.append(image.copy())
  proc.stdin.write(image.tobytes())
  if n and n%(fps*60)==0:print(f"RENDER {n/fps:.0f}/{end:.1f} sec",flush=True)
 proc.stdin.close()
 if proc.wait():raise SystemExit("NO-GO frame encoder failed")
 run("ffmpeg","-nostdin","-v","error","-y","-i",str(silent),"-i",str(AUDIO),"-t",f"{end:.3f}",
  "-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",str(final))
 run("ffmpeg","-nostdin","-v","error","-xerror","-i",str(final),"-f","null","-")
 sheet=Image.new("RGB",(5*240,math.ceil(len(shots)/5)*135),"#142436")
 for i,im in enumerate(shots):sheet.paste(im.resize((240,135)),((i%5)*240,(i//5)*135))
 sheet.save(OUT/("PREVIEW_CONTACT.jpg" if args.preview_seconds else "FILM_CONTACT.jpg"),quality=88)
 actual=json.loads(run("ffprobe","-v","error","-show_entries","format=duration","-of","json",str(final)))
 sec=float(actual["format"]["duration"])
 status="PREVIEW_ONLY" if args.preview_seconds else "DRAFT_REQUIRES_HUMAN_VISUAL_QA"
 if not args.preview_seconds and sec<1260:raise SystemExit("NO-GO actual MP4 under 21min")
 audit={"status":status,"duration_seconds":sec,"fps_output":30,"fps_authored":fps,
  "resolution":"1920x1080","visual_style":"fully generated procedural code 2D",
  "audio":"approved exact original Edge TTS Dima and Sveta","human_review":"NOT COMPLETED",
  "full_decode":"PASS","sha256":hashlib.sha256(final.read_bytes()).hexdigest(),
  "youtube_upload":"NONE"}
 (OUT/("PREVIEW_QA.json" if args.preview_seconds else "FILM_QA.json")).write_text(json.dumps(audit,ensure_ascii=False,indent=2))
 print(json.dumps(audit,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
