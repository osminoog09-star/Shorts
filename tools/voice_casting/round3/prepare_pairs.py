import os
os.environ['ORT_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['DO_NOT_TRACK']='1'
from pathlib import Path
import sys
import json,subprocess,hashlib,difflib,re
import numpy as np,soundfile as sf
from faster_whisper import WhisperModel
B=Path(sys.argv[1]).resolve();male=B.parent/'cohost_casting/Denis_answer_norm.wav';ma,SR=sf.read(male);assert SR==48000
expected='Подожди, а почему искусственный интеллект так уверенно отвечает, даже когда ошибается?'
ids=['01_kokoro_sveta','02_kokoro_masha','03_designed_warm','04_designed_clear'];model=WhisperModel('small',device='cpu',compute_type='int8',cpu_threads=4,local_files_only=True)
def run(a):return subprocess.run(a,capture_output=True,check=True)
def loud(p):
 r=run(['ffmpeg','-hide_banner','-i',str(p),'-af','loudnorm=I=-16:TP=-1:LRA=11:print_format=json','-f','null','-']);s=r.stderr.decode();return json.JSONDecoder().raw_decode(s[s.rfind('{'):])[0]
target=float(loud(male)['input_i']);audit=[]
for ident in ids:
 file=B/(ident+'_raw.wav');a,sr=sf.read(file);a=np.asarray(a).reshape(-1);win=round(sr*.02);rms=np.array([np.sqrt(np.mean(a[k:k+win]**2)) for k in range(0,len(a),win)]);active=rms>max(.004,float(rms.max())*.03);ix=np.flatnonzero(np.convolve(active.astype(int),np.ones(3,dtype=int),'same')>=2)
 assert len(ix),'no speech';st=max(0,int(ix[0])*win-round(sr*.10));en=min(len(a),int(ix[-1]+1)*win+round(sr*.15));trim=B/(ident+'_trim.wav');sf.write(trim,a[st:en],sr)
 pcm=np.frombuffer(run(['ffmpeg','-v','error','-i',str(trim),'-ar','16000','-ac','1','-f','f32le','-']).stdout,np.float32);ss,info=model.transcribe(pcm,beam_size=5,condition_on_previous_text=False,word_timestamps=True);ss=list(ss);actual=' '.join(s.text for s in ss);norm=lambda t:' '.join(re.findall('[а-яё0-9]+',t.lower()));score=difflib.SequenceMatcher(None,norm(actual),norm(expected)).ratio();print('ASR',ident,score,actual,flush=True)
 if score<.96:raise RuntimeError('TEXT NO-GO '+ident+' '+actual)
 gain=target-float(loud(trim)['input_i']);female=B/(ident+'_female.wav');run(['ffmpeg','-v','error','-y','-i',str(trim),'-af',f'volume={gain}dB,alimiter=limit=0.794328:attack=1:release=60:level=false:latency=1','-ar',str(SR),'-ac','2','-c:a','pcm_s24le',str(female)]);a,sr=sf.read(female)
 pair=np.concatenate([np.zeros((round(SR*.15),2)),a,np.zeros((round(SR*.32),2)),ma,np.zeros((round(SR*.3),2))]);w=B/('M1lash_new_pair_'+ident+'.wav');out=w.with_suffix('.mp3');sf.write(w,pair,SR,subtype='PCM_24');run(['ffmpeg','-v','error','-y','-i',str(w),'-c:a','libmp3lame','-b:a','192k','-metadata','comment='+((B/'Dialogs_LICENSE.md').read_text() if 'kokoro' in ident else 'Original synthetic voice designed with Qwen3-TTS-1.7B-VoiceDesign; no reference person cloned.'),str(out)]);run(['ffmpeg','-v','error','-xerror','-i',str(out),'-f','null','-']);j=loud(out);assert float(j['input_tp'])<=-1
 check,sr=sf.read(w);start=round(SR*.15)+len(a)+round(SR*.32);diff=float(np.max(np.abs(check[start:start+len(ma)]-ma)));assert diff==0.
 audit.append({'id':ident,'file':out.name,'actual':actual,'similarity':score,'female_duration':len(a)/SR,'female_gain_db':gain,'lufs':float(j['input_i']),'true_peak':float(j['input_tp']),'male_pcm_difference':diff,'decode':True});print('PAIR',ident,'complete',flush=True)
(B/'pairs_qa.json').write_text(json.dumps({'expected':expected,'male_sha256':hashlib.sha256(male.read_bytes()).hexdigest(),'male_reference_lufs':target,'pairs':audit,'owner_hearing_review':'pending'},ensure_ascii=False,indent=2));print('FOUR_NEW_PAIRS_DONE',flush=True)
