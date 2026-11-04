#!/usr/bin/env python3
"""Deterministic original HTML/SVG M1lash animation to video (review-only). Not PIL scenes."""
import asyncio, subprocess, hashlib, wave, argparse, math
from pathlib import Path
import numpy as np
from playwright.async_api import async_playwright
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'qa'/'demo_v3'
FPS_DRAW=12
FPS_OUTPUT=30
SECONDS=24

def audio(out):
    rate=24000;n=SECONDS*rate;t=np.arange(n,dtype=np.float64)/rate
    # Original synthetic industrial Foley, no sampled tracks or speech.
    engine=.027*np.sin(2*np.pi*(62*t+.8*np.sin(.14*t)))+.012*np.sin(2*np.pi*123*t)
    motor=.010*np.sin(2*np.pi*(190+15*np.sin(.28*t))*t)
    wheels=.011*np.sin(2*np.pi*(12*t))*np.sin(2*np.pi*80*t)
    v=engine+motor+wheels
    # Welder clicks 8s–11.8s with intentionally gated, smooth-decay metallic spark tones.
    for time in np.arange(8.15,11.65,.23):
        st=int(time*rate);end=min(n,st+int(.065*rate));dt=np.arange(end-st)/rate
        env=np.exp(-dt*66)
        v[st:end]+=.084*env*(np.sin(2*np.pi*2180*dt)+.35*np.sin(2*np.pi*3870*dt))
    # Truck beep while the forklift passes through the alley.
    for time in [13.2,14.0,14.8]:
        st=int(time*rate);end=min(n,st+int(.18*rate));dt=np.arange(end-st)/rate
        env=np.minimum(dt*23,1)*np.minimum((.18-dt)*23,1)
        v[st:end]+=.045*env*np.sin(2*np.pi*1030*dt)
    # Assorted subtle moving belt ticks and bolts.
    for tm in np.arange(.3,SECONDS,.50):
        st=int(tm*rate);end=min(n,st+int(.045*rate));dt=np.arange(end-st)/rate
        v[st:end]+=.028*np.exp(-dt*100)*np.sin(2*np.pi*460*dt)
    fade=np.minimum(t/.5,1)*np.minimum((SECONDS-t)/.6,1)
    v=np.clip(v*fade,-.85,.85)
    pcm=(v*32767).astype(np.int16)
    with wave.open(str(out),'wb') as w:
      w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm.tobytes())

async def main():
    OUT.mkdir(parents=True,exist_ok=True)
    frames=OUT/'frames';frames.mkdir(exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox','--disable-dev-shm-usage'])
        page=await b.new_page(viewport={'width':1920,'height':1080},device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        await page.set_content((ROOT/'factory_stage.html').read_text(encoding='utf-8'),wait_until='load')
        stills=[]
        for k in range(SECONDS*FPS_DRAW):
            ti=k/FPS_DRAW
            await page.evaluate('t => window.frame(t)',ti)
            await page.locator('svg').screenshot(path=str(frames/f'{k:04d}.jpg'),type='jpeg',quality=89)
            if k%48==0:
                print(f'RENDER {k}/{SECONDS*FPS_DRAW} frames',flush=True)
            if k in [6,54,102,150,198,246]:
                still=OUT/f'shot_{len(stills):02d}.png'
                await page.locator('svg').screenshot(path=str(still))
                stills.append(still)
        await b.close()
        if errors:raise ValueError(f'JS_ERRORS {errors}')
    audio(OUT/'original_factory_foley.wav')
    video=OUT/'M1lash_MultNews_24s_MEGAFABRIC_S3D25_DEMO.mp4'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
                    '-framerate',str(FPS_DRAW),'-i',str(frames/'%04d.jpg'),
                    '-i',str(OUT/'original_factory_foley.wav'),
                    '-vf',f'fps={FPS_OUTPUT},format=yuv420p',
                    '-c:v','libx264','-preset','medium','-crf','21',
                    '-c:a','aac','-b:a','160k','-ar','48000',
                    '-t',str(SECONDS),'-movflags','+faststart',str(video)],check=True)
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
    print('DECODE_PASS',video,'BYTES',video.stat().st_size,'SHA256',hashlib.sha256(video.read_bytes()).hexdigest(),flush=True)
    print(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration,size','-show_entries','stream=codec_name,width,height,r_frame_rate','-of','json',str(video)],text=True),flush=True)
if __name__=='__main__':asyncio.run(main())