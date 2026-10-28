#!/usr/bin/env python3
"""M1lash Film 54: original animated historical infographic video.
All objects are drawn procedurally; no externally licensed stock is embedded.
Voiced segments determine runtime. Empty/silent segments cannot pad the film.
"""
from __future__ import annotations
import math,random,subprocess,sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W,H=960,540
P=[(11,25,36),(15,29,36),(14,24,38),(17,30,35)]
G=(222,184,118);C=(237,229,207);M=(139,172,179);T=(82,183,155)
R=(211,114,99)
def font(s,bold=False):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    return ImageFont.truetype(paths[0],s)
H1=font(26,True);SUB=font(16);SM=font(13,True)
def line(d,points,color=G,w=3):d.line(points,fill=color,width=w,joint="curve")
def circ(d,x,y,r,color=T):
    d.ellipse((int(x-r),int(y-r),int(x+r),int(y+r)),fill=color)
def caption(d,x,y,s,f=SUB,color=C):
    d.text((x,y),str(s),font=f,fill=color,stroke_width=0)
def backdrop(d,t):
    for x in range(40,960,82):line(d,[(x+math.sin(t*.13)*12,80),(x+math.sin(t*.13)*12,490)],(32,53,66),1)
    for y in range(90,490,42):line(d,[(0,y),(960,y)],(28,48,60),1)
    for j in range(17):
        random.seed(j*11);x=random.randrange(70,915);y=random.randrange(95,477)
        circ(d,x+math.cos(t*.2+j)*5,y+math.sin(t*.17+j)*5,1,(67,106,113))
def leaf(d,x,y,s,t):
    sway=math.sin(t*.39)*s*.08
    pts=[(x+sway,y-s),(x-s*.58,y-s*.51),(x-s*.75,y+s*.1),(x-s*.25,y+s*.42),
         (x,y+s),(x+s*.27,y+s*.38),(x+s*.76,y+s*.04),(x+s*.55,y-s*.48)]
    d.polygon(pts,fill=(40,113,87),outline=T,width=3)
    line(d,[(x,y+s),(x+sway,y-s)],(163,209,163),3)
    for p in (.20,.43,.63):
        yy=y-s+2*s*p
        line(d,[(x,yy),(x-s*.55*(1-p),yy-25)],(119,176,124),2)
        line(d,[(x,yy),(x+s*.55*(1-p),yy-29)],(119,176,124),2)
def plant(d,t):
    line(d,[(482,450),(482,160)],T,6)
    for j in range(6):
        q=(-1)**j
        leaf(d,482+q*(57+j*9),363-j*29,29+j*3,t+j)
    leaf(d,482,164,66,t)
    line(d,[(320,451),(645,451)],(128,100,75),4)
def mapworld(d,t):
    paths=[
        [(121,156),(180,119),(243,140),(280,178),(256,226),(219,265),(203,322),(165,355),(130,282)],
        [(241,348),(277,369),(290,410),(260,472),(230,439)],
        [(524,156),(588,136),(649,157),(661,206),(719,215),(743,276),(682,307),(644,341),(591,303),(540,244)],
        [(668,359),(702,378),(721,420),(687,461),(657,417)]
    ]
    for p in paths:d.polygon(p,fill=(35,66,74),outline=(94,126,133),width=2)
    pts=[]
    for i in range(161):
        z=i/160
        pts.append((210+z*410,226-55*math.sin(z*math.pi)))
    line(d,pts,G,3);x,y=pts[int(t*9)%160];circ(d,x,y,7,G)
    caption(d,113,110,"АМЕРИКА",SM,M);caption(d,560,110,"ЕВРОПА",SM,M)
def ship(d,t):
    x=475+20*math.sin(t*.2);y=320+3*math.sin(t*.7)
    d.polygon([(x-80,y),(x+81,y),(x+55,y+31),(x-53,y+31)],fill=(153,105,75),outline=G,width=3)
    line(d,[(x,y),(x,y-152)],G,5)
    d.polygon([(x-6,y-137),(x-87,y-16),(x-6,y-16)],fill=(221,212,174))
    d.polygon([(x+7,y-120),(x+78,y-17),(x+7,y-17)],fill=(230,217,183))
    for j in range(13):
        px=120+j*60+11*math.sin(t+j)
        line(d,[(px,403+j%2*6),(px+29,403+j%2*6)],T,2)
def engine(d,t):
    for j,(x,y,r) in enumerate([(304,280,63),(470,272,51),(600,285,62)]):
        d.ellipse((x-r,y-r,x+r,y+r),fill=(35,66,78),outline=G,width=4)
        circ(d,x,y,r*.3,(23,43,55))
        for n in range(12):
            th=n*math.pi/6+t*(.45 if j%2==0 else -.55)
            line(d,[(x+math.cos(th)*r*.4,y+math.sin(th)*r*.4),
                    (x+math.cos(th)*r*.95,y+math.sin(th)*r*.95)],G,3)
    line(d,[(65,231),(861,231)],M,3)
    line(d,[(65,334),(861,334)],M,3)
    for j in range(10):
        x=675+j*44+(t*17)%44
        d.rounded_rectangle((x,274,x+33,284),radius=4,fill=(208,196,160))
def neurons(d,t):
    rng=random.Random(46)
    pts=[(rng.randint(165,798),rng.randint(148,419)) for _ in range(27)]
    for i,(x,y) in enumerate(pts):
        for xx,yy in pts[:i]:
            if (x-xx)**2+(y-yy)**2<150*150:line(d,[(x,y),(xx,yy)],(47,100,106),2)
        circ(d,x,y,5+3*math.sin(t*.6+i)**2,G if i%3==0 else T)
