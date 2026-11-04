"""Silent HTML/Playwright evidence. Never reads or generates any private voice."""
from pathlib import Path
import os,json,math,subprocess,shutil
from playwright.sync_api import sync_playwright
P=Path(__file__).resolve().parent;R=P.parents[1];cfg=json.loads((R/os.environ['M1LASH_JOB_PATH']).read_text());d=json.loads((P/'timeline.json').read_text());W=R/'motion-output/coffee_v8';W.mkdir(parents=True,exist_ok=True);mode=cfg.get('mode','stills')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files']);page=b.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto((P/'film.html').as_uri());page.evaluate('() => document.fonts.ready');page.evaluate('d=>setTimeline(d)',d)
 layout=[]
 for c in d['caps']:
  row=page.evaluate('''t=>{seek(t);let c=document.querySelector('#cap'),r=c.getBoundingClientRect();return {text:c.textContent,x:r.x,right:r.right,bottom:r.bottom,scroll:c.scrollWidth,width:c.clientWidth}}''',(c['start']+c['end'])/2);layout.append(row)
  if row['right']>940 or row['bottom']>1450 or row['scroll']>row['width']+2:raise RuntimeError('Caption layout FAIL '+str(row))
 (W/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2));assert not errors,errors
 times=[s['start']+min(2.3,(s['end']-s['start'])*.55) for s in d['shots']]
 # Plus the real contact/reaction phases, including first second and final kettle.
 times += [.05,.5,1.1,d['shots'][3]['start']+.6,d['shots'][3]['start']+.85,d['shots'][3]['start']+4.5,d['shots'][4]['start']+.45,d['shots'][4]['start']+1.1,d['shots'][5]['start']+1.5,d['shots'][5]['start']+3.5]
 for i,t in enumerate(times):page.evaluate('t=>seek(t)',t);page.screenshot(path=str(W/f'still_{i:02}.jpg'),type='jpeg',quality=91)
 subprocess.run(['ffmpeg','-v','error','-y','-framerate','1','-i',str(W/'still_%02d.jpg'),'-vf','scale=270:480,tile=4x4','-frames:v','1',str(W/'contact.jpg')],check=True)
 if mode in ('pilot','full'):
  start=d['shots'][4]['start'] if mode=='pilot' else 0;duration=min(7.0,d['total']-start) if mode=='pilot' else d['total'];out=W/(mode+'.mp4');proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','-','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-r','30','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709',str(out)],stdin=subprocess.PIPE)
  for i in range(math.ceil(duration*30)):
   page.evaluate('t=>seek(t)',start+i/30);proc.stdin.write(page.screenshot(type='jpeg',quality=94))
   if i%150==0:print('render',i,flush=True)
  proc.stdin.close();assert proc.wait()==0;subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-'],check=True)
 assert not errors,errors;b.close()
# Publish only silent visual evidence through the existing repository renderer.
Q=R/'reports/research/qa/coffee_v8';Q.mkdir(parents=True,exist_ok=True)
for f in W.glob('*.jpg'):shutil.copy2(f,Q/f.name)
shutil.copy2(W/'layout.json',Q/'layout.json')
(Q/'run.json').write_text(json.dumps({'run_id':os.environ.get('GITHUB_RUN_ID'),'mode':mode,'silent':True,'body_seconds':d['total'],'owner_review':'pending'}))
subprocess.run(['git','config','user.name','m1lash-render-bot'],check=True);subprocess.run(['git','config','user.email','m1lash-render-bot@users.noreply.github.com'],check=True);subprocess.run(['git','add','--sparse','reports/research/qa/coffee_v8'],check=True)
if subprocess.run(['git','diff','--cached','--quiet']).returncode:
 subprocess.run(['git','commit','-m','qa: coffee V8 silent '+mode+' real frames'],check=True)
 for _ in range(3):
  subprocess.run(['git','pull','--rebase','origin','main'],check=True)
  if subprocess.run(['git','push','origin','HEAD:main']).returncode==0:break
 else:raise RuntimeError('Could not save silent visual QA')
print('HTML_VISUAL_DONE',mode,flush=True)
