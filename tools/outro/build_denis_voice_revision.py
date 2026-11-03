"""Owner-authorized voice-only outro revision; original video streams preserved."""
from pathlib import Path
import subprocess,json,hashlib,sys
import numpy as np
B=Path(sys.argv[1]).resolve();ROOT=Path(__file__).resolve().parents[2];SR=48000;D=6.6

def run(args):return subprocess.run(args,check=True,capture_output=True)
def pcm(path,start=0,dur=None):
 cmd=['ffmpeg','-v','error','-ss',str(start),'-i',str(path)]
 if dur is not None:cmd+=['-t',str(dur)]
 return np.frombuffer(run(cmd+['-ar',str(SR),'-ac','2','-f','f32le','-']).stdout,np.float32).reshape(-1,2)
def norm(a,lufs):
 proc=subprocess.run(['ffmpeg','-v','error','-f','f32le','-ar',str(SR),'-ac','2','-i','-','-af',f'loudnorm=I={lufs}:TP=-3:LRA=11','-ar',str(SR),'-f','f32le','-'],input=a.astype(np.float32).tobytes(),capture_output=True,check=True)
 return np.frombuffer(proc.stdout,np.float32).reshape(-1,2).copy()
N=round(SR*D);voice=np.zeros((N,2),np.float32)
placements=[(1,.78,1.63,.60),(2,1.03,4.95,1.75)]
for num,a,b,at in placements:
 x=norm(pcm(B/f'voice_{num:02d}.wav',a,b-a),-16.0);fade=min(240,len(x)//2);x[:fade]*=np.linspace(0,1,fade)[:,None];x[-fade:]*=np.linspace(1,0,fade)[:,None];pos=round(at*SR);voice[pos:pos+len(x)]+=x
import wave
def write(name,a):
 with wave.open(str(B/name),'wb') as w:w.setparams((2,2,SR,0,'NONE','not compressed'));w.writeframes((np.clip(a,-.999,.999)*32767).astype('<i2').tobytes())
write('Denis_outro_voice.wav',voice)
m=pcm(B/'NCS_source.mp3',43.72,D);m=np.pad(m,((0,max(0,N-len(m))),(0,0)))[:N];t=np.arange(N)/SR
env=np.interp(t,[0,.15,.5,.65,5.5,5.75,5.9,6.6],[0,.6,.6,.12,.12,.6,.6,0]);mix=m*env[:,None]+voice
for name,at,gain in [('whoosh.wav',0,.45),('click.wav',1.35,.7),('pop.wav',5.2,.65)]:
 x=pcm(B/name)*gain;pos=round(at*SR);x=x[:N-pos];mix[pos:pos+len(x)]+=x
write('mix_raw.wav',mix)
# Two-pass loudness mastering of the NEW version only, never the approved original.
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(B/'mix_raw.wav'),'-af','loudnorm=I=-15.5:TP=-1.8:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);z=r.stderr[r.stderr.rfind('{'):];j=json.JSONDecoder().raw_decode(z)[0]
af=f"loudnorm=I=-15.5:TP=-1.8:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=192000,alimiter=limit=0.76:attack=1:release=50:level=false:latency=1,aresample=48000,apad,atrim=end=6.6"
run(['ffmpeg','-v','error','-y','-i',str(B/'mix_raw.wav'),'-af',af,'-c:a','pcm_s24le',str(B/'master.wav')])
qa=[]
for fmt,src in [('vertical',ROOT/'media/outro/m1lash_outro_v1_vertical.mp4'),('horizontal',B/'original_horizontal.mp4')]:
 out=B/f'M1lash_outro_Denis_{fmt}_PRIVATE.mp4';run(['ffmpeg','-v','error','-y','-i',str(src),'-i',str(B/'master.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar',str(SR),'-t',str(D),'-movflags','+faststart',str(out)])
 def vh(p):return hashlib.sha256(run(['ffmpeg','-v','error','-i',str(p),'-map','0:v:0','-c:v','copy','-f','h264','-']).stdout).hexdigest()
 old,new=vh(src),vh(out);assert old==new,'VIDEO CHANGED';run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'])
 with (B/f'check_{fmt}.json').open('w') as f:subprocess.run(['python','skills/ext/ffmpeg-skill/scripts/check.py',str(out),'--platform','shorts' if fmt=='vertical' else 'youtube','--json'],cwd=ROOT,stdout=f,check=True)
 run(['python',str(ROOT/'skills/ext/ffmpeg-skill/scripts/look.py'),str(out),'--tiles','3x2','--width','1080','--output',str(B/f'contact_{fmt}.png')])
 qa.append({'format':fmt,'file':out.name,'video_elementary_sha256':new,'original_video_identical':True,'full_decode':True,'duration':D});print('MADE',out.name,flush=True)
(B/'qa.json').write_text(json.dumps({'outputs':qa,'voice_placements':placements,'music_excerpt':[43.72,50.32],'owner_hearing_review':'pending','canonical_originals_replaced':False},ensure_ascii=False,indent=2))
