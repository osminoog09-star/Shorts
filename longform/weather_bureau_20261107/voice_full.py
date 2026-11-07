"""Resumable original narration, approved private Denis ICL, local only.

Each short utterance is validated by the studio job schema and independent ASR.
No failed utterance is eligible for the timeline. No speed change or fallback.
"""
from pathlib import Path
import os, sys, re, json, hashlib, time, subprocess, site
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from denis_voice_tts import check_inputs, asr_match, norm, EXPECTED_VOICE
OUT = Path(r'C:\M1lash\Работа\weather_bureau_20261107\voice_full')
ASSETS = Path(r'C:\M1lash\private\voice_ref')
MODEL = Path(r'C:\M1lash\models\Qwen3-TTS-12Hz-1.7B-Base')
WHISPER = Path.home()/'.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'

def prepare():
    rows=[]; chapter=0; paragraph=0
    for p in (Path(__file__).parent/'narration.md').read_text('utf8').split('\n\n'):
        p=p.strip()
        if p.startswith('## '): chapter+=1; paragraph=0; continue
        if not p or p.startswith('#'): continue
        paragraph+=1
        sentences=re.split(r'(?<=[.!?])\s+',p)
        chunks=[]; buf=''
        for sentence in sentences:
            if len(sentence)>210 and buf:
                chunks.append(buf);buf=''
            while len(sentence)>210:
                cut=sentence.rfind(' ',0,205)
                chunks.append(sentence[:cut]);sentence=sentence[cut:].strip()
            if len(buf)+len(sentence)+1>215:
                chunks.append(buf);buf=sentence
            else: buf=(buf+' '+sentence).strip()
        if buf: chunks.append(buf)
        for n,s in enumerate(chunks):
            rows.append(dict(id=f'c{chapter:02d}_p{paragraph:02d}_u{n:02d}',text=s,rate=1.0,chapter=chapter,paragraph=paragraph))
    OUT.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for i in range(0,len(rows),8):
        job=ROOT/'jobs/voice'/f'weather_bureau_{i//8:02d}.json'
        job.write_text(json.dumps(dict(job_id=job.stem,speaker='denis',voice_id=EXPECTED_VOICE,utterances=[{k:u[k] for k in ('id','text','rate')} for u in rows[i:i+8]]),ensure_ascii=False,indent=2)+'\n','utf8')
        jobs.append(job)
    (Path(__file__).parent/'utterances.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n','utf8')
    print('PREPARED',len(rows),'utterances',len(jobs),'jobs',flush=True)
    return rows,jobs

