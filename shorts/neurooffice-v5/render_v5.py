#!/usr/bin/env python3
"""M1lash NEUROOFFICE V5: authored, deterministic 2D code animation.
User-directed changes: eliminate overlay bugs in schedule, redraw character and robot
as articulated illustrated actors, rebuild windows/office depth and legible UI, retain
Dmitry voice and word-timed subtitles. Does not upload to YouTube.
"""
from __future__ import annotations
import argparse, importlib.util, math, hashlib, json, subprocess, time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('neurooffice_v4',HERE/'render_v4.py')
v4=importlib.util.module_from_spec(spec);spec.loader.exec_module(v4)
base=v4.base
W,H=540,960;FPS=24;CUT=base.CUT
OUT=HERE/'output';OUT.mkdir(exist_ok=True)
INK='#121f31'; TEAL='#54d7d0'; WARM='#f4c68d'; LIGHT='#f4f0e9'; PINK='#f18491'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
FONTS={n:ImageFont.truetype(BOLD,n) for n in (13,14,15,16,17,18,19,20,21,22,23,24,25,28,30,32,36)}
REG={n:ImageFont.truetype(FONT,n) for n in (13,14,16,18,19,20,22,24)}

def clamp(n,a=0,b=1):return min(b,max(a,n))
def smooth(t):t=clamp(t);return t*t*(3-2*t)
def rgba(hex_color,alpha=255):return tuple(bytes.fromhex(hex_color.lstrip('#')))+(alpha,)
def bezier(a,b,c,d,n=18):
    return [((1-u)**3*a[0]+3*(1-u)**2*u*b[0]+3*(1-u)*u*u*c[0]+u**3*d[0],
             (1-u)**3*a[1]+3*(1-u)**2*u*b[1]+3*(1-u)*u*u*c[1]+u**3*d[1]) for u in np.linspace(0,1,n)]

def rr(d,box,fill,r=12,outline=None,width=2):
    d.rounded_rectangle(tuple(map(int,box)),radius=r,fill=fill,outline=outline,width=width)
def caption_text(d,x,y,txt,size=20,fill=LIGHT,anchor='mm'):
    d.text((x,y),txt,fill=fill,font=FONTS[size],anchor=anchor)

