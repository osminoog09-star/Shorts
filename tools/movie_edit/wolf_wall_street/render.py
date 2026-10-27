#!/usr/bin/env python3
"""M1lash film edit: Wolf of Wall Street (2013). Private draft, not publication."""
import argparse, json, subprocess, shutil, wave
from pathlib import Path
import numpy as np

def cmd(*v):
    print("+", " ".join(map(str,v)),flush=True)
    subprocess.run([str(x) for x in v],check=True)

def info(p):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(p)]))

def quote_times(src):
    from faster_whisper import WhisperModel
    model=WhisperModel("base.en",device="cpu",compute_type="int8")
    segments,_=model.transcribe(str(src),language="en",word_timestamps=True,beam_size=3)
    words=[(w.word.strip().lower().strip(".,!?"),float(w.start)) for s in segments for w in (s.words or [])]
    found=[]
    for i,(w,t) in enumerate(words):
        if w in ("leaving","leavin") and any("not"==a or "i'm"==a for a,_ in words[max(0,i-5):i]):
            found.append(t)
    print("Quote locations:",found,flush=True)
    return found

def stamp(t):
    t=max(0,t);return f"{int(t//3600)}:{int(t//60)%60:02}:{t%60:05.2f}"

def subs(path,length,beats):
    head="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Main,DejaVu Sans,78,&H0000FFFF,&H00FFFFFF,&H00000000,&H98000000,1,0,0,0,100,100,2,0,1,5,3,5,45,45,550,1
Style: Punch,DejaVu Sans,88,&H0000C7FF,&H00FFFFFF,&H00000000,&H98000000,1,0,0,0,100,100,2,0,1,5,4,5,45,45,550,1
Style: White,DejaVu Sans,56,&H00FFFFFF,&H00FFFFFF,&H00000000,&H98000000,1,0,0,0,100,100,2,0,1,4,2,5,45,45,550,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
"""
    e=[]
    def add(a,b,style,words):
        if a>=length or b<=a:return
        effect=r"{\fad(100,120)\fscx135\fscy135\t(0,180,\fscx100\fscy100)}"
        e.append(f"Dialogue: 0,{stamp(a)},{stamp(min(b,length))},{style},,0,0,0,,{effect}{words}")
    add(.2,2.5,"White","ОН УЖЕ ПОПРОЩАЛСЯ...")
    add(2.6,5.2,"Main","НО ВДРУГ ПЕРЕДУМАЛ")
    for i,t in enumerate(beats):
        add(max(0,t-.7),min(length,t+.7),"Punch" if i==2 else "Main",
            ["Я НИКУДА","НЕ УХОЖУ!","Я, БЛЯТЬ, НЕ УХОЖУ!"][i])
    path.write_text(head+"\n".join(e)+"\n",encoding="utf-8")

def music(p,length,beats):
    rate=48000;n=int(length*rate)
    t=np.arange(n,dtype=np.float32)/rate
    x=(np.sin(2*np.pi*55*t)*.14+np.sin(2*np.pi*82.41*t)*.065)
    x*=np.minimum(1,t)*np.minimum(1,np.maximum(0,length-t))
    for b in beats:
        ix=int(max(0,b)*rate);k=min(n-ix,rate)
        if k<=0:continue
        tt=np.arange(k,dtype=np.float32)/rate
        x[ix:ix+k]+=.25*np.exp(-tt*7)*np.sin(2*np.pi*(100*tt-18*tt**2))
    with wave.open(str(p),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate)
        wav.writeframes((np.clip(x,-1,1)*32767).astype("<i2").tobytes())

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",required=True);ap.add_argument("--output",required=True)
    ap.add_argument("--outro",default="videos/m1lash_outro_short_ru.mp4")
    ap.add_argument("--work",default="work/wolf")
    ap.add_argument("--no-asr",action="store_true")
    a=ap.parse_args();wd=Path(a.work);wd.mkdir(parents=True,exist_ok=True)
    src=Path(a.source).resolve();out=Path(a.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    dur=float(info(src)["format"]["duration"])
    try: times=[] if a.no_asr else quote_times(src)
    except Exception as ex: print("ASR failure:",repr(ex));times=[]
    if len(times)>=2:
        q=times[-3:];start=max(0,q[0]-17);end=min(dur,max(q[-1]+4.5,start+27))
    else:
        start=max(0,dur-37);end=min(dur,start+35);q=[start+20,start+24,start+28]
    if end-start>43:start=end-43
    length=end-start;beats=[max(0,min(length-.2,t-start)) for t in q]
    print("Edit:",start,end,beats,flush=True)
    ass=wd/"subs.ass";subs(ass,length,beats)
    bed=wd/"bed.wav";music(bed,length,beats)
    film=wd/"film.mp4"
    vf=f"scale=1200:2134:force_original_aspect_ratio=increase,crop=1200:2134,zoompan=z='min(1.04+on*0.00009,1.14)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=1080x1920:fps=30,ass={ass.as_posix()},eq=contrast=1.06:saturation=1.11,format=yuv420p"
    flt=f"[0:v]{vf}[v];[0:a]volume=1[a0];[1:a]volume=.34[a1];[a0][a1]amix=inputs=2:duration=first:normalize=0,alimiter=limit=.90[a]"
    cmd("ffmpeg","-hide_banner","-loglevel","error","-y","-ss",f"{start:.3f}","-t",f"{length:.3f}","-i",src,"-i",bed,
        "-filter_complex",flt,"-map","[v]","-map","[a]","-r",30,"-c:v","libx264","-preset","veryfast","-crf",20,
        "-c:a","aac","-ar",48000,"-ac",2,"-b:a","192k",film)
    outro=Path(a.outro)
    if outro.is_file():
        normalized=wd/"outro.mp4"
        cmd("ffmpeg","-v","error","-y","-i",outro,"-vf","scale=1080:1920,fps=30,format=yuv420p",
            "-af","aresample=48000","-c:v","libx264","-preset","veryfast","-crf",20,"-c:a","aac","-ar",48000,"-ac",2,normalized)
        manifest=wd/"list.txt"
        manifest.write_text(f"file '{film.resolve()}'\nfile '{normalized.resolve()}'\n")
        cmd("ffmpeg","-v","error","-y","-f","concat","-safe",0,"-i",manifest,"-c","copy","-movflags","+faststart",out)
    else:
        print("Warning: host outro missing. Rendering film-only preview.")
        shutil.copyfile(film,out)
    meta={"movie":"The Wolf of Wall Street (2013)","segment":[start,end],"quote_beats":beats,
        "outro_present":outro.is_file(),"output_duration":float(info(out)["format"]["duration"]),
        "status":"DRAFT ONLY - NOT PUBLISHED - RIGHTS REVIEW REQUIRED","full_visual_QA":False}
    (wd/"qa.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2))
    for t in [1.5,length/2,max(.3,length-.6)]:
        cmd("ffmpeg","-v","error","-y","-ss",str(t),"-i",out,"-frames:v",1,wd/f"frame_{t:.1f}.jpg")
    print("DONE",str(out),out.stat().st_size,flush=True)

if __name__=="__main__":main()
