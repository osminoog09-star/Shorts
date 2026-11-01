# ARCHIVE ONLY — NOT AUTHORISED FOR NEW RENDERS.
# This file preserves the old 28-window REV18/19 PIL production approach for
# forensic reproducibility. AGENTS and visuals-by-code.md prohibit PIL user scenes.
# Legacy source from private QA ZIP: M1lash_REV18_VISUAL_QA_REPORT_AND_SOURCE.zip.
from PIL import Image, ImageDraw, ImageFont
import numpy as np, math, subprocess, os, json, time
from pathlib import Path
OUT=Path('/mnt/data/m1lash_secondpass');OUT.mkdir(exist_ok=True)
W,H=960,540;FPS=12;T=681.416
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONTB={n:ImageFont.truetype(BOLD,n) for n in (15,18,23,29,34,42,52,62)}
FONTN={n:ImageFont.truetype(FONT,n) for n in (13,15,17,20,24)}
RUNS=[(5,21,'ВЫБОР ИЛИ ПРИКАЗ?','Кто заранее установил условия','coin'),(36,47,'ОБЫЧНЫЙ ВОПРОС','Тон превращается в угрозу','talk'),(56,69,'ПРАВИЛА РАЗГОВОРА','Одна сторона назначает цену','deal'),(92,109,'НЕРАВНЫЙ ДИАЛОГ','Один спрашивает. Другой оправдывается','talk'),(121,137,'КТО РЕШАЕТ?','Два варианта. Один хозяин игры','paths'),(141,151,'НЕ РОБОТ','Это человек. Не алгоритм','talk'),(156,173,'ОТВЕТСТВЕННОСТЬ','За решение отвечает человек','deal'),(187,198,'ВЕЖЛИВЫЕ СЛОВА','Мягкий голос не снимает угрозу','talk'),(203,208,'МЕХАНИЗМ СТРАХА','Человек становится частью процедуры','machine'),(220,226,'ПО ТУ СТОРОНУ ДВЕРИ','Тишина говорит сильнее слов','motel'),(232,235,'У НЕГО НЕТ ПАУЗЫ','Дверь закрыта. Угроза остаётся','motel'),(255,258,'ЧУЖИЕ УСЛОВИЯ','Отказ меняет правила','coin'),(290,294,'ПРАВИЛА НЕ ИСЧЕЗЛИ','Даже когда меняется место','paths'),(333,345,'ПОЛОСА СВЕТА','Он слушает пространство','motel'),(351,354,'КОГДА ТИХО','Каждый звук становится сигналом','radar'),(361,378,'ЗВУК ЗА СТЕНОЙ','Сигнал приближается','radar'),(411,415,'КОГДА ПАУЗА ВАЖНЕЕ','Тишина работает как угроза','motel'),(421,434,'В ЧЁМ ЕГО ВЛАСТЬ?','Монета — лишь удобный предлог','deal'),(441,451,'ЭТО НЕ ЗАКОН','Никто не обязан принимать игру','carla'),(459,467,'ОТВЕТ ЗВУЧИТ ТИХО','Отказ разрушает процедуру','carla'),(475,487,'ПОЧЕМУ НЕ ДОГОВОРИТЬСЯ?','Нет общих условий','paths'),(495,502,'ТРИ МЕХАНИЗМА','Контроль · страх · отказ','final'),(509,522,'ОТКАЗ — ТОЖЕ ДЕЙСТВИЕ','Правила не принадлежат всем','carla'),(544,552,'МОНЕТА НЕ РЕШАЕТ','Решение принимает человек','coin'),(559,577,'СВОБОДА СКАЗАТЬ «НЕТ»','Выбор — не обязанность','carla'),(620,627,'УСЛОВИЕ ИЛИ ЛОВУШКА','Вслушайтесь в интонацию','talk'),(636,641,'ПРАВИЛО / КОНТРОЛЬ / ОТКАЗ','Три разных источника напряжения','final'),(648,655,'СТРАХ РОЖДАЕТСЯ В ТИШИНЕ','Чигур не спорит. Он навязывает','motel')]
# omit all confirmed actor originals: masks are intentionally restricted to card runs
G=(0,255,0);GFRAME=Image.new('RGB',(W,H),G).tobytes()
GOLD=(238,192,107);OFF=(235,231,221);BLUE=(117,206,218);DIM=(158,176,190);RED=(199,85,72)
rng=np.random.default_rng(57);yy,xx=np.mgrid[0:H,0:W];nr=rng.normal(0,2.6,(H,W));r=(13+19*xx/W+11*yy/H+nr).clip(0,255);g=(20+19*xx/W+9*yy/H+nr).clip(0,255);b=(32+20*xx/W+10*yy/H+nr).clip(0,255)
BG=Image.fromarray(np.uint8(np.stack([r,g,b],axis=2)),'RGB')
DARK=(24,36,49);MID=(44,61,74)
def bez(t): t=max(0,min(1,t));return t*t*(3-2*t)
def txt(d,x,y,t,c=OFF,f=None):d.text((int(x),int(y)),t,fill=c,font=f or FONTN[20])
def line(d,points,c=GOLD,w=3):d.line([(int(x),int(y)) for x,y in points],fill=c,width=w,joint='curve')
def glow(d,cx,cy,r,color=GOLD):
 for i in range(3,0,-1):
  rad=r+i*13;cc=tuple(int(v*(.15+(3-i)*.06)+28*(.85-(3-i)*.06)) for v in color)
  d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),outline=cc,width=2)
