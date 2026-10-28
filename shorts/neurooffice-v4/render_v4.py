#!/usr/bin/env python3
"""Neurooffice S01 teaser v4: original frame-accurate, code-driven 2D animation.
No third-party video/visual assets. Audio preserved from the owner's previous Dmitry voiced teaser.
Usage: python render_v2.py --preview | python render_v2.py --render
"""
from __future__ import annotations
import argparse, math, random, subprocess, json, hashlib, io
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parent
PREVIOUS=Path(__file__).resolve().parent/'voice_dima.m4a'
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
# Design coordinates. All vectors, shadows, faces, camera positions & text authored in code.
W,H=540,960; FPS=24
CUT=[0,7.375,13.750,20.000,29.625,38.250,46.375,51.791667]
INK='#0b1526'; LINE='#192439'; CYAN='#56dacc'; WHITE='#f9f3e9'; HOT='#f38a8f'; GOLD='#e5bb77'
P1='#10243c'; P2='#1f344c'; LIGHT='#bdd5da'; GREY='#92a5b2'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
TTF={}
for size in [12,13,15,16,17,19,20,21,22,24,26,28,30,34,38,42]:
 TTF[size]=ImageFont.truetype(BOLD,size)

def f(r):return max(0,min(1,r))
def ease(t):t=f(t);return t*t*(3-2*t)
def mix(a,b,t):return a+(b-a)*t

def rect(d,b,fill,r=10,stroke=None,sw=2):
 x,y,x1,y1=b
 d.rounded_rectangle([int(x),int(y),int(x1),int(y1)], radius=int(min(r,(x1-x)/2,(y1-y)/2)), fill=fill,outline=stroke,width=sw)
def txt(d,xy,s,size=16,col=WHITE,anchor='la'):
 d.text(xy,s,font=TTF[size],fill=col,anchor=anchor,stroke_width=0)
def poly(d,points,fill,outline=None,width=2):
 d.polygon([(int(x),int(y)) for x,y in points],fill=fill)
 if outline:d.line([(int(x),int(y)) for x,y in points]+[(int(points[0][0]),int(points[0][1]))],fill=outline,width=width,joint='curve')
def line(d,points,fill,width=3):d.line(points,fill=fill,width=width,joint='curve')
def orb(d,x,y,r,c):d.ellipse((x-r,y-r,x+r,y+r),fill=c)

def gradient(top,bottom):
 a=np.array(tuple(bytes.fromhex(top.lstrip('#'))),dtype=np.float32);b=np.array(tuple(bytes.fromhex(bottom.lstrip('#'))),dtype=np.float32)
 y=np.linspace(0,1,H,dtype=np.float32)[:,None]
 colors=(a*(1-y)+b*y).astype(np.uint8)
 return Image.fromarray(np.broadcast_to(colors[:,None,:],(H,W,3)).copy(),'RGB')
VOICE_ENERGY=[]

def load_voice_energy():
 global VOICE_ENERGY
 raw=subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(PREVIOUS),'-vn','-ac','1','-ar','8000','-f','f32le','-'])
 values=np.frombuffer(raw,dtype=np.float32)
 sz=333
 VOICE_ENERGY=[float(np.sqrt(np.mean(values[i:i+sz]**2))) for i in range(0,len(values),sz)]

def vocal_at(sec):
 if not VOICE_ENERGY:return .5
 idx=max(0,min(len(VOICE_ENERGY)-1,int(sec*8000/333)))
 # Envelope low frequencies stay below threshold. No claim of phoneme accuracy.
 v=max(VOICE_ENERGY[max(0,idx-1):min(len(VOICE_ENERGY),idx+2)])
 return f((v-.014)/.10)

BGS={0:gradient('#101e36','#294459'),1:gradient('#1c283b','#4c3b43'),2:gradient('#0d283b','#234c50'),3:gradient('#1b233c','#272c52'),4:gradient('#171f36','#3a3c55'),5:gradient('#2b253d','#302c48'),6:gradient('#161a37','#223d4a')}

