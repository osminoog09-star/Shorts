#!/usr/bin/env python3
"""M1lash / Нейроофис: original, fully code-animated vertical demo.
Reuses authentic existing ru-RU-DmitryNeural narration (not synthetic fallback).
NO YouTube/Metricool calls. Hand-reviewed quality not implied by technical QA.
"""
import hashlib, json, math, os, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'shorts/neurooffice-demo/out';OUT.mkdir(parents=True,exist_ok=True)
S=ROOT/'media/tts'
AUDIO=[*(S/'research_codex'/f'sketch_schedule_{i}.mp3' for i in range(6)),S/'host_demo/h4.mp3']
META=[*(S/'research_codex'/f'sketch_schedule_{i}.json' for i in range(6)),S/'host_demo/h4.json']
W,H,FPS=540,960,24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F={n:ImageFont.truetype(FONT,n) for n in (13,16,19,21,23,26,29,34,40,47)}
TEAL='#6be5d6';PINK='#ef8090';CREAM='#fcf1dd';MUTE='#90a8bb'
def ex(cmd):subprocess.run(cmd,check=True)
def dur(path):return float(json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','json',str(path)]))['format']['duration'])
def clip(x):return max(0.,min(1.,x))
def ease(x):x=clip(x);return x*x*(3-2*x)
def rr(d,x,y,w,h,c,r=14):d.rounded_rectangle((int(x),int(y),int(x+w),int(y+h)),radius=r,fill=c)
def txt(d,x,y,s,n,c=CREAM,anchor='la'):d.text((x,y),s,font=F[n],fill=c,anchor=anchor)
def line(d,p,c,width=3):d.line(p,fill=c,width=width,joint='curve')
def person(d,x,y,t,expr='worried',kind=0,pose=0,talking=False):
    # articulated body and actual independent arm / eyebrows / mouth poses
    x+=math.sin(t*.8)*2;y+=math.sin(t*1.5)*1
    skin='#dba483' if kind!=2 else '#c98a70'
    jacket=['#2d89a5','#8d604e','#ba6f9b'][kind]
    d.ellipse((x-57,y+2,x+59,y+15),fill='#07101e')
    for xx in (-22,19):
      line(d,[(x+xx,y-83),(x+xx+(5 if xx>0 else -4)*math.sin(t*4),y-2)],'#283447',19)
      rr(d,x+xx-17,y-16,37,19,'#132234',6)
    d.polygon([(x-52,y-189),(x+51,y-189),(x+47,y-80),(x-49,y-80)],fill=jacket)
    d.polygon([(x-10,y-188),(x+11,y-188),(x+14,y-100),(x,y-94),(x-13,y-100)],fill='#b9d9de')
    for sign in (-1,1):
      a=(x+sign*45,y-184);elbow=(x+sign*(72+pose*5),y-137)
      hand=(x+sign*(55-pose*39),y-112-pose*48)
      line(d,[a,elbow],jacket,20);line(d,[elbow,hand],skin,12)
      d.ellipse((hand[0]-9,hand[1]-10,hand[0]+9,hand[1]+10),fill=skin)
      for f in (-2,-1,0,1,2):
       line(d,[(hand[0]+f*2,hand[1]-4),(hand[0]+f*3,hand[1]-13)],skin,2)
    rr(d,x-12,y-220,24,38,skin,5);d.ellipse((x-47,y-310,x+47,y-213),fill=skin)
    hair='#2b3545' if kind==0 else '#414653' if kind==1 else '#392b36'
    d.polygon([(x-46,y-265),(x-43,y-294),(x-20,y-314),(x+20,y-308),(x+45,y-282),(x+43,y-260),(x+14,y-281),(x,y-270),(x-27,y-281)],fill=hair)
    for ix in (-17,17):
      d.ellipse((x+ix-5,y-265,x+ix+5,y-253),fill='#fff5df')
      d.ellipse((x+ix-1,y-264,x+ix+3,y-256),fill='#233649')
      line(d,[(x+ix-11,y-279),(x+ix+10,y-282-(4 if expr=='scared' else 0))],'#5f383d',3)
    if talking:d.ellipse((x-5,y-233,x+8,y-216),fill='#793c48')
    elif expr=='smile':d.arc((x-10,y-238,x+10,y-222),0,180,fill='#793c48',width=3)
    else:line(d,[(x-8,y-225),(x+9,y-225)],'#793c48',2)
def robot(d,x,y,t,alarm=False):
    y+=math.sin(t*3)*3
    d.ellipse((x-90,y+4,x+90,y+25),fill='#081b27')
    for sign in (-1,1):
      d.ellipse((x+sign*40-26,y-23,x+sign*40+26,y+24),fill='#112837')
      d.ellipse((x+sign*40-13,y-11,x+sign*40+13,y+12),fill='#427c92')
    rr(d,x-73,y-204,149,170,'#9acbd6',25);rr(d,x-50,y-151,101,48,'#1a3c50',11)
    for xx in (-87,75):rr(d,x+xx,y-178,17,108,'#c0e5e7',8)
    rr(d,x-91,y-307,184,120,'#abdae0',28)
    rr(d,x-77,y-294,156,87,'#123a50',24)
    for xx in (-37,35):
      d.ellipse((x+xx-14,y-265,x+xx+14,y-235),fill=PINK if alarm else TEAL)
      d.ellipse((x+xx-6,y-262,x+xx+3,y-255),fill=CREAM)
    if alarm:line(d,[(x-21,y-222),(x+20,y-222)],PINK,6)
    else:d.arc((x-23,y-260,x+23,y-210),0,180,fill=TEAL,width=6)
    line(d,[(x,y-308),(x,y-333)],'#bad9dc',7)
    d.ellipse((x-11,y-348,x+11,y-326),fill=PINK if alarm else TEAL)
def base(d,t,index):
    d.rectangle((0,0,W,H),fill='#101f30')
    for b in range(9):
      x=72*b-20+math.sin(t*.2+b)*4
      h=100+(b*53)%122
      rr(d,x,270-h,59,h,'#1b3449',4)
      for j in range(3):
        for k in range(2):
          if (j+k+b)%3:rr(d,x+8+k*26,280-h+j*26,9,12,'#406479',2)
    d.polygon([(0,322),(W,285),(W,H),(0,H)],fill='#1a3043')
    for y in (450,620,800):line(d,[(0,y),(W,y-45)],'#2e5060',2)
    for x in (80,185,355,480):line(d,[(x,322),(W/2+(x-270)*3,H)],'#2b495b',1)
    rr(d,16,18,508,79,'#0a1d2b',17);txt(d,35,57,'НЕЙРООФИС',34,CREAM,'lm')
    rr(d,354,40,151,36,TEAL,10);txt(d,429,58,'МИНИ-СЕРИАЛ',13,'#123447','mm')
    for j in range(3):rr(d,477,136+j*29,42,13,TEAL if (j+index)%2 else '#344e64',5)
def panel(d,title,subtitle,pink=False):
    rr(d,29,162,482,144,'#0b2132',21)
    txt(d,50,205,title,23,PINK if pink else TEAL,'lm')
    txt(d,50,264,subtitle,19,MUTE,'lm')
def box(d,x,y,w,h,c):rr(d,x,y,w,h,c,10)
def desk(d):
    d.ellipse((90,735,490,764),fill='#101825')
    rr(d,69,696,407,31,'#b6a38e',8)
    for xx in (99,449):rr(d,xx,721,20,103,'#516574',5)
def terminal(d,x=257,y=466,heading='ГРАФИК'):
    rr(d,x,y,240,177,'#071525',17);rr(d,x+10,y+9,222,148,'#153e50',12)
    txt(d,x+26,y+41,heading,19,TEAL,'lm')
    for i in range(4):rr(d,x+27,y+72+i*20,168-i*15,7,TEAL if i<2 else '#4b6778',4)
    rr(d,x+102,y+177,28,36,'#697f8b',4);rr(d,x+71,y+204,86,9,'#9cb5bb',4)
def caption(d,words,lt):
    active=0
    for i,w in enumerate(words):
      if lt>=w['start']-.08:active=i
    words=[w['w'] for w in words[max(0,active-2):active+1]]
    words=' '.join(words)
    while len(words)>31:words=' '.join(words.split(' ')[1:])
    lines=['']
    for w in words.split(' '):
      p=(lines[-1]+' '+w).strip()
      if d.textbbox((0,0),p,font=F[26])[2]>470 and lines[-1]:lines.append(w)
      else:lines[-1]=p
    top=771 if len(lines)==1 else 742
    rr(d,17,top,506,len(lines)*45+37,'#081724',17)
    for j,s in enumerate(lines):txt(d,W/2,top+35+j*45,s,26,CREAM,'mm')
    return any(w['start']<=lt<=w['end'] for w in words_info_global)
words_info_global=[]
def frame(i,tt,seconds,words):
    global words_info_global
    words_info_global=words
    im=Image.new('RGB',(W,H))
    d=ImageDraw.Draw(im)
    base(d,tt,i);top=145
    active=any(w['start']<=tt<=w['end'] for w in words)
    if i==0:
      desk(d);terminal(d,239,435,'ИИ РАСПИСАНИЕ')
      person(d,128,736,tt,'scared',pose=ease(tt/3),talking=active)
      robot(d,426,752,tt)
      panel(d,'ИИ СОСТАВИЛ ГРАФИК','Учтены пожелания всех')
    elif i==1:
      desk(d);person(d,165,755,tt,'smile',kind=1,pose=ease(tt/2),talking=active)
      robot(d,427,765,tt)
      panel(d,'НАЧАЛЬНИК ОТДЫХАЕТ','Выходные — дома')
      box(d,42,361,237,68,'#143e49');txt(d,160,395,'ОДОБРЕНО ✓',21,TEAL,'mm')
    elif i==2:
      person(d,132,748,tt,'worried',kind=2,pose=.6,talking=active)
      person(d,307,745,tt,'worried',pose=.5,talking=False)
      robot(d,461,752,tt)
      panel(d,'РАБОТНИКИ ПРОСЯТ','Без ночных смен')
      box(d,49,359,350,65,'#15434b');txt(d,219,391,'ЗАПРОС ПРИНЯТ ✓',21,TEAL,'mm')
    elif i==3:
      person(d,132,755,tt,'scared',pose=.7,talking=active)
      rr(d,259,322,246,410,'#0c2638',14)
      txt(d,382,351,'МОИ СМЕНЫ',21,TEAL,'mt')
      for j,day in enumerate(['ПОНЕДЕЛЬНИК','ВТОРНИК','СРЕДА']):
        y=406+j*101;box(d,274,y,216,83,'#1b3547')
        txt(d,284,y+14,day,16,CREAM)
        if tt>j*1.4:txt(d,291,y+66,'НОЧЬ',26,PINK)
      panel(d,'МОЙ ГРАФИК','ПН, ВТ, СР — ночные!',pink=True)
    elif i==4:
      desk(d);person(d,134,750,tt,'scared',pose=min(tt/2,1),talking=active)
      robot(d,431,754,tt)
      panel(d,'ЖАЛУЕТСЯ ТОЛЬКО ОДИН','Раньше жаловались все')
      box(d,55,381,432,31,'#274555');box(d,55,381,433*ease(tt/7),31,TEAL)
      txt(d,75,453,'ЭФФЕКТИВНОСТЬ  +96%',21,CREAM)
    elif i==5:
      desk(d);person(d,128,748,tt,'scared',pose=ease(tt/3),talking=active)
      robot(d,431,746,tt,alarm=True)
      panel(d,'ФИЗИЧЕСКИЙ ТРУД','В тариф не входит',pink=True)
      box(d,61,383,421,81,'#ac3d5b')
      txt(d,271,425,'ТРЕБУЕТСЯ ПОДПИСКА',21,CREAM,'mm')
    else:
      person(d,269,759,tt,'smile',pose=.35,talking=active)
      panel(d,'ПОЛНЫЙ МУЛЬТСЕРИАЛ','Новый директор — скоро')
      box(d,70,370,400,87,'#c75c61')
      txt(d,270,413,'ПОДПИШИСЬ',34,CREAM,'mm')
    box(d,28,729,483,7,PINK if i in (3,5) else TEAL)
    caption(d,words,tt)
    txt(d,270,941,'M1LASH • НЕЙРООФИС • ДЕМО',13,'#8aa7b3','mm')
    return im
def main():
    for p in AUDIO+META:
      if not p.exists():raise SystemExit('NO-GO: missing approved audio '+str(p))
    for j in ('research_codex','host_demo'):
      voice=json.loads((ROOT/'jobs/tts'/f'{j}.json').read_text())
      assert voice['voice']=='ru-RU-DmitryNeural' and voice['rate']=='+8%'
    durations=[dur(p) for p in AUDIO]
    metas=[json.loads(p.read_text()) for p in META]
    args=['ffmpeg','-nostdin','-v','error','-y']
    for p in AUDIO:args+=['-i',str(p)]
    filters=';'.join(f'[{i}:a]aresample=48000,aformat=sample_fmts=s16:channel_layouts=mono[a{i}]' for i in range(7))+';'+''.join(f'[a{i}]' for i in range(7))+'concat=n=7:v=0:a=1[out]'
    voice=OUT/'voice.wav'
    ex(args+['-filter_complex',filters,'-map','[out]','-c:a','pcm_s16le',str(voice)])
    silent=OUT/'silent.mp4';output=OUT/'NEUROOFFICE_VOICE_SHORT_RU.mp4'
    frames=0;proof=[]
    proc=subprocess.Popen(['ffmpeg','-nostdin','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-an','-vf','scale=1080:1920:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-movflags','+faststart',str(silent)],stdin=subprocess.PIPE)
    for i,dur_s in enumerate(durations):
      count=round(dur_s*FPS)
      for n in range(count):
        im=frame(i,n/FPS,dur_s,metas[i]['words'])
        if n==count//2:proof.append(im)
        proc.stdin.write(im.tobytes());frames+=1
      print(f'CODE ANIMATED SCENE {i+1}/7, {count} frames',flush=True)
    proc.stdin.close()
    if proc.wait():raise SystemExit('NO-GO: failed to render silent video')
    # small original procedurally synthesized synth pad; no music licenses involved
    ex(['ffmpeg','-nostdin','-v','error','-y','-i',str(silent),'-i',str(voice),'-filter_complex','[1:a]volume=1[a]','-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(output)])
    if abs(dur(output)-dur(voice))>.25:raise SystemExit('NO-GO: A/V drift')
    ex(['ffmpeg','-nostdin','-v','error','-xerror','-i',str(output),'-f','null','-'])
    sheet=Image.new('RGB',(810,1440),'#061422')
    for i,im in enumerate(proof):sheet.paste(im.resize((270,480),Image.Resampling.LANCZOS),((i%3)*270,(i//3)*480))
    sheet.save(OUT/'contact.jpg',quality=87)
    qa={'status':'VISUAL_REVIEW_REQUIRED','duration_seconds':dur(output),'resolution':'1080x1920','fps':FPS,
        'voice_id':'ru-RU-DmitryNeural','voice_rate':'+8%','voice_segments':7,
        'source_audio':[str(p.relative_to(ROOT)) for p in AUDIO],
        'ffmpeg_full_decode':'PASS','mouth':'word timing approximate, NOT phoneme-exact lip sync',
        'video_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
        'publication':'NONE / owner uploads manually'}
    (OUT/'QA.json').write_text(json.dumps(qa,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