def coin(d,x,y,t,r=75):
 wid=max(6,int(r*abs(math.cos(t*1.3+.3))));d.ellipse((x-wid+8,y-r+17,x+wid+10,y+r+21),fill=(5,12,20))
 for k in range(3):d.ellipse((x-wid-k,y-r-k,x+wid+k,y+r+k),outline=GOLD if k==0 else (145,113,68),width=2)
 if wid>18:
  d.ellipse((x-wid+7,y-r+7,x+wid-7,y+r-7),fill=(83,63,40),outline=(250,204,120),width=3)
  if wid>36:d.arc((x-wid+18,y-r+18,x+wid-18,y+r-18),5,340,fill=GOLD,width=2);txt(d,x-14,y-33,'?',GOLD,FONTB[52])
def panel(d,kind,t):
 cx,cy=699,274;phase=t*1.24
 if kind=='coin':
  glow(d,cx,cy,99);d.arc((548,122,846,426),int(phase*10)%360,200+int(phase*10)%360,fill=(107,123,124),width=2)
  coin(d,cx,cy,t,91)
  txt(d,572,442,'ОРЁЛ',BLUE,FONTB[18]);txt(d,770,442,'РЕШКА',GOLD,FONTB[18]);line(d,[(609,429),(789,429)],(112,126,132),1)
 elif kind=='talk':
  for cx1,clr,scale in [(599,BLUE,1.0),(807,GOLD,1.12)]:
   oy=25*math.sin(phase*.55) if cx1==807 else 0;cy1=239+oy
   d.ellipse((cx1-38,cy1-60,cx1+38,cy1+16),fill=(57,77,88),outline=clr,width=3)
   d.rounded_rectangle((cx1-78,cy1+20,cx1+77,cy1+160),radius=36,fill=(27,44,58),outline=clr,width=3)
  for k in range(5):
   rad=25+k*24+16*math.sin(phase*1.6);d.arc((699-rad,250-rad*.48,699+rad,250+rad*.48),310,50,fill=GOLD,width=2)
  line(d,[(697,118),(697,460)],(70,86,101),1)
 elif kind=='deal':
  d.rounded_rectangle((558,152,849,403),radius=18,fill=(29,42,52),outline=(120,137,140),width=2)
  txt(d,592,172,'УСЛОВИЯ',GOLD,FONTB[29]);txt(d,595,222,'I',DIM,FONTB[18]);line(d,[(633,239),(821,239)],BLUE,3)
  txt(d,595,280,'II',DIM,FONTB[18]);line(d,[(633,299),(821,299)],GOLD,3)
  txt(d,595,340,'III',DIM,FONTB[18]);line(d,[(633,360),(821,360)],RED,3)
  tx=700+int(90*math.sin(phase*.8));line(d,[(699,124),(tx,124),(tx,152)],GOLD,3)
 elif kind=='paths':
  sx=570;sy=248
  line(d,[(sx,sy),(665,sy),(722,166),(840,166)],BLUE,6)
  line(d,[(sx,sy),(665,sy),(725,347),(840,347)],GOLD,6)
  line(d,[(840,166),(866,166),(866,347),(840,347)],RED,4)
  for X,Y,C in [(574,248,OFF),(840,166,BLUE),(840,347,GOLD)]:d.ellipse((X-15,Y-15,X+15,Y+15),fill=DARK,outline=C,width=5)
  txt(d,749,134,'ДА',BLUE,FONTB[18]);txt(d,749,368,'НЕТ',GOLD,FONTB[18]);txt(d,694,430,'РАМКИ НЕ МЕНЯЮТСЯ',DIM,FONTN[15])
 elif kind=='machine':
  d.rounded_rectangle((554,192,843,361),radius=19,fill=(27,43,54),outline=(114,136,150),width=3)
  d.ellipse((585,231,685,331),outline=GOLD,width=5);d.ellipse((610,256,660,306),outline=GOLD,width=3)
  for k in range(6):
   y=215+k*24;line(d,[(714,y),(824,y)],BLUE if k%2 else GOLD,2)
  line(d,[(635,331),(635,401),(843,401)],(150,129,83),4)
  txt(d,604,415,'ДЕЙСТВИЕ БЕЗ ДИАЛОГА',DIM,FONTN[15])
 elif kind in ('motel','radar'):
  van=(704,208)
  d.polygon([(547,152),(840,94),(880,440),(551,448)],fill=(26,44,58))
  line(d,[(556,444),van,(851,444)],(133,152,157),3)
  line(d,[(554,155),van,(842,157)],(100,123,134),3)
  for j,x0 in enumerate([577,816]):
   door=(x0,212,x0+64,392)
   d.polygon([(door[0],door[1]),(door[2],door[1]+25),(door[2],door[3]-24),(door[0],door[3])],fill=(24,35,47),outline=GOLD if j==1 else BLUE)
   d.ellipse((x0+44,306,x0+51,313),fill=GOLD)
  beamx=int(700+100*math.sin(phase*.5));d.polygon([(706,210),(beamx-60,443),(beamx+60,443)],fill=(49,60,62))
  if kind=='radar':
   cx1,cy1=705,323
   for k in range(4):
    rr=25+((phase*34+k*37)%155)
    d.arc((cx1-rr,cy1-rr,cx1+rr,cy1+rr),-74,74,fill=BLUE if k%2 else GOLD,width=3)
   txt(d,573,430,'СИГНАЛ',GOLD,FONTB[18]);txt(d,744,430,'ДВИЖЕНИЕ',BLUE,FONTB[18])
 elif kind=='carla':
  for X,C in [(599,RED),(797,BLUE)]:
   d.ellipse((X-37,181,X+37,258),fill=(43,53,65),outline=C,width=3)
   d.rounded_rectangle((X-74,264,X+74,414),radius=35,fill=(34,45,59),outline=C,width=3)
  tx=int(690+55*math.sin(t*.6));coin(d,tx,315,t,34)
  d.line((680,360,750,380),fill=RED,width=6)
  txt(d,610,432,'ВЫБИРАЙ',GOLD,FONTN[15]);txt(d,805,432,'НЕТ.',BLUE,FONTB[29])
 elif kind=='final':
  names=['УСЛОВИЕ','КОНТРОЛЬ','ОТКАЗ'];cols=[GOLD,RED,BLUE]
  for i,(name,col) in enumerate(zip(names,cols)):
   X=553+i*109;d.rounded_rectangle((X,205,X+100,355),radius=13,fill=(28,45,58),outline=col,width=3)
   txt(d,X+10,259,str(i+1).zfill(2),col,FONTB[34]);txt(d,X+6,376,name,col,FONTB[15])
  for i in range(2):line(d,[(645+i*109,278),(661+i*109,278)],DIM,2)
