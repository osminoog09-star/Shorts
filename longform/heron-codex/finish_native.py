"""Assemble the existing horizontal render and newly rendered portrait scenes."""
import json,subprocess,wave
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parent;O=R/'out';O.mkdir(exist_ok=True);SR=44100
# Reuse the deterministic original score/speech mix without encoding old cropped Shorts.
exec((R/'compose.py').read_text().split('chunks=sorted')[0],{'__file__':str(R/'compose.py')})
S=json.loads((R/'timeline.json').read_text());base=sum(s['dur'] for s in S);M=json.loads((R/'native.json').read_text());tail=next(x for x in M if x['name']=='ending')
def read(p):
 with wave.open(str(p)) as w:return np.frombuffer(w.readframes(w.getnframes()),np.int16)
a=read(O/'mix.wav')[:round(base*SR)];b=read(R/'native_ending.wav');mix=O/'final_mix.wav'
with wave.open(str(mix),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(np.concatenate([a,b]).tobytes())
def encode(chunks,audio,out,duration):
 assert chunks
 file=O/(out.stem+'.concat');file.write_text(''.join("file '"+str(p.resolve())+"'\n" for p in chunks))
 # MJPEG-origin shards carry full range; explicitly convert to video range.
 subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(file),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-vf','scale=in_range=pc:out_range=tv,format=yuv420p','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-color_range','tv','-r','30','-c:a','aac','-b:a','160k','-af','loudnorm=I=-16:TP=-3:LRA=9','-t',str(duration),'-movflags','+faststart',str(out)],check=True)
old=sorted((R/'shards').glob('part_*.mp4'));assert len(old)==20
native=R/'native_shards'
encode(old+sorted(native.glob('native_ending_*.mp4')),mix,O/'heron_ancient_automation_ru.mp4',base+tail['duration'])
for m in M:
 if m['name']=='ending':continue
 encode(sorted(native.glob(f'native_{m["name"]}_*.mp4')),R/m['audio'],O/f'heron_short_{m["name"]}_ru.mp4',m['duration'])
ending=json.loads((R/'timeline-ending.json').read_text())
for x in ending:x.update(index=len(S),start=x['start']+base)
(R/'timeline.json').write_text(json.dumps(S+ending,ensure_ascii=False,indent=2))
print('Master',base+tail['duration'],'native Shorts',[(m['name'],m['duration']) for m in M if m['name']!='ending'])
