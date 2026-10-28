#!/usr/bin/env python3
"""M1lash Genie 4 experimental news Shorts. Copyright-clear procedural visuals.
No substitute voice, no old outro, no automatic publication. Fail closed."""
import asyncio, json, math, os, subprocess, sys, wave, random, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[2]
PACK=ROOT/"shorts"/"genie4_20261028"/"production.json"
WORK=ROOT/"work"/"genie4"
OUT=WORK/"genie4_ru_PREVIEW_QA.mp4"
W,H,FPS,SR=540,960,24,24000
CYAN="#39dcf5"; PINK="#fd54b7"; GOLD="#f5bd67"
WORK.mkdir(parents=True,exist_ok=True)
DATA=json.loads(PACK.read_text(encoding="utf8"))
SHOTS=DATA["shots"]
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def ft(n,b=True):return ImageFont.truetype(BOLD if b else REG,n)
def shell(*args):
    p=subprocess.run([str(i) for i in args],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    if p.returncode:raise RuntimeError("CMD failed: "+" ".join(str(a) for a in args)+"\n"+p.stderr[-1600:])
    return p.stdout.strip()
def probe(p):
    return json.loads(shell("ffprobe","-v","error","-show_entries","format=duration,size","-show_entries","stream=codec_type,codec_name,width,height","-of","json",p))
async def speak():
    import edge_tts
    audios=[]; segments=[]; words=[]; position=.24
    for i,s in enumerate(SHOTS):
        mp=WORK/f"line_{i:02d}.mp3"
        meta=WORK/f"line_{i:02d}.json"
        last=None
        for attempt in range(3):
            try:
                com=edge_tts.Communicate(s["text"],voice="ru-RU-DmitryNeural",rate="+0%",boundary="WordBoundary")
                w=[];received=0
                with mp.open("wb") as f:
                    async for ck in com.stream():
                        if ck["type"]=="audio":f.write(ck["data"]);received+=len(ck["data"])
                        elif ck["type"]=="WordBoundary":
                            w.append(dict(text=ck["text"],start=ck["offset"]/1e7,end=(ck["offset"]+ck["duration"])/1e7))
                if received<3000 or len(w)<4:raise RuntimeError(f"Missing audio or word boundaries: bytes={received}, words={len(w)}")
                last=None;break
            except Exception as e:
                last=e
                mp.unlink(missing_ok=True)
                await asyncio.sleep((attempt+1)*4)
        if last is not None:raise RuntimeError("NO-GO: Approved DmitryNeural voice unavailable, NO fallback: "+repr(last))
        wav=WORK/f"line_{i:02d}.wav"
        shell("ffmpeg","-hide_banner","-loglevel","error","-y","-i",mp,"-ac","1","-ar",str(SR),"-c:a","pcm_s16le",wav)
        with wave.open(str(wav),"rb") as fp:
            a=np.frombuffer(fp.readframes(fp.getnframes()),dtype="<i2").copy()
        if len(a)<SR//2 or np.max(np.abs(a))<100:raise RuntimeError("NO-GO silent TTS segment")
        dur=len(a)/SR
        for v in w:words.append(dict(text=v["text"],start=position+v["start"],end=position+v["end"]))
        segments.append(dict(id=i,text=s["text"],start=position,end=position+dur,voice_id="ru-RU-DmitryNeural",engine="edge-tts",rate="+0%",source_file=str(mp.relative_to(ROOT)),word_count=len(w)))
        audios.extend((np.zeros(round(.11*SR),dtype="<i2") if i else np.zeros(round(.24*SR),dtype="<i2")),a))
        position+=dur+.11
        meta.write_text(json.dumps(dict(voice_id="ru-RU-DmitryNeural",engine="edge-tts",word_count=len(w),words=w),ensure_ascii=False,indent=2))
    audios.append(np.zeros(round(.6*SR),dtype="<i2"))
    samples=np.concatenate(audios)
    # Original synthesised backing score, no third-party music / no licensing claim.
    t=np.arange(len(samples),dtype=np.float64)/SR
    beat=(np.maximum(0,np.sin(2*np.pi*1.55*t))**24)
    ambience=(np.sin(2*np.pi*82.4*t)*.006+np.sin(2*np.pi*123.5*t)*.004+beat*.003)*32767
    arr=np.clip(samples.astype(np.float32)*.84+ambience,-30000,30000).astype("<i2")
    audio=WORK/"speech_music.wav"
    with wave.open(str(audio),"wb") as out:
        out.setnchannels(1);out.setsampwidth(2);out.setframerate(SR);out.writeframes(arr.tobytes())
    info=dict(speaker="dima",voice_id="ru-RU-DmitryNeural",engine="edge-tts",rate="+0%",source_file=str(audio.relative_to(ROOT)),segments=segments,word_count=len(words),music="original procedural waveform",no_substitution=True)
    (WORK/"voice_manifest.json").write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf8")
    (WORK/"words.json").write_text(json.dumps(words,ensure_ascii=False,indent=2),encoding="utf8")
    return segments,words,len(arr)/SR,audio

