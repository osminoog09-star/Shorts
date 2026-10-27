#!/usr/bin/env python3
"""M1lash original moving comic, 16:9, 12fps drawn-animation, source-art and voice only.
Owner voice fixed to Microsoft DmitryNeural. No silent fallbacks and no auto-upload.
"""
import bisect, json, math, os, random, subprocess, sys, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

ROOT=Path(__file__).resolve().parent
PROJECT=json.loads((ROOT/"episode.json").read_text("utf-8"))
VOICES=json.loads((ROOT/"voice/manifest.json").read_text("utf-8"))
assert VOICES["voice"]=="ru-RU-DmitryNeural"
scenes=PROJECT["scenes"]
assert len(scenes)==len(VOICES["scenes"])
W,H,FPS=960,540,12
FPS_OUT=24
WORK=ROOT/"output";WORK.mkdir(exist_ok=True)
VIDEO=ROOT/"M1lash_AI_OFFICE_LONG_RU.mp4"
FONTREG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTBOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,b=True):return ImageFont.truetype(FONTBOLD if b else FONTREG,int(n))
def put(d,xy,text,size=22,color=(238,246,255),bold=True,anchor=None,stroke=0):
    d.text(xy,str(text),font=font(size,bold),fill=color,anchor=anchor,
           stroke_width=stroke,stroke_fill=(3,4,10))
def safe(t,d,size,maxw):
    text=str(t)
    while text and d.textbbox((0,0),text,font=font(size))[2]>maxw:
        text=text[:-2]+"…"
    return text
def rnd(d,rect,fill,r=12,outline=None,width=1):d.rounded_rectangle(rect,radius=r,fill=fill,outline=outline,width=width)
def col(name):
    return {"office":(24,55,82),"boardroom":(35,48,82),"sales":(39,77,102),"finance":(30,57,65),
    "hr":(83,49,80),"security":(58,63,82),"server":(19,53,69),"compliance":(67,52,80),
    "startup":(38,58,87),"support":(27,61,86),"corridor":(57,58,70),"recruitment":(58,55,88),
    "studio":(37,40,74)}.get(name,(39,56,82))
def backdrop(place):
    base=Image.new("RGB",(W,H),(11,17,34)); p=base.load()
    a,b,c=col(place)
    for yy in range(H):
        f=1-abs(yy/H-.42)*.52
        cc=(int(a*f),int(b*f),int(c*f))
        for xx in range(W):p[xx,yy]=cc
    d=ImageDraw.Draw(base,"RGBA")
    # Environment contains depth planes, window frames, central action space.
    d.polygon([(0,370),(960,320),(960,540),(0,540)],fill=(9,15,29,235))
    for xx in (80,325,570,815):
        rnd(d,(xx,90,xx+155,295),(10,28,54,215),13,outline=(86,150,190,115),width=3)
        d.line((xx+78,95,xx+78,285),fill=(60,117,159,120),width=3)
        d.line((xx+4,194,xx+151,194),fill=(56,126,180,88),width=2)
        for j in range(4):
            d.rectangle((xx+10+j*34,236,xx+29+j*34,245),fill=(255,204,96,25))
    for xx in range(0,1100,125):
        d.line((xx,390,xx-180,540),fill=(66,114,142,65),width=2)
    d.line((0,373,960,325),fill=(75,140,179,116),width=5)
    if place in ("finance","server","compliance"):
        for xx in range(120,940,200):
            rnd(d,(xx,100,xx+113,311),(10,27,43,245),9,outline=(61,220,197,110),width=3)
            for row in range(11):
                d.line((xx+15,120+row*15,xx+97,120+row*15),fill=(35,138,152,100),width=3)
                d.ellipse((xx+90,113+row*15,xx+97,120+row*15),fill=(75,230,185,160))
    if place=="security":
        rnd(d,(165,145,795,310),(23,35,55,220),14,outline=(254,165,96,170),width=3)
        put(d,(480,166),"ВХОД ПОД КОНТРОЛЕМ",27,(255,186,110),anchor="mt")
    if place=="boardroom":
        d.ellipse((130,308,850,445),fill=(21,35,50,220),outline=(94,150,181,130),width=5)
    if place=="startup":
        rnd(d,(210,110,750,303),(11,29,49,215),20,outline=(125,155,255,140),width=4)
        put(d,(480,161),"НЕООПТИМУС",39,(203,208,255),anchor="mt")
    return base

