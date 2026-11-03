"""Silent graphics only. No owner's voice, reference or embeddings on runner."""
import json,os,math,subprocess,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent
cfg=json.loads((ROOT/os.environ['M1LASH_JOB_PATH']).read_text());mode=cfg.get('mode','stills')
W=ROOT/'motion-output/coffee_voice_test';W.mkdir(parents=True,exist_ok=True)
if (P/'timeline.json').exists():d=json.loads((P/'timeline.json').read_text())
else:
 f=json.loads((P/'story.json').read_text());caps=[]
 for i,line in enumerate(f['lines']):
  words=line.split();groups=[words[j:j+4] for j in range(0,len(words),4)]
  for j,gr in enumerate(groups):caps.append({'start':i*6+j*6/len(groups),'end':i*6+(j+1)*6/len(groups),'words':gr})
 d={'total':36,'cuts':[0,6,12,18,24,30,36],'caps':caps,'theme':'coffee','headlines':f['headlines'],'sources':[],'label':'СКЕТЧ'}
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.environ.get('M1LASH_CHROME') or None,args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
 page=b.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1)
 page.goto((P/'film.html').as_uri());page.evaluate('() => document.fonts.ready');page.evaluate('d=>window.setTimeline(d)',d)
 for cap in d['caps']:
  row=page.evaluate('''t=>{window.seek(t);let h=document.querySelector('#title'),c=document.querySelector('#cap');return {titleWidth:h.scrollWidth,titleMax:h.clientWidth,titleBottom:h.getBoundingClientRect().bottom,capBottom:c.getBoundingClientRect().bottom,capWidth:c.scrollWidth,capMax:c.clientWidth}}''',(cap['start']+cap['end'])/2)
  if row['titleWidth']>row['titleMax']+2 or row['titleBottom']>450 or row['capBottom']>1440 or row['capWidth']>row['capMax']+2:raise RuntimeError('Layout NO-GO '+str(row))
 images=[]
 for i in range(6):
  at=.6 if i==0 else (d['cuts'][i]+d['cuts'][i+1])/2
  page.evaluate('t=>window.seek(t)',at);out=W/f'still_{i+1:02d}.jpg';page.screenshot(path=str(out),type='jpeg',quality=90);images.append(out)
 from PIL import Image,ImageDraw
 sheet=Image.new('RGB',(900,1104),'#20303a')
 for i,im in enumerate(images):
  z=Image.open(im);z.thumbnail((300,533));sheet.paste(z,(i%3*300,i//3*552+19));ImageDraw.Draw(sheet).text((i%3*300+5,i//3*552+2),str(i+1),fill='white')
 sheet.save(W/'contact.jpg',quality=85)
 if mode=='full':
  out=ROOT/'videos/coffee_voice_test_visual_v1.mp4';out.parent.mkdir(exist_ok=True)
  proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','-','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-r','30',str(out)],stdin=subprocess.PIPE)
  for i in range(math.ceil(d['total']*30)):
   page.evaluate('t=>window.seek(t)',i/30);proc.stdin.write(page.screenshot(type='jpeg',quality=92))
   if i%150==0:print('frame',i,flush=True)
  proc.stdin.close();assert proc.wait()==0;shutil.copy2(out,W/out.name)
 b.close()
qa=ROOT/'reports/research/qa/coffee_voice_test';qa.mkdir(parents=True,exist_ok=True)
selected=[]
for p in W.glob('*.jpg'):
 target=qa/(mode+'_'+p.name);shutil.copy2(p,target);selected.append(target)
if mode=='full':selected.append(out)
subprocess.run(['git','config','user.name','m1lash-render-bot'],check=True);subprocess.run(['git','config','user.email','m1lash-render-bot@users.noreply.github.com'],check=True)
subprocess.run(['git','add','--']+[str(p.relative_to(ROOT)) for p in selected],check=True)
subprocess.run(['git','commit','-m','qa: save '+mode+' silent drawn coffee visuals; no owner voice'],check=True)
for _ in range(4):
 subprocess.run(['git','pull','--rebase','origin','main'],check=True)
 if subprocess.run(['git','push','origin','HEAD:main']).returncode==0:break
else:raise RuntimeError('Evidence not saved')