def anthropoid(d,x,feet,t,identity='hero',emotion='normal',talk=False,gesture=0,scale=1,eyes_target=0):
    """Hand-drawn, softened adult actor: anatomically plausible soft jaw, articulated arms,
    pupils/eyelids/face expressions. All parts move by easing rules, no imported sprites."""
    S=2; sw,sh=300*S,540*S
    sprite=Image.new('RGBA',(sw,sh),(0,0,0,0));q=ImageDraw.Draw(sprite)
    X=lambda a:round(a*S)
    def poly(points,col,stroke=INK,thick=2):
        p=[(X(xx),X(yy)) for xx,yy in points];q.polygon(p,fill=col)
        if stroke:q.line(p+[p[0]],fill=stroke,width=X(thick),joint='curve')
    def ellipse(box,col,stroke=None,w=2):q.ellipse(tuple(X(v) for v in box),fill=col,outline=stroke,width=X(w))
    def box(b,col,r=10,stroke=None,w=2):q.rounded_rectangle(tuple(X(v) for v in b),fill=col,radius=X(r),outline=stroke,width=X(w))
    def line(p,c,w=2):q.line([(X(a),X(b)) for a,b in p],fill=c,width=X(w),joint='curve')
    who={'hero':('#237f99','#45acc1','#f0bd9d','#332f3c','#354859'),
         'boss':('#9a6550','#c69a73','#edbf9c','#584247','#54454f'),
         'colleague':('#786184','#a989ad','#dfab91','#302d41','#3e4263')}.get(identity)
    coat,coat2,skin,hair,pants=who
    bob=math.sin(t*2.05)*1.9
    handtalk=clamp(gesture)
    # cast shadow and visible, separated soles
    ellipse((71,495,236,520),'#071727')
    for side in (-1,1):
        k=150+side*37
        swing=2.5*math.sin(t*2.2+side*.5)
        poly([(k-24,405),(k+18,407),(k+12+swing,481),(k-22+swing,483)],pants)
        box((k-25+swing,478,k+22+swing,506),'#172537',10,INK,3)
        line([(k-23+swing,490),(k+15+swing,490)],'#557a91',3)
    # neck and throat shadow
    box((133,247+bob,168,300+bob),skin,13,INK,2)
    box((134,264+bob,166,279+bob),'#bb846f',7)
    # torso: tailored jacket softened shoulder and waist
    poly([(150,283),(117,289),(92,304),(76,332),(86,408),(108,439),(197,440),(217,412),(225,331),(204,300),(179,288)],coat,INK,3)
    # gradient-like material bevels, lapels, deep fabric seams
    poly([(98,309),(119,295),(147,438),(113,432),(91,406)],'#276b83' if identity=='hero' else coat2,None)
    poly([(203,299),(175,294),(159,439),(201,432),(217,397)],coat2,None)
    poly([(136,283),(150,303),(166,283),(177,293),(171,432),(130,432),(126,295)],'#eee5d9',None)
    poly([(144,298),(153,314),(165,299),(159,328),(162,387),(151,401),(145,389),(148,326)],'#365872' if identity!='boss' else '#75546c',None)
    poly([(106,308),(131,291),(150,367),(120,350)],'#337f98' if identity=='hero' else coat2,None)
    poly([(195,305),(170,291),(156,364),(184,346)],'#65b8c1' if identity=='hero' else '#d0a087',None)
    line([(106,319),(119,364),(110,416)],'#79c2ca' if identity=='hero' else '#d9af9d',2)
    line([(196,320),(182,367),(194,413)],'#addbd8',2)
    for yy in (366,397):ellipse((173,yy,179,yy+6),WARM)
    box((112,392,130,399),'#9cd1c4',3)
    # shoulders/arms: two independent bones, oriented palms and tapered fingers
    for sign in (-1,1):
        shd=(150+sign*62,315)
        if sign>0:
            elbow=(150+sign*(92+6*handtalk),367-32*handtalk+2*bob)
            hand=(150+sign*(83-35*handtalk),418-132*handtalk+3*bob)
        else:
            elbow=(150+sign*(91-7*handtalk),369+3*bob)
            hand=(150+sign*(82-4*handtalk),423-29*handtalk+2*bob)
        # sleeve tapered upper arm
        line([shd,elbow],INK,32);line([shd,elbow],coat,25)
        ellipse((elbow[0]-10,elbow[1]-11,elbow[0]+10,elbow[1]+11),coat2)
        line([elbow,hand],INK,28);line([elbow,hand],coat2,21)
        # proper cuff at wrist
        dx,dy=hand[0]-elbow[0],hand[1]-elbow[1];mag=max(1,math.hypot(dx,dy))
        vec=(dx/mag,dy/mag)
        line([(hand[0]-17*vec[0],hand[1]-17*vec[1]),(hand[0]-7*vec[0],hand[1]-7*vec[1])],'#e7ece7',17)
        # mitten palm deliberately softened with small, separated fingers, not fork/claw
        ellipse((hand[0]-12,hand[1]-11,hand[0]+12,hand[1]+13),skin,INK,2)
        for fi in (-1,0,1):
            xx=hand[0]+fi*6; yy=hand[1]+8
            line([(xx,yy),(xx+fi*1.5,yy+9)],'#b87d69',3)
        line([(hand[0]-sign*9,hand[1]-2),(hand[0]-sign*16,hand[1]-5)],skin,5)
    # face - curved jawline instead of triangular paddle: vector bezier sampled in code
    tilt=math.sin(t*.88)*1.7+(2.2 if emotion=='scared' else 0)
    face=[(106,150),(112,119),(127,108),(155,104),(179,112),(195,132),(200,157)]
    face+=bezier((200,157),(203,204),(187,249),(159,259),19)[1:]
    face+=bezier((159,259),(143,271),(111,252),(102,211),19)[1:]
    face+=bezier((102,211),(96,190),(101,164),(106,150),13)[1:]
    face=[(xx,yy+bob*.6+tilt*.2) for xx,yy in face]
    # subtle ear against back face
    ellipse((96,167,115,197),skin,INK,2)
    ellipse((186,168,205,197),skin,INK,2)
    poly(face,skin,INK,3)
    # cheek shading follows jaw, not literal rectangles
    poly([(110,180),(115,138),(132,128),(129,222),(116,241)],'#fad0af',None)
    poly([(183,141),(195,153),(193,217),(176,246),(184,210)],'#cc927f',None)
    ellipse((116,210,133,218),'#e5a18e');ellipse((175,210,190,219),'#df9b88')
    # brow arc asymmetry and eyes tracked independently
    blink=(t+(.35 if identity=='boss' else 0))%4.05<.15
    for dx in (-27,27):
        ex=152+dx;ey=165+(3 if dx>0 else 0)
        lift= -8 if emotion=='scared' else 2.3*math.sin(t*.82+dx/51)
        line([(ex-12,ey-23+lift),(ex,ey-27+lift),(ex+11,ey-23+lift)],hair,3)
        if not blink:
            ellipse((ex-11,ey-9,ex+11,ey+9),'#fffaf1',INK,2)
            look=clamp(eyes_target,-1,1)*3+1.2*math.sin(t*.65+dx*.03)
            ellipse((ex-3+look,ey-4,ex+5+look,ey+7),'#42667a')
            ellipse((ex+look,ey-3,ex+3+look,ey+4),'#172739')
            ellipse((ex+1+look,ey-3,ex+3+look,ey-1),'#ffffff')
        else:line([(ex-12,ey+1),(ex+11,ey)],hair,2)
    poly([(151,177),(158,188),(152,195),(145,194)],'#bc806c',None)
    # mouth: quiet, smile, surprised, vocal envelope, and lower lip
    voice=clamp(float(talk))
    if voice>.18:
        mh=3+13*voice
        ellipse((141,219,163,226+mh),'#683f49')
        ellipse((149,228,157,229+mh*.48),'#e7a2a0')
    elif emotion=='scared':
        line([(140,226),(149,223),(155,225),(164,222)],'#753e4c',3)
    elif emotion=='smile':
        q.arc(tuple(X(v) for v in (137,207,169,241)),0,180,fill='#854953',width=5)
    else:line([(140,225),(152,227),(164,224)],'#814f52',3)
    # original asymmetric hairline. Better detailed than polygon helmet, still reproducible.
    poly([(99,173),(101,130),(109,112),(123,101),(139,107),(157,98),(179,108),(190,126),
         (198,151),(186,145),(178,131),(160,132),(150,121),(136,139),(120,134),(106,155)],hair,INK,3)
    poly([(108,121),(125,108),(142,116),(120,126)],'#67505c',None)
    line([(160,109),(180,121)],'#65515b',3)
    # light consistent sprite movement
    sprite=sprite.resize((round(300*scale),round(540*scale)),Image.Resampling.LANCZOS)
    return sprite,(round(x-150*scale+.6*math.sin(t*1.3)),round(feet-510*scale+2*scale*math.sin(t*2.1)))

