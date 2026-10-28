import concurrent.futures,json,os,subprocess
from pathlib import Path
import cairosvg
ROOT=Path(__file__).resolve().parent;B=ROOT/'build'
for p in (B/'host').glob('*.svg'):cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))
rhubarb=os.environ['RHUBARB']
def align(p):
 wav=p.with_suffix('.wav');out=p.with_suffix('.rhubarb.json')
 subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-ac','1','-ar','16000',str(wav)],check=True)
 subprocess.run([rhubarb,'-q','-r','phonetic','-f','json','-o',str(out),str(wav)],check=True)
 data=json.loads(out.read_text());v=['X']*(int(data['metadata']['duration']*30)+30)
 for c in data['mouthCues']:
  for f in range(int(c['start']*30),min(len(v),int(c['end']*30)+1)):v[f]=c['value']
 p.with_suffix('.lipsync.json').write_text(json.dumps(dict(fps=30,visemes=''.join(v),engine='rhubarb-1.13.0',recognizer='phonetic')))
with concurrent.futures.ThreadPoolExecutor(2) as pool:list(pool.map(align,sorted(B.glob('voice_*.mp3'))))
data=json.loads((B/'timeline.json').read_text())
if data['duration']<1260:raise RuntimeError('NO-GO: narration shorter than 21 minutes. Revise content, never stretch.')
print('Measured runtime',data['duration'])
