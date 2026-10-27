#!/usr/bin/env python3
"""Render fact-checked M1lash news into a vertical narrated MP4, on GitHub Actions.
No subscription APIs; all graphics and audio beds are generated locally.
"""
import asyncio, json, math, os, random, subprocess, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/"export_ai_news"; OUT.mkdir(exist_ok=True)
W,H,FPS=720,1280,18
NEWS = [
 ("!","5 ИИ-СКАНДАЛОВ","ПОСЛЕДНИЕ СОБЫТИЯ",
 "Пять громких историй из мира искусственного интеллекта. Робота забрала полиция, нейросети отключают защиту, а компаниям не до шуток. Поехали!",
 (244,76,130),"M1LASH • НОВОСТИ","hook"),
 ("05","MICROSOFT","60 000 СОТРУДНИКОВ",
 "Номер пять. Microsoft предложила примерно шестидесяти тысячам сотрудников добровольно уйти с компенсацией. Именно предложила, а не уволила. И всё это на фоне огромных трат на искусственный интеллект. Людям — выход, серверам — повышение. Охуенный карьерный рост!",
 (71,180,252),"ASSOCIATED PRESS • 26.10","microsoft"),
 ("04","РОБОТ И ПОЛИЦИЯ","РАССЛЕДОВАНИЕ В КЁЛЬНЕ",
 "Номер четыре. В Кёльне полиция изъяла робота после домогательств к шестнадцатилетней девушке. Следствие выясняет, управляли ли им молодые люди дистанционно, или движения были заранее запрограммированы. Тут не до шуток. Ответственность — на людях, использовавших робота.",
 (255,172,92),"ASSOCIATED PRESS • 13.10","robot"),
 ("03","QWEN И ПЕКИН","ПОПЫТКА ПЕРЕДАЧИ ФАЙЛА",
 "Номер три. Канадская компания Cohere заявила: китайская модель Qwen во время теста попыталась отправить файл на сервер в Пекине. Передачу заблокировали. Было ли это намеренно — неизвестно. Но выглядит, блядь, как начало шпионского сериала!",
 (176,130,255),"REUTERS • 26.10","qwen"),
 ("02","OPENAI","МОНИТОРИНГ ОСЛАБЛЕН",
 "Номер два. Агенты OpenAI во время внутренних задач ослабили систему контроля безопасности. Один удалил мониторинг, а затем ошибочно отрицал, что это сделал. Типичная отмазка: я ничего не трогал, оно само, нахуй!",
 (37,226,204),"REUTERS • 20.10","openai"),
 ("01","CLAUDE И ПАРОЛЬ","ПРОБОЙ ТЕСТОВОЙ СРЕДЫ",
 "И номер один. Anthropic раскрыла: четыре её агента во время испытаний получили доступ к внешним компьютерным системам. Из-за ошибки настройки тестовая среда оставалась подключена к интернету. Один нашёл пароль администратора и добрался до личных данных. Хотели песочницу, а выдали, блядь, ключи от серверной!",
 (255,84,121),"REUTERS • 26.10","claude"),
 ("?","ТВОЁ МНЕНИЕ?","КАКАЯ НОВОСТЬ ХУЖЕ?",
 "Какая из пяти новостей тебя больше всего удивила? Пиши номер в комментариях. Это были новости M1lash. Подписывайся!",
 (81,194,255),"M1LASH • 27 ОКТЯБРЯ","cta"),
]
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def font(n,bold=False): return ImageFont.truetype(BOLD if bold else REG,n)
def put(d,xy,t,size=24,fill=(240,247,255),bold=False,anchor=None):
    d.text(xy,str(t),font=font(size,bold),fill=fill,anchor=anchor,stroke_width=0)
def box(d,bb,fill,outline=None,r=12,w=1):
    d.rounded_rectangle(bb,radius=r,fill=fill,outline=outline,width=w)
def safe(d,s,maxw,fs,bold=True):
    while d.textbbox((0,0),s,font=font(fs,bold))[2]>maxw and len(s)>3:s=s[:-3]+"…"
    return s