def archival(d,t):
    sh=4*math.sin(t*.4)
    for j in range(3):
        x=250+j*32;y=121+j*27+sh
        d.rounded_rectangle((x,y,x+373,y+259),radius=6,fill=(213-j*18,201-j*16,175-j*13),outline=(94,111,110),width=2)
    caption(d,355,166+sh,"ИСТОРИЧЕСКИЙ ДОКУМЕНТ",H1,(61,82,78))
    for i in range(9):line(d,[(350,211+i*18+sh),(610-i%4*23,211+i*18+sh)],(130,136,116),2)
    d.ellipse((552,343+sh,585,376+sh),fill=(158,90,76))
def timeline(d,t):
    line(d,[(120,286),(841,286)],G,5)
    eras=[("12 300 ЛЕТ",182),("1492",345),("1600",486),("1881",644),("1964",795)]
    for i,(s,x) in enumerate(eras):
        circ(d,x,286,10,T if i<3 else G)
        caption(d,x-40,317+i%2*18,s,SM)
    j=int(t*.15)%len(eras);x=eras[j][1]
    d.ellipse((x-20,266,x+20,306),outline=C,width=2)
def lungs(d,t):
    q=math.sin(t*.6)*6
    d.polygon([(478,162),(417,198),(370,265),(348,330+q),(380,389+q),(455,400+q),(474,271)],fill=(78,135,143),outline=T,width=4)
    d.polygon([(492,162),(553,198),(606,265),(624,330+q),(584,389+q),(507,400+q),(495,271)],fill=(78,135,143),outline=T,width=4)
    line(d,[(486,145),(486,270)],G,8)
    line(d,[(486,261),(429,322)],G,5);line(d,[(486,261),(543,322)],G,5)
def chart(d,t):
    vals=[.28,.53,.45,.72,.87]
    for j,v in enumerate(vals):
        x=196+j*127
        h=220*v*(.9+.1*math.sin(t*.6+j))
        d.rounded_rectangle((x,422-h,x+73,422),radius=8,fill=[T,(89,156,170),G,R,T][j])
    line(d,[(171,422),(841,422)],M,3)
def molecular(d,t):
    for j in range(18):
        yy=120+j*20
        x=475+100*math.sin(j*.4+t*.5)
        xx=960-x
        circ(d,x,yy,6,T);circ(d,xx,yy,6,G)
        line(d,[(x,yy),(xx,yy)],(77,127,137),2)
def drawframe(t,duration,ch,title,visual,beat):
    im=Image.new("RGB",(W,H),P[(ch-1)%len(P)])
    d=ImageDraw.Draw(im);backdrop(d,t)
    mods=["plant","map","ship","engine","neurons","archival","timeline","lungs","chart","molecular"]
    if beat%3==2:visual=mods[(beat+ch*3)%len(mods)]
    elif beat%3==1:visual=mods[(beat+ch*2)%len(mods)]
    if visual not in mods:visual=mods[(ch-1)%len(mods)]
    {"plant":plant,"map":mapworld,"ship":ship,"engine":engine,"neurons":neurons,
     "archival":archival,"timeline":timeline,"lungs":lungs,"chart":chart,"molecular":molecular}[visual](d,t)
    d.rectangle((0,0,960,77),fill=(8,20,30))
    caption(d,28,12,"M1LASH   •   ИСТОРИЯ И НАУКА",SM,G)
    caption(d,28,37,title[:65],H1)
    caption(d,888,21,f"{ch:02d}/07",SM,M)
    d.rectangle((0,489,960,540),fill=(8,20,30))
    caption(d,28,503,"ИСТОРИЧЕСКАЯ РЕКОНСТРУКЦИЯ   /   ОРИГИНАЛЬНАЯ ИНФОГРАФИКА",SUB,M)
    d.rectangle((0,533,int(W*min(1,t/max(1,duration))),540),fill=G)
    return im
def render(cues,out,audio=None,fps=10):
    dur=sum(float(x["duration"]) for x in cues)
    if not 1<=len(cues)<=120 or dur<1:raise ValueError("invalid timed film")
    Path(out).parent.mkdir(parents=True,exist_ok=True)
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgb24","-video_size",f"{W}x{H}","-framerate",str(fps),"-i","pipe:0"]
    if audio:cmd+=["-i",str(audio)]
    cmd+=["-vf","scale=1920:1080:flags=lanczos,format=yuv420p","-c:v","libx264","-preset","veryfast","-crf","25","-r","30","-movflags","+faststart"]
    if audio:cmd+=["-c:a","aac","-b:a","128k","-shortest"]
    else:cmd+=["-an"]
    cmd+=[str(out)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    ends=[];total=0
    for c in cues:
        total+=float(c["duration"]);ends.append(total)
    k=0
    try:
        for i in range(math.ceil(dur*fps)):
            sec=i/fps
            while k<len(cues)-1 and sec>=ends[k]:k+=1
            c=cues[k];scene_start=0 if k==0 else ends[k-1]
            beat=int((sec-scene_start)//7)
            frame=drawframe(sec,dur,int(c["chapter"]),str(c["title"]),c.get("visual","plant"),beat)
            process.stdin.write(frame.tobytes())
            if i%(fps*30)==0:print(f"RENDER {int(sec)}/{int(dur)}",flush=True)
        process.stdin.close()
        if process.wait(timeout=240):raise RuntimeError("ffmpeg encoding error")
    except BaseException:
        process.kill();raise
    return dur
if __name__=="__main__":
    cues=json.loads(Path(sys.argv[1]).read_text())["cues"]
    print(render(cues,sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None))