def bg(scene,t):
 im=BGS[scene].copy();d=ImageDraw.Draw(im)
 # Cinematic set architecture, left-lit windows, spatial perspective and material detail.
 if scene in (0,2,4,6):
  rect(d,(23,115,510,555),'#203a50',18, '#43647a',2)
  rect(d,(43,135,489,522),'#0b1e35',12)
  for cx in (48,195,342):
   rect(d,(cx,142,cx+142,516),'#173249',3)
   for n in range(7):
    bx=cx+7+17*(n%7)
    yy=293+((n*31+cx)%6)*29
    rect(d,(bx,yy,bx+13,yy+17),'#2c5265',1)
   line(d,[(cx+128,145),(cx+128,512)],'#536778',3)
  line(d,[(47,519),(491,519)],'#b47d65',6)
  rect(d,(0,551,540,960),'#20394b',2)
  for j in range(12):
   yy=552+j*43
   line(d,[(0,yy),(540,yy-46)],'#324f5d',1)
  for bx in (66,164,405,517):line(d,[(bx,552),(270+(bx-270)*1.9,960)],'#3b5765',1)
  # wall lights
  rect(d,(12,103,28,335),'#ecc085',7)
  rect(d,(506,103,520,335),'#4ea9b3',7)
 elif scene in (1,):
  rect(d,(0,106,540,660),'#372f3f',4)
  for x in range(41,500,24):line(d,[(x,118),(x,490)],'#4a3d4b',1)
  rect(d,(44,132,496,483),'#3a4557',18,'#80716e',4)
  rect(d,(70,158,470,463),'#223044',10)
  for j in range(8):line(d,[(72,180+j*35),(469,180+j*35)],'#9c8b79',3)
  rect(d,(0,555,540,960),'#483b49',3)
  poly(d,[(0,558),(540,533),(540,960),(0,960)],'#443b48')
  for j in range(7):line(d,[(0,600+j*53),(540,572+j*55)],'#625058',1)
 elif scene in (3,5):
  rect(d,(0,116,540,620),'#222e47',1)
  for x in range(0,600,80):line(d,[(x,128),(x-28,585)],'#34435a',2)
  for y in range(140,620,77):line(d,[(0,y),(540,y)],'#39495c',2)
  rect(d,(0,620,540,960),'#222a43',1)
  for n in range(6):line(d,[(0,670+n*50),(540,645+n*56)],'#374258',1)
 # Volumetric left light, additive-style translucent paths.
 fx=Image.new('RGBA',(W,H),(0,0,0,0));ld=ImageDraw.Draw(fx)
 if scene not in (3,5):
  poly(ld,[(30,180),(115,180),(400,685),(175,720)],(110,201,202,14))
  poly(ld,[(475,105),(500,140),(330,635),(288,615)],(241,182,114,12))
 for p in range(15):
  x=(p*89+26+math.sin(t*.34+p)*12)%W;y=(p*129+67+math.sin(t*.41+p*2)*9)%730+110
  orb(ld,x,y,1+(p%3==0),(144,199,198,25))
 im=Image.alpha_composite(im.convert('RGBA'),fx).convert('RGB')
 return im

def outline_ellipse(d,b,c,outline=INK,w=3):d.ellipse(b,fill=c,outline=outline,width=w)

