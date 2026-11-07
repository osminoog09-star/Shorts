"""Private final evidence for the locally recorded three-film batch."""
import argparse,json,hashlib,subprocess,os,site
from pathlib import Path
ROOT=Path(r'C:\M1lash\Работа\kino_new_20261107')
EXPECTED={'009':'Меню','010':'Апгрейд','011':'Престиж'}
def run(args):
 p=subprocess.run(list(map(str,args)),capture_output=True)
 if p.returncode:raise RuntimeError(p.stderr.decode('utf8','replace')[-1500:])
 return p.stdout

def main(key):
 f=Path(r'C:\M1lash\Готово')/f'm1lash_kino_{key}_ru.mp4';out=ROOT/f'kino{key}'
 probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',f]));v=next(s for s in probe['streams'] if s['codec_type']=='video')
 assert (v['width'],v['height'],v['r_frame_rate'],v['pix_fmt'])==(1080,1920,'30/1','yuv420p')
 assert float(probe['format']['duration'])<=59
 run(['ffmpeg','-v','error','-xerror','-i',f,'-f','null','-'])
 assembly=json.loads(Path(str(f)+'.qa.json').read_text(encoding='utf8'));assert not assembly['problems']
 voice=out/'final_title.wav';run(['ffmpeg','-v','error','-y','-ss',assembly['body_s']+assembly['outro_s'],'-i',f,'-vn','-ac','1','-ar','16000',voice])
 for base in site.getsitepackages():
  for d in Path(base).glob('nvidia/*/bin'):os.environ['PATH']=str(d)+os.pathsep+os.environ['PATH']
 from faster_whisper import WhisperModel
 modelpath=Path.home()/'.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'
 m=WhisperModel(str(modelpath),device='cuda',compute_type='float16',local_files_only=True)
 segs,_=m.transcribe(str(voice),language='ru',beam_size=5,vad_filter=False,condition_on_previous_text=False)
 text=' '.join(s.text for s in segs).strip();match=EXPECTED[key].casefold() in text.casefold()
 report={'file':str(f),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size,'duration':float(probe['format']['duration']),'full_decode':'pass','assembler':assembly,'final_spoken_title_asr':text,'title_asr_matches':match,'owner_hearing':'pending; model has no audio-input support','rights':'unverified','publication':'private local review only'}
 (out/'final_evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(report,ensure_ascii=False),flush=True)
 if not match:raise RuntimeError('Final title ASR does not match')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('id',choices=EXPECTED);main(p.parse_args().id)
