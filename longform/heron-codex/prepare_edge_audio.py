"""Use completed shared TTS job; never substitute another voice."""
import json,math,subprocess,wave
from pathlib import Path
R=Path(__file__).resolve().parent;source=R.parents[1]/'media/tts/heron_codex';out=R/'audio';out.mkdir(exist_ok=True)
S=json.loads((R/'script.json').read_text());cur=0;result=[]
for i,s in enumerate(S):
 src=source/f's{i:02}.mp3';meta=source/f's{i:02}.json';dst=out/f'{i:02}.wav'
 if not src.exists() or not meta.exists(): raise SystemExit(f'Missing shared TTS output: {src}')
 data=json.loads(meta.read_text())
 if data['text']!=s['text']:raise SystemExit('TTS text mismatch')
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-af','aresample=44100,loudnorm=I=-17:TP=-3:LRA=9','-ar','44100','-ac','1',str(dst)],check=True)
 with wave.open(str(dst)) as w:dur=w.getnframes()/w.getframerate()
 cues=[];words=data.get('words',[])
 for a in range(0,len(words),12):
  row=words[a:a+12];cues.append({'start':row[0]['start'],'end':row[-1]['end'],'text':' '.join(w['w'] for w in row)})
 d=math.ceil((dur+1.4)*30)/30;result.append({**s,'index':i,'start':cur,'speech':dur,'dur':d,'file':f'audio/{i:02}.wav','cues':cues});cur+=d
(R/'timeline.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));print('Duration',cur)
if not 480<=cur<=600:raise SystemExit(f'Duration {cur:.1f}s outside requested 8–10 min; adjust script/rate before rendering.')
