"""Original vector cartoon rendering and QA stills, no PIL scene painting."""
from pathlib import Path
import asyncio, subprocess, argparse, wave, numpy as np, hashlib, json
from playwright.async_api import async_playwright
from PIL import Image, ImageOps, ImageDraw
ROOT=Path(__file__).parent
OUT=ROOT/'qa'/'demo_v5'; OUT.mkdir(parents=True,exist_ok=True)
FPS=12; DURATION=24
async def render(mode, start=0, end=FPS*DURATION):
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        await page.set_content((ROOT/'factory_stage_v5.html').read_text(),wait_until='load')
        if mode in ['stills','all']:
            d=OUT/'stills';d.mkdir(exist_ok=True)
            for i,t in enumerate([1,5,9,13,17,22]):
                await page.evaluate('t=>window.frame(t)',t)
                await page.locator('#viewport').screenshot(path=str(d/f'shot_{i:02d}.png'))
                print('STILL',i,t,flush=True)
            images=[]
            for pth in sorted(d.glob('shot_??.png')):
                im=Image.open(pth).convert('RGB').resize((800,450))
                images.append(im)
            c=Image.new('RGB',(1600,1350),'#eee')
            for k,im in enumerate(images):c.paste(im,((k%2)*800,(k//2)*450))
            c.save(OUT/'stills_contact.jpg',quality=90)
        if mode in ['pilot','all','frames']:
            frames=OUT/'frames';frames.mkdir(exist_ok=True)
            for k in range(start,end):
                await page.evaluate('t=>window.frame(t)',k/FPS)
                await page.locator('#viewport').screenshot(path=str(frames/f'{k:04d}.jpg'),type='jpeg',quality=83)
                if k%24==0:print('FRAME',k,'/',FPS*DURATION,flush=True)
        await browser.close()
        if errors:raise RuntimeError('JS_ERRORS '+repr(errors))
    if mode in ['pilot','all','encode']:
        frames=OUT/'frames'
        assert len(list(frames.glob('*.jpg'))) == FPS*DURATION, 'missing frames'
        # Temporary foley reused only from our ORIGINAL synthetic factory effects.
        import importlib.util
        spec=importlib.util.spec_from_file_location('v3demo',ROOT/'demo_render.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        foley=OUT/'original_factory_foley.wav';module.audio(foley)
        dest=OUT/'M1lash_MultNews_factory_24s_v5_1080p.mp4'
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(frames/'%04d.jpg'),'-i',str(foley),'-vf','fps=30,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','23','-c:a','aac','-b:a','128k','-ar','48000','-movflags','+faststart','-t',str(DURATION),str(dest)],check=True)
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(dest),'-f','null','-'],check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,avg_frame_rate','-of','json',str(dest)]))
        print('VIDEO_READY',str(dest),'sha256',hashlib.sha256(dest.read_bytes()).hexdigest(),'probe',json.dumps(probe),flush=True)
        contact=[]
        for t in [1,5,9,13,17,22]:
            png=OUT/f'actual_video_t{t}.png'
            subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(dest),'-frames:v','1',str(png)],check=True)
            contact.append(Image.open(png).convert('RGB').resize((800,450)))
        sheet=Image.new('RGB',(1600,1350))
        for i,im in enumerate(contact):sheet.paste(im,((i%2)*800,(i//2)*450))
        sheet.save(OUT/'video_contact.jpg',quality=90)
if __name__=='__main__':
    arg=argparse.ArgumentParser();arg.add_argument('mode',choices=['stills','pilot','all','frames','encode']);arg.add_argument('--start',type=int,default=0);arg.add_argument('--end',type=int,default=FPS*DURATION);x=arg.parse_args()
    asyncio.run(render(x.mode,x.start,x.end))