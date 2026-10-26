"""Deterministic assembly; synthetic original bed, approved existing finale audio."""
import json, subprocess, wave, math
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parent; R=B.parents[1]; W=B/'work'; V=R/'videos';V.mkdir(exist_ok=True)
j=json.load(open(B/'script.json')); SR=48000
def run(args):
 r=subprocess.run(['ffmpeg','-v','error','-y',*map(str,args)],check=True,stderr=subprocess.PIPE,text=True)
 if r.stderr.strip():raise RuntimeError(r.stderr)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))
def cat(paths,dest):
 f=W/(dest.stem+'.concat');f.write_text('\n'.join("file '"+str(p.resolve()).replace("'","'\\''")+"'" for p in paths))
 run(['-f','concat','-safe','0','-i',f,'-c','copy',dest])
def read_audio(p):
 return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-f','f32le','-ac','1','-ar',str(SR),'-']),dtype='<f4').copy()
def wav(p,x):
 with wave.open(str(p),'wb') as f:f.setparams((1,2,SR,0,'NONE','not compressed'));f.writeframes((np.clip(x,-.99,.99)*32767).astype('<i2').tobytes())
def original_bed(n,starts):
 # Quiet original plucked triads, no sampled commercial recording or generated song.
 out=np.zeros(n,np.float32)
 chords=[(130.8128,164.8138,195.9977),(110,146.8324,174.6141),(97.9989,130.8128,164.8138),(123.4708,146.8324,195.9977)]
 for beat in np.arange(0,n/SR,60/84):
  i=int(beat*SR);length=min(int(1.1*SR),n-i);t=np.arange(length)/SR;freq=chords[int(beat/8)%4][int(beat/(60/84))%3]
  tone=(np.sin(2*np.pi*freq*t)+.23*np.sin(2*np.pi*2*freq*t))*(1-np.exp(-t*60))*np.exp(-t*6)
  out[i:i+length]+=(.013*tone).astype(np.float32)
 rng=np.random.default_rng(20261026)
 for sec in starts:
  i=int(sec*SR);length=min(int(.16*SR),n-i)
  if length>0:
   t=np.arange(length)/SR;noise=rng.normal(0,1,length);noise=np.convolve(noise,np.ones(6)/6,'same')
   out[i:i+length]+=(noise*np.sin(np.pi*t/.16)**2*.018).astype(np.float32)
 return out
def make(kind,scenes,ending):
 paths=[];voices=[];timeline=[];offset=0
 for s in scenes:
  d=W/s['id'];meta=json.load(open(d/'scene.json'));p=d/'silent.mp4';assert p.exists(),p
  dur=meta['duration'];a=read_audio(d/'aligned.wav');expected=round(dur*SR)
  a=np.pad(a,(0,max(0,expected-len(a))))[:expected];voices.append(a);paths.append(p)
  timeline.append({'id':s['id'],'start':round(offset,3),'duration':dur,'headline':s['headline'],'label':s['label']});offset+=dur
 body=np.concatenate(voices);music=original_bed(len(body),[r['start'] for r in timeline]);mix=body+music
 outro=read_audio(R/'videos/m1lash_outro_short_ru.mp4');edur=float(probe(ending)['format']['duration']);n=round(edur*SR);outro=np.pad(outro,(0,max(0,n-len(outro))))[:n]
 # Body and approved finale retain their own levels; no loudness correction per word.
 mix=np.concatenate([mix,outro]);wav(W/(kind+'_mix.wav'),mix)
 paths.append(ending);silent=W/(kind+'_silent.mp4');cat(paths,silent)
 final=V/('ai_news_20261026_'+kind+'_ru.mp4')
 run(['-i',silent,'-i',W/(kind+'_mix.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-ac','2','-movflags','+faststart','-shortest',final])
 result={'file':str(final.relative_to(R)),'seconds':float(probe(final)['format']['duration']),'bytes':final.stat().st_size,'body_seconds':offset,'timeline':timeline,'ending_seconds':edur,'style':'S2-D25'}
 (B/(kind+'_timeline.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(json.dumps(result|{'timeline':len(timeline)},ensure_ascii=False),flush=True)
if __name__=='__main__':
 make('full',j['scenes'],W/'ending_landscape.mp4')
 # Re-encode the approved vertical finale to exactly match scene video parameters.
 outro=W/'ending_vertical.mp4';run(['-i',R/'videos/m1lash_outro_short_ru.mp4','-an','-r','30','-c:v','libx264','-threads','2','-preset','fast','-crf','22','-pix_fmt','yuv420p',outro])
 make('short',j['short'],outro)
