#!/usr/bin/env python3
"""Premiya episode adapter. Reuses movie_edit base, final, kinetic, manifest."""
import sys, os, subprocess as sp, json, math, wave
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
WORK=ROOT/'work/premiya'; WORK.mkdir(parents=True,exist_ok=True)
OUT=ROOT/'videos/m1lash_premiya_final_ru.mp4'
TTS=WORK/'voice'
def run(a,**kw):
    sp.run([str(v) for v in a],check=True,**kw)
def probe(p):
    return json.loads(sp.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(p)]))
# Every shot has explicit subject framing; source starts are real footage seconds.
PLANS=[ [('office',3,.39),('money',1,.50)],
        [('meeting',0,.39),('coffee',2,.29)],
        [('meeting',2,.60),('office',8,.77)],
        [('coffee',8,.30),('money',5,.50)],
        [('meeting',5,.60),('coffee',14,.75)],
        [('pizza',2,.50),('pizza',10,.50)],
        [('coffee',4,.30),('meeting',1,.60)],
        [('money',1,.50),('pizza',14,.50)] ]
SR=48000; speech=[]; words=[]; shots=[]; t=0; segments=[]
for i,plans in enumerate(PLANS):
    mp=TTS/f's{i:02}.mp3'; meta=json.loads((TTS/f's{i:02}.json').read_text())
    raw=sp.check_output(['ffmpeg','-v','error','-i',str(mp),'-f','f32le','-ac','1','-ar',str(SR),'-'])
    a=np.frombuffer(raw,np.float32).copy()
    # Trim only measured trailing silence after last word; preserve natural pauses.
    end=meta['words'][-1]['end']+.14
    a=a[:min(len(a),round(end*SR))]
    dur=math.ceil(len(a)/SR*30)/30
    a=np.pad(a,(0,round(dur*SR)-len(a)))
    speech.append(a)
    for w in meta['words']: words.append(dict(w=w['w'],start=t+w['start'],end=min(t+dur,t+w['end'])))
    # Split near punctuation/halfway, retaining all narration without time stretch.
    midpoint=dur*.51
    ns=round(midpoint*30); durations=[ns/30,dur-ns/30]
    for j,((name,start,cx),d) in enumerate(zip(plans,durations)):
        dest=WORK/f'shot_{i}_{j}.mp4'
        run(['ffmpeg','-v','error','-y','-ss',start,'-i',WORK/f'{name}.mp4','-t',d,
             '-vf','scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30',
             '-an','-c:v','libx264','-preset','fast','-crf','18',dest])
        segments.append(dest); shots.append((t if j==0 else t+durations[0],cx,.5))
    t+=dur
T=round(t*30)/30
run([sys.executable,ROOT/'tools/movie_edit/source_manifest.py',WORK/'source_list.txt',*segments])
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',WORK/'source_list.txt','-c','copy',WORK/'source.mp4'])
# Captions grouped into short phrase chunks. Each word retains TTS timing.
phr=[]; group=[]
for k,w in enumerate(words):
    group.append((w['w'].upper(),w['start']))
    stop=len(group)>=3 or len(' '.join(x[0] for x in group))>21 or k==len(words)-1
    if stop:
        e=min(T,(words[k+1]['start']-.025) if k+1<len(words) else T)
        phr.append((None,[],('ital','gold' if any(s in ' '.join(x[0] for x in group) for s in ['ПРЕМИ','СЕМЬ','ОПЫТ','ПИЦЦ','ИПОТЕК']) else 'white'),group,e));group=[]