def director(d,x,y,t,scale=1,expression="worried"):
    # A fully original cartoon suit character with animated hand/head/expression.
    b=math.sin(t*3)*3
    x=int(x);y=int(y+b);s=scale
    def q(a):return round(a*s)
    # shadow/body, tie, arms
    d.ellipse((x-q(105),y-q(4),x+q(107),y+q(19)),fill=(0,0,0,120))
    d.polygon([(x-q(73),y-q(200)),(x+q(74),y-q(200)),(x+q(100),y-q(8)),(x-q(100),y-q(8))],fill=(20,36,63,255))
    d.line((x-q(88),y-q(165),x-q(122),y-q(66)+q(math.sin(t*2)*7)),fill=(241,178,145,255),width=q(15))
    d.line((x+q(90),y-q(161),x+q(123),y-q(103)+q(math.sin(t*2)*8)),fill=(241,178,145,255),width=q(15))
    d.polygon([(x-q(32),y-q(202)),(x+q(32),y-q(202)),(x+q(17),y-q(101)),(x-q(18),y-q(101))],fill=(240,240,233,255))
    d.polygon([(x,y-q(168)),(x-q(10),y-q(144)),(x,y-q(80)),(x+q(12),y-q(144))],fill=(248,91,130,255))
    d.rounded_rectangle((x-q(54),y-q(319),x+q(53),y-q(211)),radius=q(38),fill=(250,189,149,255))
    # sparse dark hair
    d.pieslice((x-q(60),y-q(331),x+q(58),y-q(245)),180,355,fill=(32,31,41,255))
    for xx in (-25,23):
        d.ellipse((x+q(xx)-q(8),y-q(274),x+q(xx)+q(7),y-q(265)),fill=(34,35,47,255))
    mouth=max(2,math.sin(t*12)*6+4)
    d.ellipse((x-q(11),y-q(250),x+q(12),y-q(250)+q(mouth)),fill=(117,55,58,255))
    d.line((x+q(12),y-q(290),x+q(39),y-q(297)),fill=(47,35,37,255),width=q(4))
    d.arc((x-q(8),y-q(311),x+q(38),y-q(259)),20,100,fill=(74,40,40),width=q(2))

def bot(d,x,y,t,scale=1.0,accent=(45,224,233),label="AGENT",flag=0):
    # articulated arms, round head, oscillating mouth, pulsing lens
    s=scale;b=math.sin(t*2.4+flag)*4*s
    x=int(x);y=int(y+b)
    def q(a):return int(a*s)
    d.ellipse((x-q(82),y-q(4),x+q(81),y+q(15)),fill=(0,0,0,110))
    rnd(d,(x-q(56),y-q(151),x+q(56),y-q(17)),(26,48,75,255),15,outline=(*accent,220),width=max(1,q(4)))
    for side in (-1,1):
        xx=x+side*q(57);yy=y-q(113)
        ang=math.sin(t*2.3+flag+side)*18
        d.line((xx,yy,xx+side*q(33),yy+q(50)+ang),fill=(*accent,235),width=max(3,q(11)))
        d.ellipse((xx+side*q(30)-q(9),yy+q(50)+ang-q(10),xx+side*q(30)+q(9),yy+q(50)+ang+q(10)),fill=(206,226,240,255))
    rnd(d,(x-q(72),y-q(270),x+q(72),y-q(158)),(34,50,75,255),30,outline=(181,200,227,220),width=max(2,q(4)))
    rnd(d,(x-q(61),y-q(247),x+q(62),y-q(187)),(5,27,44,255),15)
    for dx in (-27,27):
        r=q(6)+math.sin(t*2+flag)*1.5
        d.ellipse((x+q(dx)-r,y-q(222)-r,x+q(dx)+r,y-q(222)+r),fill=(*accent,255))
    h=q(4+abs(math.sin(t*10))*14)
    rnd(d,(x-q(19),y-q(197),x+q(20),y-q(197)+h),(*accent,210),max(2,q(3)))
    # antenna
    d.line((x,y-q(270),x,y-q(291)),fill=(*accent,190),width=max(2,q(3)))
    d.ellipse((x-q(7),y-q(300),x+q(7),y-q(286)),fill=(*accent,255))
    put(d,(x,y-q(146)),safe(label,d,max(11,q(12)),q(106)),max(11,q(12)),(238,240,252),anchor="mm")
