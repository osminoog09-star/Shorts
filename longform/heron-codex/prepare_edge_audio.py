"""Use completed shared Dmitry TTS; master tempo without changing pitch/voice."""
import json,math,subprocess,wave
from pathlib import Path
R=Path(__file__).resolve().parent;source=R.parents[1]/'media/tts/heron_codex';out=R/'audio';out.mkdir(exist_ok=True)
S=json.loads((R/'script.json').read_text());S[2]['model']='archive';S[2]['focus']='archive';items=[]
for i,s in enumerate(S):
 src=source/f's{i:02}.mp3';meta=source/f's{i:02}.json'
 if not src.exists() or not meta.exists():raise SystemExit(f'Missing shared TTS output: {src}')
 data=json.loads(meta.read_text())
 if data['text']!=s['text']:raise SystemExit('TTS text mismatch')
 dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(src)]))
 items.append((src,data,dur))
# Revision requested by Denis: slower narration; preserve the voice and pitch.
# 1.20 is about 14% slower than the rejected 1.3956 master.
tempo=1.20
cur=0;result=[]
for i,(s,(src,data,_)) in enumerate(zip(S,items)):
 dst=out/f'{i:02}.wav'
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-af',f'aresample=44100,atempo={tempo},loudnorm=I=-17:TP=-3:LRA=9','-ar','44100','-ac','1',str(dst)],check=True)
 with wave.open(str(dst)) as w:dur=w.getnframes()/w.getframerate()
 cues=[];words=data.get('words',[])
 for a in range(0,len(words),12):
  row=words[a:a+12];cues.append({'start':row[0]['start']/tempo,'end':row[-1]['end']/tempo,'text':' '.join(w['w'] for w in row)})
 d=math.ceil((dur+1.4)*30)/30;result.append({**s,'index':i,'start':cur,'speech':dur,'dur':d,'file':f'audio/{i:02}.wav','cues':cues});cur+=d
(R/'timeline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('Duration',cur,'tempo',tempo)
if not 600<=cur<=900:raise SystemExit(f'Duration {cur:.1f}s outside requested 10–15 min.')
