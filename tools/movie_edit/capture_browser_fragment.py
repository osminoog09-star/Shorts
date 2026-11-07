"""Bounded user-requested fullscreen browser recording + speaker loopback.

Browser selection, playback and seeking are manual/CUA only. No source URLs,
cookies, network interception, DRM operations, microphone input or OBS changes.
Keep the specified Chrome movie fullscreen for the whole 60s maximum capture.
"""
import argparse,json,os,re,subprocess,time,warnings
from pathlib import Path
import numpy as np
import soundcard as sc
import soundfile as sf

def main():
    p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--root',type=Path,default=Path(r'C:\M1lash\Работа\kino_new_20261107'));a=p.parse_args()
    if not 1<=a.seconds<=60:raise SystemExit('Capture must be 1..60 seconds')
    if not a.id.replace('_','').isalnum():raise SystemExit('Invalid id')
    a.root.mkdir(parents=True,exist_ok=True);base=a.root/a.id
    if base.with_suffix('.mp4').exists():raise SystemExit('Never overwrite an existing capture')
    speaker=sc.default_speaker();mic=sc.get_microphone(id=speaker.id,include_loopback=True)
    assert mic.isloopback,'Microphone recording forbidden for this task'
    log=base.with_suffix('.ffmpeg.log').open('wb')
    meta={'id':a.id,'capture_seconds':a.seconds,'audio':'default-speaker WASAPI loopback only','microphone':False,'screen':'fullscreen Chrome movie, user requested','rights':'owner requested short technical capture; third-party reuse license not established','publication':'private draft only'}
    video=base.with_suffix('.video.mp4');wav=base.with_suffix('.wav')
    with mic.recorder(samplerate=48000,channels=2,blocksize=4800) as recorder:
        t0=time.perf_counter();wall0=time.time()
        proc=subprocess.Popen(['ffmpeg','-hide_banner','-y','-f','gdigrab','-framerate','30','-draw_mouse','0','-i','desktop','-t',str(a.seconds),'-an','-c:v','h264_nvenc','-preset','p4','-cq','18','-pix_fmt','yuv420p',str(video)],stdout=log,stderr=log)
        print('CAPTURE_STARTED',a.id,flush=True)
        chunks=[]
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            while time.perf_counter()-t0<a.seconds:
                chunks.append(recorder.record(numframes=4800))
    proc.wait(timeout=35);log.close()
    if proc.returncode:raise SystemExit('Video capture failed; inspect private log')
    data=np.concatenate(chunks);sf.write(wav,data,48000,subtype='PCM_16')
    header=base.with_suffix('.ffmpeg.log').read_text(encoding='utf8',errors='replace')
    match=re.search(r'start: (\d+\.\d+), bitrate',header)
    video_delay=max(0,float(match[1])-wall0) if match else 0
    if video_delay>1:raise SystemExit('Unexpected capture start skew; do not deliver unsynchronised audio')
    meta['loopback_trim_seconds']=round(video_delay,6)
    meta.update(audio_seconds=len(data)/48000,audio_peak=float(np.max(np.abs(data))),audio_rms=float(np.sqrt(np.mean(data**2))))
    subprocess.run(['ffmpeg','-hide_banner','-v','error','-y','-i',str(video),'-ss',str(video_delay),'-i',str(wav),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(base.with_suffix('.mp4'))],check=True)
    meta['file']=str(base.with_suffix('.mp4'));base.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
    print('CAPTURE_COMPLETE',json.dumps(meta,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