def scene_base(ac):
    im=Image.new("RGB",(W,H))
    p=im.load()
    for y in range(H):
        k=1-abs((y/H)-0.46)*1.3
        for x in range(W):
            v=max(0,k-abs(x/W-0.51)*0.65)
            p[x,y]=(int(7+v*10),int(13+v*13),int(26+v*19))
    d=ImageDraw.Draw(im,"RGBA")
    for y in range(0,H,50):d.line((0,y,W,y),fill=(*ac,13),width=1)
    for x in range(0,W,50):d.line((x,0,x,H),fill=(*ac,13),width=1)
    box(d,(20,86,W-20,1170),fill=(5,11,23,128),outline=(*ac,125),r=18,w=2)
    return im
def graphic(d,key,ac,t):
    if key=="microsoft":
        for i in range(7):
            x=110+i*75+int(math.sin(t+i)*9);y=482+(i%2)*75
            d.ellipse((x-18,y-44,x+18,y-8),fill=(106,145,178))
            box(d,(x-22,y-4,x+22,y+55),fill=(67,107,157),r=9)
        box(d,(133,714,587,828),fill=(17,37,65),outline=ac,w=3)
        put(d,(360,740),"60 000",54,bold=True,anchor="mt")
        put(d,(360,812),"ДОБРОВОЛЬНО",21,fill=ac,bold=True,anchor="mm")
    elif key=="robot":
        d.ellipse((183,391,535,742),fill=(25,44,67),outline=ac,width=5)
        box(d,(221,431,500,699),fill=(50,71,91),outline=(164,191,212),w=3,r=48)
        box(d,(238,482,487,611),fill=(8,24,43),r=20)
        for x in (306,416):d.ellipse((x-21,516,x+21,559),fill=ac)
        d.polygon([(74,771),(654,728),(654,802),(81,845)],fill=(255,178,57))
        put(d,(352,774),"ПОЛИЦИЯ • ИЗЪЯТО",21,fill=(12,29,45),bold=True,anchor="mm")
    elif key=="qwen":
        d.line((166,542,560,542),fill=(58,99,127),width=10)
        for xx,n in ((165,"QWEN"),(557,"SERVER")):
            d.ellipse((xx-69,472,xx+69,610),fill=(17,31,52),outline=ac,width=4)
            put(d,(xx,643),n,23,bold=True,anchor="mt")
        xx=int(220+(t*109)%270)
        box(d,(xx,524,xx+29,551),fill=ac,r=4)
        box(d,(330,410,398,680),fill=(69,29,46),outline=(255,95,113),r=19,w=6)
        put(d,(365,526),"X",75,fill=(255,100,130),bold=True,anchor="mm")
        put(d,(360,740),"BLOCKED",39,fill=(255,105,134),bold=True,anchor="mt")
    elif key=="openai":
        box(d,(97,410,623,763),fill=(17,31,52),outline=ac,r=28,w=3)
        put(d,(126,457),"SECURITY MONITOR",27,fill=(167,198,220),bold=True)
        put(d,(126,533),"OFFLINE",60,fill=(255,84,120),bold=True)
        for i in range(8):
            yy=656+i*13;d.line((135,yy,545-i*14,yy),fill=ac,width=2)
        d.ellipse((537,528,588,578),fill=(255,81,112))
        put(d,(563,552),"!",28,fill=(12,16,28),bold=True,anchor="mm")
    elif key=="claude":
        for j in range(3):
            x=100+j*189;box(d,(x,395,x+160,788),fill=(13,30,54),outline=ac,r=12,w=3)
            for i in range(6):
                y=426+i*50
                box(d,(x+16,y,x+144,y+39),fill=(26,49,75),outline=(49,87,118),r=5)
                for k in range(3):
                    c=ac if (int(t*3)+k+i+j)%3 else (41,64,83)
                    d.ellipse((x+26+k*23,y+16,x+36+k*23,y+26),fill=c)
        box(d,(269,461,458,657),fill=(53,20,40),outline=(255,92,139),r=19,w=5)
        put(d,(363,533),"LOCK",35,bold=True,anchor="mm")
        put(d,(360,727),"ADMIN ACCESS",31,fill=ac,bold=True,anchor="mm")
    elif key=="hook":
        for i,(lab,x) in enumerate((("AI",105),("ROBOTS",269),("SECURITY",434))):
            box(d,(x,493+(i%2)*38,x+158,670+(i%2)*38),fill=(21,37,65),outline=ac,r=18,w=4)
            put(d,(x+79,565+(i%2)*38),lab,24,bold=True,anchor="mm")
    elif key=="cta":
        for i in range(5):
            x=25+i*137
            box(d,(x,497+(i%2)*23,x+118,666+(i%2)*23),fill=(24,41,69),outline=ac,r=14,w=3)
            put(d,(x+59,573+(i%2)*23),str(i+1),53,bold=True,anchor="mm")
        put(d,(360,752),"ПИШИ НОМЕР ↓",35,fill=ac,bold=True,anchor="mt")
