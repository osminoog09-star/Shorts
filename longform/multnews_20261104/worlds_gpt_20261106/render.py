#!/usr/bin/env python3
"""Original M1lash four-world storyboard renderer, HTML+SVG+Playwright only; SILENT."""
import asyncio, json, hashlib, subprocess, sys
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent
SCENES=('park','home','pando','labor')
TIMES=(1,3.5,5.3,7.6,10.3,14.5)
async def run(phase):
 async with async_playwright() as pl:
  browser=await pl.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content((ROOT/'worlds.html').read_text(),wait_until='load')
  for scene in SCENES:
   out=ROOT/scene;out.mkdir(exist_ok=True)
   if phase in ('stills','all'):
    for i,t in enumerate(TIMES):
     await page.evaluate('([t,s])=>window.frame(t,s)',[t,scene])
     await page.screenshot(path=str(out/f'still_{i:02d}.png'))
    print('STILLS',scene,len(TIMES),'1920x1080',flush=True)
   if phase in ('pilot','all'):
    await page.set_viewport_size({'width':1280,'height':720})
    frames=out/'frames';frames.mkdir(exist_ok=True)
    for k in range(16*10):
     target=frames/f'{k:04d}.jpg'
     if not target.exists():
      await page.evaluate('([t,s])=>window.frame(t,s)',[k/10,scene])
      await page.screenshot(path=str(target),type='jpeg',quality=88)
     if k%40==0:print('RENDER',scene,k,'/160',flush=True)
    movie=out/f'M1lash_MultNews_{scene}_SILENT_v1_16s.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-y','-framerate','10','-i',str(frames/'%04d.jpg'),'-vf','fps=30,format=yuv420p','-c:v','libx264','-crf','23','-preset','veryfast','-pix_fmt','yuv420p','-an','-movflags','+faststart',str(movie)],check=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(movie),'-f','null','-'],check=True)
    pr=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(movie)]))
    streams=[s['codec_type'] for s in pr['streams']]
    assert streams==['video'],streams
    assert abs(float(pr['format']['duration'])-16)<.03,pr['format']['duration']
    assert pr['streams'][0]['width']==1280 and pr['streams'][0]['height']==720
    assert int(pr['streams'][0].get('nb_frames','480'))==480
    sha=hashlib.sha256(movie.read_bytes()).hexdigest()
    (out/'qa.json').write_text(json.dumps({'scene':scene,'path':str(movie),'duration':pr['format']['duration'],'streams':streams,'frames':480,'size':movie.stat().st_size,'sha256':sha,'browser_errors':errors},ensure_ascii=False,indent=2))
    print('VIDEO_OK',scene,movie.stat().st_size,sha,flush=True)
   await page.set_viewport_size({'width':1920,'height':1080})
  await browser.close()
  if errors:raise RuntimeError(errors)
if __name__=='__main__':asyncio.run(run(sys.argv[1] if len(sys.argv)>1 else 'stills'))