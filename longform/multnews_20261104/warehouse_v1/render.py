#!/usr/bin/env python3
"""M1lash MultNews warehouse original vector animation; silent pilot and stills only."""
from pathlib import Path
import asyncio,json,subprocess,hashlib,argparse
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'qa';OUT.mkdir(parents=True,exist_ok=True)
TIMES=[1.5,4.8,5.25,6.6,9.2,11.2,13.8,14.5]
async def go(mode):
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  await page.set_content((ROOT/'warehouse_stage.html').read_text(encoding='utf-8'),wait_until='load')
  if mode in ('stills','all'):
   data=[]
   for i,t in enumerate(TIMES):
    a=await page.evaluate('(t)=>{let r=window.frame(t);return {...r,robot:window.__warehouseQA}}',t)
    await page.locator('#viewport').screenshot(path=str(OUT/f'still_{i:02d}.png'))
    data.append(a)
   (OUT/'frame_states.json').write_text(json.dumps(data,indent=2))
   print('STILLS 8*1920x1080, JS_ERRORS',errors,flush=True)
  if mode in ('pilot','all'):
   frames=OUT/'pilot_frames';frames.mkdir(exist_ok=True)
   # 12 unique frames/sec, 1280x720 preview, 16 seconds at 30fps no audio.
   await page.set_viewport_size({'width':1280,'height':720})
   for k in range(16*12):
    target=frames/f'{k:04d}.jpg'
    if target.exists():continue
    await page.evaluate('(t)=>window.frame(t)',k/12)
    await page.locator('#viewport').screenshot(path=str(target),type='jpeg',quality=88)
    if k%48==0:print('WAREHOUSE FRAMES',k,'/192',flush=True)
   video=Path('/mnt/data/M1lash_MultNews_WAREHOUSE_v1_SILENT_16s_PILOT.mp4')
   subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','12','-i',str(frames/'%04d.jpg'),'-vf','fps=30,format=yuv420p','-c:v','libx264','-preset','fast','-crf','23','-pix_fmt','yuv420p','-an','-movflags','+faststart','-t','16',str(video)],check=True)
   subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
   probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
   stats={'path':str(video),'size':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'duration':probe['format']['duration'],'streams':[(x['codec_type'],x['codec_name']) for x in probe['streams']],'frames':probe['streams'][0].get('nb_frames'),'browser_errors':errors,'decode':'PASS'}
   (OUT/'render_stats.json').write_text(json.dumps(stats,indent=2));print('WAREHOUSE_STATS',json.dumps(stats),flush=True)
  await browser.close()
  if errors:raise RuntimeError('JS_ERRORS '+str(errors))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['stills','pilot','all']);args=a.parse_args();asyncio.run(go(args.mode))