def wrap(d,txt,face,maxwidth,maxlines=3):
    out=[];cur=""
    for w in txt.split():
        s=(cur+" "+w).strip()
        if d.textbbox((0,0),s,font=face)[2]>maxwidth and cur:
            out.append(cur);cur=w
        else:cur=s
    if cur:out.append(cur)
    return out[:maxlines]

def render_frame(t,segments,words,total):
    idx=next((j for j,s in enumerate(segments) if t<s["end"]+.11),len(segments)-1)
    shot=SHOTS[idx]; seg=segments[idx]
    rnd=random.Random(20261028)
    im=Image.new("RGB",(W,H),"#070e22")
    d=ImageDraw.Draw(im)
    # S7-D25 HUD: layered parallax horizon, procedural geometry, no copied Google demos.
    for yy in range(H):
        k=yy/H
        if yy%3==0:
            color=(int(6+10*k),int(12+14*k),int(31+34*k))
            d.rectangle((0,yy,W,yy+3),fill=color)
    for k in range(70):
        xx=rnd.randrange(W); yy=rnd.randrange(30,700); r=rnd.choice([1,1,2])
        d.ellipse((xx,yy,xx+r,yy+r),fill=CYAN if k%3 else PINK)
    # angular rolling topography parallax
    shift=math.sin(t*.3)*25
    for layer in range(4):
        depth=layer+1; base=410+layer*63
        pts=[(int(x),int(base+38*math.sin(x/72+depth*.9+t*(.13+depth*.03))+11*math.cos(x/31+depth))) for x in range(-20,W+21,18)]
        d.polygon([(0,820)]+pts+[(W,820)],fill=("#112b49","#133456","#153c5f","#194773")[layer])
        d.line(pts,fill=("#185779","#276e9e","#4a92b7","#73b3c6")[layer],width=2)
    # floor grid with moving parallax and perspective
    van=(W//2+int(shift),465)
    for x in range(-W,2*W,43):
        d.line((van[0],van[1],x+int(t*9)%43,H),fill="#24617c",width=2)
    for j in range(1,12):
        yy=int(465+((j/12)**1.55)*550);d.line((0,yy,W,yy),fill="#1d5974",width=1)
    # scene-specific procedural visuals
    kind=shot["shot"];cx=int(W*.52+math.sin(t*.6)*17);cy=420
    if kind in ("prompt_world","world_build","game_developer_joke"):
        for n in range(5):
            rad=45+n*32; p=[(cx+rad*math.cos(2*math.pi*m/6+t*.07+n*.17),cy+rad*.65*math.sin(2*math.pi*m/6+t*.07+n*.17)) for m in range(6)]
            d.line(p+[p[0]],fill=CYAN if n%2 else PINK,width=3)
        for n in range(9):
            x=cx-180+40*n;y=390-55*math.sin(n/1.5+t*.55)
            d.line((x,cy,x,y),fill=CYAN,width=3);d.ellipse((x-5,y-5,x+5,y+5),fill=GOLD)
    elif kind=="weather_control":
        for k in range(42):
            x=(k*71+int(t*230))%(W+100)-50;y=(k*113+int(t*160))%400+230
            d.line((x,y,x-18,y+38),fill=CYAN,width=3)
        d.ellipse((cx-95,260,cx+95,450),outline=PINK,width=6)
        d.arc((cx-75,280,cx+75,430),45,280,fill=GOLD,width=7)
    elif kind=="native_audio":
        for k in range(57):
            x=33+k*9;h=17+abs(math.sin(k*.43+t*7)*math.cos(t*2+k*.12))*170
            d.line((x,450-h/2,x,450+h/2),fill=CYAN if k%3 else PINK,width=4)
    elif kind=="research_preview":
        d.rounded_rectangle((85,286,455,535),18,outline=GOLD,width=7)
        d.text((141,333),"RESEARCH",font=ft(41),fill=GOLD)
        d.text((159,410),"PREVIEW",font=ft(38),fill=CYAN)
        d.line((115,475,422,475),fill=PINK,width=6)
    elif kind=="simulation_limits":
        for k in range(11):
            x=85+k*34;y=350+int(math.sin(t*5+k*.4)*28)
            d.rectangle((x,y,x+18,y+110+(k%3)*15),outline=PINK if k%2 else CYAN,width=3)
            d.line((x-9,y+95,x+25,y-12),fill=GOLD,width=3)
        d.text((180,518),"ERROR 404",font=ft(27),fill=PINK)
    elif kind=="host_cta":
        for n in range(7):
            r=33+n*34
            d.arc((cx-r,cy-r,cx+r,cy+r),int((t*41+n*7)%360),int((t*41+n*7)%360+180),fill=CYAN if n%2 else PINK,width=5)
    # readable HUD title and source, safe subtitle area above host card
    d.rounded_rectangle((21,24,W-21,94),18,fill="#101c37",outline="#2b85ab",width=2)
    d.text((36,41),"M1LASH / TECH  ·  28.10.26",font=ft(20),fill=CYAN)
    bar=d.textbbox((0,0),shot["overlay"],font=ft(27))
    title_f=ft(27) if bar[2]<W-55 else ft(22)
    for k,line in enumerate(wrap(d,shot["overlay"],title_f,W-70,2)):
        d.text((29,124+k*38),line,font=title_f,fill="#fcf9fd",stroke_width=1,stroke_fill="#080f24")
    d.text((27,205),"ХУДОЖЕСТВЕННАЯ РЕКОНСТРУКЦИЯ",font=ft(14),fill="#a5b8cb")
    # true TTS word boundaries drive subtitle display, not word-count per fixed scene
    active=[w for w in words if w["start"]<=t+1.7 and w["end"]>=t-1.5]
    active=active[-12:]
    sub=" ".join(w["text"] for w in active).strip()
    if sub:
        face=ft(23); lines=wrap(d,sub,face,W-76,3)
        top=700-len(lines)*28
        d.rounded_rectangle((19,top-12,W-19,top+len(lines)*30+11),radius=15,fill="#111a36",outline="#277395",width=2)
        for n,line in enumerate(lines): d.text((34,top+n*30),line,font=face,fill="#ffffff")
    d.text((26,748),"Источник: Google DeepMind • TechCrunch",font=ft(15,False),fill="#9bd2e4")
    # bottom left 380 px high is reserved for approved HostCorner transparent overlay
    d.rounded_rectangle((11,782,231,944),radius=24,fill="#0a1128",outline="#285876",width=1)
    # progress scrub
    d.rectangle((0,952,int(W*t/max(1,total)),960),fill=PINK)
    return im

def render_base(segs,words,total):
    path=WORK/"base.mp4"
    cmd=["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","pipe:0","-vf","scale=1080:1920:flags=lanczos,setsar=1","-c:v","libx264","-preset","veryfast","-crf","22","-pix_fmt","yuv420p","-an",str(path)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for j in range(math.ceil(total*FPS)):
            p.stdin.write(render_frame(j/FPS,segs,words,total).tobytes())
        p.stdin.close();err=p.stderr.read().decode();ret=p.wait()
        if ret:raise RuntimeError("base encoding failed "+err[-1000:])
    finally:
        if p.poll() is None:p.kill()
    return path

def main():
    segs,words,total,audio=asyncio.run(speak())
    # Rhubarb lip sync required; complete speech, matching voice ID. HostCorner imports local JSON.
    lips=WORK/"visemes.json"
    shell("bash",ROOT/"tools"/"lipsync.sh",audio,lips)
    lip=json.loads(lips.read_text())
    if len(lip.get("visemes",""))<total*25:raise RuntimeError("NO-GO: incomplete Rhubarb visemes")
    (ROOT/"studio"/"src"/"host_corner.json").write_text(json.dumps(dict(duration=total+0.5,fps=30,visemes=lip["visemes"]),ensure_ascii=False))
    base=render_base(segs,words,total)
    # Reuse the original approved HostCorner.tsx / Narrator2 components, no invented host.
    shell("bash","-lc",f"cd {ROOT/'studio'} && npx remotion render src/index.ts host-corner {WORK/'host.mov'} --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le --frames=0-{int(math.ceil(total*30))-1} --log=error")
    host=WORK/"host.mov"
    if not host.exists() or host.stat().st_size<100000:raise RuntimeError("NO-GO host overlay missing")
    shell("ffmpeg","-y","-v","error","-i",base,"-i",host,"-i",audio,
          "-filter_complex","[0:v]fps=30,format=rgba[bg];[1:v]fps=30,format=rgba[fg];[bg][fg]overlay=0:0:shortest=1:format=auto,format=yuv420p[v]",
          "-map","[v]","-map","2:a:0","-c:v","libx264","-preset","fast","-crf","20","-c:a","aac","-b:a","192k","-ar","48000","-ac","2","-t",str(total),"-movflags","+faststart",OUT)
    meta=probe(OUT)
    video=next(v for v in meta["streams"] if v["codec_type"]=="video")
    assert video["width"]==1080 and video["height"]==1920 and video["codec_name"]=="h264",meta
    assert any(v["codec_type"]=="audio" and v["codec_name"]=="aac" for v in meta["streams"])
    assert 30<float(meta["format"]["duration"])<180 and int(meta["format"]["size"])>1_000_000
    shell("ffmpeg","-v","error","-i",OUT,"-f","null","-")
    frames=[]
    for i,sec in enumerate([0.5,total*.18,total*.4,total*.65,total*.85,total-1]):
        p=WORK/f"qa_{i:02d}.png"
        shell("ffmpeg","-y","-v","error","-ss",f"{sec:.3f}","-i",OUT,"-frames:v","1",p)
        frames.append(str(p.relative_to(ROOT)))
    report=dict(status="AUTOMATED_QA_PASS_HUMAN_REVIEW_PENDING",file=str(OUT.relative_to(ROOT)),duration=meta["format"]["duration"],bytes=int(meta["format"]["size"]),codec="h264+aac",size="1080x1920",full_decode=True,voice_manifest="work/genie4/voice_manifest.json",visemes=True,source="Google DeepMind + TechCrunch 27 Oct 2026",visuals="Original procedural S7-D25 illustrated reconstruction",music="Original procedural audio",frames=frames,human_visual_review=False,human_audio_listening=False,published=False)
    (WORK/"qa.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print("SUCCESS",json.dumps(report,ensure_ascii=False),flush=True)
if __name__=="__main__":main()
