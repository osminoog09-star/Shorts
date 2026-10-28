#!/usr/bin/env python3
"""M1lash 2026-10-28 original S8-D25 source-control news motion film.
Strict voices Dmitry/Svetlana; no TTS fallbacks. Original procedural sound bed.
Run from repo root: python tools/scion_weekly/produce.py
"""
from __future__ import annotations
import asyncio, hashlib, json, math, os, re, subprocess, time, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path("tools/scion_weekly")
OUT=ROOT/"work"
OUT.mkdir(parents=True,exist_ok=True)
FPS=30
W,H=720,1280
SR=48000
DIMA="ru-RU-DmitryNeural"
SVETA="ru-RU-SvetlanaNeural"

S=[
("hook","ИИ ПЕРЕПИСЫВАЕТ ПРАВИЛА","Что происходит с Git?","Дима","Пока ты споришь с Гитом, ИИ агенты уже заставляют компании переделывать сами инструменты программирования."),
("chart","ПОЧТИ В 12 РАЗ БОЛЬШЕ","Anthropic · 13 октября","Дима","В мае Антропик объединяла около двух с половиной тысяч изменений кода в день. К сентябрю стало больше тридцати тысяч."),
("weight","100 ГИГАБАЙТ ИСТОРИИ","Монорепозиторий Anthropic","Дима","История главной ветки почти сто гигабайт. А сборочные системы получают код около двадцати пяти миллионов раз за день."),
("scion","SCION ВМЕСТО GIT","Система внутри Anthropic","Дима","Поэтому Антропик сделала собственную систему Сайон. Почти всю тяжёлую работу с историей и изменениями выполняет сервер."),
("flow","МЕНЬШЕ ЛИШНЕЙ РАБОТЫ","Всё необходимое — по запросу","Дима","Агенты получают только нужные данные. По оценке Антропик, инфраструктура потребляет в двести раз меньше ресурсов, чем прежняя сеть зеркал Гит."),
("entire","НОВОСТЬ ЭТОЙ НЕДЕЛИ","26 октября 2026","Дима","А двадцать шестого октября бывший глава Гитхаба Томас Домке представил Энтайр: новую платформу для совместной работы программистов и ИИ агентов."),
("trails","АГЕНТЫ ПРОВЕРЯЮТ КОД","Entire · Trails","Дима","Вместо обычного пул реквеста предлагаются Трейлс. Проверки запускают агенты, а человек видит результаты и решает, когда объединить код."),
("claim","89× БЫСТРЕЕ?","Света · проверка утверждения","Света","Энтайр заявляет о скорости отправки изменений до восьмидесяти девяти раз выше Гитхаба. Но это тесты самой компании, а не независимая оценка."),
("skills","ЕЩЁ НОВОСТЬ НЕДЕЛИ","22 октября · Agent Skills","Света","А Антропик передала стандарт Агент Скиллс независимому фонду. По данным компании, его уже поддерживают больше семидесяти агентных платформ."),
("twist","GIT НЕ УМЕР","Важное ограничение","Дима","Но Гит не умер. Даже Антропик говорит, что Сайон нужен для необычайно больших репозиториев. Для обычных проектов Гит пока остаётся отличным выбором."),
("outro","А ЧТО ВЫБЕРЕШЬ ТЫ?","M1lash · обсуждаем","Дима","Как думаешь, ИИ агенты поменяют Гитхаб до неузнаваемости? Пиши в комментариях. Подпишись! И спасибо всем, кто досмотрел и поставил лайк."),
]
VOICES={"Дима":DIMA,"Света":SVETA}
COLORS={"bg":"#0b1525","panel":"#162a40","stroke":"#42637e","teal":"#65ead1","white":"#eef6fb","muted":"#acc4d1","gold":"#ffc477","red":"#ff778c"}
def run(*args):
    subprocess.run(list(args),check=True)
def font(size,bold=False):
    p="/usr/share/fonts/truetype/dejavu/DejaVuSans-"+("Bold" if bold else "")+".ttf"
    if not Path(p).exists():p="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p,size)
def rounded(d,box,fill,r=22,outline=None,width=2):
    d.rounded_rectangle(tuple(map(int,box)),radius=int(r),fill=fill,outline=outline,width=width)