edit=f"SRC = {str(WORK/'source.mp4')!r}\nPIC=(0,0,1920,1080)\nFPS=30\nW,H=1080,1920\nSEGMENTS=[(0,{T})]\nSHOTS={shots!r}\nPHRASES={phr!r}\nLETTERS={{}}\nPUNCH={[s[0] for s in shots[::2]]!r}\nSHAKE=[]\nFLASH=[]\ndef edit_time(t): return t\ndef total(): return {T}\ndef shot_at(t):\n cur=SHOTS[0]\n for s in SHOTS:\n  if t>=s[0]:cur=s\n return cur,next((s[0] for s in SHOTS if s[0]>t),{T})\n"
(WORK/'edit.py').write_text(edit)
# Invoke unchanged common passes with the episode configuration first on sys.path.
launcher="import sys,runpy; sys.path[:0]=[sys.argv.pop(1),sys.argv.pop(1)]; p=sys.argv.pop(1); sys.argv[0]=p; runpy.run_path(p,run_name='__main__')"
env=dict(os.environ,MOVIE_EDIT_FONT_DIR=str(ROOT/'studio/public/fonts'),MOVIE_EDIT_CAPTION_Y='1430')
run([sys.executable,'-c',launcher,WORK,ROOT/'tools/movie_edit',ROOT/'tools/movie_edit/base.py',WORK/'base.mp4'],env=env)
run([sys.executable,'-c',launcher,WORK,ROOT/'tools/movie_edit',ROOT/'tools/movie_edit/final.py',WORK/'base.mp4',WORK/'captioned.mp4'],env=env)
# Original light funk-like bed made from oscillators and filtered noise, no samples.
voice=np.concatenate(speech);N=len(voice);tt=np.arange(N)/SR;rng=np.random.default_rng(20261027)
music=np.zeros(N); beat=60/112
for b in range(int(T/beat)+1):
    st=round(b*beat*SR);n=min(round(.18*SR),N-st)
    if n<=0:continue
    z=np.arange(n)/SR
    music[st:st+n]+=.045*np.sin(2*np.pi*(58*z+4*(1-np.exp(-z*30))))*np.exp(-z*22)
    if b%2:music[st:st+n]+=.018*rng.standard_normal(n)*np.exp(-z*55)
    note=[110,110,130.81,98][(b//4)%4]
    n=min(round(.28*SR),N-st);z=np.arange(n)/SR
    music[st:st+n]+=.017*np.sin(2*np.pi*note*z)*np.exp(-z*12)
# Duck bed for joke after family and mortgage payoff.
for i in [3,7]:
    start=sum(len(x) for x in speech[:i]);end=start+len(speech[i]);music[start:end]*=.25
mix=voice+music
run(['ffmpeg','-v','error','-y','-f','f32le','-ar',SR,'-ac','1','-i','-','-af','loudnorm=I=-15:TP=-1.5:LRA=7','-ar',SR,'-c:a','pcm_s16le',WORK/'mix.wav'],input=mix.astype('float32').tobytes())
run(['ffmpeg','-v','error','-y','-i',WORK/'captioned.mp4','-i',WORK/'mix.wav','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-ac','2','-ar',SR,'-b:a','192k','-t',T,WORK/'story.mp4'])
# Keep approved moving host and exact Liam recording; replace unconfirmed NCS music.
# Cover obsolete music attribution only in our derivative, not the approved source.
run(['ffmpeg','-v','error','-y','-i',ROOT/'videos/m1lash_outro_short_ru.mp4','-ss','20','-i',ROOT/'media/tts/host_demo/eleven.mp3',
     '-map','0:v','-map','1:a','-vf','drawbox=x=0:y=1680:w=1080:h=160:color=0x070912:t=fill',
     '-af','loudnorm=I=-15:TP=-1.5:LRA=7,apad','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',
     '-c:a','aac','-ac','2','-ar',SR,'-b:a','192k','-t','5.8',WORK/'outro.mp4'])
run([sys.executable,ROOT/'tools/movie_edit/source_manifest.py',WORK/'final_list.txt',WORK/'story.mp4',WORK/'outro.mp4'])
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',WORK/'final_list.txt','-c','copy','-movflags','+faststart',OUT])
run(['ffmpeg','-v','error','-i',OUT,'-f','null','-'])
(WORK/'timeline.json').write_text(json.dumps({'story_duration':T,'words':words,'shots':shots},ensure_ascii=False,indent=2))
(WORK/'probe.json').write_text(json.dumps(probe(OUT),indent=2))
print('FINAL',OUT,'STORY',T,flush=True)
