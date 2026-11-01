#!/usr/bin/env python3
"""Audit approved outro decoded PCM against final MP4. Never modifies either.
--video-start must be independently observed first video frame of outro.
"""
import argparse,json,subprocess
import numpy as np

def audio(path,start,seconds,rate=12000):
    cmd=['ffmpeg','-hide_banner','-nostdin','-v','error','-ss',f'{start:.5f}',
         '-t',f'{seconds:.5f}','-i',str(path),'-vn','-ac','1','-ar',str(rate),
         '-f','f32le','-']
    return np.frombuffer(subprocess.check_output(cmd),dtype='<f4').copy()

def compare(approved,final,video_start):
    rate=12000;lo=max(0,video_start-.5)
    ref=audio(approved,0,4.5).astype(np.float64)
    target=audio(final,lo,5.6).astype(np.float64)
    a,b=int(.5*rate),int(3.5*rate);tmpl=ref[a:b]
    n=1<<((len(tmpl)+len(target)-2).bit_length())
    corr=np.fft.irfft(np.fft.rfft(target,n)*np.fft.rfft(tmpl[::-1],n),n)
    idx=int(np.argmax(corr[len(tmpl)-1:len(target)]))
    onset=lo+(idx-a)/rate;seg=target[idx:idx+len(tmpl)]
    similarity=float(np.dot(seg,tmpl)/(np.linalg.norm(seg)*np.linalg.norm(tmpl)))
    delta=round(1000*(onset-video_start),2)
    return {'audio_onset_s':round(onset,5),'video_onset_s':video_start,
            'audio_minus_video_ms':delta,'pcm_correlation':round(similarity,5),
            'sync_gate':'PASS' if similarity>.995 and abs(delta)<50 else 'FAIL'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('approved_outro');p.add_argument('final_mp4')
    p.add_argument('--video-start',type=float,required=True)
    a=p.parse_args()
    value=compare(a.approved_outro,a.final_mp4,a.video_start)
    print(json.dumps(value,ensure_ascii=False))
    raise SystemExit(0 if value['sync_gate']=='PASS' else 1)
