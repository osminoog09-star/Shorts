"""Original procedural cartoon foley and music. No synthesized narrator."""
from pathlib import Path
import numpy as np,wave,subprocess,json
R=Path(__file__).resolve().parent;O=R/'out';O.mkdir(exist_ok=True)
SR=48000;D=22.;x=np.zeros(int(SR*D),dtype=np.float64);rng=np.random.default_rng(821)
def add(at,a):
 i=round(at*SR);n=min(len(a),len(x)-i)
 if n>0:x[i:i+n]+=a[:n]
def tone(f,d=.25,amp=.06):
 t=np.arange(int(d*SR))/SR
 return (np.sin(2*np.pi*f*t)+.25*np.sin(2*np.pi*f*3*t))*np.exp(-t*14)*amp
for t in np.arange(0,21.5,.375):
 hz=[261.626,329.628,391.995,329.628][int(t/.375)%4];add(t,tone(hz))
 if int(t/.375)%2==0:add(t,tone(hz/4,.3,.035))
# Footsteps stop at the collision and resume for the final proud walk.
for a,b in [(0,2.7),(13,17)]:
 for at in np.arange(a,b,.30):
  u=np.arange(int(.075*SR))/SR;add(at,rng.normal(0,.035,len(u))*np.exp(-u*55)+tone(180,.075,.025))
u=np.arange(int(.4*SR))/SR
bonk=(np.sin(2*np.pi*160*u)+.7*np.sin(2*np.pi*363*u))*np.exp(-u*16)*.28
add(2.8,bonk);add(3.03,bonk*.32)
# Cartoon disappointed whistle, then robot acknowledgement.
u=np.arange(int(.6*SR))/SR;add(3.6,.07*np.sin(2*np.pi*(620*u-190*u*u))*np.sin(np.pi*u/.6)**2)
for at,f in [(5.3,780),(5.5,1040),(8.8,660),(9.0,880)]:add(at,tone(f,.18,.09))
# Tool rattle and tumbling masonry, timed to the animated widening.
u=np.arange(int(2.3*SR))/SR
add(10,(rng.normal(0,.035,len(u))+.03*np.sin(2*np.pi*92*u))*np.minimum(1,u/.06)*np.minimum(1,(2.3-u)/.1))
for i in range(9):add(10.6+i*.14,bonk*.22)
# Two original formant-like cartoon woofs, no third-party animal recording.
for at in [13.3,13.65]:
 u=np.arange(int(.20*SR))/SR;env=np.sin(np.pi*u/.20)**1.5
 add(at,.12*env*(np.sin(2*np.pi*155*u)+.5*np.sin(2*np.pi*465*u))*(.7+.3*np.sin(2*np.pi*27*u)))
for i,f in enumerate([392,494,587,784]):add(17.1+i*.1,tone(f,.45,.09))
t=np.arange(len(x))/SR;x*=np.minimum(1,t/.04)*np.minimum(1,np.maximum(0,(D-t)/.45));x=np.clip(x,-.85,.85)
with wave.open(str(O/'original_sfx.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((x*32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg','-y','-v','error','-i',str(O/'dog_big_stick_visual_silent.mp4'),'-i',str(O/'original_sfx.wav'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-af','loudnorm=I=-17:TP=-3:LRA=9','-t','22','-movflags','+faststart',str(O/'dog_big_stick_preview_ru.mp4')],check=True)
f=O/'dog_big_stick_preview_ru.mp4';d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(f)]));subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
(O/'qa.json').write_text(json.dumps({'duration':d['format']['duration'],'streams':[{k:s.get(k) for k in ['codec_name','width','height','pix_fmt','r_frame_rate']} for s in d['streams']],'full_decode':'passed','voice':'none: visual workprint with original SFX/music','full_continuous_human_review':'not performed','publication':'not scheduled'},ensure_ascii=False,indent=2))
print(f)
