from pathlib import Path
import hashlib,json,subprocess,tempfile,re,textwrap,shutil,datetime
from faster_whisper import WhisperModel
ROOT=Path(r'C:\M1lash\Shorts')
P=ROOT/'longform/bot_audit_20261112'
W=Path(r'C:\M1lash\Работа\bot_audit_20261112')
D=Path(r'C:\M1lash\Готово')
MP4=D/'m1lash_bot_audit_ru.mp4'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def secs(s):
    h,m,t=s.split(':')
    return 3600*int(h)+60*int(m)+float(t.replace(',','.'))
def stamp(s):
    n=round(s*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
def captions():
    cues=[]
    for block in (W/'narration.srt').read_text('utf-8').strip().split('\n\n'):
        _, span, *text=block.splitlines()
        start,end=map(secs,span.split(' --> '))
        lines=textwrap.wrap(' '.join(text),width=40,break_long_words=False,break_on_hyphens=False)
        chunks=['\n'.join(lines[k:k+2]) for k in range(0,len(lines),2)]
        weights=[max(1,len(c)) for c in chunks];elapsed=0
        for chunk,n in zip(chunks,weights):
            a=start+(end-start)*elapsed/sum(weights);elapsed+=n;b=start+(end-start)*elapsed/sum(weights)
            cues.append(f'{len(cues)+1}\n{stamp(a)} --> {stamp(b)}\n{chunk}')
    return '\n\n'.join(cues)+'\n'
def main():
    tech=read(W/'final_check.json'); a=read(MP4.with_suffix('.mp4.qa.json'));tl=read(W/'timeline.json')
    assert tech['ok'] and tech['failed']==0 and a['decode_ok'] and not a['problems'] and a['duration']>=1260
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(MP4)],encoding='utf-8'))
    v=next(s for s in probe['streams'] if s['codec_type']=='video')
    assert v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='30/1'
    modeldir=Path(r'C:\M1lash\models\faster-whisper-small')
    model=WhisperModel(str(modeldir) if (modeldir/'model.bin').exists() else 'small',device='cpu',compute_type='int8',local_files_only=True)
    actual={}
    with tempfile.TemporaryDirectory() as td:
        for label,start,stop,token in [('head',0,14,'чек длиннее моего галстука'),('tail',a['body_s']-10,a['body_s'],'кем именно')]:
            wav=Path(td)/(label+'.wav')
            subprocess.run(['ffmpeg','-v','error','-ss',str(start),'-i',str(MP4),'-t',str(stop-start),'-vn','-ac','1','-ar','16000',str(wav)],check=True)
            segs,_=model.transcribe(str(wav),language='ru',beam_size=5,vad_filter=True)
            actual[label]=' '.join(s.text.strip() for s in segs)
            assert token in actual[label].casefold(),(label,actual[label])
    release=dict(title='Притворись ботом: проверка на человека',file=str(MP4),sha256=hashlib.file_digest(MP4.open('rb'),'sha256').hexdigest(),size_bytes=MP4.stat().st_size,duration_seconds=float(probe['format']['duration']),resolution='1920x1080',fps=30,shots=len(tl['scenes']),chapters=tl['chapters'],locations=len({s['location'] for s in tl['scenes']}),voice_utterances=102,voice_seconds=tl['voice_seconds'],check={'failed':tech['failed'],'warnings':[x['check'] for x in tech['checks'] if x['status']=='WARN'],'decode':'PASS','duration':'PASS','loudness':next(x['value'] for x in tech['checks'] if x['check']=='loudness')},actual_mp4_asr=actual,owner_hearing='pending',publication='LOCAL_REVIEW')
    (P/'release.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (D/'m1lash_bot_audit_ru.srt').write_text(captions(),encoding='utf-8')
    shutil.copy2(W/'thumbnail.png',D/'m1lash_bot_audit_thumbnail.png')
    shutil.copy2(P/'PUBLISH.md',D/'m1lash_bot_audit_PUBLISH.md')
    print(json.dumps(release,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
