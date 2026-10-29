#!/usr/bin/env python3
"""X-59 M1lash S5-D25 pixel motion internal PREVIEW, no publication or approved HostCorner.
Original graphics and synthesized procedural score. Real Edge DmitryNeural only; no fallback.
"""
import asyncio, json, math, os, random, subprocess, time, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'work'/'x59_20261029'; WORK.mkdir(parents=True,exist_ok=True)
OUT=WORK/'x59_s5d25_INTERNAL_PREVIEW_NO_GO.mp4'
W,H,FPS,SR=540,960,24,24000
TEXT=[
'Представь: самолёт летит быстрее звука, а вместо громового удара — тихий стук. Это идея NASA X-59.',
'Двадцать восьмого октября исполнился год с первого полёта. За год он совершил ещё сорок испытательных вылетов.',
'Разогнался до Маха один и пятьдесят три сотых и поднялся выше семнадцати километров.',
'Его необычно длинный нос должен изменить ударные волны так, чтобы на земле слышали не грохот, а короткий хлопок.',
'Но не спеши радоваться: испытания акустики и опросы жителей ещё впереди. Тишину пока не доказали.',
'Представляешь: сверхзвуковой самолёт учится быть тише соседа с перфоратором. Это, конечно, шутка.',
'Если измерения подтвердят идею, это может повлиять на правила сверхзвуковых полётов над сушей.',
'Хотел бы летать быстрее звука без оглушительного удара? Напиши в комментариях. Подпишись! И спасибо всем, кто досмотрел и поставил лайк.'
]
HEAD=['СВЕРХЗВУК БЕЗ ГРОМА?','40 ПОЛЁТОВ ЗА ГОД','МАХ 1,53','ЗАЧЕМ ТАКОЙ НОС?','ГЛАВНОЕ — ЕЩЁ ВПЕРЕДИ','ШУТКА ПРО ПЕРФОРАТОР','ЧТО ИЗМЕНИТСЯ?','А ТЫ БЫ ПОЛЕТЕЛ?']
SMALL=['NASA X-59 / КОНЦЕПЦИЯ','28.10.2025 → 28.10.2026','ВЫСОТА > 56 000 ФУТОВ','УДАРНАЯ ВОЛНА / СХЕМА','АКУСТИЧЕСКИЕ ИСПЫТАНИЯ','НЕ РЕАЛЬНЫЙ ЗАМЕР ШУМА','РЕШЕНИЕ ЗА ИСПЫТАНИЯМИ','M1LASH / ПОДПИСЫВАЙСЯ']
BG=(9,16,33); BLUE=(65,197,235); GOLD=(253,184,76); WHITE=(246,245,231); RED=(247,97,94)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONTR='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
f_big=ImageFont.truetype(FONT,31); f_mid=ImageFont.truetype(FONT,23)
f_small=ImageFont.truetype(FONT,15); f_sub=ImageFont.truetype(FONT,22)
def run(args,check=True):
 p=subprocess.run(args,capture_output=True,text=True)
 if check and p.returncode:raise RuntimeError(' '.join(args)+'\n'+p.stderr[-1500:])
 return p
def dur(p):
 return float(json.loads(run(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(p)]).stdout)['format']['duration'])
async def voice():
 import edge_tts
 segments=[];start=0.
 for i,s in enumerate(TEXT):
  dest=WORK/f'dima_{i:02d}.mp3'
  if not dest.exists() or dest.stat().st_size<900:
   for attempt in range(12):
    try:
     await asyncio.wait_for(edge_tts.Communicate(s,'ru-RU-DmitryNeural',rate='+8%').save(str(dest)),timeout=50)
     if dest.stat().st_size<900:raise ValueError('audio too short')
     break
    except Exception as ex:
     print('TTS retry',i,attempt,str(ex)[:130],flush=True)
     if dest.exists():dest.unlink()
     if attempt==11:raise
     await asyncio.sleep(3+attempt*.8)
  seconds=dur(dest);segments.append(dict(id=f'{i:02d}',speaker='dima',voice_id='ru-RU-DmitryNeural',engine='Microsoft Edge TTS',rate='+8%',source_file=str(dest.relative_to(ROOT)),start=round(start,3),end=round(start+seconds,3),duration=round(seconds,3)))
  start+=seconds+.17
 # Join audio using a filter graph; no accidental literal newline in concat list
 manifest={'segments':segments,'voice_id':'ru-RU-DmitryNeural','total_duration':round(start,3),'status':'PREVIEW_NO_GO_MISSING_APPROVED_HOST_LIPSYNC'}
 (WORK/'voice_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
 listfile=WORK/'concat.txt'
 listfile.write_text(''.join("file '"+str((ROOT/s['source_file']).resolve())+"'"+chr(10) for s in segments))
 raw=WORK/'speech.mp3'
 run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listfile),'-ar',str(SR),'-ac','1',str(raw)])
 return segments,dur(raw)