def draw_human(d,x,feet,t,identity='hero',emotion='normal',talk=False,gesture=0.0,scale=1,eyes_target=0):
 """Premium bespoke 2D cutout-ish articulated actor: curves, hands/fingers, hair, shoulder weights.
 every component positioned relative to bones, head and shoulder independent motion.
 """
 # Local 300x540 sprite keeps rig deterministic and supports different shot scales.
 S=2; a=Image.new('RGBA',(300*S,540*S));q=ImageDraw.Draw(a)
 def sc(v):return round(v*S)
 def coords(bb):return tuple(sc(v) for v in bb)
 def R(bb,col,rad=8,edge=None,ew=2):
  q.rounded_rectangle(coords(bb),radius=sc(rad),fill=col,outline=edge,width=sc(ew))
 def E(bb,col,edge=None,width=2):q.ellipse(coords(bb),fill=col,outline=edge,width=sc(width))
 def P(p,col,edge=None,width=2):
  pp=[(sc(px),sc(py)) for px,py in p];q.polygon(pp,fill=col)
  if edge:q.line(pp+[pp[0]],fill=edge,width=sc(width),joint='curve')
 def L(p,col,w):q.line([(sc(u),sc(v)) for u,v in p],fill=col,width=sc(w),joint='curve')
 def T(x,y,word,size,col):q.text((sc(x),sc(y)),word,font=ImageFont.truetype(BOLD,sc(size)),fill=col)
 idle=math.sin(t*1.9)*2
 headtilt=math.sin(t*.7)*.6+(6 if emotion=='scared' else 0)
 blink=(t*1.04+.7+(0.35 if identity=='boss' else 0))%4.3<.13
 # feet shadows / boots
 E((59,494,239,522),'#102637')
 for dx in (-32,29):
  P([(148+dx-20,404),(148+dx+16,404),(147+dx+13,486),(147+dx-22,488)],'#314057',INK,3)
  R((107+dx,477,159+dx,507),'#0b1b30',13)
  L([(110+dx,488),(156+dx,488)],'#668795',3)
 # hair & suits vary, boss earthy orange, hero cyan jacket, colleague plum
 colors={'hero':('#327b8b','#59bfc0','#d49b7d','#2d2835','#334455'),
         'boss':('#8e5b43','#b98561','#e2b091','#3d343d','#45505e'),
         'colleague':('#7b5a82','#a57caa','#bb856c','#2b2536','#2e3551')}
 suit,lit,skin,hair,trou=colors[identity]
 # neck behind head
 R((132,245,164,313),skin,11,INK,2)
 P([(149,279),(119,289),(90,309),(71,422),(90,445),(208,445),(228,422),(202,307),(175,290)],suit,INK,4)
 P([(133,288),(145,306),(154,287),(169,308),(177,289),(168,442),(132,442)],'#ece6d9')
 P([(143,300),(155,310),(168,300),(162,322),(166,388),(152,409),(145,384),(149,322)],'#db967a' if identity=='boss' else '#3b6177')
 P([(99,308),(126,291),(144,443),(94,441)],'#255568' if identity=='hero' else '#704d48' if identity=='boss' else '#65446b')
 P([(201,307),(171,292),(166,443),(207,439)],lit)
 # fabric crease seams
 L([(105,319),(121,365),(103,419)],'#679baa' if identity=='hero' else '#d3a084',2)
 L([(197,319),(182,360),(201,421)],'#b2d1cc',2)
 # arm segments, wrists, expressive gesture; physical shoulder/elbow/hand
 for sign in (-1,1):
  sh=(150+sign*61,313)
  if gesture>.2 and sign>0:
   elbow=(150+sign*(86+8*gesture),365-40*gesture)
   hand=(150+sign*(51+28*gesture),389-130*gesture)
  else:
   elbow=(150+sign*(94-10*gesture),367+3*idle)
   hand=(150+sign*(82-10*gesture),426-35*gesture)
  L([sh,elbow],INK,31);L([sh,elbow],suit,23)
  L([elbow,hand],INK,26);L([elbow,hand],lit,18)
  # cuff
  dx=hand[0]-elbow[0];dy=hand[1]-elbow[1];mag=max(1,(dx*dx+dy*dy)**.5)
  vx,vy=dx/mag,dy/mag
  L([(hand[0]-vx*16,hand[1]-vy*16),(hand[0]-vx*2,hand[1]-vy*2)],'#ece9de',20)
  # palm as oriented mitten + five small fingers, deliberately anatomical rather than circle
  E((hand[0]-12,hand[1]-15,hand[0]+12,hand[1]+10),skin,INK,2)
  for fi in range(4):
   wx=hand[0]+(fi-1.5)*5;wy=hand[1]+6
   L([(wx,wy),(wx+sign*2,wy+9+2*(fi%2))],skin,3.8)
  L([(hand[0]-sign*9,hand[1]-4),(hand[0]-sign*18,hand[1]-12)],skin,4)
 # ears, neck shadow, face side volume, sculpted jaw
 E((92,144,114,185),skin,INK,2);E((187,144,211,185),skin,INK,2)
 P([(111,99),(181,103),(199,129),(204,180),(196,232),(174,259),(153,271),(127,261),(105,232),(97,185),(100,132)],skin,INK,4)
 # soft warm skin lighting
 P([(111,127),(135,113),(126,222),(115,244),(104,206)],'#f1c0a0')
 P([(183,122),(200,148),(194,225),(171,256),(184,218)],'#b9816e')
 # nose 3/4 profile and lips
 P([(153,167),(164,195),(157,201),(146,196)],'#bb816d')
 # eyes expressive with actual separate pupils, eyelids and brow asymmetry
 for dx in (-27,27):
  xx=150+dx;yy=166+(3 if dx>0 else 0)- (3 if emotion=='scared' else 0)
  if not blink:
   E((xx-12,yy-9,xx+12,yy+10),'#f6f1df',INK,2)
   pupil=eyes_target*4+1.8*math.sin(t*0.96+dx*.04)
   E((xx-2+pupil,yy-5,xx+7+pupil,yy+9),'#324a58')
   E((xx+1+pupil,yy-4,xx+4+pupil,yy+1),'#0b2131')
   E((xx+1+pupil,yy-5,xx+4+pupil,yy-2),'#ffffff')
  else:L([(xx-13,yy),(xx+13,yy)],INK,3)
  by=yy-22-(6 if emotion=='scared' else 0)
  brow_lift=(2.0*math.sin(t*1.25+dx*.12)) if emotion!='scared' else -2
  L([(xx-14,by+1+brow_lift),(xx+6,by-2+brow_lift if emotion=='scared' else by+4+brow_lift)],hair,5)
 if emotion=='scared':
  if talk:
   E((142,221,162,235+5*f(talk)),'#603b47')
  else:
   L([(141,228),(148,224),(156,227),(162,225)],'#603b47',3)
 elif talk:
  # mouth driven by actual audio amplitude, not permanent O
  E((142,222,164,226+14*f(talk)),'#583141');E((150,227,156,230+8*f(talk)),'#df979b')
 elif emotion=='smile':q.arc(coords((135,212,171,241)),start=4,end=176,fill='#5c3440',width=sc(3))
 else:L([(140,227),(163,228)],'#6d4751',3)
 E((110,210,129,219),'#e4a08e');E((177,210,193,219),'#d8927a')
 # subtle smile lines and cheek catchlights
 if emotion=='smile':
  L([(128,225),(134,230)],'#b77c69',2)
  L([(169,230),(175,224)],'#b77c69',2)
 E((109,194,114,198),'#f8c5a4');E((186,194,191,198),'#f8c5a4')
 # hair shape with asymmetric cropped quiff and tiny highlight, no generic round cap
 if identity=='hero':
  P([(98,161),(100,112),(119,86),(140,95),(157,86),(177,94),(193,112),(199,145),(186,132),(174,135),(166,115),(140,132),(123,127),(106,150)],hair,INK,3)
  P([(107,115),(131,99),(153,110),(125,116)],'#5b4a55')
 elif identity=='boss':
  P([(96,159),(92,118),(120,87),(148,81),(176,96),(201,130),(190,144),(178,119),(145,124),(125,112),(108,144)],hair,INK,4)
  P([(99,124),(123,95),(137,96),(115,128)],'#665152')
  # subtle sideburns
  P([(100,162),(107,161),(113,193),(99,187)],hair)
 else:
  P([(98,169),(95,113),(112,88),(137,77),(164,89),(189,112),(200,157),(189,183),(184,132),(166,105),(137,118),(108,146),(109,189)],hair,INK,4)
  P([(98,163),(110,161),(113,217),(100,213)],hair)
  P([(184,158),(196,166),(193,217),(184,219)],hair)
 # V4 original code-drawn clothing finish, highlights and lapel stitches.
 L([(185,350),(193,354),(201,351)],'#accfc8',2)
 L([(106,354),(118,359)],'#9ac2b9',2)
 E((176,370,180,374),'#eac48d')
 E((176,404,180,408),'#eac48d')
 # light animated face tilt/body tilt
 if abs(headtilt)>1:pass
 # scale local sprite and paste alpha
 newsize=(round(300*scale),round(540*scale))
 a=a.resize((newsize[0]*S,newsize[1]*S),Image.Resampling.LANCZOS)
 a=a.resize(newsize,Image.Resampling.LANCZOS)
 return a,(round(x-150*scale+scale*.8*math.sin(t*1.35)),round(feet-510*scale+scale*1.5*math.sin(t*2.9)))

