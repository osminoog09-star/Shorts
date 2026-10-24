import json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'out';O.mkdir(exist_ok=True)
exec((R/'compose.py').read_text().split('chunks=sorted')[0],{'__file__':str(R/'compose.py')})
S=json.loads((R/'timeline.json').read_text());D=sum(x['dur'] for x in S)
def encode(parts,audio,out,dur):
 listing=O/(out.stem+'.concat');listing.write_text(''.join("file '"+str(p.resolve())+"'\n" for p in parts))
 subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-vf','scale=in_range=pc:out_range=tv,format=yuv420p','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p','-color_range','tv','-r','30','-c:a','aac','-b:a','160k','-af','loudnorm=I=-16:TP=-3:LRA=9','-t',str(dur),'-movflags','+faststart',str(out)],check=True)
parts=R/'v2_shards';main=sorted(parts.glob('main_*.mp4'));assert len(main)==32
encode(main,O/'mix.wav',O/'heron_ancient_automation_v2_ru.mp4',D)
for m in json.loads((R/'native.json').read_text()):
 if m['name']=='ending':continue
 chunk=sorted(parts.glob(m['name']+'_*.mp4'));assert len(chunk)==4
 encode(chunk,R/m['audio'],O/f'heron_short_{m["name"]}_v2_ru.mp4',m['duration'])
print('Revised final:',D)