def robot(d_x,feet,t,scale=1,emotion='normal',gesture=0,talk=False):
    """Articulated glass-faced AI director: rounded silhouette, real layered visor and motor joints."""
    S=2; im=Image.new('RGBA',(340*S,560*S));q=ImageDraw.Draw(im)
    X=lambda n:round(n*S)
    def p(points,fill,outline=INK,w=3):
        pp=[(X(a),X(b)) for a,b in points];q.polygon(pp,fill=fill)
        if outline:q.line(pp+[pp[0]],fill=outline,width=X(w),joint='curve')
    def e(box,fill,outline=None,w=2):q.ellipse(tuple(X(v) for v in box),fill=fill,outline=outline,width=X(w))
    def r(box,fill,rad=10,outline=None,w=2):q.rounded_rectangle(tuple(X(v) for v in box),radius=X(rad),fill=fill,outline=outline,width=X(w))
    def l(points,fill,w=3):q.line([(X(a),X(b)) for a,b in points],fill=fill,width=X(w),joint='curve')
    bob=math.sin(t*1.9)*2.5; g=clamp(gesture)
    e((85,505,257,532),'#071625')
    # boots/legs - elliptical cuffs with articulated ankle housings
    for sx in (123,219):
        p([(sx-26,410),(sx+19,410),(sx+20,482),(sx-22,485)],'#4e7184')
        r((sx-37,474,sx+35,509),'#263e55',11,INK,3)
        l([(sx-20,494),(sx+23,494)],'#789da3',3)
        r((sx-6,448,sx+9,475),'#5ce0d2',5)
    # body and shoulder yoke elliptical armor, not a single gray box
    p([(114,271),(216,271),(250,302),(260,349),(251,416),(216,458),(118,459),(81,420),(78,349),(90,303)],'#49687b',INK,4)
    p([(111,299),(221,299),(241,348),(233,409),(210,435),(124,435),(105,410),(96,347)],'#9abdc0',INK,3)
    p([(113,309),(220,308),(231,358),(219,411),(169,437),(122,415),(106,355)],'#bcd3ce',None)
    p([(129,337),(206,336),(215,382),(173,413),(126,387)],'#315368',INK,3)
    r((150,348,192,379),'#4fd5d0',11,INK,2)
    r((160,358,181,369),'#ddfff6',4)
    l([(111,317),(126,309),(147,316)],'#e4e8d9',3)
    l([(202,420),(225,402)],'#749eab',3)
    # arms with joint discs and gripper fingers (actual movement)
    for sign in (-1,1):
        sh=(169+sign*95,309)
        el=(169+sign*(117-13*g),381-40*g if sign>0 else 386)
        hand=(169+sign*(103-58*g),454-140*g if sign>0 else 450)
        l([sh,el],INK,32);l([sh,el],'#5c8292',23)
        e((el[0]-16,el[1]-16,el[0]+16,el[1]+16),'#254154',INK,3)
        e((el[0]-7,el[1]-7,el[0]+7,el[1]+7),'#70d9ce')
        l([el,hand],INK,23);l([el,hand],'#9fbec0',16)
        r((hand[0]-13,hand[1]-10,hand[0]+13,hand[1]+11),'#295065',6,INK,2)
        for fi in (-1,0,1):
            l([(hand[0]+fi*7,hand[1]+6),(hand[0]+fi*10,hand[1]+17)],'#a0c7c3',3)
        e((sh[0]-21,sh[1]-17,sh[0]+21,sh[1]+20),'#d5e0d6',INK,3)
    # neck struts and subtle pistons
    for xx in (143,192):
        r((xx-8,252,xx+9,298),'#315063',4)
        r((xx-3,265,xx+4,288),'#60d6cd',3)
    # round helmet with thick gasket, expressive faceplate / reflections
    head=(80,101+bob,260,269+bob)
    r(head,'#86aeb7',45,INK,5)
    r((89,111+bob,251,256+bob),'#dae4d8',38,'#5f8291',2)
    r((101,125+bob,240,236+bob),'#152a3d',36,INK,2)
    p([(111,160+bob),(133,135+bob),(157,134+bob),(128,217+bob),(110,205+bob)],'#2b4d5e',None)
    p([(209,135+bob),(232,156+bob),(226,202+bob),(207,220+bob)],'#28485a',None)
    # electric oval eyes with upper eyelids
    for xx in (144,200):
        active=PINK if emotion=='deny' else TEAL
        e((xx-16,169+bob,xx+16,194+bob),'#2a4c57')
        e((xx-9,175+bob,xx+7,189+bob),active)
        e((xx-7,175+bob,xx-2,180+bob),'#e6ffff')
    # energy equalizer tied to genuine envelope
    if emotion=='deny':
        r((146,210+bob,204,218+bob),PINK,4)
    elif float(talk)>.15:
        for j in range(5):
            amp=3+15*float(talk)*(.4+.6*math.sin(t*10+j*.7)**2)
            r((146+j*12,216+bob-amp/2,152+j*12,216+bob+amp/2),TEAL,3)
    else:
        q.arc(tuple(X(v) for v in (148,193+bob,207,231+bob)),start=8,end=175,fill=TEAL,width=X(4))
    r((153,117+bob,209,129+bob),'#e9b987',5)
    r((80,179+bob,90,215+bob),TEAL if emotion!='deny' else PINK,5)
    r((251,159+bob,271,229+bob),'#658f9e',9,INK,3)
    e((260,182+bob,278,201+bob),PINK if emotion=='deny' else TEAL,INK,2)
    l([(106,151+bob),(127,128+bob),(146,122+bob)],'#fff4e1',3)
    l([(210,247+bob),(239,226+bob)],'#c5e6df',3)
    # decorative but meaningful CEO seal on chassis, no technical caption
    l([(165,390),(174,397),(183,390)],'#63bcb3',3)
    im=im.resize((round(340*scale),round(560*scale)),Image.Resampling.LANCZOS)
    return im,(round(d_x-170*scale+1*math.sin(t*.9)),round(feet-510*scale+scale*1.7*math.sin(t*2)))

