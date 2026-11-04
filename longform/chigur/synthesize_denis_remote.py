import os
os.environ.update({'ORT_DISABLE_TELEMETRY':'1','HF_HUB_DISABLE_TELEMETRY':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','DO_NOT_TRACK':'1','GRADIO_ANALYTICS_ENABLED':'False','TOKENIZERS_PARALLELISM':'false','OMP_NUM_THREADS':'4'})
from pathlib import Path
import json,time,hashlib,sys,shutil
import numpy as np,torch,soundfile as sf
from qwen_tts import Qwen3TTSModel
ROOT=Path('/home/user/chigur_private');OUT=ROOT/'segments';OUT.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'voice_chunks_denis_film_only.json').read_text())
assert manifest['speaker']=='denis' and len(manifest['utterances'])==38
start=time.monotonic();torch.set_num_threads(min(4,os.cpu_count() or 1));torch.set_num_interop_threads(1)
model=Qwen3TTSModel.from_pretrained('/home/user/chigur_qwen17_model',device_map='cpu',dtype=torch.bfloat16,attn_implementation='eager',local_files_only=True)
ref='До работы десять минут. А кофемашина требует доказать, что я проснулся.'
prompt=model.create_voice_clone_prompt(ref_audio=str(ROOT/'coffee_voice_ref_from_owner_approved_public_video.wav'),ref_text=ref,x_vector_only_mode=False)
print('READY',round(time.monotonic()-start,1),flush=True)
test=ROOT/'d01_p02_test.wav';existing=OUT/'d01_p02.wav'
if test.is_file() and not existing.is_file():shutil.copy2(test,existing)
for i,u in enumerate(manifest['utterances']):
 name=u['id'];p=OUT/(name+'.wav');meta=OUT/(name+'.json')
 if p.is_file() and p.stat().st_size>20000:
  if not meta.exists():
   y,s=sf.read(p);meta.write_text(json.dumps({'id':name,'text':u['text'],'duration':round(len(y)/s,4),'sample_rate':s,'speaker':'denis','voice_id':'denis-qwen3tts-reference-v1','engine':'qwen3-tts-local','model':'Qwen3-TTS-12Hz-1.7B-Base','source':'approved coffee_v8 video voice isolated 0-5.5s','asr_status':'pending','owner_hearing':'pending'},ensure_ascii=False))
  print('SKIP',name,flush=True);continue
 if time.monotonic()-start>690:
  print('BATCH_TIME_CAP',round(time.monotonic()-start,1),'next',name,flush=True);break
 t=time.monotonic();torch.manual_seed(810+i)
 print('SYNTH',i+1,'/',len(manifest['utterances']),name,'words',u['word_count'],flush=True)
 try:
  with torch.no_grad():wav,sr=model.generate_voice_clone(text=u['text'],language='Russian',voice_clone_prompt=prompt,max_new_tokens=700,temperature=.55,top_p=.85,repetition_penalty=1.05)
  y=np.asarray(wav[0],dtype=np.float32)
  if len(y)<int(sr*.6):raise ValueError('too short audio')
  sf.write(p,y,sr,subtype='PCM_16')
  meta.write_text(json.dumps({'id':name,'text':u['text'],'duration':round(len(y)/sr,4),'sample_rate':sr,'speaker':'denis','voice_id':'denis-qwen3tts-reference-v1','engine':'qwen3-tts-local','model':'Qwen3-TTS-12Hz-1.7B-Base','source':'approved coffee_v8 video voice isolated 0-5.5s','asr_status':'pending','owner_hearing':'pending','source_sha256':hashlib.sha256(p.read_bytes()).hexdigest()},ensure_ascii=False,indent=2))
  print('DONE',name,round(len(y)/sr,2),'sec in',round(time.monotonic()-t,1),'s',flush=True)
 except Exception as e:
  print('ERROR',name,repr(e),flush=True)
  raise
print('BATCH_END','generated_total',len(list(OUT.glob('*.wav'))),'/',len(manifest['utterances']),'elapsed',round(time.monotonic()-start,1),flush=True)
