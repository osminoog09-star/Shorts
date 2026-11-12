from pathlib import Path
import csv,hashlib,json,math
import numpy as np
import soundfile as sf
HERE=Path(__file__).parent
OUT=Path(r'C:\M1lash\Работа\bot_audit_20261112')
def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))
def ts(x):
    m=round(x*1000)
    return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'
def main():
    plan=read(HERE/'staging.json')
    specs=read(HERE/'utterances.json')
    meta=read(OUT/'voice_full/manifest.json')
    rows={x['id']:x for x in meta['utterances']}
    assert len(rows)==len(specs)
    cursor=0
    sr=24000
    audio=[]
    scenes=[]
    captions=[]
    chapters=[]
    previous=None
    paragraph_shot=0
    modes=['wide','medium','insert','portrait','reaction']
    for i,spec in enumerate(specs):
        item=rows[spec['id']]
        chapter,p=spec['chapter'],spec['paragraph']
        assert item['asr_pass'] and item['rate']==1.0 and item['text']==spec['text']
        wav=OUT/'voice_full'/item['source_file']
        assert hashlib.file_digest(wav.open('rb'),'sha256').hexdigest()==item['sha256']
        a,rate=sf.read(wav,dtype='float32')
        assert rate==sr and a.ndim==1 and np.max(np.abs(a))<.9999
        chapter_start=previous is None or previous[0]!=chapter
        paragraph_start=previous!=(chapter,p)
        gap=.45 if chapter_start else .28 if paragraph_start else .12
        if paragraph_start:paragraph_shot=0
        if chapter_start:
            chapters.append({'chapter':chapter,'title':plan['chapterTitles'][chapter-1],'start':cursor/sr})
        audio.append(np.zeros(round(gap*sr),dtype='float32'))
        t0=cursor/sr
        cursor+=round(gap*sr)
        a0=cursor/sr
        audio.append(a)
        cursor+=len(a)
        t1=cursor/sr
        captions.append(f'{i+1}\n{ts(a0)} --> {ts(t1)}\n{item["text"]}')
        location,other,prop,action=plan['chapters'][chapter-1][p-1].split('/')
        count=max(1,round((t1-t0)/6.2))
        for j in range(count):
            ix=len(scenes)
            pattern=modes if p%2 else ['wide','insert','reaction','portrait','medium']
            mode=pattern[paragraph_shot%len(pattern)]
            if chapter==1 and p==1:mode=['insert','portrait','reaction','medium'][paragraph_shot%4]
            if scenes and scenes[-1]['mode']==mode:mode='medium' if mode!='medium' else 'reaction'
            paragraph_shot+=1
            if action=='unlock' and 'Диод' in spec['text'] and j==count-1:mode='pilot'
            scenes.append(dict(id=f's{ix+1:03d}',serial=ix,chapter=chapter,paragraph=p,location=location,other=other,prop=prop,action=action,mode=mode,start=t0+(t1-t0)*j/count,end=t0+(t1-t0)*(j+1)/count))
        previous=(chapter,p)
    duration=cursor/sr
    assert duration+6.6>=1260, f'Natural speech cut too short: {duration:.2f}'
    tl=dict(duration_s=duration,fps=30,chapters=chapters,scenes=scenes,voice_seconds=sum(r['duration_s'] for r in rows.values()))
    (OUT/'timeline.json').write_text(json.dumps(tl,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'narration.srt').write_text('\n\n'.join(captions)+'\n',encoding='utf-8')
    sf.write(OUT/'narration_raw.wav',np.concatenate(audio),sr,subtype='PCM_24')
    with (OUT/'shotlist.csv').open('w',encoding='utf-8-sig',newline='') as f:
        c=csv.DictWriter(f,fieldnames=list(scenes[0]));c.writeheader();c.writerows(scenes)
    print('ACTUAL_TIMELINE',duration,len(scenes),len(rows),flush=True)
if __name__=='__main__':main()
