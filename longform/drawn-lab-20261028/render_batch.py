from pathlib import Path
import argparse,json,os,subprocess,shutil
from build_drawn import captions
R=Path(__file__).resolve().parent;B=R/'build';M=B/'masters';M.mkdir(exist_ok=True)
ap=argparse.ArgumentParser();ap.add_argument('--ids',required=True);ids={int(x)for x in ap.parse_args().ids.split(',')}
cli=Path(os.environ['HUASHU_ROOT'])/'cli/om.js'
def run(*a):subprocess.run([str(x)for x in a],check=True)
scenes=json.loads((B/'timeline.json').read_text())['scenes']
for i in [90,91,92]:scenes+=json.loads((B/f'short_{i}_timeline.json').read_text())['scenes']
for s in scenes:
 if s['id']not in ids:continue
 n=s['id'];folder=B/'native'/f'scene_{n:02d}';target=M/f'part_{n:02d}.mp4';dur=s['duration']+.18
 for cmd in [('check','--source'),('sound',),('render','--fps','30','--workers','4'),('qa',)]:run('node',cli,cmd[0],folder,*cmd[1:])
 mp4=sorted((folder/'out').glob('*.mp4'),key=lambda p:p.stat().st_mtime)[-1]
 run('ffmpeg','-xerror','-v','error','-y','-i',mp4,'-t',str(dur),'-c:v','copy','-af',f'afade=t=out:st={dur-.1}:d=0.1','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-map_metadata','-1','-movflags','+faststart',target)
 run('ffmpeg','-xerror','-v','error','-i',target,'-f','null','-')
 run('ffmpeg','-xerror','-v','error','-y','-ss','0.4','-i',target,'-vf','fps=1/6,scale=480:-1,tile=4x2','-frames:v','1',M/f'part_{n:02d}_contact.jpg')
 (M/f'part_{n:02d}.captions.json').write_text(json.dumps(captions(s),ensure_ascii=False))
 meta=json.loads((B/f'voice_{n:02d}.json').read_text())
 assert meta['voice_id']=='ru-RU-DmitryNeural'and meta['rate']=='+0%'and meta['text']==s['text']
 (M/f'part_{n:02d}.json').write_text(json.dumps(dict(id=n,chapter=s['chapter'],duration=dur,speaker=meta['speaker'],voice_id=meta['voice_id'],engine=meta['engine'],rate=meta['rate'],source_file=meta['source_file']),ensure_ascii=False,indent=2))
 print('VERIFIED',target,flush=True)
 if n==92:shutil.copy2(B/'movie_shots_private.json',M/'movie_shots_private.json')
