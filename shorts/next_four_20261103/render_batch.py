"""Four original HTML/SVG animated Shorts; preflight before full production.
No movie downloads, paid APIs, YouTube writes or schedule changes.
"""
import json, os, subprocess, sys, shutil, math, wave, hashlib
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
PROJECT=Path(__file__).resolve().parent
SPEC=json.loads((ROOT/os.environ['M1LASH_JOB_PATH']).read_text())
MODE=SPEC.get('mode','stills')
ITEMS=json.loads((PROJECT/'spec.json').read_text())['items']
if SPEC.get('only_ids'): ITEMS=[f for f in ITEMS if f['id'] in SPEC['only_ids']]
WORK=ROOT/'motion-output/next_four_20261103'; WORK.mkdir(parents=True,exist_ok=True)
QA=ROOT/'reports/research/qa/next_four_20261103'; QA.mkdir(parents=True,exist_ok=True)
SR=48000

def run(args,**kw):
    print('RUN',args[0], str(args[1])[:100] if len(args)>1 else '',flush=True)
    return subprocess.run([str(a) for a in args],check=True,**kw)

def timeline(f,folder,actual):
    samples=[np.zeros(round(.1*SR),np.float32)]; at=.1;segments=[];caps=[]
    job=PROJECT/(f['id']+'_voice.json')
    job.write_text(json.dumps({k:f[k] for k in ['voice','rate','pitch','lines']},ensure_ascii=False,indent=2))
    if actual:
        run([sys.executable,ROOT/'scripts/tts_job.py',job],cwd=ROOT,env=dict(os.environ,TTS_ENGINE='edge'))
    for line in f['lines']:
        if actual:
            voice=ROOT/'media/tts'/job.stem
            audio=voice/(line['id']+'.mp3');m=json.loads((voice/(line['id']+'.json')).read_text())
            assert m['voice_id']=='ru-RU-DmitryNeural' and m['engine']=='edge-tts'
            pcm=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(audio),'-ar',str(SR),'-ac','1','-f','f32le','-']),np.float32)
            words=m.get('words',[]);dur=len(pcm)/SR
            if len(words)<2:raise RuntimeError('Word timestamps missing; do not fake speech captions')
        else:
            ws=line['text'].split();dur=max(2.0,len(ws)*.43)
            words=[{'w':w,'start':i*dur/len(ws),'end':(i+1)*dur/len(ws)} for i,w in enumerate(ws)]
            pcm=np.zeros(round(dur*SR),np.float32)
        segments.append({'start':at,'end':at+dur,'text':line['text']})
        groups=[];cursor=0
        while cursor<len(words):
            group=words[cursor:cursor+4];cursor+=len(group)
            end=words[cursor]['start'] if cursor<len(words) else dur
            if end-group[0]['start']<.8 and groups:groups[-1]+=group
            else:groups.append(group)
        for i,group in enumerate(groups):
            start=at+group[0]['start'];end=at+(groups[i+1][0]['start'] if i+1<len(groups) else dur)
            if end-start<.79:raise RuntimeError('Caption reading gate <0.8s')
            caps.append({'start':start,'end':end,'words':[w['w'] for w in group]})
        samples+=[pcm,np.zeros(round(.08*SR),np.float32)];at+=dur+.08
    signal=np.concatenate(samples);duration=len(signal)/SR
    cuts=[0]+[segments[i]['start'] for i in [2,4,6,8,10]]+[duration]
    data={k:f[k] for k in ['id','theme','label','headlines','sources']}
    data.update(total=duration,cuts=cuts,caps=caps,segments=segments,actual_audio=actual)
    if actual:
        if not 29<=duration<=52:raise RuntimeError(f'Story duration {duration:.2f}; revise, never stretch')
        # Quiet original score + landing Foley; no external song in story.
        t=np.arange(len(signal))/SR;beat=(t*1.4)%1
        music=.005*np.sin(2*np.pi*110*t)+.006*np.sin(2*np.pi*330*t)*np.exp(-beat*17)
        rng=np.random.default_rng(20261103)
        for cut in cuts[1:-1]:
            pos=round(cut*SR);n=min(round(.085*SR),len(signal)-pos);tau=np.arange(n)/SR
            music[pos:pos+n]+=.014*rng.normal(size=n)*np.exp(-tau*58)
        out=np.clip(signal+music,-.95,.95)
        with wave.open(str(folder/'score.wav'),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((out*32767).astype(np.int16).tobytes())
        shutil.copytree(voice,folder/'voices',dirs_exist_ok=True)
    (folder/'timeline.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
    return data

def contact(paths,target):
    from PIL import Image,ImageDraw
    sheet=Image.new('RGB',(900,1104),'#20303a')
    for i,p in enumerate(paths):
        im=Image.open(p);im.thumbnail((300,533));x=i%3*300;y=i//3*552
        sheet.paste(im,(x,y+19));ImageDraw.Draw(sheet).text((x+5,y+2),p.stem[:30],fill='white')
    sheet.save(target,quality=83)

def capture(browser,f,data,folder,full):
    page=browser.new_page(viewport={'width':1080,'height':1920},device_scale_factor=1)
    page.goto((PROJECT/'film.html').as_uri());page.evaluate('() => document.fonts.ready')
    page.evaluate('d=>window.setTimeline(d)',data)
    layout=[]
    for cap in data['caps']:
        when=(cap['start']+cap['end'])/2
        row=page.evaluate('''t=>{window.seek(t);let c=document.querySelector('#cap'),h=document.querySelector('#title'),cb=c.getBoundingClientRect(),hb=h.getBoundingClientRect();return {t,left:cb.left,right:cb.right,bottom:cb.bottom,capOverflow:c.scrollHeight>c.clientHeight+1,titleOverflow:h.scrollWidth>h.clientWidth+1,titleBottom:hb.bottom}}''',when)
        if row['left']<95 or row['right']>925 or row['bottom']>1420 or row['titleBottom']>450 or row['titleOverflow']:
            raise RuntimeError('Layout NO-GO '+str(row))
        layout.append(row)
    (folder/'layout.json').write_text(json.dumps(layout,indent=2))
    stills=[]
    for n in range(6):
        t=.6 if n==0 else (data['cuts'][n]+data['cuts'][n+1])/2
        page.evaluate('t=>window.seek(t)',t)
        out=folder/f'still_{n+1:02d}.jpg';page.screenshot(path=str(out),type='jpeg',quality=88);stills.append(out)
    contact(stills,folder/'stills_contact.jpg')
    if full:
        # Pipe JPEG screenshots to ffmpeg: deterministic frames, no real-time capture.
        silent=folder/'silent.mp4'
        proc=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-vcodec','mjpeg','-framerate','30','-i','-','-c:v','libx264','-preset','fast','-crf','19','-threads','2','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709',str(silent)],stdin=subprocess.PIPE)
        try:
            for i in range(math.ceil(data['total']*30)):
                page.evaluate('t=>window.seek(t)',i/30)
                proc.stdin.write(page.screenshot(type='jpeg',quality=91))
                if i%150==0:print(f['id'],'frame',i,flush=True)
            proc.stdin.close()
            if proc.wait():raise RuntimeError('Frame encoder failed')
        except BaseException:
            proc.kill();raise
    page.close()

def save(selected):
    # All writes are own new paths; queue/dates never staged. Retry on fresh main.
    run(['git','config','user.name','m1lash-render-bot'],cwd=ROOT)
    run(['git','config','user.email','m1lash-render-bot@users.noreply.github.com'],cwd=ROOT)
    run(['git','add','--']+[p.relative_to(ROOT) for p in selected],cwd=ROOT)
    if subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode:
        run(['git','commit','-m',f'video: four new drawn Shorts {MODE} evidence (private review only)'],cwd=ROOT)
        run(['git','restore','--','media/tts/'],cwd=ROOT)
        run(['git','clean','-fd','--','media/tts/'],cwd=ROOT)
        for _ in range(4):
            run(['git','pull','--rebase','origin','main'],cwd=ROOT)
            if subprocess.run(['git','push','origin','HEAD:main'],cwd=ROOT).returncode==0:return
        raise RuntimeError('Could not save verified outputs')

selected=[];reports=[]
with sync_playwright() as p:
    chrome=shutil.which('google-chrome') or shutil.which('chromium')
    browser=p.chromium.launch(executable_path=chrome,headless=True,args=['--no-sandbox','--disable-dev-shm-usage','--allow-file-access-from-files'])
    for f in ITEMS:
        folder=WORK/f['id'];folder.mkdir(exist_ok=True)
        data=timeline(f,folder,MODE=='full');capture(browser,f,data,folder,MODE=='full')
        for source in folder.glob('*.jpg'):
            target=QA/(f['id']+'_'+MODE+'_'+source.name);shutil.copy2(source,target);selected.append(target)
        report={'id':f['id'],'mode':MODE,'run_id':os.environ.get('GITHUB_RUN_ID'),'body_seconds':data['total'],'timeline':data,'personal_listening':'NOT_VERIFIED','visual_review':'PENDING_MANUAL','youtube_uploaded':False}
        if MODE=='full':
            body=folder/'body.mp4';out=ROOT/'videos'/(f['id']+'_v1.mp4');out.parent.mkdir(exist_ok=True)
            run(['ffmpeg','-v','error','-y','-i',folder/'silent.mp4','-i',folder/'score.wav','-map','0:v','-map','1:a','-t',str(data['total']),'-c:v','copy','-c:a','pcm_s16le',folder/'body.mkv'])
            run([sys.executable,ROOT/'tools/assemble_with_outro.py',folder/'body.mkv','-o',out,'--audio-bitrate','320k','--preset','fast','--crf','18','--max-seconds','65'])
            check=folder/'check.json'
            with check.open('w') as h:
                checked=subprocess.run([sys.executable,str(ROOT/'skills/ext/ffmpeg-skill/scripts/check.py'),str(out),'--platform','shorts','--json'],stdout=h,stderr=subprocess.PIPE,text=True)
            if checked.returncode:
                try:
                    evidence=json.loads(check.read_text())
                    failed=[{'check':x.get('check'),'value':x.get('value'),'expected':x.get('expected')} for x in evidence.get('checks',[]) if x.get('status')=='FAIL']
                    print('M1LASH_CHECK_FAIL',json.dumps(failed,ensure_ascii=False),flush=True)
                except (ValueError,KeyError):
                    print('M1LASH_CHECK_RAW',check.read_text()[:1800],flush=True)
                raise RuntimeError('Shorts technical check failed; see M1LASH_CHECK_FAIL above')
            run([sys.executable,ROOT/'skills/ext/ffmpeg-skill/scripts/look.py',out,'--tiles','3x2','--output',folder/'final_look.png'])
            run(['ffmpeg','-v','error','-xerror','-i',out,'-f','null','-'])
            report.update(sha256=hashlib.sha256(out.read_bytes()).hexdigest(),bytes=out.stat().st_size,assembly=json.loads(Path(str(out)+'.qa.json').read_text()),check=json.loads(check.read_text()))
            shutil.copy2(out,folder/out.name)
            target=QA/(f['id']+'_final_look.png');shutil.copy2(folder/'final_look.png',target);selected.append(target)
            selected.extend([out,Path(str(out)+'.qa.json')])
        target=ROOT/'reports/research'/('2026-11-03_'+f['id']+'_'+MODE+'_QA.json');target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');selected.append(target);reports.append(report)
        # Checkpoint each completed item, rather than losing 4 on last-item failure.
        save(selected);selected=[]
    browser.close()
print(json.dumps({'mode':MODE,'completed':[r['id'] for r in reports]},ensure_ascii=False),flush=True)
