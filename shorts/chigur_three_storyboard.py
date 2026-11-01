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
    page.add_script_tag(path=str(ROOT/'longform/chigur/graphics/three_stage_prototype_v3.js'))
    page.wait_for_function('window.ready !== undefined')
    for i in range(6):
        shot=page.evaluate('(t)=>window.frame(t)',i*6+2)
        dest=ART/f'chigur_scene_{i+1:02d}.png'
        dest.write_bytes(base64.b64decode(shot.split(',',1)[1]))
        print('3D STILL',i+1,dest.stat().st_size,flush=True)
    # Six-second deterministic camera/coin action pilot, after six stills.
    seq=ART/"chigur_pilot_frames"
    seq.mkdir(exist_ok=True)
    for f in range(180):
        shot=page.evaluate("(t)=>window.frame(t)",f/30.0)
        (seq/f"f{f:04d}.png").write_bytes(base64.b64decode(shot.split(",",1)[1]))
        if f%60==0:print("PILOT FRAME",f,flush=True)
    browser.close()
# Real 6-second movement pilot; silent only because narrator/film audio is not yet assembled.
PILOT=ART/"chigur_coin_motion_6s_PRIVATE_PREVIEW.mp4"
subprocess.run(["ffmpeg","-hide_banner","-nostdin","-y","-v","error",
 "-framerate","30","-i",str(ART/"chigur_pilot_frames"/"f%04d.png"),
 "-f","lavfi","-i","anullsrc=r=48000:cl=stereo",
 "-t","6","-c:v","libx264","-preset","veryfast","-crf","20",
 "-pix_fmt","yuv420p","-r","30","-c:a","aac","-b:a","96k",
 "-movflags","+faststart",str(PILOT)],check=True)
import shutil
shutil.rmtree(ART/"chigur_pilot_frames")
print("SIX SECOND TRUE ANIMATION PILOT:",PILOT.stat().st_size,flush=True)

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

# Bundle installed QA scripts for offline validation of private MP4s.

# Export first-party ffmpeg-skill CLI for private local compliance verification.
import zipfile
qa_source=ROOT/'skills/ext/ffmpeg-skill/scripts'
with zipfile.ZipFile(ART/'ffmpeg_skill_local_QA_tools.zip','w',zipfile.ZIP_DEFLATED) as toolpack:
    for source in qa_source.rglob('*'):
        if source.is_file() and source.suffix in ('.py','.json','.yaml','.yml'):
            toolpack.write(source,source.relative_to(qa_source))
print('QA_TOOLS', (ART/'ffmpeg_skill_local_QA_tools.zip').stat().st_size, flush=True)