def draw_robot(x,feet,t,scale=1,emotion='normal',gesture=0.0,talk=False):
 """Director K-07: asymmetrical cybernetic executive with ceramic material and hinged actuators."""
 S=2;a=Image.new('RGBA',(340*S,560*S));d=ImageDraw.Draw(a)
 def zz(v):return round(v*S)
 def R(bb,c,r=8,ed=None,w=2):d.rounded_rectangle(tuple(zz(u) for u in bb),fill=c,radius=zz(r),outline=ed,width=zz(w))
 def P(pp,c,ed=None,w=2):
  ps=[(zz(q),zz(r)) for q,r in pp];d.polygon(ps,fill=c)
  if ed:d.line(ps+[ps[0]],fill=ed,width=zz(w),joint='curve')
 def E(bb,c,ed=None,w=2):d.ellipse(tuple(zz(u) for u in bb),fill=c,outline=ed,width=zz(w))
 def L(pp,c,w=3):d.line([(zz(u),zz(v)) for u,v in pp],fill=c,width=zz(w),joint='curve')
 bob=math.sin(t*2.1)*5
 E((74,500,284,524),'#071625')
 # instead of toy wheels, articulated lower suit legs, floating heavy metallic body
 for sx in (111,225):
  P([(sx-26,402),(sx+20,402),(sx+11,484),(sx-18,487)],'#567784',INK,4)
  P([(sx-32,479),(sx+24,478),(sx+35,502),(sx-30,504)],'#21374c',INK,4)
  R((sx-11,451,sx+3,479),CYAN,3)
 P([(119,275),(213,275),(268,323),(260,422),(207,460),(123,454),(68,414),(70,322)],'#55778a',INK,5)
 P([(97,310),(235,310),(247,393),(204,438),(126,434),(88,397)],'#a6bfc1')
 P([(135,331),(207,331),(216,404),(177,431),(126,398)],'#233c50')
 P([(139,348),(211,348),(210,391),(178,416),(140,394)],'#152737')
 R((155,355,195,386),CYAN,9)
 R((164,363,185,376),'#f2fff6',3)
 # shoulders and arms, true hinged elbow and fingertip grippers, no simple bars
 for sign in (-1,1):
  sh=(170+sign*99,309);el=(170+sign*122,382-32*gesture if sign>0 else 382)
  hand=(170+sign*(108-55*gesture),453-127*gesture if sign>0 else 452)
  L([sh,el],INK,35);L([sh,el],'#67899a',27)
  E((el[0]-17,el[1]-18,el[0]+17,el[1]+18),'#223548',INK,3)
  E((el[0]-8,el[1]-8,el[0]+8,el[1]+8),'#70d9d2')
  L([el,hand],INK,24);L([el,hand],'#9ab7bd',16)
  E((hand[0]-13,hand[1]-10,hand[0]+13,hand[1]+12),'#2f5365',INK,3)
  for idx in (-1,0,1):
   L([(hand[0]+idx*7,hand[1]+4),(hand[0]+idx*9,hand[1]+17)],'#9db9b8',4)
  P([(sh[0]-sign*19,290),(sh[0]+sign*24,294),(sh[0]+sign*28,333),(sh[0]-sign*16,340)],'#acc8c9',INK,3)
 # neck pistons with shaded mechanisms
 for dx in (-20,20):
  R((170+dx-8,250,170+dx+8,297),'#314c5c',5)
  R((170+dx-3,252,170+dx+4,285),CYAN,3)
 # head asymmetrical angular helmet, not square box
 dy=bob*.4
 P([(76,158+dy),(96,118+dy),(144,105+dy),(228,111+dy),(265,141+dy),(278,200+dy),
    (261,249+dy),(211,276+dy),(120,270+dy),(79,231+dy)],'#274257',INK,6)
 P([(84,168+dy),(103,133+dy),(147,118+dy),(232,127+dy),(261,161+dy),(250,232+dy),(213,258+dy),(119,252+dy)],'#a5c4c7')
 P([(100,170+dy),(115,146+dy),(146,136+dy),(227,143+dy),(240,170+dy),(229,214+dy),(204,233+dy),(135,229+dy),(111,210+dy)],'#152c3e')
 # glass sheen with diagonal reflection
 P([(113,162+dy),(151,143+dy),(161,144+dy),(127,218+dy),(114,205+dy)],'#2b5060')
 P([(218,148+dy),(237,167+dy),(227,205+dy),(210,228+dy)],'#1b394a')
 # expressive slit eyes and movable pupil LEDs
 for sx in (143,207):
  E((sx-17,169+dy,sx+12,193+dy),'#274c53')
  R((sx-9,174+dy,sx+7,185+dy),HOT if emotion=='deny' else CYAN,5)
  R((sx-7,174+dy,sx-2,178+dy),'#e6ffff',2)
 if emotion=='deny':L([(145,215+dy),(200,215+dy)],HOT,7)
 elif talk:
  amp=float(talk)
  for k in range(5):
   wave=.30+.70*math.sin(t*10.5+k*.83)**2
   bar_h=3+amp*14*wave
   R((145+k*12,222+dy-bar_h/2,152+k*12,222+dy+bar_h/2),CYAN,2)
 else:
  L([(152,216+dy),(167,224+dy),(188,222+dy),(203,215+dy)],CYAN,5)
 # asymmetrical helm sidepanel & optic
 P([(265,161+dy),(284,157+dy),(286,213+dy),(265,223+dy)],'#6e969c',INK,3)
 E((277,176+dy,296,197+dy),HOT if emotion=='deny' else CYAN,INK,3)
 # fine lit casing bevels
 L([(90,165+dy),(102,139+dy),(130,125+dy)],'#f1e7d3',4)
 L([(215,258+dy),(255,239+dy),(269,221+dy)],'#d8eeeb',4)
 # top forehead identity mark
 R((153,122+dy,210,132+dy),'#e4af79',5)
 # V4 reflections and additional mechanical panel detailing.
 L([(123+math.sin(t*1.3)*5,153+dy),(139+math.sin(t*1.3)*5,165+dy)],'#9ad9d4',2)
 L([(219,141+dy),(229,144+dy)],'#f0f3dc',2)
 for stripe in (346,362,377):L([(117,stripe),(124,stripe+1)],'#8ab7ba',2)
 # animated indicators, faceplate details and moving energy core
 R((90,188+dy,96,211+dy),CYAN if emotion!='deny' else HOT,3)
 E((169+3*math.sin(t*2.2),364,180+3*math.sin(t*2.2),375),'#ffffff')
 L([(129,346),(143,338)],'#bde1d9',2)
 L([(200,420),(218,402)],'#5c92a3',2)
 z=a.resize((round(340*scale),round(560*scale)),Image.Resampling.LANCZOS)
 return z,(round(x-170*scale+scale*1.5*math.sin(t*.88)),round(feet-510*scale+scale*2.2*math.sin(t*2.1)))

