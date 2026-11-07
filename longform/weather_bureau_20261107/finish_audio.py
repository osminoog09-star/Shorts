"""Original procedural underscore and quiet room/rain Foley. Private stems only."""
from pathlib import Path
import json, subprocess
import numpy as np
import soundfile as sf
HERE=Path(__file__).parent;OUT=Path(r'C:\M1lash\Работа\weather_bureau_20261107')

def main():
    tl=json.loads((HERE/'timeline.json').read_text('utf8'))
    voice,sr=sf.read(OUT/'narration_raw.wav',dtype='float32')
    active=voice[np.abs(voice)>.008];rms=float(np.sqrt(np.mean(active**2)))
    n=len(voice);music=np.zeros(n,np.float32);atmos=np.zeros(n,np.float32)
    # Slow original suspended triads. No borrowed score, loops or external audio.
    chords=[(146.832,220,293.665),(130.813,196,293.665),(164.814,220,329.628),(146.832,195.998,293.665)]
    rng=np.random.default_rng(20261107)
    block=round(24*sr)
    for j,start in enumerate(range(0,n,round(20*sr))):
        length=min(block,n-start);t=np.arange(length,dtype=np.float32)/sr
        env=np.minimum(1,t/3)*np.minimum(1,(length/sr-t)/3)
        pad=np.zeros(length,np.float32)
        for k,f in enumerate(chords[j%len(chords)]):pad+=np.sin(2*np.pi*f*t+.6*k)*(.7+.3*np.sin(t*.13+k))
        music[start:start+length]+=pad*env
    music*=rms*.015/max(1e-6,float(np.sqrt(np.mean(music**2))))
    # Low-level atmosphere follows locations, with half-second boundary fades.
    for s in tl['scenes']:
        a=round(s['start']*sr);b=min(n,round(s['end']*sr));length=b-a
        if length<=0:continue
        t=np.arange(length,dtype=np.float32)/sr
        env=np.minimum(1,t/.5)*np.minimum(1,(length/sr-t)/.5)
        outside=s['location'] in ['street','bureau_front','canal','roof','city']
        if outside:
            noise=rng.normal(0,1,length).astype(np.float32)
            # Gentle band-limited rain texture, not harsh full-band hiss.
            from scipy.signal import butter,sosfilt
            noise=sosfilt(butter(2,[400,3500],btype='bandpass',fs=sr,output='sos'),noise).astype(np.float32)
            noise/=max(.01,float(np.sqrt(np.mean(noise**2))))
            atmos[a:b]+=noise*env*rms*.004
        elif s['location'] in ['pump','control','vault','laundry']:
            atmos[a:b]+=(np.sin(t*2*np.pi*72)+.3*np.sin(t*2*np.pi*144))*env*rms*.0025
    fade=np.minimum(1,np.arange(n,dtype=np.float32)/(sr*1.2))*np.minimum(1,np.arange(n,0,-1,dtype=np.float32)/(sr*1.8))
    music*=fade;atmos*=fade
    sf.write(OUT/'original_music.wav',music,sr,subtype='PCM_16')
    sf.write(OUT/'original_atmosphere.wav',atmos,sr,subtype='PCM_16')
    sf.write(OUT/'mix_raw.wav',voice+music+atmos,sr,subtype='PCM_24')
    p=subprocess.run(['ffmpeg','-v','info','-y','-i',str(OUT/'mix_raw.wav'),'-af','loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json','-ar','48000','-ac','2','-c:a','pcm_s24le',str(OUT/'mix.wav')],capture_output=True,text=True,encoding='utf8')
    (OUT/'mix_loudnorm.log').write_text(p.stderr,'utf8');assert p.returncode==0
    report=dict(voice_active_rms=rms,music_rms=float(np.sqrt(np.mean(music**2))),atmosphere_rms=float(np.sqrt(np.mean(atmos**2))),music_ratio_to_voice=float(np.sqrt(np.mean(music**2)))/rms,source='Original code-generated tones and noise; no reference audio',owner_hearing='pending',outro='Excluded: append approved untouched horizontal v7 separately')
    (OUT/'audio_mix_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n','utf8')
    print('AUDIO_MIX_READY',len(voice)/sr,report['music_ratio_to_voice'])

if __name__=='__main__':main()
