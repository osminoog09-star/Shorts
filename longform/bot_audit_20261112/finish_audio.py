from pathlib import Path
import json
import numpy as np
import soundfile as sf
OUT=Path(r'C:\M1lash\Работа\bot_audit_20261112')
def main():
    tl=json.loads((OUT/'timeline.json').read_text('utf-8'))
    voice,sr=sf.read(OUT/'narration_raw.wav',dtype='float32')
    rms=float(np.sqrt(np.mean(voice[np.abs(voice)>.008]**2)))
    fx=np.zeros(len(voice),np.float32)
    def tone(start,seconds,freq,level,decay):
        a=round(start*sr)
        n=min(round(seconds*sr),len(fx)-a)
        if n<=0:return
        x=np.arange(n,dtype='float32')/sr
        env=np.minimum(1,x/.009)*np.exp(-x*decay)*np.minimum(1,(seconds-x)/.018)
        fx[a:a+n]+=(np.sin(2*np.pi*freq*x)+.2*np.sin(2*np.pi*freq*1.78*x))*env*(rms*level)
    played=set()
    for s in tl['scenes']:
        key=(s['chapter'],s['paragraph'])
        if s['mode']=='pilot':
            t=s['start']+(s['end']-s['start'])*.42
            tone(t,.24,622,.17,9)
            tone(t+.08,.24,810,.095,10)
        elif s['mode']=='insert' and key not in played and s['prop'] in ('coffee','reader','receipt','phone'):
            played.add(key)
            t=s['start']+.7
            tone(t,.19,124 if s['prop']=='coffee' else 430,.11,14)
    sf.write(OUT/'effects.wav',fx,sr,subtype='PCM_24')
    sf.write(OUT/'mix.wav',np.clip(voice+fx,-.99,.99),sr,subtype='PCM_24')
    print('MIX',len(voice)/sr,'original effects, no background score',flush=True)
if __name__=='__main__':main()