def paste(im,thing):
 obj,xy=thing;im.paste(obj,xy,obj)

def glass(d,b,fill='#11263a',edge='#4c6b77',r=14,width=2):
 rect(d,b,fill,r,edge,width)

def desk(im,x,y,w=350):
 d=ImageDraw.Draw(im);d.ellipse((x+5,y+63,x+w+35,y+102),fill='#132136')
 poly(d,[(x,y),(x+w,y-23),(x+w+35,y+35),(x+23,y+67)],'#ae8b76','#302c38',3)
 poly(d,[(x+20,y+51),(x+w+33,y+33),(x+w+33,y+50),(x+20,y+70)],'#6f5962')
 rect(d,(x+45,y+67,x+64,y+237),'#4b5466',2)
 rect(d,(x+w-12,y+47,x+w+9,y+231),'#4b5466',2)

def monitor(d,x,y,w=200,h=137,show='SCHEDULE'):
 rect(d,(x,y,x+w,y+h),'#0a1729',14,'#7e8a93',4)
 rect(d,(x+9,y+9,x+w-9,y+h-9),'#18334b',8)
 txt(d,(x+19,y+21),show,13,CYAN)
 for j in range(5):
  rect(d,(x+18,y+55+j*13,x+w-20-j*20,y+61+j*13),('#f08589' if j==4 else '#3b7e89'),3)
 rect(d,(x+w/2-8,y+h,x+w/2+8,y+h+27),'#708694',3)
 rect(d,(x+w/2-36,y+h+25,x+w/2+36,y+h+36),'#748a91',3)

def header(im,chapter):
 d=ImageDraw.Draw(im)
 rect(d,(16,23,166,57),'#091729',10)
 txt(d,(32,41),'M1LASH  /  NEURO',13,WHITE,'lm')
 rect(d,(384,27,522,53),'#2d6669',8)
 txt(d,(452,40),'СЕРИЯ 01 · ТЕСТ',12,'#e7ffff','mm')

def wrap_center(d,text,size=20,max_width=492):
 words=text.split();rows=[];cur=''
 for word in words:
  nxt=(cur+' '+word).strip()
  if d.textbbox((0,0),nxt,font=TTF[size])[2]>max_width and cur:
   rows.append(cur);cur=word
  else:cur=nxt
 if cur:rows.append(cur)
 return rows[-2:]

CAPS=[
 ('ИИ СОСТАВИЛ ГРАФИК','УЧТУ КАЖДОГО'),
 ('НАЧАЛЬНИК ДОВОЛЕН','ВСЕ ВЫХОДНЫЕ ДОМА'),
 ('КОЛЛЕГИ ПОПРОСИЛИ','НИКАКИХ НОЧНЫХ'),
 ('Я ОТКРЫВАЮ ГРАФИК','ПОНЕДЕЛЬНИК · НОЧЬ'),
 ('СПРАВЕДЛИВОСТЬ?','НЕДОВОЛЕН ОДИН'),
 ('ОТВЕТ СИСТЕМЫ','ТАРИФ НЕ ПОЗВОЛЯЕТ'),
 ('НЕЙРООФИС','СКОРО ПОЛНАЯ СЕРИЯ')]