# Replace old simple rig. Base's scene acting automatically uses our new actors.
base.draw_human=anthropoid;base.draw_robot=robot

# Sophisticated, perspective office windows with layered city, mullions and light pools.
ORIG_BG=base.bg
BG_CACHE={}
def set_bg(scene,t):
    key=scene
    if key not in BG_CACHE:
        im=base.BGS[scene].copy()
        d=ImageDraw.Draw(im)
        if scene in (3,5):
            # previous version had featureless blue graph-paper grid. Real atrium wall instead.
            d.rectangle((0,95,540,960),fill='#1a2b40')
            rr(d,(23,100,517,618),'#31516b',14,'#628599',3)
            rr(d,(39,116,500,596),'#10253a',9)
            # skyline three-depth parallax layers are purpose-designed vector shapes.
            for idx in range(15):
                xx=40+idx*36
                h=75+((idx*29)%151)
                rr(d,(xx,590-h,xx+45,592),'#203d53' if idx%2 else '#1b354b',2)
                for yy in range(590-h+13,585,19):
                    for x2 in range(xx+9,xx+40,15):
                        if ((yy+x2+idx)%5)<2:rr(d,(x2,yy,x2+5,yy+9),'#48768b',1)
            # soft cyan atmospheric sunrise horizon, no giant skybox blur
            d.line((40,569,502,569),fill='#416d79',width=4)
            for xx in (43,197,352,496):d.line((xx,116,xx,596),fill='#698497',width=5)
            d.line((39,354,502,354),fill='#4e687c',width=4)
            d.line((39,596,500,596),fill='#c1947e',width=6)
            d.polygon([(0,613),(540,589),(540,960),(0,960)],fill='#20374c')
            for yy in (670,749,828,907):d.line((0,yy,540,yy-17),fill='#375065',width=2)
            for xx in (65,155,371,511):d.line((xx,616,270+(xx-270)*2,960),fill='#355268',width=2)
            # sconces
            rr(d,(5,121,17,300),'#e5be87',5)
            rr(d,(523,121,536,300),'#69b8bd',5)
        else:
            im=ORIG_BG(scene,0)
        BG_CACHE[key]=im
    im=BG_CACHE[key].copy();d=ImageDraw.Draw(im)
    # ambient status lamps breathe; do not cover characters or legibility
    if scene in (3,5):
        yy=140+4*math.sin(t*.65)
        d.ellipse((481,yy,489,yy+8),fill='#71d9cf')
    return im
