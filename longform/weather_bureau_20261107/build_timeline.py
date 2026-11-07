"""Build the film from verified real speech lengths; no estimated final timing."""
from pathlib import Path
import json, re, csv, hashlib
import numpy as np
import soundfile as sf
HERE=Path(__file__).parent
OUT=Path(r'C:\M1lash\Работа\weather_bureau_20261107')

def main():
    expected=json.loads((HERE/'utterances.json').read_text('utf8'))
    manifest=json.loads((OUT/'voice_full/manifest.json').read_text('utf8'))
    got={u['id']:u for u in manifest['utterances']}
    assert len(got)==len(expected),'Incomplete narration'
    blueprint=json.loads((HERE/'blueprint.json').read_text('utf8'))['chapters']
    audio=[];groups={}; cursor=0; subs=[];sr=24000
    for i,u in enumerate(expected):
        item=got[u['id']];assert item['asr_pass'] and item['text']==u['text'] and item['rate']==1
        wav=OUT/'voice_full'/item['source_file']
        assert hashlib.sha256(wav.read_bytes()).hexdigest()==item['sha256']
        a,rate=sf.read(wav,dtype='float32');assert rate==sr and a.ndim==1
        key=(u['chapter'],u['paragraph']);g=groups.setdefault(key,dict(start=cursor/sr,utterances=[],text=[]))
        g['utterances'].append(dict(id=u['id'],start=cursor/sr,end=(cursor+len(a))/sr,text=u['text']))
        subs.append(g['utterances'][-1]);g['text'].append(u['text']);audio.append(a);cursor+=len(a)
        nxt=expected[i+1] if i+1<len(expected) else None
        gap=.10 if nxt and (nxt['chapter'],nxt['paragraph'])==key else .30
        if nxt and nxt['chapter']!=u['chapter']:gap=.65
        audio.append(np.zeros(round(gap*sr),np.float32));cursor+=len(audio[-1]);g['end']=cursor/sr
    voice=np.concatenate(audio)
    sf.write(OUT/'narration_raw.wav',voice,sr,subtype='PCM_16')
    scenes=[]
    for (ch,par),g in groups.items():
        row=blueprint[ch-1]['rows'][par-1].split('/')
        loc,other,prop,action,emotion=row
        duration=g['end']-g['start'];count=max(3,round(duration/6))
        modes=['wide','insert','medium','reaction','insert','reverse','environment']
        if (ch,par)==(7,7):count=3
        for j in range(count):
            bounds=[g['start']+duration*k/count for k in range(count+1)]
            if (ch,par)==(7,7):
                first=min(12,duration*.6);bounds=[g['start'],g['start']+first,g['start']+first+(duration-first)/2,g['end']]
            start,end=bounds[j:j+2]
            mode=modes[j%len(modes)]
            if j==0 and par==1 and ch in [3,4,5,7]:mode='environment'
            if j==2 and par%3==0:mode='reverse'
            if prop=='umbrella' and mode=='insert':prop_shot='contract' if ch==1 else 'board'
            elif prop=='gauge' and mode=='insert':prop_shot='tube' if ch==5 else 'gauge'
            else:prop_shot=prop
            words=[]
            for u in g['utterances']:
                ws=u['text'].split()
                for k,w in enumerate(ws):
                    tm=u['start']+(u['end']-u['start'])*(k+.5)/len(ws)
                    if start<=tm<end:words.append(w)
            other_action='telescope' if ch==8 and par>=6 and other=='child' else 'inspect' if other=='nora' else 'box' if other=='woman' and prop=='flowers' else 'read' if other in ['chief','manager'] else 'explain' if other=='client' else 'idle'
            sc=dict(id=f'c{ch:02d}p{par:02d}s{j:02d}',chapter=ch,paragraph=par,start=round(start,6),end=round(end,6),location=loc,mode=mode,other=other,otherAction=other_action,action=action if mode!='reaction' else 'idle',emotion=emotion,prop=prop_shot,variant=2 if ch==8 else 1 if ch==7 else 3 if (ch,par)==(4,1) and j>0 else 0,spoken_words=' '.join(words),transition='cut',reason='Событие и реакция в исходном абзаце',source_utterances=[u['id'] for u in g['utterances']])
            sc['propVariant']=2 if (ch,par)==(3,3) and prop=='jar' else 2 if (ch,par)==(3,4) and prop=='ledger' else 3 if (ch,par) in [(3,5),(5,6),(5,7)] and prop=='ledger' else 4 if (ch,par)==(6,7) and prop=='ledger' else 2 if prop=='contract' and ch==1 and par<=2 else 1 if prop=='contract' and ch==4 else 3 if prop=='contract' and ch==6 else 2 if prop=='map' and (ch,par)==(5,3) else 1 if prop=='ledger' and ch>=6 else int(ch>=7)
            if (ch,par,j)==(1,1,0):sc['mode']='hook'
            if (ch,par,j)==(2,4,0):sc['mode']='environment';sc['location']='city'
            if (ch,par)==(7,7) and j==0:sc['mode']='pilot'
            if (ch,par)==(8,8) and j==count-1:sc['action']='closedUmbrella';sc['mode']='wide'
            if par==1 and j==0:sc['chapterTitle']=blueprint[ch-1]['title']
            if ch==1 and par==1 and j==0:sc['chapterTitle']=''
            scenes.append(sc)
    timeline=dict(title='POV: ты работаешь в городе, где продают погоду',fps=30,width=1920,height=1080,duration_s=len(voice)/sr,voice_rate=1,voice_id=manifest['voice_id'],owner_hearing='pending',scenes=scenes,utterances=subs)
    (HERE/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2)+'\n','utf8')
    fields='shot_id scene_id start_s end_s spoken_words location shot_size action emotion camera foreground middle background lighting props sfx transition asset_refs status'.split()
    with (HERE/'shotlist.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for s in scenes:
            writer.writerow(dict(shot_id=s['id'],scene_id=f"c{s['chapter']:02d}p{s['paragraph']:02d}",start_s=s['start'],end_s=s['end'],spoken_words=s['spoken_words'],location=s['location'],shot_size=s['mode'],action=s['action'],emotion=s['emotion'],camera='establish / optical push 1–3% / distinct close-up',foreground=s['prop'] if s['mode']=='insert' else 'руки и реквизит',middle='герой + '+s['other'],background='native Canvas '+s['location'],lighting='diffuse overcast / warm practical lamps',props=s['prop'],sfx='quiet rain / room tone',transition='cut',asset_refs='src/art.cjs;src/actors.cjs;src/props.cjs',status='TIMED_REAL_VOICE'))
    def stamp(t):
        ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
    (OUT/'narration.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(s['start'])} --> {stamp(s['end'])}\n{s['text']}" for i,s in enumerate(subs))+'\n','utf8')
    assert len(voice)/sr>=1254,'Narrative too short: expand original story, never slow or pad'
    print('TIMELINE_REAL_VOICE',round(len(voice)/sr,3),'seconds',len(scenes),'shots',len(groups),'paragraphs')

if __name__=='__main__':main()
