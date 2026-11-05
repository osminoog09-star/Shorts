#!/usr/bin/env python3
"""M1lash MultNews v6. SVG/Playwright renderer, STRICTLY SILENT video-only output."""
import asyncio, subprocess, hashlib, json
from pathlib import Path
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'qa'/'v7'
FRAMES=OUT/'render_frames'
SECONDS=24
DRAW_FPS=15
VIDEO_FPS=30
MASTER=Path('/mnt/data/M1lash_MultNews_FACTORY_v7_SILENT_24s_1080p.mp4')
async def main():
 OUT.mkdir(exist_ok=True,parents=True);FRAMES.mkdir(exist_ok=True)
 async with async_playwright() as p:
  browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
  page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
  errors=[]
  page.on('pageerror',lambda x: errors.append(str(x)))
  await page.set_content((ROOT/'factory_stage_v7.html').read_text(encoding='utf-8'),wait_until='load')
  for i in range(SECONDS*DRAW_FPS):
   if (FRAMES/f'{i:04d}.jpg').exists(): continue
   t=i/DRAW_FPS
   await page.evaluate('(t)=>window.frame(t)',t)
   await page.locator('#viewport').screenshot(path=str(FRAMES/f'{i:04d}.jpg'),type='jpeg',quality=88)
   if i % 60==0: print('STAGE',i,'/',SECONDS*DRAW_FPS,'time',t,flush=True)
  await browser.close()
  if errors:raise RuntimeError('JS_ERRORS '+str(errors))
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(DRAW_FPS),'-i',str(FRAMES/'%04d.jpg'),'-vf',f'fps={VIDEO_FPS},format=yuv420p','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-an','-movflags','+faststart','-t',str(SECONDS),str(MASTER)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(MASTER)]))
 streams=probe['streams']
 assert len(streams)==1 and streams[0]['codec_type']=='video', streams
 assert int(streams[0]['nb_frames'])==SECONDS*VIDEO_FPS,streams[0].get('nb_frames')
 assert abs(float(probe['format']['duration'])-SECONDS)<.06,probe['format']['duration']
 subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(MASTER),'-f','null','-'],check=True)
 with MASTER.open('rb') as fp:h=hashlib.file_digest(fp,'sha256').hexdigest()
 stats={'video':str(MASTER),'bytes':MASTER.stat().st_size,'sha256':h,'duration':probe['format']['duration'],'frames':streams[0]['nb_frames'],'width':streams[0]['width'],'height':streams[0]['height'],'fps':streams[0]['r_frame_rate'],'audio_streams':len([s for s in streams if s['codec_type']=='audio']),'full_decode':'pass','js_errors':errors}
 (OUT/'render_stats.json').write_text(json.dumps(stats,indent=2))
 print('FINAL_STATS',json.dumps(stats),flush=True)
if __name__=='__main__':asyncio.run(main())