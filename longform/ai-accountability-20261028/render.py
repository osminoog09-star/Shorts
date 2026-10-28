"""Deterministic 2.5D editorial renderer. Requires accepted Dmitry audio + Rhubarb.
No silent voice replacement; measured timing determines all scene lengths.
"""
import argparse, bisect, concurrent.futures, csv, json, math, os, subprocess, sys
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent; BUILD=ROOT/'build'; FPS=30
INK='#eaf2fc'; MUTED='#9cafc4'; BLUE='#57bbf5'; PINK='#ed86bb'; GREEN='#72d5b2'; ORANGE='#f3ae69'
SOURCE={'amazon':'Amazon · 27.10.2026 / The Next Web · 28.10.2026','cloud':'Cloudflare · 26.10 / Knostic · 27.10 / SGLang · 26.10','opera':'Opera · 27.10.2026 / TechRepublic · 28.10.2026'}
@lru_cache(None)
def font(n,b=False):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',n)
def wrap(text,width,ft):
 lines=[];row=''
 for w in text.split():
  candidate=(row+' '+w).strip()
  if ft.getlength(candidate)>width and row:lines.append(row);row=w
  else:row=candidate
 if row:lines.append(row)
 return lines
def text(draw,xy,s,size=30,color=INK,bold=False,width=None):
 x,y=xy;ft=font(size,bold);lines=wrap(s,width,ft) if width else [s]
 for l in lines:draw.text((x,y),l,font=ft,fill=color);y+=size*1.35
 return y
@lru_cache(None)
def background(w,h):
 yy=np.arange(h)[:,None,None]/h
 a=np.array([13,23,41])[None,None,:];b=np.array([25,41,62])[None,None,:]
 arr=np.broadcast_to(a*(1-yy)+b*yy,(h,w,3)).astype('uint8').copy()
 im=Image.fromarray(arr);d=ImageDraw.Draw(im)
 for x in range(0,w,80):d.line((x,0,x,h),fill='#1a2c41')
 for y in range(0,h,80):d.line((0,y,w,y),fill='#1a2c41')
 return im
