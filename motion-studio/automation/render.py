"""Deterministic Canvas -> MP4 render. No API keys are written to files."""
import asyncio, base64, functools, http.server, json, math, os, re, subprocess, sys, threading, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def run(*args):
    subprocess.run([str(a) for a in args],check=True,stdout=subprocess.DEVNULL)

def google_voice(text, dest, model, voice):
    import requests
    key=os.environ.get('GEMINI_API_KEY','')
    if not key: raise RuntimeError('GEMINI_API_KEY is not configured')
    r=requests.post('https://generativelanguage.googleapis.com/v1beta/models/'+model+':generateContent',headers={'x-goog-api-key':key},json={'contents':[{'role':'user','parts':[{'text':text,'speech_metadata':{'style':'Clear, engaging documentary narration'}}]}],'generationConfig':{'responseModalities':['AUDIO'],'speechConfig':{'voiceConfig':{'voice':voice}}}},timeout=180)
    if not r.ok: raise RuntimeError('Google TTS HTTP '+str(r.status_code))
    parts=r.json().get('candidates',[{}])[0].get('content',{}).get('parts',[])
    inline=next((p['inlineData'] for p in parts if 'inlineData'in p),None)
    if not inline: raise RuntimeError('Google TTS returned no audio')
    data=base64.b64decode(inline['data']); dest=Path(dest)
    if data.startswith(b'RIFF'): dest.write_bytes(data)
    else:
        rate=int(re.search(r'rate=(\d+)',inline.get('mimeType','')).group(1)) if re.search(r'rate=(\d+)',inline.get('mimeType','')) else 24000
        with wave.open(str(dest),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(data)

async def render(job_path, outdir):
    from playwright.async_api import async_playwright
    import edge_tts
    job=json.loads(Path(job_path).read_text());p=job['project'];scenes=p['scenes']
    if not 1<=len(scenes)<=100:raise ValueError('Expected 1–100 scenes')
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    name=re.sub('[^a-zA-Z0-9_-]','',job.get('id','video'))[:80] or 'video'
    folder=out/name;folder.mkdir(exist_ok=True)
    audio=[];offset=0;subs=[]
    for i,s in enumerate(scenes):
        text=str(s.get('text',''))[:5000]; raw=folder/f'voice-{i}.wav'; norm=folder/f'audio-{i}.wav'
        if text.strip():
            if job.get('tts_provider')=='google':await asyncio.to_thread(google_voice,text,raw,job.get('tts_model','gemini-3.8-flash-tts'),job.get('google_voice','Kore'))
            else:
                raw=folder/f'voice-{i}.mp3'
                await edge_tts.Communicate(text,job.get('voice','ru-RU-DmitryNeural')).save(str(raw))
            run('ffmpeg','-y','-i',raw,'-af','apad=pad_dur=0.25','-ar','24000','-ac','1',norm)
        else:run('ffmpeg','-y','-f','lavfi','-i','anullsrc=r=24000:cl=mono','-t',max(2,min(180,float(s.get('duration',8)))),norm)
        with wave.open(str(norm)) as w:duration=w.getnframes()/w.getframerate()
        if duration>180:raise ValueError('Scene exceeds 180 seconds; split it')
        s['duration']=duration;audio.append(norm)
        def tc(t):
            ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
        words=text.split();count=max(1,math.ceil(len(words)/15))
        for k in range(count):subs.append(f'{len(subs)+1}\n{tc(offset+duration*k/count)} --> {tc(offset+duration*(k+1)/count)}\n'+ ' '.join(words[k*15:(k+1)*15])+'\n')
        offset+=duration
    if offset>1000:raise ValueError('Video exceeds 1000-second run budget')
    with wave.open(str(folder/'voice.wav'),'wb') as dst:
        dst.setparams((1,2,24000,0,'NONE','not compressed'))
        for a in audio:
            with wave.open(str(a)) as src:dst.writeframes(src.readframes(src.getnframes()))
    (folder/'project.json').write_text(json.dumps(p,ensure_ascii=False,indent=2));(folder/'subtitles.srt').write_text('\n'.join(subs))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    height=min(1080,max(720,int(p.get('resolution',720))));width=round(height*16/9)
    if p.get('format')=='portrait':width,height=height,width
    p['resolution']=min(1080,int(p.get('resolution',720)))
    process=None
    try:
        async with async_playwright() as pw:
            browser=await pw.chromium.launch(args=['--no-sandbox']);page=await browser.new_page(viewport={'width':width,'height':height},device_scale_factor=1)
            await page.goto(f'http://127.0.0.1:{server.server_port}/');await page.wait_for_function('window.motionReady === true')
            await page.evaluate('(p)=>window.motionSetProject(p)',p)
            await page.add_style_tag(content='body>*{display:none!important} body{margin:0!important;background:black!important} #preview{display:block!important;position:fixed!important;left:0!important;top:0!important;max-width:none!important;width:'+str(width)+'px!important;height:'+str(height)+'px!important} body>.app,main,#view-studio,.studio-grid,.preview-panel,.canvas-wrap{display:contents!important} canvas{visibility:visible!important}')
            # Move only the actual canvas to the body, no UI CSS affects the render.
            await page.evaluate('()=>{const c=document.getElementById("preview");document.body.appendChild(c);c.style.cssText="display:block!important;position:fixed;inset:0;max-width:none!important;width:'+str(width)+'px;height:'+str(height)+'px";}')
            fps=30;frames=math.ceil(offset*fps)
            process=subprocess.Popen(['ffmpeg','-y','-f','image2pipe','-vcodec','mjpeg','-framerate',str(fps),'-i','pipe:0','-i',str(folder/'voice.wav'),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-t',str(offset),'-movflags','+faststart',str(out/(name+'.mp4'))],stdin=subprocess.PIPE,stderr=(folder/'ffmpeg.log').open('w'))
            for n in range(frames):
                await page.evaluate('(t)=>window.motionRenderFrame(t)',n/fps)
                image=await page.screenshot(type='jpeg',quality=92)
                process.stdin.write(image)
                if n%900==0:print(f'Render {n}/{frames}',flush=True)
            process.stdin.close();code=process.wait()
            if code:raise RuntimeError('FFmpeg failed; inspect ffmpeg.log')
            await page.evaluate('()=>window.motionRenderFrame(2)');await page.screenshot(path=str(out/(name+'-thumbnail.png')))
            await browser.close()
    finally:
        server.shutdown()
        if process and process.poll() is None:process.kill()
    return out/(name+'.mp4')
if __name__=='__main__':asyncio.run(render(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else 'motion-output'))
