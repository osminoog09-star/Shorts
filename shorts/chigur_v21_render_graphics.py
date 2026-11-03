#!/usr/bin/env python3
"""V21 deterministic Three.js graphic-only 1080p clips. No film / actors / original audio.

Uses existing motion-render.yml. Four 7-shot batches avoid timeout and protect
source clips from the public repository. Render after the V21 six-still gate.
"""
from pathlib import Path
import os,json,base64,subprocess,hashlib,requests,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'motion-output'
OUT.mkdir(exist_ok=True)
CAT=ROOT/'longform/chigur/graphics/v21_graphic_asset_catalogue.json'
data=json.loads(CAT.read_text(encoding='utf8'))
shots=data['shots']
assert len(shots)==28
job=Path(os.environ['M1LASH_JOB_PATH'])
spec=json.loads(job.read_text(encoding='utf8'))
batch=int(spec['batch'])
if batch not in range(4):raise ValueError('batch expected 0..3')
selected=shots[batch*7:(batch+1)*7]
LIB=ROOT/'shorts/chigur_three.min.js'
if not LIB.is_file():
    r=requests.get('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',timeout=60)
    r.raise_for_status();LIB.write_bytes(r.content)
SCRIPTS=[
 'three_stage_v7.js','three_stage_v11.js','three_stage_v14_atmosphere.js',
 'three_stage_v12_motion.js','three_stage_v15_actions.js','three_stage_v21_editorial.js'
]
SC=ROOT/'longform/chigur/graphics'
results=[]
t0=time.monotonic()
with sync_playwright() as pw:
    browser=pw.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--disable-dev-shm-usage'])
    page=browser.new_page(viewport={'width':1280,'height':720})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content('<html><body style="margin:0"><canvas id="scene"></canvas></body></html>')
    page.add_script_tag(path=str(LIB))
    for file in SCRIPTS:page.add_script_tag(path=str(SC/file))
    page.wait_for_function('window.chigurV21Ready===true',timeout=30000)
    for shot in selected:
        name=shot['id']+'_3D_ONLY.mp4'
        output=OUT/name
        dur=float(shot['seconds'])
        frames=int(round(dur*30))
        command=['ffmpeg','-hide_banner','-nostdin','-y','-v','error','-f','image2pipe','-framerate','30',
                 '-vcodec','mjpeg','-i','pipe:0',
                 '-f','lavfi','-i','anullsrc=r=48000:cl=stereo',
                 '-t',str(dur),'-vf','scale=1920:1080:flags=lanczos',
                 '-r','30','-pix_fmt','yuv420p','-c:v','libx264',
                 '-preset','veryfast','-crf','21','-c:a','aac','-b:a','96k',
                 '-movflags','+faststart',str(output)]
        process=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        for n in range(frames):
            pos=n/30
            data64=page.evaluate("([s,t])=>window.frameV21(s,t,'image/jpeg')",[shot,pos])
            process.stdin.write(base64.b64decode(data64.split(',',1)[1]))
        process.stdin.close()
        err=process.stderr.read().decode(errors='replace')
        rc=process.wait()
        if rc or not output.is_file() or output.stat().st_size<120000:
            raise RuntimeError(name+' encode failed '+err[-700:])
        # Full stream decode catches codec corruption but is NOT visual review.
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(output),'-f','null','-'],check=True)
        h=hashlib.sha256(output.read_bytes()).hexdigest()
        results.append({'id':shot['id'],'bytes':output.stat().st_size,'seconds':dur,'sha256':h})
        print('V21_GRAPHIC_FINISHED',shot['id'],output.stat().st_size,flush=True)
    browser.close()
    if errors:raise RuntimeError('Three.js error(s): '+' | '.join(errors))
(OUT/f'v21_graphics_batch_{batch}_report.json').write_text(json.dumps({
    'version':'V21','batch':batch,'status':'graphics_only_not_movie',
    'movie_frames':False,'movie_audio':False,'review':'PENDING',
    'clip_count':len(results),'render_elapsed_sec':round(time.monotonic()-t0,1),
    'results':results
},ensure_ascii=False,indent=2)+'\n')
print('V21 batch complete; independent visual QA still required')
