import json,subprocess,wave,math
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/'audio';out.mkdir(exist_ok=True)
script=json.loads((root/'script.json').read_text())
segments=[];cur=0
for i,s in enumerate(script):
 raw=out/f'{i:02}.raw.wav';wav=out/f'{i:02}.wav'
 if not wav.exists():
  if not raw.exists(): subprocess.run(['RHVoice-test','-p','aleksandr-hq','-o',str(raw)],input=s['text'].encode(),check=True,capture_output=True)
  with wave.open(str(raw)) as w: actual=len(w.readframes(min(w.getnframes(),raw.stat().st_size//2)))/(w.getframerate()*w.getsampwidth()*w.getnchannels())
  tempo=max(.8,min(1.5,actual/(len(s['text'].split())*60/170)))
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(raw),'-af',f'aresample=44100,atempo={tempo},loudnorm=I=-17:TP=-3:LRA=9','-ar','44100','-ac','1',str(wav)],check=True)
 with wave.open(str(wav)) as w:dur=w.getnframes()/w.getframerate()
 segments.append({**s,'index':i,'start':cur,'speech':dur,'dur':math.ceil((dur+1.4)*30)/30,'file':f'audio/{i:02}.wav'})
 cur+=segments[-1]['dur']
print('Total',cur,flush=True)
# Narration is original; pause length is fixed, no silent padding to reach target.
(root/'timeline.json').write_text(json.dumps(segments,ensure_ascii=False,indent=2))
