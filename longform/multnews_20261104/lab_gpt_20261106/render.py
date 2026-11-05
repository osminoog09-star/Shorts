#!/usr/bin/env python3
"""MultNews #01 / Korean training lab: deterministic HTML/SVG original animation; no audio."""
import argparse, asyncio, subprocess, hashlib, json
from pathlib import Path
from playwright.async_api import async_playwright
DIR=Path(__file__).resolve().parent;QA=DIR/'qa'; QA.mkdir(exist_ok=True)
STILLS=[1.5,4.8,7.75,10.5,13.7,16.5]
async def main(mode):
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await browser.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        await page.set_content((DIR/'lab_stage.html').read_text(),wait_until='load')
        if mode in ('stills','all'):
            checks=[]
            for i,t in enumerate(STILLS):
                state=await page.evaluate('(t)=>window.frame(t)',t)
                await page.locator('#viewport').screenshot(path=str(QA/f'still_{i:02d}.png'))
                checks.append(state)
            (QA/'shot_states.json').write_text(json.dumps(checks,indent=2))
            print('STILLS',len(STILLS),'browser errors',errors,flush=True)
        if mode in ('video','all'):
            # SVG/CSS owns a 1920x1080 element: match browser viewport to actual export size.
            await page.set_viewport_size({'width':1920,'height':1080})
            frames=QA/'frames';frames.mkdir(exist_ok=True)
            for k in range(18*12):
                out=frames/f'{k:04d}.jpg'
                if not out.exists():
                    await page.evaluate('(t)=>window.frame(t)',k/12)
                    await page.locator('#viewport').screenshot(path=str(out),type='jpeg',quality=87)
                if k%36==0:print('FRAME',k,'/216',flush=True)
            dst=DIR/'M1lash_MultNews_LAB_v1_SILENT_18s_1080p.mp4'
            subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','12','-i',str(frames/'%04d.jpg'),'-vf','fps=30,format=yuv420p','-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p','-an','-movflags','+faststart','-t','18',str(dst)],check=True)
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(dst),'-f','null','-'],check=True)
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(dst)]))
            stats={'file':str(dst),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'bytes':dst.stat().st_size,'duration':probe['format']['duration'],'streams':[(s['codec_type'],s['codec_name']) for s in probe['streams']],'frames':probe['streams'][0].get('nb_frames'),'errors':errors,'full_decode':'PASS'}
            (QA/'stats.json').write_text(json.dumps(stats,indent=2));print('STATS',json.dumps(stats),flush=True)
        await browser.close()
        if errors:raise RuntimeError(errors)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['stills','video','all']);args=ap.parse_args();asyncio.run(main(args.mode))