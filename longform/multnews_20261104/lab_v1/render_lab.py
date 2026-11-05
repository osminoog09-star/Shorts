#!/usr/bin/env python3
"""M1lash Korea lab: deterministic HTML/SVG stills and strictly silent MP4."""
from pathlib import Path
import asyncio, subprocess, json, hashlib, argparse
from playwright.async_api import async_playwright

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'qa'
TIMES=[1.0,5.4,9.7,11.3,13.45,17.5]

async def go(mode):
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        await page.set_content((ROOT/'lab_stage.html').read_text(encoding='utf8'),wait_until='load')
        if mode in ('stills','all'):
            observations=[]
            for i,t in enumerate(TIMES):
                observations.append(await page.evaluate('(t)=>window.frame(t)',t))
                await page.locator('#viewport').screenshot(path=str(OUT/f'still_{i:02d}_{t}.png'))
            (OUT/'state_stills.json').write_text(json.dumps(observations,indent=2,ensure_ascii=False))
        if mode in ('pilot','all'):
            frames=OUT/'frames'
            frames.mkdir(exist_ok=True)
            await page.set_viewport_size({'width':1280,'height':720})
            for i in range(200):
                file=frames/f'{i:04d}.jpg'
                if file.exists():
                    continue
                await page.evaluate('(t)=>window.frame(t)',i/10)
                await page.locator('#viewport').screenshot(path=str(file),type='jpeg',quality=88)
            video=Path('/mnt/data/M1lash_MultNews_LAB_v1_SILENT_20s_720p.mp4')
            subprocess.run(['ffmpeg','-v','error','-y','-framerate','10','-i',str(frames/'%04d.jpg'),
                            '-vf','fps=30,format=yuv420p','-c:v','libx264','-preset','veryfast','-crf','21',
                            '-pix_fmt','yuv420p','-an','-t','20','-movflags','+faststart',str(video)],check=True)
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
            meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
            assert len(meta['streams'])==1 and meta['streams'][0]['codec_type']=='video'
            stats={'duration':meta['format']['duration'],'frames':meta['streams'][0]['nb_frames'],
                   'size_bytes':video.stat().st_size,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),
                   'audio_streams':0,'javascript_errors':errors,'decode':'PASS'}
            (OUT/'stats.json').write_text(json.dumps(stats,indent=2))
            print(json.dumps(stats))
        await browser.close()
        if errors:
            raise RuntimeError(str(errors))
if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('mode',choices=['stills','pilot','all'])
    asyncio.run(go(ap.parse_args().mode))
