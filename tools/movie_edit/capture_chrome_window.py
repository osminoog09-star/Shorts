"""Record only the user-selected Chrome HWND with Windows Graphics Capture.

No browser control, networking, stream extraction, mic, or DRM operations.
Only a bounded fragment, stored privately. Switch/seek/play through CUA.
"""
import argparse,json,subprocess,time,threading,warnings
from pathlib import Path
import numpy as np
import soundcard as sc
import soundfile as sf
from windows_capture import WindowsCapture

def main():
    p=argparse.ArgumentParser();p.add_argument('--hwnd',type=int,required=True);p.add_argument('--id',required=True);p.add_argument('--seconds',type=float,default=60);p.add_argument('--probe',action='store_true');a=p.parse_args()
    assert 0<a.seconds<=60 and a.id.replace('_','').isalnum()
    root=Path(r'C:\M1lash\Работа\kino_new_20261107');root.mkdir(exist_ok=True);base=root/a.id
    assert not base.with_suffix('.mp4').exists(),'Never overwrite capture'
    state={'frame':None,'frames_received':0};lock=threading.Lock();done=threading.Event();ready=threading.Event()
    capture=WindowsCapture(cursor_capture=False,draw_border=True,window_hwnd=a.hwnd,minimum_update_interval=16)
    @capture.event
    def on_frame_arrived(frame,control):
        with lock:state.update(frame=frame.frame_buffer.copy(),frames_received=state['frames_received']+1)
        ready.set()
    @capture.event
    def on_closed():done.set()
    controller=capture.start_free_threaded()
    if not ready.wait(10):controller.stop();raise SystemExit('No Chrome window frames')
    if a.probe:
        from PIL import Image
        with lock:arr=state['frame'].copy()
        Image.fromarray(arr[:,:,[2,1,0]]).save(base.with_suffix('.png'))
        controller.stop();print('PROBE',arr.shape,flush=True);return
    with lock:h,w=state['frame'].shape[:2]
    logfile=base.with_suffix('.encode.log').open('wb')
    proc=subprocess.Popen(['ffmpeg','-hide_banner','-y','-f','rawvideo','-pixel_format','bgra','-video_size',f'{w}x{h}','-framerate','30','-i','pipe:0','-an','-c:v','h264_nvenc','-preset','p4','-cq','18','-pix_fmt','yuv420p',str(base.with_suffix('.video.mp4'))],stdin=subprocess.PIPE,stdout=logfile,stderr=logfile)
    times=[];audio=[];timing={}
    def video_writer():
        start=timing['t0']
        for n in range(round(a.seconds*30)):
            remaining=start+n/30-time.perf_counter()
            if remaining>0:time.sleep(remaining)
            with lock:arr=state['frame'].copy()
            if arr.shape[:2]!=(h,w):done.set();break
            times.append(time.perf_counter()-start);proc.stdin.write(arr.tobytes())
        proc.stdin.close()
    speaker=sc.default_speaker();loop=sc.get_microphone(id=speaker.id,include_loopback=True);assert loop.isloopback
    with loop.recorder(samplerate=48000,channels=2,blocksize=4800) as rec:
        timing['t0']=time.perf_counter();thread=threading.Thread(target=video_writer);thread.start()
        print('WINDOW_CAPTURE_STARTED',a.id,w,h,flush=True)
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            while time.perf_counter()-timing['t0']<a.seconds and not done.is_set():audio.append(rec.record(numframes=4800))
    thread.join(timeout=20);controller.stop();proc.wait(timeout=30);logfile.close()
    if done.is_set() or proc.returncode:raise SystemExit('Capture changed/closed/failed; reject result')
    data=np.concatenate(audio);sf.write(base.with_suffix('.wav'),data,48000,subtype='PCM_16')
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(base.with_suffix('.video.mp4')),'-i',str(base.with_suffix('.wav')),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart',str(base.with_suffix('.mp4'))],check=True)
    meta={'id':a.id,'hwnd':a.hwnd,'capture':'Windows Graphics Capture, specific Chrome window only','frames_received':state['frames_received'],'frames_encoded':len(times),'width':w,'height':h,'audio_seconds':len(data)/48000,'audio_rms':float(np.sqrt(np.mean(data**2))),'microphone':False,'max_cfr_clock_error_s':max(abs(t-i/30) for i,t in enumerate(times)),'publication':'private draft, source reuse rights unknown'}
    base.with_suffix('.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8');print('WINDOW_CAPTURE_COMPLETE',json.dumps(meta),flush=True)
if __name__=='__main__':main()
