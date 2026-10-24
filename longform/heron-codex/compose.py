"""Mix original local speech/music/SFX, concatenate render shards, cut vertical Shorts."""
import json,math,subprocess,wave
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;SR=44100
S=json.loads((R/'timeline.json').read_text());D=sum(s['dur'] for s in S)
out=R/'out';out.mkdir(exist_ok=True)
def wavread(p):
 with wave.open(str(p)) as w:return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
x=np.zeros(round((D+.05)*SR),np.float32)
for s in S:
 a=wavread(R/s['file']);i=round((s['start']+.15)*SR);x[i:i+len(a)]+=a
# Original ambient score. Quiet, no borrowed commercial recording.
t=np.arange(len(x),dtype=np.float32)/SR
for j,hz in enumerate([130.8128,164.8138,195.9977,261.6256]):
 beat=(t+j*.55)%8
 env=np.exp(-beat*1.5)*np.minimum(beat/.03,1)
 x+=(np.sin(2*np.pi*hz*t)+.23*np.sin(2*np.pi*hz*2*t))*env*.007
rng=np.random.default_rng(193)
def add(at,a):
 i=round(at*SR);n=min(len(a),len(x)-i)
 if i>=0 and n>0:x[i:i+n]+=a[:n]
for s in S:
 at=s['start'];u=np.arange(int(.28*SR))/SR
 add(at,.035*np.sin(2*np.pi*(150*u+160*u*u))*np.exp(-u*15))
 if s['model']=='coin':
  for k in np.arange(1.8,s['dur'],9):
   u=np.arange(int(.18*SR))/SR;add(at+k,.05*np.sin(2*np.pi*1300*u)*np.exp(-u*38))
 if s['model']=='steam':
  a=rng.normal(0,.004,int(s['dur']*SR));add(at,a)
x*=np.minimum(1,t/1.2)*np.minimum(1,np.maximum(0,(D-t)/2))
peak=np.max(np.abs(x));
if peak>.85:x*=.85/peak
with wave.open(str(out/'mix.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(x,-1,1)*32767).astype(np.int16).tobytes())
chunks=sorted((R/'shards').glob('part_*.mp4'))
if not chunks:raise SystemExit('No video shards')
(out/'concat.txt').write_text(''.join("file '"+str(p.resolve())+"'\n" for p in chunks))
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-i',str(out/'mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-af','loudnorm=I=-16:TP=-3:LRA=9','-t',str(D),'-movflags','+faststart',str(out/'heron_ancient_automation_ru.mp4')],check=True)
def stamp(sec):
 cs=round(sec*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
shorts=[('coin',4,6,'Торговый автомат\n2000 лет назад'),('doors',9,11,'Огонь открывает\nдвери храма'),('steam',14,16,'Паровой шар\nиз древнего текста')]
for name,first,last,title in shorts:
 start=S[first]['start'];end=S[last]['start'];dur=end-start
 ass='''[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding\nStyle: Sub,DejaVu Sans,45,&H003A3626,&H0,&H00E1E9EE,&H00E1E9EE,-1,0,0,0,100,100,0,0,1,3,0,2,80,80,250,1\nStyle: Title,DejaVu Sans,68,&H003A3626,&H0,&H00E1E9EE,&H00E1E9EE,-1,0,0,0,100,100,0,0,1,0,0,8,65,65,250,1\nStyle: Foot,DejaVu Sans,30,&H00786F58,&H0,&H00E1E9EE,&H00E1E9EE,-1,0,0,0,100,100,0,0,1,0,0,2,70,70,90,1\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n'''
 ass+=f'Dialogue: 0,0:00:00.00,{stamp(dur)},Title,,0,0,0,,{title.replace(chr(10),chr(92)+"N")}\n'
 ass+=f'Dialogue: 0,0:00:00.00,{stamp(dur)},Foot,,0,0,0,,ПОЛНЫЙ РАЗБОР НА КАНАЛЕ M1LASH\\NУчебная 3D-реконструкция\n'
 for s in S[first:last]:
  import re
  parts=re.findall(r'[^.!?]+[.!?]+|[^.!?]+$',s['text']);pos=0
  for part in parts:
   a=.15+s['start']-start+s['speech']*pos/len(s['text']);pos+=len(part);b=.15+s['start']-start+s['speech']*pos/len(s['text'])
   ass+=f'Dialogue: 0,{stamp(a)},{stamp(b)},Sub,,0,0,0,,{part.strip()}\n'
 af=out/f'{name}.ass';af.write_text(ass)
 # Original horizontal footage is reframed around its central model; captions rebuilt for mobile.
 filt=f"[0:v]crop=1080:640:420:245,pad=1080:1920:0:560:color=0xeee9e1,ass={af.as_posix()}[v]"
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(out/'heron_ancient_automation_ru.mp4'),'-t',str(dur),'-filter_complex',filt,'-map','[v]','-map','0:a:0','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(out/f'heron_short_{name}_ru.mp4')],check=True)
print('FINAL',D,'SHORTS',[(name,S[b]['start']-S[a]['start']) for name,a,b,_ in shorts])