def wrap(draw,txt,font,maxwidth):
 words=txt.split();rows=[];line=''
 for word in words:
  cand=(line+' '+word).strip()
  if draw.textbbox((0,0),cand,font=font)[2]>maxwidth and line:rows.append(line);line=word
  else:line=cand
 if line:rows.append(line)
 return rows
def text_center(draw,y,txt,font,color=WHITE,stroke=0):
 bb=draw.textbbox((0,0),txt,font=font,stroke_width=stroke)
 x=(W-(bb[2]-bb[0]))//2
 draw.text((x,y),txt,font=font,fill=color,stroke_width=stroke,stroke_fill=BG)
def plane(d,cx,cy,scale=1.0,tilt=0,light=BLUE):
 # Stylized X-59 inspired geometry; expressly not a NASA technical drawing.
 def pt(x,y):return (int(cx+x*scale),int(cy+y*scale))
 body=[(-245,0),(-95,-13),(72,-19),(177,-9),(216,-4),(248,2),(215,8),(76,17),(-95,11)]
 d.polygon([pt(x,y) for x,y in body],fill=(216,226,231))
 d.polygon([pt(-36,-9),pt(40,-87),pt(106,-76),pt(69,-3)],fill=(70,160,186))
 d.polygon([pt(-20,9),pt(34,82),pt(106,73),pt(66,4)],fill=(40,111,150))
 d.polygon([pt(136,-4),pt(179,-47),pt(193,-44),pt(183,0)],fill=(56,139,184))
 d.line([pt(-234,-2),pt(180,-2)],fill=(89,164,188),width=max(1,int(3*scale)))
 d.rectangle([pt(-3,-7),pt(26,-3)],fill=(10,24,43))
 d.ellipse([pt(196,-6),pt(206,6)],fill=GOLD)