base.bg=set_bg

ORIG_SCENE=base.scene_frame

def schedule_screen(t):
    """Redesigned graph, no overpaint on row data. One translucent container, 3 distinct rows,
    only actual spoken days show night badges; 'Thursday' intentionally omitted.
    """
    im=set_bg(3,t);d=ImageDraw.Draw(im)
    # left actor framed to preserve breathing room
    base.paste(im,anthropoid(d,111,766,t,'hero','scared',talk=base.vocal_at(CUT[3]+t),
                              gesture=.45+.35*math.sin(t*1.9)**2,scale=.78,eyes_target=1))
    d=ImageDraw.Draw(im)
    # one panel rather than overlapping floating bars
    rr(d,(231,129,520,681),'#0b2135',19,'#6a93a5',3)
    rr(d,(244,144,508,202),'#244e66',12)
    caption_text(d,376,173,'МОЙ ГРАФИК',23,LIGHT)
    # three rows stacked with a full-width coherent hierarchy, no hidden labels
    for idx,(day,stamp) in enumerate((('ПОНЕДЕЛЬНИК',3.37),('ВТОРНИК',5.48),('СРЕДА',8.02))):
        top=217+idx*136;bottom=top+121
        rr(d,(244,top,508,bottom),'#1a354b',13,'#40647b',2)
        caption_text(d,260,top+26,day,16,'#b8d3db','lm')
        if t<stamp:
            rr(d,(264,top+62,481,top+91),'#27465c',8)
            # three quiet inactive blocks, no meaningless empty alert frame
            for k in range(3):rr(d,(277+k*58,top+73,312+k*58,top+79),'#3e6575',3)
        else:
            rr(d,(265,top+57,485,top+103),'#7c3b55',11,'#cc8195',1)
            # tiny moon icon and strong text, both visible above all overlays
            d.ellipse((282,top+71,299,top+88),fill='#ffe9ca')
            d.ellipse((290,top+68,306,top+85),fill='#7c3b55')
            caption_text(d,389,top+79,'НОЧЬ',21,'#fff1e8')
    # Punchline appears with the final phrase, no fourth blank row implying shifts we don't know.
    if t>=8.26:
        rr(d,(255,641,497,673),'#59394c',9)
        caption_text(d,376,656,'ТРИ НОЧИ ПОДРЯД',15,'#ffd5d0')
    # label at upper far left is story-relevant, not technical metadata
    if t>=7.5:
        rr(d,(17,130,209,183),'#523147',13)
        caption_text(d,112,156,'СЕРЬЁЗНО?!',18,'#f6d6d4')
    return im

