from pathlib import Path
import argparse,json,os,subprocess
R=Path(__file__).resolve().parent;B=R/'build';ap=argparse.ArgumentParser();ap.add_argument('--ids',required=True);a=ap.parse_args();wanted={int(x)for x in a.ids.split(',')};cli=Path(os.environ['HUASHU_ROOT'])/'cli/om.js'
def run(*args):subprocess.run([str(x)for x in args],check=True)
scenes=json.loads((B/'timeline.json').read_text())['scenes']+json.loads((B/'short_timeline.json').read_text())['scenes']
out=B/'masters';out.mkdir(exist_ok=True)
for s in scenes:
 if s['id'] not in wanted:continue
 folder=B/'native'/('short'if s['id']==90 else f"chapter_{s['id']:02d}")
 run('node',cli,'check',folder,'--source')
 run('node',cli,'sound',folder)
 run('node',cli,'render',folder,'--fps','30','--workers','4','--verbose')
 run('node',cli,'qa',folder)
 mp4=sorted((folder/'out').glob('*.mp4'),key=lambda p:p.stat().st_mtime)[-1]
 target=out/('Short_RU.mp4'if s['id']==90 else f"part_{s['id']:02d}.mp4")
 dur=s['duration']+.18
 # Remove any bar-rounded music tail while retaining every spoken syllable.
 run('ffmpeg','-v','error','-y','-i',mp4,'-t',str(dur),'-c:v','copy','-af',f'afade=t=out:st={dur-.1}:d=0.1','-c:a','aac','-b:a','160k','-ar','48000','-ac','2','-movflags','+faststart',target)
 run('ffmpeg','-v','error','-i',target,'-f','null','-')
 contact=out/(target.stem+'_contact.jpg')
 run('ffmpeg','-v','error','-y','-ss','.4','-i',target,'-vf','fps=1/6,scale=480:-1,tile=4x2','-frames:v','1',contact)
 (out/f"part_{s['id']:02d}.json").write_text(json.dumps(dict(scene_id=s['id'],chapter=s['chapter'],duration=dur,voice='ru-RU-DmitryNeural',rate='+0%',engine='native huashu-motion 0.3.1',file=target.name),ensure_ascii=False,indent=2))
 print('VERIFIED',target,flush=True)