def clouds(d,t,offset=0):
 for j in range(13):
  x=int(((j*147-t*(16+(j%3)*7)+offset)%810)-130)
  y=130+j*58
  r=20+(j*13)%34
  d.ellipse((x-r,y-r//3,x+r,y+r//3),fill=(22+int(j%3)*3,42+int(j%4)*3,67+int(j%2)*4))
def pixel_grid(d,t):
 for x in range(0,W,30):d.line([(x,0),(x,H)],fill=(13,27,47),width=1)
 for y in range(0,H,30):d.line([(0,y),(W,y)],fill=(13,27,47),width=1)
def scene(d,idx,local,t):
 if idx in (0,1,2,3):
  clouds(d,t*1.3,idx*80)
  yy=370+int(math.sin(t*1.9)*12)
  xx=265+int(math.sin(t*.7)*16)
  if idx==0:
   for j in range(4):
    r=90+j*68+int((t*40)%70)
    d.arc((xx-r,yy-r//2,xx+r,yy+r//2),190,355,fill=GOLD,width=3)
   plane(d,xx,yy,0.93)
  elif idx==1:
   plane(d,xx,yy,1.02)
   for j in range(6):
    x=60+j*74;h=int(18+abs(math.sin(t*1.5+j))*100)
    d.rectangle((x,575-h,x+35,575),fill=(39,120,161))
   text_center(d,625,'+40',ImageFont.truetype(FONT,102),GOLD)
  elif idx==2:
   plane(d,xx,yy,.90)
   d.arc((95,170,445,520),190,355,fill=GOLD,width=9)
   text_center(d,595,'1.53',ImageFont.truetype(FONT,94),GOLD)
   text_center(d,697,'MACH',f_mid,BLUE)
  else:
   plane(d,320,340,1.10)
   for j in range(5):
    x=105+int(t*13)+j*55
    d.arc((x-105,240,x+105,480),230,315,fill=GOLD,width=4)
   d.line([(75,490),(465,490)],fill=BLUE,width=3)
   text_center(d,530,'УСЛОВНАЯ СХЕМА',f_small,GOLD)
 elif idx==4:
  for j in range(11):
   x=60+j*40;y=420-int(math.sin(j*.73+t*.9)*50)
   d.line([(x,420),(x,y)],fill=BLUE,width=4)
  d.rectangle((50,300,490,550),outline=BLUE,width=3)
  text_center(d,600,'НЕ ДОКАЗАНО',ImageFont.truetype(FONT,42),RED)
  text_center(d,674,'ПРОВЕРКА ШУМА ВПЕРЕДИ',f_small,GOLD)
 elif idx==5:
  d.rectangle((100,250,440,590),fill=(39,48,64))
  for j in range(8):d.line([(130+j*40,250),(130+j*40,590)],fill=(56,63,75),width=3)
  d.rectangle((180,400,350,438),fill=GOLD)
  d.polygon([(320,389),(385,412),(320,448)],fill=(218,224,232))
  for j in range(3):
   x=405+j*12
   d.arc((x-18,380,x+18,465),-60,60,fill=RED,width=3)
  text_center(d,618,'ТУК-ТУК-ТУК!',f_big,GOLD)
  text_center(d,676,'АВТОРСКАЯ ШУТКА',f_small,BLUE)
 elif idx==6:
  d.rectangle((0,550,W,700),fill=(24,41,60))
  for j in range(13):
   x=j*43;h=35+(j*29)%130
   d.rectangle((x,550-h,x+33,550),fill=(51,83,113))
  plane(d,285,315,.83)
  d.line([(90,580),(460,580)],fill=GOLD,width=3)
  text_center(d,625,'ЕСЛИ ПОДТВЕРДИТСЯ',f_mid,GOLD)
 else:
  clouds(d,t)
  plane(d,270,340,1.0)
  text_center(d,590,'НАПИШИ В КОММЕНТАРИЯХ',f_mid,GOLD)
  text_center(d,647,'ПОДПИШИСЬ',ImageFont.truetype(FONT,43),BLUE)
  text_center(d,708,'M1LASH',f_big,WHITE)
def draw_frame(idx,local,t,txt):
 im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
 pixel_grid(d,t);scene(d,idx,local,t)
 # No persistent giant frames, just two tiny metadata labels.
 d.rectangle((0,0,W,8),fill=GOLD if idx in (0,4) else BLUE)
 d.text((26,34),'M1LASH  /  НАУКА',font=f_small,fill=BLUE)
 d.text((26,62),'29 ОКТ 2026',font=f_small,fill=(143,165,188))
 for n,line in enumerate(wrap(d,HEAD[idx],f_big,W-44)[:2]):
  text_center(d,108+n*42,line,f_big,GOLD)
 text_center(d,205,SMALL[idx],f_small,BLUE)
 # Subtitle zone y=760..860, full bleed background behind, readable and away from right-side controls.
 d.rectangle((18,765,520,878),fill=(7,15,29))
 lines=wrap(d,txt,f_sub,475)
 if len(lines)>3:
  lines=wrap(d,txt,ImageFont.truetype(FONT,19),475);sf=ImageFont.truetype(FONT,19)
 else:sf=f_sub
 for n,line in enumerate(lines[:3]):text_center(d,780+n*30,line,sf,WHITE)
 d.text((25,917),'РЕКОНСТРУКЦИЯ / ДАННЫЕ NASA',font=f_small,fill=(120,147,170))
 return im
def render_video(segments):
 timeline=[];at=0
 for i,s in enumerate(segments):
  n=max(1,round((s['duration']+.12)*FPS));timeline.append((i,at,at+n,n));at+=n
 video=WORK/'silent.mp4'
 cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-vf','scale=1080:1920:flags=neighbor,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','20','-r',str(FPS),str(video)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
 for idx,start,end,n in timeline:
  for k in range(n):
   t=(start+k)/FPS;local=k/max(1,n)
   # Sentence-by-sentence subtitle not fake word timings; scene-level only, see QA gate.
   frame=draw_frame(idx,local,t,TEXT[idx])
   try:p.stdin.write(frame.tobytes())
   except BrokenPipeError:raise RuntimeError('ffmpeg stopped rendering')
 p.stdin.close();err=p.stderr.read().decode();ret=p.wait()
 if ret:raise RuntimeError('ffmpeg render failed: '+err[-2000:])
 return video,timeline
def main():
 segments,speechdur=asyncio.run(voice())
 print('Dima TTS PASS',len(segments),'speech',speechdur,flush=True)
 video,timeline=render_video(segments)
 # Original self-generated music bed (not third-party): gentle sub pulses at -34 dBFS
 duration=dur(video);N=int(duration*SR)
 t=np.arange(N,dtype=np.float64)/SR
 music=(.006*np.sin(2*np.pi*88*t)+.004*np.sin(2*np.pi*132*t))*np.minimum(1,t/2)
 music+=(.005*np.sin(2*np.pi*330*t)*np.exp(-((t*1.3)%1)*28))
 wav=WORK/'own_score.wav'
 with wave.open(str(wav),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR)
  w.writeframes((np.clip(music,-1,1)*32767).astype('<i2').tobytes())
 speech=WORK/'speech.mp3'
 run(['ffmpeg','-y','-v','error','-i',str(video),'-i',str(speech),'-i',str(wav),'-filter_complex','[1:a]volume=1.15[v];[2:a]volume=0.75[m];[v][m]amix=inputs=2:duration=longest:dropout_transition=0[a]','-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-shortest',str(OUT)])
 qa={'status':'NO_GO_PREVIEW','reason':'approved HostCorner and phoneme-level lip sync not yet integrated; subtitles are sentence-level','style':'S5-D25','voice_id':'ru-RU-DmitryNeural','source':'original pixel reconstruction + NASA facts','video':str(OUT),'duration':dur(OUT),'dimensions':'1080x1920','frames':sum(x[3] for x in timeline),'segments':segments}
 (WORK/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
 for i,s in enumerate(segments):
  f=int((timeline[i][1]+timeline[i][3]//2))
  run(['ffmpeg','-y','-v','error','-ss',str(f/FPS),'-i',str(OUT),'-frames:v','1',str(WORK/f'qa_{i:02d}.jpg')])
 run(['ffmpeg','-v','error','-i',str(OUT),'-f','null','-'])
 print('PREVIEW QA decode PASS',qa['duration'],OUT,flush=True)
if __name__=='__main__':main()