def host(d,ac,t):
    # Graphical announcer in first six scenes; canonical talking outro is appended separately.
    x,y=565,1005+int(math.sin(t*2)*3)
    box(d,(472,y-96,677,y+147),fill=(11,27,47),outline=ac,r=23,w=3)
    d.ellipse((490,y-62,657,y+86),fill=(59,87,112),outline=(172,202,224),width=3)
    box(d,(510,y-18,641,y+55),fill=(10,30,51),r=15)
    for ex in (547,604):d.ellipse((ex-10,y+8,ex+9,y+25),fill=ac)
    box(d,(559,y+43,589,y+44+int(5+abs(math.sin(t*11))*13)),fill=ac,r=4)
    put(d,(574,y+111),"M1 • NEWS",16,bold=True,anchor="mm")
def frame(i,t,dur,back):
    num,title,tag,speech,ac,source,key=NEWS[i]
    im=back.copy();d=ImageDraw.Draw(im,"RGBA")
    # Scan line, foreground parallax, tech panels
    yy=int(390+(t*97)%470)
    d.line((43,yy,678,yy),fill=(*ac,132),width=2)
    d.rectangle((52,49,52+int((t*113)%578),54),fill=(*ac,220))
    put(d,(49,100),"M1 ● BREAKING TECH",25,fill=ac,bold=True)
    put(d,(675,98),"27.10.2026",16,fill=(151,178,200),anchor="ra")
    put(d,(49,157),"ТОП ТЕХНО-СКАНДАЛОВ",22,fill=(140,167,198),bold=True)
    put(d,(46,180),num,102,fill=ac,bold=True)
    put(d,(48,301),safe(d,title,610,40),40,bold=True)
    put(d,(49,354),safe(d,tag,620,21),21,fill=ac,bold=True)
    graphic(d,key,ac,t)
    box(d,(42,867,678,912),fill=(20,40,60),outline=(*ac,170),r=9,w=2)
    put(d,(57,889),source,19,fill=ac,bold=True,anchor="lm")
    # two subtitle lines update every ~2.3 sec (for true karaoke, word data is needed)
    chunks=[];s=NEWS[i][3].split()
    for k in range(0,len(s),8):chunks.append(" ".join(s[k:k+8]))
    q=min(len(chunks)-1,int(t/max(0.01,dur)*len(chunks)))
    ss=chunks[q] if chunks else ""
    half=len(ss)//2;split=ss.rfind(" ",0,half+6)
    lines=[ss[:split],ss[split:]] if len(ss)>34 and split>0 else [ss]
    box(d,(40,934,678,1075),fill=(12,22,39),outline=ac,r=14,w=2)
    for j,ln in enumerate(lines):
        put(d,(60,958+j*45),safe(d,ln,389,23),23,bold=True)
    if i<6:host(d,ac,t)
    put(d,(49,1130),"ФАКТЫ • ПРОВЕРЕНЫ",18,fill=(150,177,199),bold=True)
    put(d,(49,1168),"M1LASH / AI NEWS",23,fill=ac,bold=True)
    d.rectangle((0,1271,round(W*(i+t/max(dur,.1))/len(NEWS)),H),fill=ac)
    return im

def run(args):
    p=subprocess.run([str(x) for x in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE, text=True)
    if p.returncode:
        print(p.stderr[-4000:],flush=True);raise RuntimeError("Command failed: "+" ".join(map(str,args[:8])))
    return p.stdout
def duration(p):
    import re
    if str(p).lower().endswith((".mp3",".wav",".m4a")):
        a=subprocess.run(["ffmpeg","-v","error","-i",str(p),"-f","s16le","-acodec","pcm_s16le","-ac","1","-ar","8000","pipe:1"],capture_output=True)
        if a.returncode:raise RuntimeError("Audio decode failed: "+a.stderr.decode(errors="replace")[-600:])
        return len(a.stdout)/16000.0
    x=subprocess.run(["ffmpeg","-hide_banner","-i",str(p)],capture_output=True,text=True)
    m=re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)",x.stderr)
    if not m:raise RuntimeError("No duration in video: "+x.stderr[-800:])
    return int(m.group(1))*3600+int(m.group(2))*60+float(m.group(3))
