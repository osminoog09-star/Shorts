"""Original score and effects under exact approved Dima/Sveta narration."""
from pathlib import Path
import numpy as np, json, subprocess, wave,sys
R=Path(__file__).resolve().parent.parent; SR=48000
job=json.loads((R/'tts_job.json').read_text()); selected=job['lines']
if '--opening' in sys.argv:selected=[l for l in selected if l['chapter']==0]
if '--edited' in sys.argv:
 selected=[l for l in selected if l['id'] not in {'c03p07','c04p07','c05p07','c07p05','c09p00','c09p01','c09p02'}]
chunks=[];manifest=[];offset=0
for l in selected:
 p=R/'audio_verified'/(l['id']+'.mp3');m=p.with_suffix('.json')
 if not p.exists() or not m.exists():raise SystemExit('MISSING '+l['id'])
 meta=json.loads(m.read_text());assert meta['voice_id']==l['voice'] and meta['text']==l['text']
 a=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','1','-ar',str(SR),'-']),dtype=np.float32)
 
 # Editorial cut: omit single-source fresh Hera observation; retain DART context corroborated by NASA and ESA.
 if l['id']=='c08p00':
  start=meta['words'][2]['start'];a=a[int(start*SR):];meta=dict(meta,text=' '.join(w['w'] for w in meta['words'][2:]),editorial_trim_start=start,words=[dict(w,start=max(0,w['start']-start),end=max(0,w['end']-start)) for w in meta['words'][2:]])
 duration=len(a)/SR;manifest.append(dict(meta,start=offset,end=offset+duration));chunks.extend([a,np.zeros(int(SR*.14),np.float32)]);offset+=duration+.14
speech=np.concatenate(chunks);N=len(speech);t=np.arange(N,dtype=np.float32)/SR;music=np.zeros(N,np.float32)
# Original synth score, 96 BPM; four distinct chord sections. Deterministic; no external recordings.
progressions=[[48,55,60,63],[44,51,56,60],[51,58,63,67],[46,53,58,62]]
block=int(10*SR)
for start in range(0,N,block):
 n=min(block,N-start);tt=np.arange(n,dtype=np.float32)/SR;notes=progressions[(start//block)%4];env=np.minimum(tt/.5,1)*np.minimum((n/SR-tt)/1.2,1)
 for note in notes:
  hz=440*2**((note-69)/12);music[start:start+n]+=.004*env*(np.sin(2*np.pi*hz*tt)+.18*np.sin(2*np.pi*hz*2*tt))
 # Restrained bass pulse with long release.
 for beat in range(int(n/SR/.625)):
  q=int(beat*.625*SR);ln=min(n-q,int(.4*SR));z=np.arange(ln)/SR;hz=440*2**((notes[0]-12-69)/12)
  music[start+q:start+q+ln]+=.007*np.sin(2*np.pi*hz*z)*np.exp(-z*10)
# Smooth ducking under narration, no music pumping on individual syllables.
step=480;levels=np.array([np.sqrt(np.mean(speech[i:i+step]**2)) for i in range(0,N,step)])
for i in range(1,len(levels)):levels[i]=max(levels[i],levels[i-1]*.94)
duck=np.repeat(np.where(levels>.018,.35,.8),step)[:N];music*=duck
fx=np.zeros(N,np.float32);last=-1
for m in manifest:
 if m['chapter']!=last:
  q=int(m['start']*SR);n=min(int(.32*SR),N-q);u=np.arange(n)/SR
  fx[q:q+n]+=.022*np.sin(2*np.pi*(600*u-550*u*u))*np.exp(-u*12);last=m['chapter']
mix=speech+music+fx;mix=np.tanh(mix*.9)
name='M1lash_Opening_Dima_MIX' if '--opening' in sys.argv else 'M1lash_News_20261029_Dima_Sveta_MIX'
out=R/'out';out.mkdir(exist_ok=True)
raw=out/(name+'.wav')
with wave.open(str(raw),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((np.clip(mix,-1,1)*32767).astype('<i2').tobytes())
subprocess.run(['ffmpeg','-v','error','-y','-i',str(raw),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','libmp3lame','-b:a','192k',str(out/(name+'.mp3'))],check=True)
(out/(name+'_manifest.json')).write_text(json.dumps({'segments':manifest,'duration':len(mix)/SR,'music':'Original procedural score, no third-party recording','effects':'Original synthesized chapter accents','timing':'Actual decoded audio sample counts'},ensure_ascii=False,indent=2))
print(name,'seconds',len(mix)/SR)