# Actual voice captions from the recorded narration, constrained visually.
LINES=[
 'Попросил ИИ составить справедливый график смен. Он сказал: учту пожелания абсолютно каждого.',
 'Начальник хочет все выходные дома. ИИ: готово, пожелание учтено.',
 'Коллеги просят убрать ночные. ИИ: без проблем, пожелания тоже учтены.',
 'Я открываю свой график. Понедельник — ночь. Вторник — ночь. Среда — угадай, блин.',
 'Спрашиваю: а где справедливость? Он отвечает: недовольный всего один. Раньше недовольны были все.',
 'Говорю: тогда сам выходи на смену. Он пишет: к сожалению, ваша подписка не включает физический труд.',
 'Подпишись! И спасибо всем, кто досмотрел и поставил лайк.'
]

# V4 exact voice word-boundary metadata from seven existing Dmitry segments.
SOURCE_ROOT=Path(__file__).resolve().parents[2]
WORDS=[json.loads((SOURCE_ROOT/'media/tts/research_codex'/f'sketch_schedule_{i}.json').read_text())['words'] for i in range(6)]
WORDS.append(json.loads((SOURCE_ROOT/'media/tts/host_demo/h4.json').read_text())['words'])
PHRASES=[
 [(0,5,'Попросил ИИ составить|справедливый график смен.'),(6,11,'Он сказал: учту пожелания|абсолютно каждого.')],
 [(0,4,'Начальник хочет все|выходные дома.'),(5,8,'ИИ: готово, пожелание учтено.')],
 [(0,3,'Коллеги просят убрать ночные.'),(4,9,'ИИ: без проблем,|пожелания тоже учтены.')],
 [(0,3,'Я открываю свой график.'),(4,5,'Понедельник — ночь.'),(6,7,'Вторник — ночь.'),(8,10,'Среда — угадай, блин.')],
 [(0,3,'Спрашиваю: а где справедливость?'),(4,8,'Он отвечает: недовольный|всего один.'),(9,12,'Раньше недовольны были все.')],
 [(0,5,'Говорю: тогда сам|выходи на смену.'),(6,9,'Он пишет: к сожалению,'),(10,15,'ваша подписка не включает|физический труд.')],
 [(0,0,'Подпишись!'),(1,4,'И спасибо всем, кто'),(5,8,'досмотрел и поставил лайк.')]
]
def subtitle(d,scene,local,duration):
 # Stable full phrase cards from actual speech timestamps; account for pauses.
 words=WORDS[scene]
 for j,(a,b,label) in enumerate(PHRASES[scene]):
  start=float(words[a]['start']); end=float(words[b]['end'])
  nxt=float(words[PHRASES[scene][j+1][0]]['start']) if j+1<len(PHRASES[scene]) else duration
  if not start-.1<=local<min(nxt-.09,end+.70):continue
  rows=label.split('|');height=117 if len(rows)==2 else 88
  top=814 if len(rows)==1 else 790
  rect(d,(23,top,517,top+height),'#071829',18,'#416373',2)
  for n,row in enumerate(rows):
   size=22
   while size>17 and d.textbbox((0,0),row,font=TTF[size])[2]>454:size-=1
   txt(d,(270,top+43+n*39),row,size,WHITE,'mm')
  p=f((local-start)/max(.2,end-start))
  rect(d,(75,top+height-17,465,top+height-13),'#243a48',2)
  if p>0:rect(d,(75,top+height-17,75+390*p,top+height-13),CYAN if scene not in (3,5) else HOT,2)
  break