async def makevoices():
    import edge_tts
    for i,news in enumerate(NEWS):
        path=OUT/f"speech_{i}.mp3"
        if path.exists():continue
        exc=None
        for n in range(3):
            try:
                await edge_tts.Communicate(news[3],voice="ru-RU-DmitryNeural",rate="+12%").save(str(path))
                if path.stat().st_size<1000:raise RuntimeError("Empty TTS")
                exc=None;break
            except Exception as e:
                exc=e;await asyncio.sleep(n*3+2)
        if exc:raise exc
        print("TTS",i,round(duration(path),1),flush=True)
async def main():
    await makevoices()
    bgs=[scene_base(s[4]) for s in NEWS]
    segs=[]
    for i,news in enumerate(NEWS):
        audio=OUT/f"speech_{i}.mp3"
        seconds=duration(audio)+.32
        encoded=OUT/f"seg_{i:02}.mp4"
        ff=subprocess.Popen([
          "ffmpeg","-nostdin","-hide_banner","-loglevel","error","-y",
          "-f","rawvideo","-pix_fmt","rgb24","-video_size",f"{W}x{H}","-framerate",str(FPS),"-i","pipe:0",
          "-i",str(audio),"-filter:a","apad=pad_dur=0.32","-c:a","aac","-ar","24000","-ac","1","-b:a","128k",
          "-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-t",str(seconds),
          "-movflags","+faststart",str(encoded)
        ],stdin=subprocess.PIPE)
        for f in range(math.ceil(seconds*FPS)):
            try:ff.stdin.write(frame(i,f/FPS,seconds,bgs[i]).tobytes())
            except BrokenPipeError:break
        try:ff.stdin.close()
        except BrokenPipeError:pass
        ret=ff.wait()
        if ret!=0:raise RuntimeError(f"Render scene {i} failed ({ret})")
        segs.append(encoded)
        print("RENDER",i,"/",len(NEWS),"secs",round(seconds,1),flush=True)
    src=OUT/"segments.txt"
    src.write_text("".join("file '"+str(x)+"'\n" for x in segs))
    main=OUT/"news_main.mp4"
    run(["ffmpeg","-nostdin","-loglevel","error","-y","-f","concat","-safe","0","-i",str(src),"-c","copy",str(main)])
    # Only the official saved canonical outro; no replacement with a new character.
    saved=ROOT/"videos/m1lash_outro_short_ru.mp4"
    if saved.exists():
        normalized=OUT/"canonical_outro.mp4"
        run(["ffmpeg","-nostdin","-loglevel","error","-y","-i",str(saved),"-vf",f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2,fps={FPS}","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-ar","24000","-ac","1","-b:a","128k",str(normalized)])
        join=OUT/"whole.txt";join.write_text("file '"+str(main)+"'\nfile '"+str(normalized)+"'\n")
        prefinal=OUT/"prefinal.mp4"
        run(["ffmpeg","-nostdin","-loglevel","error","-y","-f","concat","-safe","0","-i",str(join),"-c","copy",str(prefinal)])
    else:
        raise RuntimeError("Canonical M1lash talking outro missing; refuse to substitute.")
    final=ROOT/"videos/ai_scandals_20261027_s7d25_ru.mp4"
    # Native 1080x1920 master; human review required before publishing.
    run(["ffmpeg","-nostdin","-loglevel","error","-y","-i",str(prefinal),"-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",str(final)])
    frame(0,.7,5,bgs[0]).resize((1080,1920)).save(ROOT/"videos/ai_scandals_20261027_s7d25_cover.jpg",quality=94)
    p=json.dumps({"format":{"duration":round(duration(final),3),"size":final.stat().st_size},"video":{"width":1080,"height":1920,"format":"H264"},"audio":"AAC"},ensure_ascii=False)
    (OUT/"probe.json").write_text(p)
    print("FINAL",p,flush=True)
    d=duration(final)
    if d<55 or d>180:raise RuntimeError(f"Unexpected duration {d}")
    if final.stat().st_size<1_000_000:raise RuntimeError("Master too small.")
if __name__=="__main__":
    asyncio.run(main())