def render_scene(scene,t,span):
    if scene==3:
        im=schedule_screen(t)
    else:
        im=ORIG_SCENE(scene,t,span)
    # v4 has intentional story VFX but buggy schedule overpaint; skip scene 3 fully.
    if scene!=3:im=v4.story_fx(im,scene,t,span)
    else:im=Image.alpha_composite(im.convert('RGBA'),v4.VIGNETTE).convert('RGB')
    # Eliminate double progress UI. Paint safe underlay over V3's old long progress bar.
    # For other scenes, erase only progress strip (not the actors, whose feet end above it).
    d=ImageDraw.Draw(im)
    if scene!=3:
        d.rectangle((0,787,540,813),fill='#1d3045' if scene in (3,5) else '#1c3247')
    # Single caption container, at a consistent bottom baseline.
    im=caption_v5(im,scene,t)
    return im

def caption_v5(im,scene,t):
    item=v4.caption_at(scene,t)
    if item is None:return im
    label,st,en,_,_=item
    d=ImageDraw.Draw(im)
    rows=label.split('|')
    # Keep 2-line cards readable and below the action safe area.
    top=810 if len(rows)==1 else 793;h=103 if len(rows)==1 else 120
    rr(d,(20,top,520,top+h),'#091c2e',17,'#537487',2)
    for j,row in enumerate(rows):
        text_size=22
        while text_size>16 and d.textbbox((0,0),row,font=FONTS[text_size])[2]>455:text_size-=1
        caption_text(d,270,top+37+j*42,row,text_size,LIGHT)
    # Only one unobtrusive progress line, no full-video timeline across person feet.
    p=clamp((t-st)/max(.15,en-st))
    rr(d,(69,top+h-16,471,top+h-12),'#344b5d',2)
    if p>0:rr(d,(69,top+h-16,69+402*p,top+h-12),PINK if scene in (3,5) else TEAL,2)
    return im

