import json,subprocess,wave,math,struct
from pathlib import Path
from episodes import EPISODES
B=Path(__file__).resolve().parent; ROOT=B.parents[1]
def run(a):subprocess.run(a,check=True)
def duration(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],text=True).strip())
def prepare(e):
 out=B/'work'/e['id'];out.mkdir(parents=True,exist_ok=True)
 timeline=[];at=0;parts=[]
 for i,line in enumerate(e['lines']):
  indices=e.get('scene_indices',list(range(len(e['lines']))));stem=e.get('tts_ids',[e['id']+'_'+str(n) for n in indices])[i];mp=ROOT/'media/tts/research_codex'/f'{stem}.mp3';meta=mp.with_suffix('.json')
  if stem is None:
   wav=out/f'{i}.wav';d=float(e['silent_durations'][i]);run(['ffmpeg','-v','error','-y','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t',str(d),str(wav)]);timeline.append({'start':at,'end':at+d,'words':[],'text':'','silent':True});at+=d;parts.append(wav);continue
  assert mp.exists() and meta.exists(),f'Missing TTS: {mp}'
  m=json.loads(meta.read_text());assert m['text']==line[2]
  wav=out/f'{i}.wav';run(['ffmpeg','-v','error','-y','-i',str(mp),'-af','apad=pad_dur=0.12','-ar','48000','-ac','1',str(wav)])
  d=duration(wav);timeline.append({'start':at,'end':at+d,'words':m.get('words',[]),'text':line[2]});at+=d;parts.append(wav)
 (out/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2))
 (out/'parts.txt').write_text(''.join("file '"+str(p)+"'\n" for p in parts))
 run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(out/'parts.txt'),'-c:a','pcm_s16le',str(out/'voice.wav')])
 # Body is full-screen illustration; host appears only in the unchanged approved outro.
 (out/'visemes.json').write_text(json.dumps({'fps':30,'visemes':'X'*(int(at*30)+2),'body_host':False,'outro':'approved original Rhubarb visemes'}))
 # Original procedural bed, soft low notes plus deliberate scene-change clicks.
 rate=48000; total=int(at*rate);seq=[146.832,174.614,130.813,164.814];starts=[s['start'] for s in timeline]
 silent=[s for s in timeline if s.get('silent')]
 for seg in silent:starts += [seg['start']+k*.65 for k in range(1,8) if seg['start']+k*.65<seg['end']]
 vol="0.65"
 if silent:vol="if(between(t,%.6f,%.6f),2.5,0.65)"%(silent[0]['start'],silent[0]['end'])
 mixfilter="[0:a]loudnorm=I=-16:TP=-2:LRA=7[v];[1:a]volume='%s':eval=frame[m];[v][m]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=false[a]"%vol
 with wave.open(str(out/'bed.wav'),'wb') as w:
  w.setparams((1,2,rate,0,'NONE','not compressed'));block=[]
  for n in range(total):
   t=n/rate;note=seq[int(t/3)%4];beat=t%(.48 if e['style']=='S6-D2' else .65)
   v=.018*math.sin(2*math.pi*note*t)+.011*math.sin(2*math.pi*note*1.5*t)
   v+=.024*math.exp(-beat*25)*math.sin(2*math.pi*note*2*t)
   for st in starts:
    dt=t-st
    if 0<=dt<.12:v+=.055*math.sin(2*math.pi*(700+dt*2000)*dt)*math.exp(-dt*35)
   v*=min(1,t/.1,max(0,(at-t)/.2));block.append(struct.pack('<h',int(max(-1,min(1,v))*32767)))
   if len(block)>=12000:w.writeframes(b''.join(block));block=[]
  if block:w.writeframes(b''.join(block))
 run(['ffmpeg','-v','error','-y','-i',str(out/'voice.wav'),'-i',str(out/'bed.wav'),'-filter_complex',mixfilter,'-map','[a]','-ar','48000','-ac','2','-c:a','aac','-b:a','192k','-movflags','+faststart',str(out/'mix.m4a')])
 duration(out/'mix.m4a')
 print(json.dumps({'id':e['id'],'body_seconds':at},ensure_ascii=False))
if __name__=='__main__':
 import sys
 for e in EPISODES:
  if len(sys.argv)<2 or e['id']==sys.argv[1]:prepare(e)