def scene_frame(scene,local,duration):
 # Camera cuts are motivated by action; each scene also has an alternate dramatic subshot.
 t=local;late=local>duration*.58
 speaking=vocal_at(CUT[scene]+local)
 beat=ease((local-.25)/1.1)
 gest=beat*(1-.32*ease((local-(duration-1.7))/1.3))*(.88+.12*math.cos(t*2.2))
 im=bg(scene,t);d=ImageDraw.Draw(im)
 # Storyboard-specific stage and actor actions (not one repeated master scene)
 if scene==0:
  if not late:
   paste(im,draw_human(d,143,706,t,'hero','normal',talk=speaking,gesture=gest,scale=.76,eyes_target=1))
   paste(im,draw_robot(427,722,t,scale=.82,gesture=ease(t/2),talk=False))
   desk(im,150,625,300);monitor(ImageDraw.Draw(im),267,452,172,116,'PLAN AI')
   d=ImageDraw.Draw(im);glass(d,(55,91,469,164));txt(d,(261,127),'У НАС НОВЫЙ ДИРЕКТОР',20,CYAN,'mm')
  else:
   paste(im,draw_robot(265,790,t,scale=1.22,gesture=.75,talk=speaking))
   d=ImageDraw.Draw(im);glass(d,(28,112,511,196));txt(d,(270,152),'«УЧТУ ПОЖЕЛАНИЯ ВСЕХ»',22,WHITE,'mm')
   for n in range(3):
    rect(d,(36,405+n*42,145+n*23,419+n*42),'#327382',6)
 elif scene==1:
  if not late:
   paste(im,draw_human(d,264,748,t,'boss','smile',talk=speaking,gesture=gest*.55,scale=1.02,eyes_target=1))
   desk(im,59,633,420);d=ImageDraw.Draw(im)
   rect(d,(65,570,170,624),'#e7bf83',12);txt(d,(115,598),'ОТПУСК',15,INK,'mm')
   glass(d,(40,130,502,203),'#30283b','#846f74');txt(d,(270,165),'НАЧАЛЬНИК: ВЫХОДНЫЕ МОИ',20,WHITE,'mm')
  else:
   paste(im,draw_human(d,128,741,t,'boss','smile',talk=speaking,gesture=gest*.92,scale=.82))
   paste(im,draw_robot(434,770,t,scale=.83,gesture=.3,talk=False))
   d=ImageDraw.Draw(im);glass(d,(103,286,474,409),'#0e3b3e','#6fbea5')
   txt(d,(281,330),'ПРОШЕНИЕ ПРИНЯТО',19,CYAN,'mm')
   rect(d,(155,354,426,380),'#205d5a',8);txt(d,(290,367),'ОДОБРЕНО ✓',17,WHITE,'mm')
 elif scene==2:
  if not late:
   paste(im,draw_human(d,140,751,t,'colleague','scared',talk=speaking,gesture=gest*.9,scale=.88,eyes_target=1))
   paste(im,draw_human(d,319,755,t,'hero','normal',talk=False,gesture=.2,scale=.84))
   d=ImageDraw.Draw(im);glass(d,(40,136,494,230),'#173e46','#67a59e')
   txt(d,(270,177),'«УБЕРИТЕ НОЧНЫЕ СМЕНЫ»',19,WHITE,'mm')
  else:
   paste(im,draw_robot(260,782,t,scale=1.15,gesture=.8,talk=speaking))
   d=ImageDraw.Draw(im);glass(d,(70,127,477,219),'#13383c','#65b3b0')
   txt(d,(270,169),'ПРОШЕНИЕ УЧТЕНО',22,CYAN,'mm')
 elif scene==3:
  # Completely different computer-screen composition, real UI animation and character reaction.
  if not late:
   paste(im,draw_human(d,139,734,t,'hero','scared',talk=speaking,gesture=gest,scale=.82,eyes_target=1))
  else:
   paste(im,draw_human(d,109,749,t,'hero','scared',talk=speaking,gesture=gest*.98,scale=.87,eyes_target=1))
  d=ImageDraw.Draw(im);glass(d,(230,117,521,712),'#0c1b30','#6c92a6',20,3)
  rect(d,(245,133,505,190),'#244c60',7);txt(d,(373,160),'МОИ СМЕНЫ',22,WHITE,'mm')
  for idx,day in enumerate(['ПОНЕДЕЛЬНИК','ВТОРНИК','СРЕДА','ЧЕТВЕРГ']):
   y=219+idx*103;glass(d,(245,y,505,y+88),'#142e43','#2d5365',8)
   txt(d,(262,y+25),day,15,GREY)
   if idx<3 and t>({0:3.35,1:5.47,2:7.48}[idx]):
    rect(d,(363,y+44,493,y+75),'#713747',8)
    txt(d,(426,y+59),'НОЧЬ',19,'#ffd3d0','mm')
   else:rect(d,(367,y+48,490,y+69),'#243d53',5)
  if late:txt(d,(371,682),'ВСЕ НОЧНЫЕ?!',19,HOT,'mm')
 elif scene==4:
  if not late:
   paste(im,draw_human(d,138,769,t,'hero','scared',talk=speaking,gesture=gest*.8,scale=.9,eyes_target=1))
   paste(im,draw_robot(413,759,t,scale=.89,emotion='normal',talk=False))
  else:
   paste(im,draw_robot(258,792,t,scale=1.16,emotion='normal',gesture=.92,talk=speaking))
  d=ImageDraw.Draw(im);glass(d,(54,121,491,277),'#102a3c','#496777')
  txt(d,(270,157),'СЧЁТЧИК НЕДОВОЛЬНЫХ',19,WHITE,'mm')
  for k,st in enumerate(['БЫЛО     12 / 12','СТАЛО     1 / 12']):
   col=HOT if k==0 else CYAN
   txt(d,(270,207+k*40),st,21,col,'mm')
 elif scene==5:
  if not late:
   paste(im,draw_human(d,130,753,t,'hero','scared',talk=speaking,gesture=gest*.99,scale=.91,eyes_target=1))
   paste(im,draw_robot(419,779,t,scale=.86,emotion='deny',talk=False))
  else:
   paste(im,draw_robot(276,795,t,scale=1.18,emotion='deny',gesture=.8,talk=speaking))
  d=ImageDraw.Draw(im);glass(d,(39,112,509,284),'#48263b','#bb6175')
  txt(d,(272,151),'ОШИБКА ТАРИФА',26,'#ffd5c9','mm')
  rect(d,(63,187,482,258),'#64283b',14)
  txt(d,(270,221),'«ФИЗИЧЕСКИЙ ТРУД»',20,WHITE,'mm')
  txt(d,(270,248),'НЕ ВКЛЮЧЁН',22,HOT,'mm')
 elif scene==6:
  paste(im,draw_human(d,148,755,t,'hero','smile',talk=speaking,gesture=gest,scale=.96,eyes_target=1))
  paste(im,draw_robot(405,759,t,scale=.86,emotion='normal',talk=False))
  d=ImageDraw.Draw(im);glass(d,(29,120,508,272),'#0d293b','#4c928f')
  txt(d,(270,166),'НЕЙРООФИС',38,WHITE,'mm')
  txt(d,(270,208),'ПОСМОТРИ, ЧТО БУДЕТ ДАЛЬШЕ',17,CYAN,'mm')
  rect(d,(96,341,442,399),'#e0ae82',16);txt(d,(270,370),'ПОДПИШИСЬ',26,INK,'mm')
 # V4: small story-driven effects; all drawn procedurally in code.
 if scene==0:orb(ImageDraw.Draw(im),438,570,4+3*math.sin(t*2.8)**2,CYAN)
 elif scene==2 and t<2.1:
  dd=ImageDraw.Draw(im);dd.ellipse((452,294,473,315),fill='#e4e6d7');dd.ellipse((458,290,479,309),fill='#1b3c4a')
 elif scene==3:
  dd=ImageDraw.Draw(im)
  for stamp,yy in ((3.35,278),(5.47,381),(7.48,484)):
   if t>=stamp:rect(dd,(251,yy,502,yy+54),'#26374e',10,HOT,2)
 elif scene==5 and t>5.33:orb(ImageDraw.Draw(im),485,154,6,HOT if math.sin(t*3)>0 else CYAN)
 # No test, template, technical or style corner labels.
 d=ImageDraw.Draw(im)
 # progress mark and voice-specific subtitles
 rect(d,(19,796,521,801),'#2c4555',2)
 rect(d,(19,796,19+502*min(1,t/max(.01,duration)),801),CYAN if scene not in (3,5) else HOT,2)
 subtitle(d,scene,t,duration)
 # no bottom technical caption or style metadata
 return im

