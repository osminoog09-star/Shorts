from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent.parent
(R/'out/chunks').mkdir(exist_ok=True)
def run(i):
 with (R/'out/chunks'/f'part_{i}.log').open('w') as f:
  subprocess.run(['node','tools/render_full.cjs',str(i)],cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('finished',i,flush=True)
with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(run,range(6)))
playlist=R/'out/chunks/list.txt';playlist.write_text(''.join(f"file '{(R/'out/chunks'/f'part_{i}.mp4').resolve()}'\n" for i in range(6)))
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(playlist),'-i',str(R/'out/M1lash_News_20261029_Dima_Sveta_MIX.mp3'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(R/'out/M1lash_News_DIMA_SVETA_REVIEW.mp4')],check=True)
print('FULL RENDER COMPLETE',flush=True)
