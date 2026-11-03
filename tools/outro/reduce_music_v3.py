from pathlib import Path
import json,subprocess,wave,hashlib,sys
import numpy as np
B=Path(sys.argv[1]).resolve();O=B/'music80';O.mkdir(exist_ok=True);SR=48000;N=round(SR*6.6)
def run(a):return subprocess.run(a,check=True,capture_output=True)
def pcm(p):return np.frombuffer(run(['ffmpeg','-v','error','-i',str(p),'-ar',str(SR),'-ac','2','-f','f32le','-']).stdout,np.float32).reshape(-1,2).copy()
def write(p,a):
 with wave.open(str(p),'wb') as w:w.setparams((2,3,SR,0,'NONE','not compressed'));v=(np.clip(a,-.999999,.999999)*8388607).astype('<i4');w.writeframes(v.view(np.uint8).reshape(-1,4)[:,:3].tobytes())
raw=pcm(B/'mix_raw.wav');old=pcm(B/'master.wav');n=min(len(raw),len(old));raw=raw[:n];old=old[:n]
gain=float(np.sum(old*raw,dtype=np.float64)/np.sum(raw*raw,dtype=np.float64));err=old-raw*gain
music=pcm(B/'NCS_excerpt_43_72.wav');music=np.pad(music,((0,max(0,n-len(music))),(0,0)))[:n];t=np.arange(n)/SR
env=np.interp(t,[0,.15,.5,.65,5.5,5.75,5.9,6.6],[0,.6,.6,.12,.12,.6,.6,0]);music_master=music*env[:,None]*gain
# Preserve the previous master, including its voice/FX and tiny mastering residual.
# Only subtract 20% of the isolated clean music component; no renormalization.
voice=pcm(B/'Denis_outro_voice.wav')[:n]*gain
voice_boost=10**(1/20)
new=old-.2*music_master+(voice_boost-1)*voice;write(O/'master_music80.wav',new);write(O/'music_before.wav',music_master);write(O/'music_after.wav',.8*music_master)
qa={'music_gain':.8,'music_delta_db':float(20*np.log10(.8)),'old_master_linear_gain':gain,'old_master_linear_residual_db':float(20*np.log10(np.sqrt(np.mean(err**2))/np.sqrt(np.mean(old**2)))),'voice_gain_db':1.,'fx_gain':1.,'video_unchanged':True,'canonical_voice':'denis-qwen3tts-reference-v1','files':[]}
for fmt in ('vertical','horizontal'):
 src=B/f'M1lash_outro_Denis_{fmt}_PRIVATE.mp4';out=O/f'M1lash_outro_Denis_v3_music80_{fmt}.mp4'
 run(['ffmpeg','-v','error','-y','-i',str(src),'-i',str(O/'master_music80.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','320k','-ar',str(SR),'-t','6.6','-movflags','+faststart',str(out)])
 vh=lambda p:hashlib.sha256(run(['ffmpeg','-v','error','-i',str(p),'-map','0:v','-c:v','copy','-f','h264','-']).stdout).hexdigest()
 assert vh(src)==vh(out);run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'])
 root=Path(__file__).resolve().parents[2]
 with (O/f'check_{fmt}.json').open('w') as f:subprocess.run(['python','skills/ext/ffmpeg-skill/scripts/check.py',str(out),'--platform','shorts' if fmt=='vertical' else 'youtube','--json'],cwd=root,stdout=f,check=True)
 run(['python',str(root/'skills/ext/ffmpeg-skill/scripts/look.py'),str(out),'--tiles','3x2','--width','900','--output',str(O/f'contact_{fmt}.png')])
 qa['files'].append({'format':fmt,'file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'video_sha256':vh(out)});print(out.name,flush=True)
(O/'qa.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2));print(qa)