def render_preview():
 images=[]
 for s in range(7):
  span=CUT[s+1]-CUT[s]
  for portion in (.25,.79):
   t=span*portion; im=scene_frame(s,t,span)
   im.save(OUT/f'frame_{s:02d}_{int(portion*100)}.png')
   images.append(im.resize((216,384),Image.Resampling.LANCZOS))
 grid=Image.new('RGB',(216*7,384*2),'#081725')
 for s in range(7):
  for k in range(2):grid.paste(images[s*2+k],(s*216,k*384))
 grid.save(OUT/'V4_STORYBOARD.jpg',quality=92)
 print('WROTE PREVIEW', OUT/'V2_STORYBOARD.jpg')

def run():
    """Render deterministic code-animation frames, then encode in a separate ffmpeg pass."""
    if not PREVIOUS.is_file():
        raise SystemExit(f'Voice recording not found: {PREVIOUS}')
    source_dur=float(json.loads(subprocess.check_output(['ffprobe','-v','error',
           '-show_entries','format=duration','-of','json',str(PREVIOUS)]))['format']['duration'])
    if abs(source_dur-CUT[-1])>.10:
        raise SystemExit(f'Voice duration mismatch: {source_dur:.3f} vs {CUT[-1]:.3f}')
    load_voice_energy()
    render_preview()
    frames=ROOT/'frames';frames.mkdir(exist_ok=True)
    count=round(CUT[-1]*FPS)
    for k in range(count):
        t=k/FPS
        scene=next((j for j in range(7) if CUT[j]<=t<CUT[j+1]),6)
        image=scene_frame(scene,t-CUT[scene],CUT[scene+1]-CUT[scene])
        image.save(frames/f'{k:05d}.jpg',format='JPEG',quality=87,subsampling=0)
        if k%200==0:print(f'Frame {k}/{count}',flush=True)
    mp4=OUT/'NEUROOFFICE_V4_SYNC_RU.mp4'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y',
      '-framerate',str(FPS),'-i',str(frames/'%05d.jpg'),'-i',str(PREVIOUS),
      '-map','0:v:0','-map','1:a:0',
      '-vf','scale=1080:1920:flags=lanczos,format=yuv420p',
      '-c:v','libx264','-preset','ultrafast','-crf','17',
      '-c:a','copy','-movflags','+faststart',str(mp4)],check=True)
    actual=float(json.loads(subprocess.check_output(['ffprobe','-v','error',
      '-show_entries','format=duration','-of','json',str(mp4)]))['format']['duration'])
    if abs(actual-CUT[-1])>.10:raise RuntimeError('NO-GO: output duration mismatch')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(mp4),'-f','null','-'],check=True)
    result={'status':'TECHNICAL_PASS_VISUAL_REVIEW_REQUIRED',
        'seconds':actual,'frames':count,'resolution':'1080x1920',
        'voice':'existing confirmed DmitryNeural recording; audio stream copied',
        'lip_sync':'RMS envelope approximation only','captions':'original TTS exact word timestamps grouped in 19 readable phrase cards','publish':False,
        'sha256':hashlib.sha256(mp4.read_bytes()).hexdigest()}
    (OUT/'QA_V4.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--render',action='store_true');ns=parser.parse_args()
 if ns.preview and not ns.render:load_voice_energy();render_preview()
 else:run()
