#!/usr/bin/env python3
"""Render a non-public VISUAL ONLY proof of the Genie 4 original HUD scenes.
Not a finished Shorts: no voice, music, lip-sync or approved host. No release claim."""
import json, shutil
from pathlib import Path
import render_genie4 as m

def main():
    seconds_per_scene=2.5
    segments=[];words=[]
    for i,shot in enumerate(m.SHOTS):
        a=i*seconds_per_scene;b=(i+1)*seconds_per_scene
        segments.append(dict(id=i,start=a,end=b))
        sample=shot["text"].split()[:13]
        for n,w in enumerate(sample):
            start=a+.1+n*(2.2/max(1,len(sample)))
            words.append(dict(text=w,start=start,end=start+.15))
    total=len(m.SHOTS)*seconds_per_scene
    base=m.render_base(segments,words,total)
    preview=m.WORK/"GENIE4_S7D25_VISUAL_ONLY_NO_AUDIO.mp4"
    shutil.copyfile(base,preview)
    frames=[]
    for i in range(len(m.SHOTS)):
        out=m.WORK/f"visual_shot_{i+1:02d}.png"
        m.shell("ffmpeg","-v","error","-y","-ss",str(i*seconds_per_scene+1.25),"-i",preview,"-frames:v","1",out)
        frames.append(str(out.relative_to(m.ROOT)))
    meta=m.probe(preview)
    vid=next(x for x in meta["streams"] if x["codec_type"]=="video")
    assert (vid["width"],vid["height"])==(1080,1920)
    assert not any(x["codec_type"]=="audio" for x in meta["streams"])
    m.shell("ffmpeg","-v","error","-i",preview,"-f","null","-")
    qa=dict(status="VISUAL_PREVIEW_ONLY",for_review=True,voice="MISSING -- EDGE TTS NoAudioReceived",lip_sync=False,host="Not rendered",music="not included",audio=False,publish_ready=False,frames=frames,file=str(preview.relative_to(m.ROOT)),full_decode=True,source="original procedural illustration, not Google demo")
    (m.WORK/"visual_preview_qa.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2))
    print(json.dumps(qa,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
