"""Host-free Claude sketch preflight; no video or publication."""
import os,subprocess,shutil,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
subprocess.run(['git','submodule','update','--init','--depth','1','skills/ext/huashu-motion'],cwd=root,check=True)
chrome=shutil.which('google-chrome') or shutil.which('chromium')
if not chrome:
 from playwright.sync_api import sync_playwright
 with sync_playwright() as p: chrome=p.chromium.executable_path
subprocess.run(['node',str(root/'shorts/ai_bureaucracy/preflight_hostfree.mjs')],cwd=root,check=True,env=dict(os.environ,OM_CHROME=chrome))
out=root/'motion-output/ai_bureaucracy_v2'
assert len(list(out.glob('still_*.jpg')))==4
(out/'status.json').write_text(json.dumps({'status':'stills_only_not_video','frames':[1,12,25,47],'body_end':51.033,'no_upload':True,'full_render_requires_visual_review':True},indent=2))
