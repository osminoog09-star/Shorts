#!/usr/bin/env python3
# Six review stills from Three.js, no movie media.
from pathlib import Path
import base64,subprocess,requests
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'motion-output'; ART.mkdir(exist_ok=True)
LIB=ROOT/'shorts/chigur_three.min.js'
if not LIB.is_file():
    response=requests.get('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',timeout=60)
    response.raise_for_status()
    LIB.write_bytes(response.content)
src=ROOT/'longform/chigur/graphics/three_stage_v7.js'
with sync_playwright() as pw:
    browser=pw.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl'])
    page=browser.new_page(viewport={'width':960,'height':540})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.set_content('<body style="margin:0"><canvas id="scene"></canvas></body>')
    page.add_script_tag(path=str(LIB))
    page.add_script_tag(path=str(src))
    page.wait_for_function('window.ready===true',timeout=30000)
    for i in range(6):
        png=page.evaluate('(t)=>window.frame(t)',i*6+2)
        target=ART/f'chigur_v7_scene_{i+1:02d}.png'
        target.write_bytes(base64.b64decode(png.split(',',1)[1]))
        print('STILL',i+1,target.stat().st_size,flush=True)
        if target.stat().st_size<2000:
            raise RuntimeError('empty scene')
    browser.close()
    if errors:raise RuntimeError('browser errors: '+';'.join(errors))
out=ROOT/'videos/chigur_v7_six_stills_REVIEW_ONLY.mp4'
out.parent.mkdir(parents=True,exist_ok=True)
cmd=['ffmpeg','-y','-v','error','-framerate','1/6','-i',str(ART/'chigur_v7_scene_%02d.png')]
cmd.extend(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo'])
cmd.extend(['-t','36','-vf','fps=30,scale=1080:608,pad=1080:1920:0:656:black'])
cmd.extend(['-r','30','-c:v','libx264','-preset','veryfast','-crf','22'])
cmd.extend(['-pix_fmt','yuv420p'])
cmd.extend(['-c:a','aac','-b:a','96k',str(out)])