def center(d,y,string,size=42,color="#eef6fb",bold=True,maxw=650):
    f=font(size,bold)
    while d.textbbox((0,0),string,font=f)[2]>maxw and size>18:
        size-=2;f=font(size,bold)
    d.text((W//2,int(y)),string,font=f,fill=color,anchor="mt")
def line(d,y,string,size=26,color="#eef6fb"):
    d.text((75,int(y)),string,font=font(size,True),fill=color)
def rectbg(d,light=False):
    d.rectangle((0,0,W,H),fill="#eef4f6" if light else COLORS["bg"])
    if not light:
        for x in range(35,760,65):d.line((x,265,x,H-160),fill="#152b3d",width=1)
        for y in range(265,1120,65):d.line((0,y,W,y),fill="#152b3d",width=1)
def infochip(d,text,x,y,width=520):
    rounded(d,(x,y,x+width,y+74),"#1d374d",16,"#477185")
    d.text((x+22,y+18),text,font=font(26,True),fill=COLORS["white"])
def visual(d,kind,progress,t):
    p=max(0,min(1,progress))
    C=COLORS
    if kind=="hook":
        for j in range(6):
            xx=110+j*92;yy=575+math.sin(j*.75+t*.65)*55
            if j:d.line((110+(j-1)*92,575+math.sin((j-1)*.75+t*.65)*55,xx,yy),fill=C["stroke"],width=4)
            rounded(d,(xx-11,yy-11,xx+11,yy+11),C["teal"],6)
        rounded(d,(192,755,528,858),C["panel"],26,C["stroke"],4)
        center(d,775,"GIT",55,C["white"])
        if p>.33:d.line((210,831,512,777),fill=C["red"],width=14)
        center(d,912,"КОД ПИШУТ АГЕНТЫ",27,C["teal"])
    elif kind=="chart":
        rounded(d,(58,345,660,880),"#fefefe",30)
        d.line((103,757,618,757),fill="#c5d6dc",width=4)
        h2=40+310*p
        rounded(d,(148,710,275,757),"#8fa9b7",10)
        rounded(d,(420,757-h2,547,757),C["teal"],10)
        center(d,400,"≈ 2 500   →   > 30 000",35,"#132333")
        line(d,799,"МАЙ",24,"#18334d");d.text((405,799),"СЕНТЯБРЬ",font=font(23,True),fill="#18334d")
        center(d,945,"ЗА ЧЕТЫРЕ МЕСЯЦА",31,C["teal"])
    elif kind=="weight":
        rounded(d,(65,372,655,830),"#fefefe",28)
        center(d,455,"≈ 100 GB",88,"#16293d")
        center(d,616,"ИСТОРИИ КОДА",34,"#324e65")
        center(d,760,"≈ 25 000 000",38,"#123241")
        center(d,840,"ЗАГРУЗОК В ДЕНЬ",28,C["teal"])
    elif kind=="scion":
        for j in range(10):
            a=j*math.pi/5+t*.16
            x=360+260*math.cos(a);y=635+213*math.sin(a)
            d.line((360,635,x,y),fill=C["stroke"],width=3)
            rounded(d,(x-21,y-21,x+21,y+21),C["panel"],8,C["teal"],3)
        d.ellipse((248,526,472,750),fill=C["panel"],outline=C["teal"],width=7)
        center(d,605,"SCION",44)
        center(d,970,"ОДИН ЦЕНТР · ДАННЫЕ ПО ЗАПРОСУ",22,C["teal"])
    elif kind=="flow":
        for j,word in enumerate(("КЛИЕНТ","SCION","НУЖНЫЕ ФАЙЛЫ")):
            y=332+j*235
            rounded(d,(96,y,624,y+150),C["panel"],20,C["stroke"],3)
            d.text((126,y+35),f"0{j+1}",font=font(30,True),fill=C["teal"])
            d.text((210,y+52),word,font=font(29,True),fill=C["white"])
            if j<2:
                d.line((360,y+154,360,y+228),fill=C["teal"],width=5)
                d.polygon([(348,y+211),(372,y+211),(360,y+231)],fill=C["teal"])
    elif kind=="entire":
        rounded(d,(72,338,648,840),C["panel"],34,C["stroke"],3)
        rounded(d,(112,386,608,490),"#264a5d",18)
        center(d,410,"ENTIRE",57)
        center(d,550,"GIT FORGE",50,C["teal"])
        center(d,640,"ДЛЯ ЛЮДЕЙ И АГЕНТОВ",25)
        for j in range(3):
            x=190+j*170;y=775+math.sin(t*2+j)*6
            d.ellipse((x-30,y-30,x+30,y+30),fill=C["teal"] if j%2==0 else C["gold"])
            d.ellipse((x-11,y-4,x-3,y+4),fill=C["bg"])
            d.ellipse((x+3,y-4,x+11,y+4),fill=C["bg"])
        center(d,956,"26 ОКТЯБРЯ",33,C["gold"])
    elif kind=="trails":
        rounded(d,(60,330,660,894),C["panel"],28,C["stroke"],2)
        center(d,365,"TRAIL / REVIEW",39)
        for j,(name,lab) in enumerate((("SECURITY","АГЕНТ"),("QUALITY","АГЕНТ"),("MERGE","ЧЕЛОВЕК"))):
            y=478+j*132
            rounded(d,(97,y,624,y+106),"#234155",15,"#3d6a79")
            d.ellipse((117,y+22,179,y+84),fill=C["teal"] if j<2 else C["gold"])
            centerx=153
            d.text((centerx,y+53),"✓" if j<2 else "!",font=font(36,True),fill="#14313b",anchor="mm")
            d.text((205,y+12),name,font=font(32,True),fill=C["white"])
            d.text((205,y+62),lab,font=font(22),fill=C["muted"])
    elif kind=="claim":
        rounded(d,(67,324,653,884),"#fefefe",32)
        center(d,407,"ДО",34,"#587084")
        center(d,480,"89×",138,"#122538")
        center(d,680,"БЫСТРЕЕ PUSH",33,"#193a4d")
        rounded(d,(120,770,600,852),"#ffead3",15)
        center(d,784,"ЗАЯВЛЕНИЕ ENTIRE",25,"#513219")
        center(d,944,"НЕ НЕЗАВИСИМЫЙ ТЕСТ",23,C["gold"])
    elif kind=="skills":
        rounded(d,(75,352,644,880),C["panel"],25,C["stroke"],3)
        center(d,413,"SKILL.md",63,C["teal"])
        for j,txt in enumerate(("ЗАДАЧА","ПРАВИЛА","ИНСТРУМЕНТЫ")):
            y=536+j*99
            infochip(d,f"{j+1:02d}     {txt}",129,y,468)
        center(d,967,"70+ ПЛАТФОРМ",33,C["teal"])
    elif kind=="twist":
        rounded(d,(121,385,599,554),C["panel"],25,C["stroke"])
        center(d,427,"GIT  ✓",70,C["teal"])
        d.line((360,555,360,736),fill=C["stroke"],width=6)
        d.polygon(((347,723),(373,723),(360,744)),fill=C["stroke"])
        rounded(d,(86,760,634,930),C["panel"],25,C["teal"],3)
        center(d,784,"SCION — НЕ ДЛЯ ВСЕХ",30)
        center(d,862,"ОГРОМНЫЕ МАСШТАБЫ",27,C["teal"])
    elif kind=="outro":
        rounded(d,(86,380,634,840),C["panel"],28,C["stroke"])
        center(d,438,"M1LASH",76,C["white"])
        center(d,567,"ТВОЁ МНЕНИЕ?",42,C["teal"])
        center(d,745,"ПИШИ В КОММЕНТАРИЯХ",27,C["white"])
        rounded(d,(115,905,605,987),"#c92c51",22)
        center(d,923,"ПОДПИШИСЬ!",38,C["white"])

async def speak(i,rec):
    import edge_tts
    kind,title,sub,speaker,copy=rec
    voice=VOICES[speaker]
    path=OUT/f"{i:02d}.mp3"
    wav=OUT/f"{i:02d}.wav"
    meta=OUT/f"{i:02d}.json"
    # Cache ONLY the exact approved voice+text. This survives interrupted Actions runs.
    if meta.is_file() and wav.is_file() and path.is_file():
        try:
            previous=json.loads(meta.read_text(encoding="utf-8"))
            verified=(previous.get("voice_id")==voice and previous.get("text")==copy
                      and previous.get("audio_sha256")==hashlib.sha256(wav.read_bytes()).hexdigest())
            if verified:
                with wave.open(str(wav)) as f:
                    verified=f.getframerate()==SR and f.getnframes()>SR
            if verified:
                print("CACHED",i,voice,flush=True)
                return previous
        except (OSError,ValueError,KeyError,EOFError,wave.Error):
            pass
    words=[]
    last=None
    for attempt in range(12):
        try:
            path.unlink(missing_ok=True)
            words=[]
            with path.open("wb") as fp:
                tts=edge_tts.Communicate(copy,voice=voice,rate="+5%",pitch="+0Hz")
                async for block in tts.stream():
                    if block["type"]=="audio":fp.write(block["data"])
                    elif block["type"]=="WordBoundary":
                        words.append([block["text"],block["offset"]/1e7,(block["offset"]+block["duration"])/1e7])
            if not path.exists() or path.stat().st_size<2000:raise RuntimeError("No TTS audio")
            wav=OUT/f"{i:02d}.wav"
            run("ffmpeg","-y","-v","error","-xerror","-i",str(path),"-ac","1","-ar",str(SR),str(wav))
            with wave.open(str(wav)) as f:
                if f.getframerate()!=SR or f.getnframes()<SR:raise RuntimeError("Bad speech duration")
                duration=f.getnframes()/SR
            record=dict(index=i,kind=kind,title=title,sub=sub,speaker=speaker,
                        voice_id=voice,text=copy,words=words,duration=duration,
                        audio_sha256=hashlib.sha256(wav.read_bytes()).hexdigest())
            meta.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf-8")
            return record
        except Exception as e:
            last=e
            await asyncio.sleep(min(16,2+attempt*2))
    raise RuntimeError(f"NO-GO: {voice} unavailable at scene {i}: {last}")

def readwav(path):
    with wave.open(str(path)) as f:
        return np.frombuffer(f.readframes(f.getnframes()),dtype="<i2").astype(np.float32)/32768

def subtitle_for(row,scene_t):
    # WordBoundary-linked short phrase captions. Falls back to documented segment cue if no boundaries.
    words=row["words"]
    if not words:
        parts=re.findall(r"\S+",row["text"])
        n=max(1,len(parts))
        ix=int(min(n-1,max(0,scene_t/max(.1,row["duration"])*n)))
        return " ".join(parts[max(0,ix-2):min(n,ix+3)])
    ix=0
    for j,x in enumerate(words):
        if scene_t>=x[1]-.15:ix=j
    start=max(0,(ix//4)*4)
    return " ".join(x[0] for x in words[start:start+4])

def frame(f,items,total):
    now=f/FPS
    row=items[-1]
    for r in items:
        if now<r["end"]:row=r;break
    idx=row["index"]
    local=max(0,now-row["start"])
    progress=max(0,min(1,local/max(.2,row["end"]-row["start"])))
    kind,title,sub,speaker,_=S[idx]
    im=Image.new("RGB",(W,H),COLORS["bg"])
    d=ImageDraw.Draw(im)
    rectbg(d)
    rounded(d,(36,35,145,85),COLORS["teal"],15)
    d.text((56,42),"M1",font=font(30,True),fill="#10303a")
    d.text((171,50),"TECH · ОБЪЯСНЯЕМ",font=font(19,True),fill=COLORS["muted"])
    d.text((620,50),f"{idx+1:02d}/{len(S):02d}",font=font(21,True),fill=COLORS["muted"])
    center(d,115,title,47)
    center(d,185,sub,23,COLORS["gold"] if kind in ("entire","claim","skills") else COLORS["muted"])
    visual(d,kind,progress,local)
    if speaker=="Света":
        rounded(d,(455,1005,656,1063),"#574554",14,"#987c8d")
        d.text((485,1021),"СВЕТА",font=font(23,True),fill="#f9d8ec")
    else:
        rounded(d,(476,1005,654,1063),"#244858",14)
        d.text((510,1021),"ДИМА",font=font(23,True),fill=COLORS["teal"])
    spoken_t=max(0,local-.17)
    caption=subtitle_for(row,spoken_t)
    if caption:
        words=caption.split()
        groups=[]
        linebuf=""
        for w in words:
            if len(linebuf+" "+w)>23 and linebuf:
                groups.append(linebuf);linebuf=w
            else:linebuf=(linebuf+" "+w).strip()
        if linebuf:groups.append(linebuf)
        y=1065
        for tx in groups[:2]:
            w=d.textbbox((0,0),tx,font=font(29,True))[2]
            x=(W-w)//2
            rounded(d,(max(18,x-16),y-9,min(W-18,x+w+16),y+48),"#0c1723",12,"#274255")
            center(d,y,tx,29)
            y+=56
    if idx in [1,2,3,4]: center(d,1178,"Anthropic Engineering · 13.10.2026",17,COLORS["muted"])
    if idx in [5,6,7]:center(d,1178,"Entire · 26.10.2026",17,COLORS["muted"])
    if idx==8:center(d,1178,"Anthropic · 22.10.2026",17,COLORS["muted"])
    rounded(d,(52,1220,668,1226),"#2e4553",4)
    rounded(d,(52,1220,52+int(616*min(1,now/total)),1226),COLORS["teal"],4)
    return im

async def main():
    items=[]
    for i,scene in enumerate(S):
        item=await speak(i,scene)
        items.append(item)
        print("TTS",i+1,"/",len(S),item["speaker"],round(item["duration"],2),flush=True)
        await asyncio.sleep(4)  # keep load low on Microsoft voice service
    pos=0.0;blocks=[]
    for r in items:
        samples=readwav(OUT/f'{r["index"]:02d}.wav')
        head=np.zeros(int(.16*SR),dtype=np.float32)
        tail=np.zeros(int((.4 if r["index"]<len(S)-1 else .65)*SR),dtype=np.float32)
        combined=np.concatenate([head,samples,tail])
        r["start"]=pos
        r["speech_start"]=pos+len(head)/SR
        r["end"]=pos+len(combined)/SR
        pos=r["end"];blocks.append(combined)
    voice=np.concatenate(blocks)
    voice=voice/max(.8,np.max(np.abs(voice))/.75)
    n=len(voice);t=np.arange(n,dtype=np.float32)/SR
    bed=(.006*np.sin(2*np.pi*92*t)+.004*np.sin(2*np.pi*184*t)+.003*np.sin(2*np.pi*276*t)).astype(np.float32)
    # Minimal original pulse, ducked below voice.
    for tm in np.arange(.0,pos,1.35):
        s=int(tm*SR);m=min(n-s,int(.19*SR))
        if m>0:
            tt=np.arange(m)/SR
            bed[s:s+m]+=.014*np.sin(2*np.pi*160*tt)*np.exp(-23*tt)
    joined=np.clip(voice+bed,-.95,.95)
    wavpath=OUT/"audio.wav"
    with wave.open(str(wavpath),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
        w.writeframes((joined*32767).astype("<i2").tobytes())
    (OUT/"manifest.json").write_text(json.dumps({"engine":"edge-tts","date":"2026-10-28",
        "approved_voice_ids":VOICES,"segments":items},ensure_ascii=False,indent=2),encoding="utf-8")
    total=pos
    dest=OUT/"base.mp4"
    args=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pix_fmt","rgb24",
          "-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-i",str(wavpath),
          "-vf","scale=1080:1920:flags=lanczos,format=yuv420p",
          "-c:v","libx264","-preset","veryfast","-crf","19","-c:a","aac","-b:a","160k",
          "-shortest","-movflags","+faststart",str(dest)]
    p=subprocess.Popen(args,stdin=subprocess.PIPE)
    frames=int(total*FPS)
    try:
        for i in range(frames):
            p.stdin.write(frame(i,items,total).tobytes())
            if i%600==0:print("RENDER",i,frames,flush=True)
    finally:
        p.stdin.close()
    if p.wait()!=0:raise RuntimeError("ffmpeg encode failed")
    for name,idx in (("opening",0),("middle",len(S)//2),("end",len(S)-1)):
        im=frame(int((items[idx]["start"]+items[idx]["end"])/2*FPS),items,total)
        im.save(OUT/f"still_{name}.jpg",quality=90)
    print("BASE READY",dest,"duration",round(total,2),flush=True)

if __name__=="__main__":
    asyncio.run(main())