def get_bg(ri):
 s,e,title,sub,kind=RUNS[ri];im=BG.copy();d=ImageDraw.Draw(im)
 for x in range(38,930,48):line(d,[(x,87),(x,456)],(30,44,55),1)
 for y in range(91,460,48):line(d,[(37,y),(923,y)],(30,44,55),1)
 d.rounded_rectangle((39,35,88,47),radius=4,fill=GOLD)
 txt(d,102,29,'M1LASH  /  КИНОРАЗБОР',DIM,FONTN[15])
 txt(d,786,29,f'СЦЕНА  {ri+1:02d}',GOLD,FONTN[15])
 line(d,[(39,65),(917,65)],(100,103,105),2)
 if len(title)>27:
  parts=title.split(' ');l1=[];l2=[]
  for w in parts:
   (l1 if len(' '.join(l1+[w]))<=25 else l2).append(w)
  lines=[' '.join(l1),' '.join(l2)]
 else: lines=[title]
 yy=130
 for name in lines:
  txt(d,42,yy,name,GOLD if yy>130 else OFF,FONTB[29 if len(name)>25 else 34]);yy+=52
 d.rounded_rectangle((38,yy+10,49,yy+114),radius=4,fill=GOLD)
 sublines=[];words=sub.split();now=''
 for w in words:
  if len(now+' '+w)>37: sublines.append(now);now=w
  else: now=(now+' '+w).strip()
 if now:sublines.append(now)
 for j,x in enumerate(sublines[:3]):txt(d,65,yy+20+j*29,x,DIM,FONTN[20])
 line(d,[(38,479),(917,479)],(72,96,109),2)
 txt(d,42,490,'АНТОН ЧИГУР   •   КАК РАБОТАЕТ УГРОЗА',DIM,FONTN[15])
 return im
