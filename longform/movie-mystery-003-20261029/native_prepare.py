from pathlib import Path
import argparse,concurrent.futures,json,os,subprocess
import cairosvg
R=Path(__file__).resolve().parent;B=R/'build';ap=argparse.ArgumentParser();ap.add_argument('--ids');a=ap.parse_args()
for p in (B/'host').glob('*.svg'):cairosvg.svg2png(url=str(p),write_to=str(p.with_suffix('.png')))
wanted={int(x)for x in a.ids.split(',')}if a.ids else None
paths=[p for p in B.glob('voice_*.mp3')if wanted is None or int(p.stem.split('_')[1])in wanted]
def align(p):
 out=p.with_suffix('.rhubarb.json')
 if out.exists():return
 wav=p.with_suffix('.wav');subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-ac','1','-ar','16000',str(wav)],check=True)
 subprocess.run([os.environ['RHUBARB'],'-q','-r','phonetic','-f','json','-o',str(out),str(wav)],check=True)
with concurrent.futures.ThreadPoolExecutor(3)as pool:list(pool.map(align,paths))