def npc(d,x,y,t):
    # Silhouette of original presenter in the narrative language (not replacing canonical video outro).
    director(d,x,y,t,.85)

def wrap(d,text,width,size,maxlines=2):
    words=text.split();rows=[];line=""
    for wd in words:
        tmp=(line+" "+wd).strip()
        if d.textbbox((0,0),tmp,font=font(size))[2] > width:
            if line:rows.append(line)
            line=wd
        else:line=tmp
    if line:rows.append(line)
    if len(rows)>maxlines:
        rows=rows[:maxlines];rows[-1]=safe(rows[-1]+"…",d,size,width)
    return rows

def chunks(text,n=10):
    w=text.split();return [" ".join(w[i:i+n]) for i in range(0,len(w),n)]
def get_subtitle(meta,t):
    words=meta.get("words") or []
    if len(words)>=8:
        starts=[float(x["start"]) for x in words]
        j=max(0,bisect.bisect_right(starts,t)-1)
        a=(j//9)*9
        return " ".join(str(v["text"]) for v in words[a:a+9])
    pieces=chunks(meta["text"],9)
    return pieces[min(len(pieces)-1,int(t/max(.1,meta["duration"])*len(pieces)))]

def draw_frame(i,t,duration,scene,meta,base):
    im=base.copy();d=ImageDraw.Draw(im,"RGBA")
    place=scene["location"];focus=scene["focus"]
    cyan=(68,218,237);rose=(255,108,152)
    # foreground rails, signage and clocked progress
    par=math.sin(t*.6+i)*10
    d.polygon([(0,457),(960,412),(960,540),(0,540)],fill=(6,11,24,130))
    for xx in range(150,1000,300):
        d.ellipse((xx-180+par,320,xx+110+par,475),outline=(59,148,199,65),width=3)
    # scene animation: characters visibly move (heads, arms, eyes, mouth), spatial staging
    director(d,220+int(math.sin(t*.26)*18),479,t,.84)
    bot(d,550+int(math.sin(t*.32+i)*18),481,t,.76,cyan,"AGENT",i)
    bot(d,780+int(math.sin(t*.28+i)*18),487,t,.67,rose,"HR",i+2)
    # floating interactive monitor panels (move + swap visual story every 6.6 sec)
    phase=int(t/6.4)%5
    bubble=(44,350,57)
    panel=(360,111,835,290)
    rnd(d,panel,(12,21,39,242),15,outline=(*cyan,200),width=3)
    d.rectangle((380,135,405,157),fill=(*rose,255))
    put(d,(416,133),["НОВАЯ ЗАДАЧА","АУДИТ","ОПТИМИЗАЦИЯ","СОВЕЩАНИЕ","СИСТЕМА ONLINE"][phase],16,cyan)
    if phase==0:
        for n in range(4):
            d.line((400,181+n*20,740-n*33,181+n*20),fill=(*cyan,95+n*38),width=5)
    elif phase==1:
        for n in range(8):
            yy=177+n*12
            d.line((402,yy,402+int(170+math.sin(t*2+n)*74),yy),fill=(*cyan,200),width=3)
    elif phase==2:
        for n in range(7):
            xx=403+n*48
            hh=(n*19+int(t*6))%88+15
            d.rectangle((xx,272-hh,xx+24,271),fill=(*cyan,130+n*12))
    elif phase==3:
        for n in range(4):
            xx=416+n*83
            d.ellipse((xx,191,xx+32,223),fill=(37,86,121,225),outline=(*rose,210),width=3)
        put(d,(593,256),"ОДОБРЕНО",17,rose,anchor="mm")
    else:
        w=330+int(math.sin(t*2)*30)
        rnd(d,(407,201,407+w,226),(21,77,89,245),6)
        rnd(d,(407,201,407+int(w*.65),226),(*cyan,230),6)
        put(d,(400,244),"ПЕРЕЗАГРУЗКА...",16,rose)
    # scene landmarks: falling memos/screens and urgency marks
    for j in range(4):
        if (i+j)%3==0:
            xx=(54+j*204+int(t*(10+j*4)))%960
            yy=165+(int(t*(13+j*4))+j*91)%300
            d.ellipse((xx,yy,xx+5,yy+5),fill=(*cyan,100))
    # episodic signal
    rnd(d,(33,28,927,87),(10,17,31,226),13,outline=(76,122,160,160),width=2)
    put(d,(52,37),"M1LASH // СКЕТЧ",20,cyan)
    put(d,(908,37),f"ГЛАВА {i+1:02d} / {len(scenes):02d}",19,(213,223,249),anchor="ra")
    put(d,(52,97),safe(scene["title"],d,31,815),31,(255,240,209),stroke=1)
    # transient notification labels every 7 seconds:
    prompt=["ЗАДАЧА ОБРАБОТАНА","ВЫСТАВЛЕН СЧЁТ","ЭФФЕКТИВНОСТЬ +200%","НАЧАЛО СОВЕЩАНИЯ","ТРЕБУЕТСЯ ЧЕЛОВЕК"][phase]
    rnd(d,(430,311,865,355),(19,36,57,227),10,outline=(*rose,184),width=2)
    put(d,(647,333),prompt,16,rose,anchor="mm")
    # subtitles 2-line max in lower 15%: never cover scene captions
    subtitle=get_subtitle(meta,t)
    rnd(d,(32,441,928,512),(6,12,27,244),13,outline=(*cyan,155),width=2)
    lines=wrap(d,subtitle,845,22,maxlines=2)
    for j,line in enumerate(lines):
        put(d,(480,455+j*25),line,22,(251,253,255),anchor="mt")
    d.rectangle((0,532,int(W*(i+t/max(.1,duration))/len(scenes)),540),fill=(*rose,230))
    # Important transparent fictional satirical label
    put(d,(38,514),"ВЫМЫШЛЕННАЯ ИСТОРИЯ • ГОЛОС ДМИТРИЙ",11,(160,185,207),bold=False)
    return im

def cmd(argv):
    print("CMD",str(argv[:7]),flush=True)
    p=subprocess.run(argv,capture_output=True)
    if p.returncode:
        raise RuntimeError("FFmpeg failed: "+p.stderr.decode(errors="replace")[-4000:])
    return p.stdout

def generate_music():
    # Fully original deterministic underscore: low clean chord arps and muted pulses.
    f=WORK/"original_music.wav"
    sr=22050; seconds=32
    t=np.arange(int(sr*seconds),dtype=np.float64)/sr
    chord=np.array([110,164.81,220,277.18,329.63])
    samples=np.zeros_like(t)
    for k,note in enumerate(chord):
        gate=(.62+.38*np.cos(2*np.pi*(.12+.025*k)*t+k))
        samples+=np.sin(2*np.pi*note*t+np.sin(2*np.pi*.12*t)*.2)*gate/(13+k*2)
    bass=.06*np.sin(2*np.pi*55*t)*(.6+.4*np.cos(2*np.pi*.75*t))
    samples+=bass
    pulse=np.exp(-((t%(.75))/.055)**2)*np.sin(2*np.pi*66*t)*.035
    samples+=pulse
    fade=np.minimum(1.0,np.minimum(t,seconds-t)*.6)
    samples*=fade
    import wave
    with wave.open(str(f),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((np.clip(samples,-.9,.9)*32767).astype(np.int16).tobytes())
    return f

def main():
    assert VOICES["voice"]=="ru-RU-DmitryNeural", "No substitute allowed"
    bed=generate_music()
    clips=[]
    total=0.0
    for i,(scene,meta) in enumerate(zip(scenes,VOICES["scenes"])):
        assert meta["text"]==scene["text"],f"TTS text changed at {i}"
        length=float(meta["duration"])+.55;total+=length
        base=backdrop(scene["location"])
        mp3=ROOT/"voice"/meta["file"]
        assert mp3.stat().st_size>10000
        seg=WORK/f"scene_{i:02}.mp4"
        frames=math.ceil(length*FPS)
        # Encode every original moving frame, direct no palette/image stock slideshow.
        ff=subprocess.Popen(
            ["ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
             "-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0",
             "-i",str(mp3),"-af","apad=pad_dur=0.65,volume=1.8",
             "-c:v","libx264","-preset","veryfast","-crf","26","-pix_fmt","yuv420p",
             "-c:a","aac","-ar","24000","-ac","1","-b:a","96k",
             "-t",f"{length:.4f}",str(seg)],stdin=subprocess.PIPE,stderr=(WORK/f"ffmpeg_{i:02}.log").open("w"))
        try:
            for n in range(frames):
                im=draw_frame(i,n/FPS,length,scene,meta,base)
                ff.stdin.write(im.tobytes())
        except BrokenPipeError:
            raise RuntimeError(f"Broken pipe on scene {i}: "+(WORK/f"ffmpeg_{i:02}.log").read_text()[-1200:])
        finally:
            try:ff.stdin.close()
            except:pass
        err=ff.wait()
        if err:raise RuntimeError(f"Scene {i} failed: "+(WORK/f"ffmpeg_{i:02}.log").read_text()[-1500:])
        clips.append(seg)
        print(f"SCENE_READY {i+1}/{len(scenes)} {length:.1f}s",flush=True)
    # Approved M1lash talking outro visual silently (voice remains Dmitry throughout).
    old=Path("videos/m1lash_outro_short_ru.mp4")
    if old.exists():
        outro=WORK/"m1lash_outro_muted.mp4"
        cmd(["ffmpeg","-nostdin","-loglevel","error","-y","-i",str(old),
             "-f","lavfi","-i","anullsrc=r=24000:cl=mono",
             "-vf",f"scale=300:510:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x121e35,fps={FPS}",
             "-t","5.0","-shortest","-c:v","libx264","-preset","veryfast","-crf","24","-pix_fmt","yuv420p",
             "-c:a","aac","-b:a","96k",str(outro)])
        clips.append(outro)
    concat=WORK/"concat.txt"
    concat.write_text("".join("file '"+str(p.resolve())+"'\n" for p in clips))
    joined=WORK/"joined.mp4"
    cmd(["ffmpeg","-nostdin","-loglevel","error","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(joined)])
    # Composition: voiced animated film + locally generated unobtrusive background score.
    cmd(["ffmpeg","-nostdin","-loglevel","error","-y","-i",str(joined),
         "-stream_loop","-1","-i",str(bed),
         "-filter_complex","[0:a]aformat=sample_rates=24000:channel_layouts=mono,volume=1.0[voice];[1:a]aformat=sample_rates=24000:channel_layouts=mono,volume=0.12[bed];[voice][bed]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.94[a]",
         "-map","0:v:0","-map","[a]","-vf",f"fps={FPS_OUT},scale=1920:1080:flags=lanczos",
         "-c:v","libx264","-preset","veryfast","-crf","28","-maxrate","1100k","-bufsize","2200k",
         "-pix_fmt","yuv420p","-c:a","aac","-ar","24000","-ac","2","-b:a","128k",
         "-movflags","+faststart",str(VIDEO)])
    import re
    result=subprocess.run(["ffmpeg","-hide_banner","-i",str(VIDEO)],capture_output=True,text=True)
    match=re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)",result.stderr)
    if not match: raise RuntimeError("Cannot inspect export: "+result.stderr[-1100:])
    dur=int(match.group(1))*3600+int(match.group(2))*60+float(match.group(3))
    data={"format":{"duration":dur,"size":VIDEO.stat().st_size},"video":{"codec":"h264","width":1920,"height":1080,"fps":24},"audio":{"codec":"aac"},"voice":"ru-RU-DmitryNeural","scene_count":len(scenes)}
    (WORK/"qa.json").write_text(json.dumps(data,indent=2))
    print("EXPORT_READY",json.dumps(data),flush=True)
    assert float(data["format"]["duration"])>600.0,"Movie is too short"
    assert VIDEO.stat().st_size>10000000
    # Poster
    draw_frame(0,3,60,scenes[0],VOICES["scenes"][0],backdrop("boardroom")).resize((1920,1080),Image.Resampling.LANCZOS).save(ROOT/"M1lash_AI_OFFICE_THUMB.jpg",quality=93)
if __name__=="__main__":main()