CACHED=[get_bg(i) for i in range(len(RUNS))]
def render(ri,t):
 im=CACHED[ri].copy();d=ImageDraw.Draw(im)
 kind=RUNS[ri][4];panel(d,kind,t)
 start,end,*_=RUNS[ri];rel=(t-start)/(end-start)
 line(d,[(39,473),(39+878*bez(rel),473)],GOLD,4)
 return im
END=682; out=str(OUT/'m1lash_long_art_only_greenkey_682s_12fps.mp4')
cmd=['ffmpeg','-hide_banner','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-c:v','libx264','-threads','3','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p','-g','48','-movflags','+faststart',out]
p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=open(str(OUT/'art_encoder.log'),'wb'))
start_time=time.time();n=0
try:
 for sec in range(END):
  for frame in range(FPS):
   t=sec+frame/FPS
   ri=next((i for i,(s,e,*other) in enumerate(RUNS) if s<=t<e),None)
   data=GFRAME if ri is None else render(ri,t).tobytes()
   p.stdin.write(data);n+=1
  if sec%30==0:
   (OUT/'art_progress.txt').write_text(f'{sec}/{END} | {n} frames | {time.time()-start_time:.1f}sec elapsed\n')
 p.stdin.close();rc=p.wait()
 if rc:raise RuntimeError('ffmpeg failed '+str(rc))
except BaseException as ex:
 p.kill();(OUT/'art_error.txt').write_text(repr(ex));raise
print('WROTE',out,os.stat(out).st_size, time.time()-start_time)
(OUT/'new_graphics_ranges.json').write_text(json.dumps({'runs':RUNS,'seconds_replaced':sum(e-s for s,e,*_ in RUNS),'source':'REV14','method':'greenkey overlay only on safe-card regions; preserve original movie audio and original movie shots'},ensure_ascii=False,indent=2))