class World:
 def __init__(self,d,w,h,t,shot):
  self.d=d;self.w=w;self.h=h;self.items=[]
  presets=[(-.34,1.0),(.22,1.12),(-.55,1.4),(.40,1.18),(-.12,1.6),(.12,1.0)]
  a,z=presets[shot%6];self.angle=a+.06*math.sin(t*.23);self.z=z
  self.cx=w*(.47 if w>h else .5);self.cy=h*(.54 if w>h else .49);self.scale=(w/1920*135 if w>h else w/1080*115)*z
 def project(self,p):
  x,y,z=p;a=self.angle;xx=x*math.cos(a)-z*math.sin(a);zz=x*math.sin(a)+z*math.cos(a)
  dep=1/(1+zz*.025);return (self.cx+xx*self.scale*dep,self.cy+(zz*.36-y)*self.scale*dep)
 def line(self,a,b,c=BLUE,width=3):self.d.line((self.project(a),self.project(b)),fill=c,width=width)
 def label(self,p,s,c=INK,size=24):
  x,y=self.project(p);ft=font(size,True);self.d.text((x-ft.getlength(s)/2,y),s,font=ft,fill=c)
 def box(self,p,sz,c,tag=''):
  x,y,z=p;dx,dy,dz=[a/2 for a in sz]
  verts=[(x+a*dx,y+b*dy,z+q*dz) for a,b,q in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
  rgb=tuple(int(c[i:i+2],16) for i in (1,3,5))
  side=([1,5,6,2],.78) if self.angle<0 else ([0,3,7,4],.70)
  faces=[([0,1,2,3],.82),side,([3,2,6,7],1.12)]
  for ids,m in faces:
   pts=[verts[i] for i in ids];depth=sum(p[2] for p in pts)/4
   fill=tuple(min(255,int(v*m)) for v in rgb);self.items.append((depth,pts,fill))
  if tag:self.tags.append(((x,y+dy+.18,z),tag,c))
 def floor(self):
  self.tags=[]
  for i in range(-7,8):self.line((i,-1.1,-3),(i,-1.1,4),'#30465d',1)
  for j in range(-3,5):self.line((-7,-1.1,j),(7,-1.1,j),'#30465d',1)
 def finish(self):
  for depth,pts,c in sorted(self.items,key=lambda q:-q[0]):
   self.d.polygon([self.project(p) for p in pts],fill=c,outline='#34506c',width=2)
  for p,tag,c in self.tags:self.label(p,tag,c,24 if self.w>self.h else 26)
 def route(self,a,b,t,c=BLUE,n=4):
  self.line(a,b,'#42647e',4)
  for i in range(n):
   u=(t*.28+i/n)%1;p=tuple(a[k]*(1-u)+b[k]*u for k in range(3));x,y=self.project(p)
   self.d.ellipse((x-5,y-5,x+5,y+5),fill=c)
def machine(world,x,z,color,title):
 world.box((x,.0,z),(1.3,1.8,1.1),color,title)
 for y in [-.4,0,.4]:world.box((x,y,z-.57),(.85,.08,.06),'#c4d6e7')
 world.box((x,-.98,z),(1.6,.12,1.3),'#263f5b')
def laptop(world,x,z,color=BLUE):
 world.box((x,-.6,z),(2.7,.16,1.8),'#879fb8')
 world.box((x,.45,z+.75),(2.7,1.9,.14),color)
 world.box((x,.45,z+.64),(2.4,1.55,.06),'#112a40')
 for i in range(4):world.box((x-.22,.85-i*.26,z+.59),(1.45-i*.15,.05,.03),GREEN)
 for i in range(7):world.box((x-1+i*.32,-.48,z),(.19,.03,.50),'#344a61')
def visual(world,mode,t,shot):
 world.floor();stage=shot%6;phase=(t%6)/6
 if mode in ['factory','meter','tokens','ledger']:
  if mode=='ledger':
   for i,(tag,c) in enumerate([('ГЕНЕРАЦИЯ',BLUE),('ПРОВЕРКА',PINK),('ИСПРАВЛЕНИЯ',ORANGE)]):
    height=.8+(i+1)*.37+max(0,math.sin(t*.45+i))*.4
    world.box((-3+i*3,-.8+height/2,0),(1.6,height,1.4),c,tag)
   world.label((0,3.1,0),'УЧЕБНАЯ СХЕМА · НЕ ТАРИФЫ',MUTED)
  else:
   for x in [-4,0,4]:machine(world,x,0,BLUE if x!=0 else PINK,['ЗАДАЧА','ОБРАБОТКА','РЕЗУЛЬТАТ'][int((x+4)/4)])
   world.route((-3,0,0),(-1,0,0),t,BLUE);world.route((1,0,0),(3,0,0),t,PINK)
   for j in range(6):
    xx=-4.5+((t*.9+j*1.7)%9);world.box((xx,-.55,2.0),(.5,.3,.55),GREEN if mode=='tokens' else ORANGE)
   if mode=='meter':world.label((0,2.6,0),'АКТИВНОСТЬ ≠ ПОЛЬЗА',ORANGE)
 elif mode in ['leak','cache']:
  for side,c in [(-1,BLUE),(1,ORANGE)]:
   for i in range(6):
    xx=side*3+(i%3-1)*.75;zz=(i//3)*1.0
    world.box((xx,-.5,zz),(.65,.42,.8),c)
   world.label((side*3,1.2,0),'КОНТЕКСТ А' if side<0 else 'КОНТЕКСТ Б',c)
  world.box((0,-.85,0),(.13,.5,3),'#95adc3','ГРАНИЦА')
  if stage in [0,2,4]:
   u=phase;world.box((3-6*u,.6+math.sin(u*math.pi)*.5,0),(.65,.42,.8),ORANGE)
   world.label((0,2.5,0),'ЧУЖОЙ ФРАГМЕНТ',ORANGE)
  else:
   world.route((-3,.5,0),(-3,.5,2),t,BLUE);world.route((3,.5,0),(3,.5,2),t,ORANGE)
 elif mode=='handoff':
  machine(world,-4,0,BLUE,'ВХОД');machine(world,0,0,ORANGE,'ДОПУСК');machine(world,4,0,PINK,'ВЫХОД')
  world.route((-3,.1,0),(-1,.1,0),t,BLUE)
  if stage%2==0:world.route((1,.1,0),(3,.1,0),t,ORANGE)
  else:world.box((1.8,.1,0),(.18,2.5,2),'#e27a7a','СТОП')
 elif mode in ['permissions','office']:
  laptop(world,-4,0);machine(world,0,0,PINK,'ПОМОЩНИК')
  world.route((-2.7,0,0),(-1,0,0),t,BLUE)
  for i,(tag,c) in enumerate([('ЧИТАТЬ',GREEN),('ЧЕРНОВИК',BLUE),('ОТПРАВИТЬ',ORANGE)]):
   z=-2+i*2;world.box((4,.0,z),(.18,1.8,1.3),c,tag)
   if mode=='office' or stage==i:world.route((1,0,0),(3.8,0,z),t,c,3)
 elif mode in ['laptop','browser']:
  laptop(world,0,0);machine(world,-4,1,BLUE,'УСТРОЙСТВО');machine(world,4,1,PINK,'ОБЛАКО')
  if stage%2:world.route((1,0,0),(3,.0,1),t,PINK)
  else:world.route((-3,0,1),(-1,0,0),t,BLUE)
  for i in range(3):world.box((-1.5+i*1.4,-.8,-2),(1,.12,.7),[BLUE,GREEN,ORANGE][i])
 elif mode in ['tickets','detective']:
  for i,c in enumerate([BLUE,ORANGE,GREEN]):
   world.box((-3+i*3,0,0),(1.8,2,.16),c,['ОБРАЩЕНИЕ','ПРОВЕРКА','РЕШЕНИЕ'][i])
   for j in range(4):world.box((-3+i*3,.55-j*.3,-.1),(1.15-j*.08,.08,.05),'#d3e6ed')
  world.route((-1.9,0,0),(-1.1,0,0),t,BLUE,2);world.route((1.1,0,0),(1.9,0,0),t,GREEN,2)
  if stage%2:world.label((0,2.3,0),'ОТКУДА ДАННЫЕ?',ORANGE)
 elif mode=='split':
  laptop(world,-3,0,BLUE);laptop(world,3,0,PINK)
  world.box((0,-.9,0),(.12,.25,4),'#a6bdcc')
  world.label((-3,2,0),'ЗАДАЧА',BLUE);world.label((3,2,0),'РЕЗУЛЬТАТ',PINK)
 world.finish()
def captions(words,t):
 groups=[];current=[];start=0;end=0
 for w in words:
  a=w['offset']/1e7;b=a+w['duration']/1e7;s=w['text']
  if current and (len(' '.join(current)+' '+s)>48 or a-end>.42 or ''.join(current)[-1:] in '.!?'):
   groups.append((start,end,' '.join(current)));current=[]
  if not current:start=a
  current.append(s);end=b
 if current:groups.append((start,end,' '.join(current)))
 for i,(a,b,s) in enumerate(groups):
  if len(s.split())==1 and i:
   pa,pb,ps=groups[i-1];groups[i-1]=(pa,b,ps+' '+s);groups[i]=(a,b,'')
 return next((s for a,b,s in groups if a-.04<=t<=b+.12 and s),'')
@lru_cache(None)
def sprite(pose,v,size):
 im=Image.open(BUILD/'host'/f'{pose}_{v}.png').convert('RGBA');return im.resize(size,Image.Resampling.LANCZOS)
def frame(scene,t,portrait=False,visemes=None,show_sub=True):
 w,h=(1080,1920) if portrait else (1920,1080)
 im=background(w,h).copy();d=ImageDraw.Draw(im);shot=int(t//6)
 world=World(d,w,h,t,shot);visual(world,scene['visual'],t,shot)
 # Native-resolution editorial type. Internal scene IDs are never displayed.
 d.rounded_rectangle((45,38,w-45,100),radius=18,fill='#20394e')
 text(d,(68,52),'M1LASH  /  НОВОСТИ ИИ',27,BLUE,True)
 text(d,(w-280,54),'28.10.2026',24,MUTED,True)
 y=text(d,(62,140 if portrait else 132),scene['title'],48 if portrait else 53,INK,True,w-124)
 kind=scene['kind'];label={'fact':'НОВОСТЬ · ПРОВЕРЕННЫЕ ПУБЛИКАЦИИ','example':'УСЛОВНЫЙ ПРИМЕР · СХЕМА','analysis':'РАЗБОР M1LASH · ВЫВОДЫ АВТОРА'}[kind]
 text(d,(65,y+16),label,22,ORANGE if kind=='example' else MUTED,True,w-130)
 if kind=='fact':
  k='amazon' if scene['id']==2 else 'cloud' if scene['visual'] in ['leak','detective','handoff'] else 'opera'
  text(d,(65,h-74),SOURCE[k],20,MUTED,width=w-130)
 else:text(d,(65,h-72),'Стилизованная кодовая реконструкция · не съёмка события',20,MUTED,width=w-130)
 if show_sub:
  cap=captions(scene.get('words',[]),t)
  if cap:
   cw=w-140 if portrait else 1300;cy=1390 if portrait else 855
   lines=wrap(cap,cw-44,font(38,True));bh=18+len(lines)*51
   d.rounded_rectangle((60,cy,60+cw,cy+bh),radius=16,fill='#0a1323')
   text(d,(82,cy+10),cap,38,INK,True,cw-44)
 # Approved narrator art, actual Rhubarb cues, no volume/sine mouth inference.
 if visemes is not None and (portrait or t<5 or shot%4==2 or scene.get('cta')):
  cue=visemes[min(int(t*30),len(visemes)-1)] if visemes else 'X'
  pose='point' if t<3 else 'talk'
  size=(270,320) if portrait else (228,270)
  host=sprite(pose,cue,size);pos=(65,1000) if portrait else (w-278,h-340)
  im.paste(host,pos,host)
 return im

def render_scene(item):
 idx,scene,portrait=item;out=BUILD/(('short_' if portrait else '')+f'scene_{idx:02d}.mp4')
 if out.exists():return str(out)
 lip=json.loads((BUILD/f'voice_{scene["id"]:02d}.lipsync.json').read_text())['visemes']
 n=math.ceil((scene['duration']+.18)*FPS);w,h=(1080,1920) if portrait else (1920,1080)
 cmd=['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{w}x{h}','-r',str(FPS),'-i','-','-i',str(BUILD/scene['audio']),'-af','apad=pad_dur=0.18','-t',str(n/FPS),'-c:v','libx264','-preset','veryfast','-crf','20','-threads','1','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000','-ac','2',str(out)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for f in range(n):p.stdin.write(frame(scene,min(f/FPS,scene['duration']),portrait,lip).tobytes())
  p.stdin.close();rc=p.wait()
  if rc:raise RuntimeError(f'ffmpeg failed {rc}')
 except Exception:
  p.kill();out.unlink(missing_ok=True);raise
 print('RENDERED',idx,out.name,flush=True);return str(out)
def join(paths,name):
 li=BUILD/(name+'.concat.txt');li.write_text('\n'.join("file '"+str(Path(p).resolve())+"'" for p in paths))
 out=BUILD/(name+'.mp4');subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(li),'-c','copy','-movflags','+faststart',str(out)],check=True);return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--stills',action='store_true');ap.add_argument('--pilot',action='store_true');ap.add_argument('--short',action='store_true');ap.add_argument('--workers',type=int,default=5);args=ap.parse_args()
 timeline=json.loads((BUILD/'timeline.json').read_text());scenes=timeline['scenes'];scenes[-1]['cta']=True
 if args.stills:
  qa=BUILD/'qa';qa.mkdir(exist_ok=True)
  for s in scenes:
   for tt in [1,9,20]:frame(s,min(tt,s['duration']),visemes='X'*int((s['duration']+1)*30)).save(qa/f"scene_{s['id']:02d}_{tt}.jpg",quality=90)
 elif args.short:
  short=json.loads((BUILD/'short_timeline.json').read_text())['scenes'][0];print(join([render_scene((90,short,True))],'M1lash_AI_Context_Short_20261028_RU'))
 elif args.pilot:
  s=dict(scenes[0]);s['duration']=min(24,s['duration']);join([render_scene((99,s,False))],'pilot')
 else:
  with concurrent.futures.ProcessPoolExecutor(args.workers) as pool:paths=list(pool.map(render_scene,[(i,s,False) for i,s in enumerate(scenes)]))
  print(join(paths,'M1lash_AI_Accountability_20261028_RU'))
