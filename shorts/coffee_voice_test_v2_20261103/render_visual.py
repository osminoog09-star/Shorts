"""Deterministic HTML/SVG graphics only; owner's voice never leaves local runtime."""
from pathlib import Path
import os,json,subprocess,math,shutil
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2];P=Path(__file__).resolve().parent;cfg=json.loads((ROOT/os.environ['M1LASH_JOB_PATH']).read_text());mode=cfg.get('mode','stills');W=ROOT/'motion-output/coffee_voice_test_v2';W.mkdir(parents=True,exist_ok=True)
if (P/'timeline.json').exists():d=json.loads((P/'timeline.json').read_text())
else:
 s=json.loads((P/'story.json').read_text());caps=[]
 for i,line in enumerate(s['lines']):
  words=line.split();groups=[words[j:j+3] for j in range(0,len(words),3)]
  for j,g in enumerate(groups):caps.append({'start':i*6+j*6/len(groups),'end':i*6+(j+1)*6/len(groups),'words':g})
 d={'total':36,'cuts':[0,6,12,18,24,30,36],'caps':caps,'headlines':s['headlines'],'sources':[]}
layout=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path=os.environ.get('M1LASH_CHROME') or None,args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files']);page=b.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1);page.goto((P/'film.html').as_uri());page.evaluate('() => document.fonts.ready');page.evaluate('d=>window.setTimeline(d)',d)
 for cap in d['caps']:
  row=page.evaluate('''t=>{window.seek(t);let h=document.querySelector('#title'),c=document.querySelector('#cap');return {title:h.textContent,cap:c.textContent,titleWidth:h.scrollWidth,titleMax:h.clientWidth,titleBottom:h.getBoundingClientRect().bottom,capBottom:c.getBoundingClientRect().bottom,capWidth:c.scrollWidth,capMax:c.clientWidth}}''',(cap['start']+cap['end'])/2);layout.append(row)
  if row['titleWidth']>row['titleMax']+2 or row['titleBottom']>405 or row['capBottom']>1440 or row['capWidth']>row['capMax']+2:raise RuntimeError('Layout NO-GO '+str(row))
 (W/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2))
 images=[]
 for i,at in enumerate([0,7.95,9.2,10.6,14.3,18.3,19.3,20.6,23,25,29.91,30.15,30.5,31,36,37.7]):
  page.evaluate('t=>window.seek(t)',at);f=W/f'still_{i+1:02d}.jpg';page.screenshot(path=str(f),type='jpeg',quality=92);images.append(f)
 from PIL import Image,ImageDraw
 sheet=Image.new('RGB',(1200,2208),'#21313c')
 for i,f in enumerate(images):
  im=Image.open(f);im.thumbnail((300,533));sheet.paste(im,(i%4*300,i//4*552+19));ImageDraw.Draw(sheet).text((i%4*300+5,i//4*552+2),str(i+1),fill='white')
 sheet.save(W/'contact.jpg',quality=88)
 if mode in ('pilot','full'):
  start=d['cuts'][5] if mode=='pilot' else 0;duration=d['total']-start
  out=W/('coffee_v2_pilot.mp4' if mode=='pilot' else 'coffee_voice_test_visual_v2.mp4');proc=subprocess.Popen([os.environ.get('M1LASH_FFMPEG','ffmpeg'),'-v','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','-','-vf','scale=in_range=pc:out_range=tv:out_color_matrix=bt709','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-r','30','-colorspace','bt709','-color_trc','bt709','-color_primaries','bt709',str(out)],stdin=subprocess.PIPE)
  for frame in range(math.ceil(duration*30)):
   page.evaluate('t=>window.seek(t)',start+frame/30);proc.stdin.write(page.screenshot(type='jpeg',quality=93))
   if frame%150==0:print('frame',frame,flush=True)
  proc.stdin.close();assert proc.wait()==0
 b.close()
qa=ROOT/'reports/research/qa/coffee_voice_test_v2';qa.mkdir(parents=True,exist_ok=True);selected=[]
for f in W.glob('*.jpg'):
 target=qa/(mode+'_'+f.name);shutil.copy2(f,target);selected.append(target)
subprocess.run(['git','config','user.name','m1lash-render-bot'],check=True);subprocess.run(['git','config','user.email','m1lash-render-bot@users.noreply.github.com'],check=True);subprocess.run(['git','add','--sparse','--']+[str(p.relative_to(ROOT)) for p in selected],check=True);subprocess.run(['git','commit','-m','qa: coffee V2 '+mode+' actual frames; private speech excluded'],check=True)
for _ in range(4):
 subprocess.run(['git','pull','--rebase','origin','main'],check=True)
 if subprocess.run(['git','push','origin','HEAD:main']).returncode==0:break
else:raise RuntimeError('QA evidence not saved')
print('VISUAL_DONE',mode,flush=True)