def build_preview():
    base.load_voice_energy()
    thumbs=[]
    for si in range(7):
        span=CUT[si+1]-CUT[si]
        for f in (.28,.78):
            im=render_scene(si,span*f,span)
            im.save(OUT/f'V5_SCENE_{si+1}_{int(f*100)}.png')
            thumbs.append(im.resize((216,384),Image.Resampling.LANCZOS))
    contact=Image.new('RGB',(216*7,384*2),'#092138')
    for i,thumb in enumerate(thumbs):contact.paste(thumb,((i//2)*216,(i%2)*384))
    contact.save(OUT/'V5_STORYBOARD.jpg',quality=91)
    return contact

def audio_pcm_hash(path):
    x=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(path),'-vn','-ac','1','-ar','48000','-f','s16le','-'])
    return hashlib.sha256(x).hexdigest()

def run(preview_only=False):
    v4.validate_cues()
    assert (HERE/'voice_dima.m4a').exists(), 'Owner voice missing'
    base.load_voice_energy()
    build_preview()
    if preview_only:return
    frames=HERE/'frames';frames.mkdir(exist_ok=True)
    n=round(CUT[-1]*FPS)
    for i in range(n):
        p=frames/f'{i:05d}.jpg'
        if p.exists():continue
        time_i=i/FPS
        scene=next((j for j in range(7) if CUT[j]<=time_i<CUT[j+1]),6)
        im=render_scene(scene,time_i-CUT[scene],CUT[scene+1]-CUT[scene])
        im.save(p,'JPEG',quality=87,subsampling=0)
        if i%120==0:print('V5:',i,'/',n,flush=True)
    file=OUT/'M1LASH_NEUROOFFICE_V5_RU.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-framerate',str(FPS),'-i',str(frames/'%05d.jpg'),
                    '-i',str(HERE/'voice_dima.m4a'),'-map','0:v:0','-map','1:a:0',
                    '-vf','scale=1080:1920:flags=lanczos,format=yuv420p',
                    '-c:v','libx264','-preset','veryfast','-crf','20','-c:a','copy','-movflags','+faststart',str(file)],check=True)
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(file),'-f','null','-'],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(file)]))
    sec=float(probe['format']['duration'])
    if abs(sec-CUT[-1])>.12:raise RuntimeError('A/V drift')
    qa={'status':'TECH_PASS_ARTISTIC_QA_REQUIRED','duration':sec,'fps':FPS,'frames':n,
        'size':file.stat().st_size,'resolution':'1080x1920',
        'audio_pcm_identical':audio_pcm_hash(file)==audio_pcm_hash(HERE/'voice_dima.m4a'),
        'caption_cues':'original 80 speech word timings; 19 phrase cards',
        'schedule_overdraw':'fixed: no visual overlays drawn over schedule rows',
        'new_characters':'bezier human rounded jaw, full new robot curved visor, animated rig, code-only',
        'new_bg':'parallax-looking hand-coded office window/city skyline stage, no template labels',
        'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'youtube_uploaded':False}
    if not qa['audio_pcm_identical']:raise RuntimeError('NO-GO: voice changed')
    (OUT/'QA_V5.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    print(json.dumps(qa,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--preview',action='store_true');ap.add_argument('--render',action='store_true')
    args=ap.parse_args();run(preview_only=args.preview and not args.render)