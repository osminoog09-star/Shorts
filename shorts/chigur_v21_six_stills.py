#!/usr/bin/env python3
"""Chigur V21 editorial visual gate: six representative Three.js stills and an 8s pilot.

QA-only. It does not contain copyrighted film/audio or imply a ready movie.
"""
from pathlib import Path
import base64,json,subprocess,requests,os
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'motion-output'
OUT.mkdir(exist_ok=True)
LIB=ROOT/'shorts/chigur_three.min.js'
if not LIB.is_file():
    response=requests.get('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',timeout=60)
    response.raise_for_status()
    LIB.write_bytes(response.content)
SOURCE=[
 'longform/chigur/graphics/three_stage_v7.js',
 'longform/chigur/graphics/three_stage_v11.js',
 'longform/chigur/graphics/three_stage_v14_atmosphere.js',
 'longform/chigur/graphics/three_stage_v12_motion.js',
 'longform/chigur/graphics/three_stage_v15_actions.js',
 'longform/chigur/graphics/three_stage_v21_editorial.js',
]
SHOTS=[
 {'scene_id':0,'chapter_title':'ВЫБОР ИЛИ ПРИКАЗ?','seconds':6,'index':0},
 {'scene_id':1,'chapter_title':'ТИШИНА В ГОСТИНИЦЕ','seconds':6,'index':8},
 {'scene_id':2,'chapter_title':'ЗВУК КАК УГРОЗА','seconds':6,'index':15},
 {'scene_id':3,'chapter_title':'КАРЛА НЕ ИГРАЕТ','seconds':6,'index':22},
 {'scene_id':4,'chapter_title':'СКОЛЬКО СТОИТ ОТКАЗ?','seconds':6,'index':11},
 {'scene_id':5,'chapter_title':'ХОЛОДНАЯ ПРОЦЕДУРА','seconds':6,'index':16}
]
frames=OUT/'v21_preview_8s_frames'
frames.mkdir(exist_ok=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--disable-dev-shm-usage'])
 page=browser.new_page(viewport={'width':1280,'height':720})
 errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content('<html><body style="margin:0"><canvas id="scene"></canvas></body></html>')
 page.add_script_tag(path=str(LIB))
 for x in SOURCE:page.add_script_tag(path=str(ROOT/x))
 page.wait_for_function('window.chigurV21Ready===true',timeout=30000)
 for i,shot in enumerate(SHOTS):
    png=page.evaluate('([s,t])=>window.frameV21(s,t)',[shot,3])
    path=OUT/f'chigur_v21_scene_{i+1:02}.png'
    path.write_bytes(base64.b64decode(png.split(',',1)[1]))
    if path.stat().st_size<50000:raise RuntimeError('Blank scene '+str(i))
    print('V21 STILL',i+1,path.stat().st_size,flush=True)
 for n in range(240):
    i=0 if n<120 else 1
    t=(n if i==0 else n-120)/30
    png=page.evaluate('([s,t])=>window.frameV21(s,t)',[SHOTS[i],t])
    (frames/f'f{n:04d}.png').write_bytes(base64.b64decode(png.split(',',1)[1]))
 browser.close()
 if errors:raise RuntimeError('JavaScript errors: '+' | '.join(errors))
pilot=OUT/'chigur_v21_8sec_3D_GRAPHICS_ONLY_NO_FILM.mp4'
subprocess.run(['ffmpeg','-hide_banner','-nostdin','-y','-v','error',
 '-framerate','30','-i',str(frames/'f%04d.png'),
 '-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
 '-t','8','-vf','scale=1920:1080:flags=lanczos','-r','30',
 '-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p',
 '-c:a','aac','-b:a','96k','-movflags','+faststart',str(pilot)],check=True)
subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(pilot),'-f','null','-'],check=True)
if (frames/'f0000.png').read_bytes()==(frames/'f0119.png').read_bytes():raise RuntimeError('Coin frozen')
if (frames/'f0120.png').read_bytes()==(frames/'f0239.png').read_bytes():raise RuntimeError('Door frozen')
from shutil import rmtree
rmtree(frames)
(OUT/'chigur_v21_visual_gate.json').write_text(json.dumps({
 'stage':'V21 six still + 8s motion gate',
 'run_id':os.environ.get('GITHUB_RUN_ID'),
 'movie_media':False,'movie_speech':False,'human_visual_QA':'PENDING',
 'decode':'PASS','full_28_windows_rendered':False
},ensure_ascii=False,indent=2)+'\n')
print('V21 PILOT TECHNICAL PASS; VISUAL QA PENDING; NO MOVIE',flush=True)
