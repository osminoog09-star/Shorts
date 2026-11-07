"""Owner-private source inspection. Never writes movie media/transcripts into Git."""
import os, json, subprocess, argparse
from pathlib import Path
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['DO_NOT_TRACK']='1'
ROOT=Path(r'C:\M1lash\Работа\kino_batch_20261107')

def run(args):
    p=subprocess.run([str(a) for a in args],capture_output=True)
    if p.returncode: raise RuntimeError(p.stderr.decode('utf-8','replace')[-2000:])
    return p.stdout

def contact_range(name,start,end,label):
    from PIL import Image,ImageDraw
    import math
    count=math.ceil((end-start)/1.5); rows=math.ceil(count/5)
    canvas=Image.new('RGB',(1800,rows*180),'#141722');pen=ImageDraw.Draw(canvas)
    for i in range(count):
        t=min(end-.05,start+i*1.5+.2);f=ROOT/f'{label}_{i:02d}.jpg'
        run(['ffmpeg','-v','error','-y','-ss',t,'-i',ROOT/(name+'.mp4'),'-frames:v','1','-vf','crop=1258:524:0:278,scale=350:146',f])
        im=Image.open(f);canvas.paste(im,((i%5)*360,(i//5)*180));pen.text(((i%5)*360+5,(i//5)*180+150),str(round(t,2)),fill='white')
    canvas.save(ROOT/(label+'_shots.jpg'),quality=92)

def inspect(name,asr=False):
    src=ROOT/(name+'.mp4'); out=ROOT/name; out.mkdir(exist_ok=True)
    probe=json.loads(run(['ffprobe','-v','error','-show_streams','-show_format','-of','json',src]))
    (out/'probe.json').write_text(json.dumps(probe,indent=2),encoding='utf-8')
    dur=float(probe['format']['duration']); print(name,'duration',dur,flush=True)
    from PIL import Image,ImageDraw
    canvas=Image.new('RGB',(1440,6*195),'#141722'); pen=ImageDraw.Draw(canvas)
    for i in range(24):
        t=(i+.5)*dur/24
        frame=out/f'frame_{i:02d}.jpg'
        run(['ffmpeg','-v','error','-y','-ss',t,'-i',src,'-frames:v','1','-vf','scale=350:165:force_original_aspect_ratio=decrease',frame])
        im=Image.open(frame).convert('RGB'); x=(i%4)*360+(360-im.width)//2;y=(i//4)*195
        canvas.paste(im,(x,y));pen.text(((i%4)*360+8,y+169),f'{t:.2f}s',fill='white')
    canvas.save(out/'contact.jpg',quality=88)
    if not asr:return
    wav=out/'speech.wav'
    run(['ffmpeg','-v','error','-y','-i',src,'-vn','-ac','1','-ar','16000',wav])
    from faster_whisper import WhisperModel
    import site
    for base in site.getsitepackages():
        for d in Path(base).glob('nvidia/*/bin'):
            os.environ['PATH']=str(d)+os.pathsep+os.environ['PATH']
    modelpath=Path.home()/'.cache/huggingface/hub/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120'
    model=WhisperModel(str(modelpath),device='cuda',compute_type='float16',cpu_threads=8,local_files_only=True)
    segments,info=model.transcribe(str(wav),language='ru',beam_size=3,word_timestamps=True,vad_filter=True,condition_on_previous_text=False)
    rows=[]
    for s in segments:
        row={'start':round(s.start,3),'end':round(s.end,3),'text':s.text,'words':[{'start':round(w.start,3),'end':round(w.end,3),'text':w.word} for w in s.words or []]}
        rows.append(row)
        print(f'{s.start:.2f} {s.end:.2f} {s.text}',flush=True)
        (out/'transcript.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print('ASR_COMPLETE',name,len(rows),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('name');p.add_argument('--asr',action='store_true');p.add_argument('--range',nargs=3);p.add_argument('--root',type=Path);a=p.parse_args()
    if a.root:ROOT=a.root
    if a.range:contact_range(a.name,float(a.range[0]),float(a.range[1]),a.range[2])
    else:inspect(a.name,a.asr)
