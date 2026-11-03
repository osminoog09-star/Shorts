from pathlib import Path
import json,subprocess,hashlib,sys
import numpy as np,soundfile as sf
B=Path(sys.argv[1]).resolve();B.mkdir(parents=True,exist_ok=True);S=Path(sys.argv[2]).resolve();source=S/'01_Serena_trim.wav';male=S/'Denis_answer_norm.wav'
variants=[
 {'id':'01_low_calm','label':'Ниже и спокойнее','pitch_semitones':-1.,'tempo':.97,'eq':'highpass=f=85,equalizer=f=190:t=q:w=0.8:g=1.2,equalizer=f=380:t=q:w=1:g=-1.2,equalizer=f=3200:t=q:w=0.9:g=-1.0,treble=g=-1.5:f=6000'},
 {'id':'02_soft_clear','label':'Мягкая и ясная','pitch_semitones':-.25,'tempo':1.,'eq':'highpass=f=90,equalizer=f=260:t=q:w=1:g=-1.3,equalizer=f=2300:t=q:w=0.8:g=1.1,treble=g=-2.5:f=5500'},
 {'id':'03_light_quick','label':'Легче и быстрее','pitch_semitones':.4,'tempo':1.08,'eq':'highpass=f=100,equalizer=f=300:t=q:w=1:g=-1.4,equalizer=f=2900:t=q:w=1:g=0.8,treble=g=-1:f=6500'}]
def run(args):return subprocess.run(args,capture_output=True,check=True)
def loud(path):
 r=run(['ffmpeg','-hide_banner','-i',str(path),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-']);s=r.stderr.decode();return json.JSONDecoder().raw_decode(s[s.rfind('{'):])[0]
target=float(loud(male)['input_i']);ma,ms=sf.read(male);assert ms==48000
for v in variants:
 fac=2**(v['pitch_semitones']/12);raw=B/(v['id']+'_filtered.wav');female=B/(v['id']+'_female.wav')
 filt=f"rubberband=tempo={v['tempo']}:pitch={fac}:formant=preserved:pitchq=quality:transients=smooth:detector=soft,"+v['eq']
 run(['ffmpeg','-v','error','-y','-i',str(source),'-af',filt,'-ar','48000','-ac','2',str(raw)]);before=loud(raw);gain=target-float(before['input_i']);run(['ffmpeg','-v','error','-y','-i',str(raw),'-af',f'volume={gain}dB,alimiter=limit=0.794328:attack=1:release=60:level=false:latency=1','-ar','48000','-c:a','pcm_s24le',str(female)])
 a,sr=sf.read(female);assert sr==ms;pair=np.concatenate([np.zeros((round(sr*.15),2)),a,np.zeros((round(sr*.32),2)),ma,np.zeros((round(sr*.3),2))]);wav=B/('M1lash_Serena_'+v['id']+'_with_Denis.wav');mp3=wav.with_suffix('.mp3');sf.write(wav,pair,sr,subtype='PCM_24');run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','libmp3lame','-b:a','192k',str(mp3)]);run(['ffmpeg','-v','error','-xerror','-i',str(mp3),'-f','null','-']);j=loud(mp3);assert float(j['input_tp'])<=-1;v.update({'file':mp3.name,'gain_db':gain,'pair_lufs':float(j['input_i']),'pair_true_peak':float(j['input_tp']),'female_duration':len(a)/sr,'female_lufs':float(loud(female)['input_i']),'male_reference_unchanged':True});print(v,flush=True)
(B/'manifest.json').write_text(json.dumps({'source_voice':'Serena','source_engine':'Qwen3-TTS-0.6B-CustomVoice','method':'DSP variants of same actual original female speech; no new emotion or pronunciation synthesis','male_source_sha256':hashlib.sha256(male.read_bytes()).hexdigest(),'male_lufs':target,'female_expected_text':json.loads((S/'script.json').read_text())['female_question'],'variants':variants,'owner_choice':'pending'},ensure_ascii=False,indent=2))
