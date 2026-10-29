from pathlib import Path
import subprocess,os
from concurrent.futures import ThreadPoolExecutor
r=Path(__file__).resolve().parent.parent
(r/'out/motion_chunks').mkdir(exist_ok=True)
def run(i):
 with (r/'out/motion_chunks'/f'log_{i}.txt').open('w') as f:subprocess.run(['node','tools/render_raw.cjs',str(i)],cwd=r,stdout=f,stderr=subprocess.STDOUT,check=True)
 print('DONE',i,flush=True)
with ThreadPoolExecutor(max_workers=8) as e:list(e.map(run,range(8)))
playlist=r/'out/motion_chunks/playlist.txt';playlist.write_text(''.join(f"file '{(r/'out/motion_chunks'/f'part_{i}.mp4').resolve()}'\n" for i in range(8)))
print('COMPRESSING FINAL',flush=True)
subprocess.run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i',str(playlist),'-i',str(r.parent/'input/original_audio.m4a'),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','veryfast','-crf','18','-threads','8','-c:a','copy','-shortest','-movflags','+faststart',str(r/'out/M1lash_News_V2_Quality_26m50.mp4')],check=True)
print('FINAL MOTION COMPLETE',flush=True)
