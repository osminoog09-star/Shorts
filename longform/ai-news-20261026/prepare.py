import json,subprocess,math,hashlib,sys
from pathlib import Path
B=Path(__file__).resolve().parent
RH='/workspace/scratch/45719f0e4ec5/rhubarb/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb'
def run(a):subprocess.run(a,check=True)
def dur(p):return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)],text=True))
def one(s,short=False):
 p=B/'audio'/(s['id']+'.mp3');m=p.with_suffix('.json');meta=json.loads(m.read_text());assert meta['text']==s['text'],s['id']+' narration text mismatch';o=B/'work'/s['id'];o.mkdir(exist_ok=True)
 tempo=1.15 if short else 1.06;lead=.20;tail=.30
 out=o/'voice.wav'
 run(['ffmpeg','-v','error','-y','-i',str(p),'-af',f'atempo={tempo},adelay=200,apad=pad_dur={tail},loudnorm=I=-17:TP=-2:LRA=7','-ac','1','-ar','48000',str(out)])
 d=math.ceil(dur(out)*30)/30
 # Exact frame-aligned sound duration, including a short natural inter-scene transition.
 run(['ffmpeg','-v','error','-y','-i',str(out),'-af',f'apad,atrim=duration={d}','-c:a','pcm_s16le',str(o/'aligned.wav')])
 words=[{'w':w['w'],'start':w['start']/tempo+lead,'end':w['end']/tempo+lead} for w in meta['words']]
 vis=''
 if s['id'] in ['hook','kimi_fact','reddit_fact','security_fact','elvis_fact','end','short_0']:
  run(['ffmpeg','-v','error','-y','-i',str(o/'aligned.wav'),'-ac','1','-ar','16000',str(o/'rhubarb.wav')])
  run([RH,'-q','--threads','2','-r','phonetic','-f','json','-o',str(o/'mouth.json'),str(o/'rhubarb.wav')])
  cues=json.loads((o/'mouth.json').read_text());vv=['X']*(int(d*30)+3)
  for cue in cues['mouthCues']:
   for f in range(int(cue['start']*30),min(len(vv),int(cue['end']*30)+1)):vv[f]=cue['value']
  vis=''.join(vv)
 row={**s,'words':words,'duration':d,'tempo':tempo,'voice':'Dmitry','visemes':vis,'narration_sha256':hashlib.sha256(p.read_bytes()).hexdigest()};(o/'scene.json').write_text(json.dumps(row,ensure_ascii=False,indent=2));print('PREPARED',s['id'],d,flush=True)
if __name__=='__main__':
 j=json.loads((B/'script.json').read_text());wanted=sys.argv[1:] or [s['id'] for s in j['scenes']+j['short']]
 for s in j['scenes']+j['short']:
  if s['id'] in wanted:one(s,s in j['short'])
