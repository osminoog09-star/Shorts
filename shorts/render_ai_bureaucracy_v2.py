"""Render existing Claude sketch without host, then append approved outro; never publish."""
import os,subprocess,shutil,json,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run(['git','submodule','update','--init','--depth','1','skills/ext/huashu-motion'],cwd=root,check=True)
chrome=shutil.which('google-chrome') or shutil.which('chromium')
if not chrome:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as p:chrome=p.chromium.executable_path
subprocess.run(['node',str(root/'shorts/ai_bureaucracy/preflight_hostfree.mjs'),'--render'],cwd=root,check=True,env=dict(os.environ,OM_CHROME=chrome))
frames=root/'motion-output/ai_bureaucracy_v2/frames'
body=root/'motion-output/ai_bureaucracy_v2/body.mp4'
subprocess.run(['ffmpeg','-v','error','-y','-framerate','30','-i',str(frames/'%05d.jpg'),'-i',str(root/'videos/ai_bureaucracy_claude_ru.mp4'),'-map','0:v','-map','1:a','-t','51.033333','-c:v','libx264','-threads','2','-preset','fast','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k',str(body)],check=True)
out=root/'videos/ai_bureaucracy_claude_v2.mp4'
subprocess.run([sys.executable,str(root/'tools/assemble_with_outro.py'),str(body),'-o',str(out),'--audio-bitrate','320k','--preset','fast'],check=True)
qa=root/'motion-output/ai_bureaucracy_v2'
with (qa/'check.json').open('w') as f:subprocess.run([sys.executable,str(root/'skills/ext/ffmpeg-skill/scripts/check.py'),str(out),'--platform','shorts','--json'],stdout=f,check=True)
subprocess.run([sys.executable,str(root/'skills/ext/ffmpeg-skill/scripts/look.py'),str(out),'--tiles','3x2','-o',str(qa/'final_look.jpg')],check=True)
shutil.copyfile(out,qa/out.name)
shutil.copyfile(str(out)+'.qa.json',qa/'assembly.json')
shutil.rmtree(frames)
body.unlink(missing_ok=True)
