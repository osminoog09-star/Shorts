#!/usr/bin/env python3
"""Six literal 3D storyboard stills, before the motion pilot. PRIVATE REVIEW."""
import base64
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"motion-output"
ART.mkdir(exist_ok=True)
OUT=ROOT/"videos/chigur_three_storyboard_PRIVATE_REVIEW.mp4"
LIB=ROOT/"shorts/chigur_three.min.js"
if not LIB.is_file():
    url="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
    response=requests.get(url,timeout=45)
    response.raise_for_status()
    LIB.write_bytes(response.content)

print('storyboard setup')

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl'])
    page=browser.new_page(viewport={'width':960,'height':540})
    page.set_content('<body style="margin:0"><canvas id="scene"></canvas></body>')
    page.add_script_tag(path=str(LIB))
    page.add_script_tag(path=str(ROOT/'shorts/chigur_scene_preflight.js'))
    page.wait_for_function('window.ready !== undefined')
    for i in range(6):
        shot=page.evaluate('(t)=>window.frame(t)',i*6+2)
        dest=ART/f'chigur_scene_{i+1:02d}.png'
        dest.write_bytes(base64.b64decode(shot.split(',',1)[1]))
        print('3D STILL',i+1,dest.stat().st_size,flush=True)
    browser.close()
# QA carrier only: six 6-second holds, not the real animated film.
# Render the actual moving pilot only after human inspection of these six PNGs.
command=['ffmpeg','-hide_banner','-nostdin','-y','-v','error',
 '-framerate','1/6','-start_number','1','-i',str(ART/'chigur_scene_%02d.png'),
 '-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
 '-filter:v','scale=1080:608:flags=lanczos,pad=1080:1920:0:656:black,fps=30',
 '-t','36','-c:v','libx264','-preset','veryfast','-crf','22',
 '-pix_fmt','yuv420p','-r','30','-c:a','aac','-b:a','128k',
 '-movflags','+faststart',str(OUT)]
subprocess.run(command,check=True)
print('STORYBOARD REVIEW ONLY:',OUT,OUT.stat().st_size)
