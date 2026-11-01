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
    page.add_script_tag(path=str(ROOT/'longform/chigur/graphics/three_stage_v11.js'))
    page.add_script_tag(path=str(ROOT/'longform/chigur/graphics/three_stage_v14_atmosphere.js'))
    page.add_script_tag(path=str(ROOT/'longform/chigur/graphics/three_stage_v12_motion.js'))
    page.add_script_tag(path=str(ROOT/'longform/chigur/graphics/three_stage_v12_overlay.js'))
    page.wait_for_function('window.ready===true',timeout=30000)
    for i in range(6):
        png=page.evaluate('(t)=>window.frame(t)',i*6+2)
        target=ART/f'chigur_v14_scene_{i+1:02d}.png'
        target.write_bytes(base64.b64decode(png.split(',',1)[1]))
        print('STILL',i+1,target.stat().st_size,flush=True)
        if target.stat().st_size<2000:
            raise RuntimeError('empty scene')
    browser.close()
    if errors:raise RuntimeError('browser errors: '+';'.join(errors))
out=ROOT/'videos/chigur_v14_six_stills_REVIEW_ONLY.mp4'
out.parent.mkdir(parents=True,exist_ok=True)
cmd=['ffmpeg','-y','-v','error','-framerate','1/6','-i',str(ART/'chigur_v14_scene_%02d.png')]
cmd.extend(['-f','lavfi','-i','anullsrc=r=48000:cl=stereo'])
cmd.extend(['-t','36','-vf','fps=30,scale=1080:608,pad=1080:1920:0:656:black'])
cmd.extend(['-r','30','-c:v','libx264','-preset','veryfast','-crf','22'])
cmd.extend(['-pix_fmt','yuv420p'])
cmd.extend(['-c:a','aac','-b:a','96k',str(out)])
subprocess.check_call(cmd)

# Preserve exact approved assembler source for offline private remaster QA.
from shutil import copy2
copy2(ROOT/'tools/assemble_with_outro.py',ART/'assemble_with_outro.py')
copy2(LIB,ART/'three_r128.min.js')

# Studio Short recovery: exact approved rev4 ending and Dima reveal voices.
# These are PRIVATE production assets, not movie source data, not final Chigur media.
from pathlib import Path as _Path
import asyncio as _asyncio
import edge_tts as _edge_tts
_approved=ROOT/'media/outro/m1lash_outro_v1_vertical.mp4'
if not _approved.is_file():raise RuntimeError("Approved outro not present in main")
copy2(_approved,ART/'approved_m1lash_outro_v1_vertical.mp4')
_reveals={
 '001':'Это был фильм «Старикам тут не место»',
 '002':'Это был фильм «Старикам тут не место»',
 '003':'Это был фильм «Одержимость»',
 '004':'Это был фильм «Из машины»',
 '005':'Это был фильм «Стрингер»',
 '006':'Это был фильм «Интерстеллар»',
}
async def _voices():
    for _id,_phrase in _reveals.items():
        _dest=ART/f'approved_dima_title_{_id}.mp3'
        await _edge_tts.Communicate(_phrase,voice='ru-RU-DmitryNeural',rate='+4%').save(str(_dest))
        if _dest.stat().st_size<3000:raise RuntimeError("Missing approved Dima voice")
_asyncio.run(_voices())
print("M1lash studio assets (exact outro, six RU titles) exported PRIVATE to motion artifact",flush=True)
 # QA-only asset for local code-based V14 render, not distributed video

# Report actual run number for retrieving 6 stills + r128 runtime back to local QA.
import json,os
marker=ROOT/'reports/research/chigur_v14_run.json'
marker.write_text(json.dumps({'run_id':os.environ.get('GITHUB_RUN_ID'),'stage':'V14','status':'stills_generated_not_visual_qa'},indent=2)+'\n')