def main():
    rows,jobs=prepare()
    if '--prepare-only' in sys.argv:return
    subprocess.run([sys.executable,'scripts/voice_private_io.py','verify','--dest',str(ASSETS)],cwd=ROOT,check=True)
    for job in jobs: _,_,params=check_inputs(ASSETS,job,MODEL)
    for k,v in {'TRANSFORMERS_OFFLINE':'1','HF_HUB_DISABLE_TELEMETRY':'1','TOKENIZERS_PARALLELISM':'false','DO_NOT_TRACK':'1'}.items():os.environ[k]=v
    for base in site.getsitepackages():
        for d in Path(base).glob('nvidia/*/bin'):os.environ['PATH']=str(d)+os.pathsep+os.environ['PATH']
    while True:
        free=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).splitlines()[0])
        if free>=(5000 if int(os.environ.get('WEATHER_VOICE_BATCH','6'))<=2 else 7500):break
        print('WAITING_FOR_GPU_OTHER_PROJECT free_MiB',free,flush=True);time.sleep(20)
    import torch, numpy as np, soundfile as sf
    from qwen_tts import Qwen3TTSModel
    from faster_whisper import WhisperModel
    torch.set_num_threads(4)
    torch.set_num_interop_threads(2)
    whisper=WhisperModel(str(WHISPER),device='cpu',compute_type='int8',cpu_threads=3,num_workers=1,local_files_only=True)
    model=Qwen3TTSModel.from_pretrained(str(MODEL),device_map='cuda',dtype=torch.bfloat16,attn_implementation='sdpa',local_files_only=True)
    prompt=model.create_voice_clone_prompt(ref_audio=str(ASSETS/'reference_clean.wav'),ref_text=(ASSETS/'ref_text.txt').read_text('utf8').strip(),x_vector_only_mode=False)
    audio_dir=OUT/'audio';audio_dir.mkdir(exist_ok=True)
    manifest_path=OUT/'manifest.json'
    previous=json.loads(manifest_path.read_text('utf8')) if manifest_path.exists() else {'utterances':[]}
    done={u['id']:u for u in previous['utterances'] if u.get('asr_pass')}
    def save():
        manifest_path.write_text(json.dumps(dict(job_id='weather_bureau_full',speaker='denis',voice_id=EXPECTED_VOICE,engine='qwen3-tts-local',model='Qwen3-TTS-12Hz-1.7B-Base',attention='sdpa',rate=1,owner_hearing='pending',publication='forbidden',utterances=[done[u['id']] for u in rows if u['id'] in done]),ensure_ascii=False,indent=2)+'\n','utf8')
    pending=[]
    for u in rows:
        old=done.get(u['id']); wav=audio_dir/(u['id']+'.wav')
        if old and old['text']==u['text'] and wav.exists() and hashlib.sha256(wav.read_bytes()).hexdigest()==old['sha256']:continue
        done.pop(u['id'],None);pending.append(u)
    args=params.get('inference',{})
    started=time.monotonic()
    def synth(batch,attempt=0):
        torch.manual_seed(733+rows.index(batch[0])+attempt*1000)
        arrs,sr=model.generate_voice_clone(text=[u['text'] for u in batch],language='Russian',voice_clone_prompt=prompt,max_new_tokens=int(args.get('max_new_tokens',400)),temperature=float(args.get('temperature',.55)),top_p=float(args.get('top_p',.85)),repetition_penalty=float(args.get('repetition_penalty',1.05)))
        failed=[]
        for u,arr in zip(batch,arrs):
            arr=np.asarray(arr,dtype=np.float32)
            if arr.ndim!=1 or not np.isfinite(arr).all() or len(arr)<sr//2:raise RuntimeError('Invalid voice '+u['id'])
            wav=audio_dir/(u['id']+'.wav');sf.write(wav,arr,sr,subtype='PCM_16')
            segs,_=whisper.transcribe(str(wav),language='ru',beam_size=4,vad_filter=False,condition_on_previous_text=False)
            recognized=' '.join(s.text.strip() for s in segs).strip()
            score,_=asr_match(u['text'],recognized)
            passed=score>=.8 and len(norm(recognized))>=max(5,int(len(norm(u['text']))*.55))
            print('VOICE',u['id'],round(len(arr)/sr,3),'ASR',round(score,4),'PASS' if passed else 'RETRY','completed',len(done),'elapsed',round(time.monotonic()-started),flush=True)
            item={**u,'source_file':'audio/'+wav.name,'sample_rate':sr,'duration_s':len(arr)/sr,'sha256':hashlib.sha256(wav.read_bytes()).hexdigest(),'asr_text':recognized,'asr_similarity':round(score,4),'asr_pass':passed,'seed_attempt':attempt,'owner_hearing':'pending','voice_id':EXPECTED_VOICE,'speaker':'denis','engine':'qwen3-tts-local'}
            if passed:done[u['id']]=item;save()
            else:
                (OUT/(u['id']+f'_failed_{attempt}.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2),'utf8');failed.append(u)
        for u in failed:
            if attempt>=3:raise RuntimeError('ASR failed after four attempts '+u['id'])
            synth([u],attempt+1)
    batch_size=int(os.environ.get('WEATHER_VOICE_BATCH','6'))
    assert 1<=batch_size<=6
    for i in range(0,len(pending),batch_size):synth(pending[i:i+batch_size])
    assert len(done)==len(rows)
    print('ALL_VOICE_PASS',len(done),'duration_s',sum(u['duration_s'] for u in done.values()),flush=True)

if __name__=='__main__':main()
