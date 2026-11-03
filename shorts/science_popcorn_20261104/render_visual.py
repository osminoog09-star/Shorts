#!/usr/bin/env python3
"""M1lash popcorn ONLY. Deterministic silent HTML/SVG art preflight.
No TTS, no YouTube, no touching next_four_20261104 or vacuum.
Stages: stills -> manual image inspection -> pilot -> owner voice locally -> full.
"""
from __future__ import annotations
import json, os, sys, math, shutil, subprocess, hashlib, re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
CFG=json.loads((HERE/"spec.json").read_text(encoding="utf-8"))
JOB=json.loads((ROOT/os.environ["M1LASH_JOB_PATH"]).read_text(encoding="utf-8"))
assert CFG["id"]=="science_popcorn_20261104"
assert CFG["voice"]["speaker"]=="denis"
assert CFG["voice"]["engine"]=="qwen3-tts-local"
assert CFG["outro"]["id"]=="denis-v3-music80"
assert JOB.get("mode") in ("stills","pilot","full_silent")
assert JOB.get("preflight_only") is True
assert JOB.get("only_id") == CFG["id"]
OUT=ROOT/"motion-output"/"science_popcorn_20261104"/JOB["mode"]
OUT.mkdir(parents=True,exist_ok=True)

def timeline():
    cuts=[0.0]; caps=[]; segments=[]; at=0.
    for scene in CFG["scenes"]:
        for text in scene["voice"]:
            words=re.findall(r"\S+",text)
            # Provisional reading pace ONLY for graphics. Not aligned to owner voice.
            dur=max(2.1,len(words)*.42)
            segments.append({"start":round(at,5),"end":round(at+dur,5),"text":text,"scene":scene["n"]})
            for off in range(0,len(words),4):
                chunk=words[off:off+4]
                t=at+dur*off/len(words)
                end=at+dur*min(len(words),off+4)/len(words)
                if end-t<.79 and caps:
                    caps[-1]["words"].extend(chunk)
                    caps[-1]["end"]=end
                else: caps.append({"start":t,"end":end,"words":chunk})
            at+=dur+.08
        cuts.append(at)
    return dict(id=CFG["id"],theme="popcorn",label="M1lash · НАУКА",
      headlines=CFG["headlines"],sources=CFG["sources"],segments=segments,
      cuts=cuts,caps=caps,total=at,voice_id=CFG["voice"]["voice_id"],
      engine=CFG["voice"]["engine"],actual_audio=False,
      notes="PROVISIONAL captions; DO NOT publish or claim speech synced")
def ff(args):
    subprocess.run([str(a) for a in args],check=True)
def main():
    data=timeline()
    (OUT/"provisional_visual_timeline.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    from PIL import Image,ImageDraw
    stills=[]; layout=[]
    with sync_playwright() as play:
        chrome=shutil.which("google-chrome") or shutil.which("chromium")
        browser=play.chromium.launch(executable_path=chrome,headless=True,
                   args=["--no-sandbox","--disable-dev-shm-usage","--allow-file-access-from-files"])
        page=browser.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
        errors=[]
        page.on("pageerror",lambda err:errors.append(str(err)))
        page.goto((HERE/"film.html").as_uri())
        page.evaluate("() => document.fonts.ready")
        if not page.evaluate("() => typeof window.seek === 'function' && typeof window.setTimeline === 'function'"):
            raise RuntimeError("Timeline API missing; no frame output accepted")
        page.evaluate("d=>window.setTimeline(d)",data)
        for cap in data["caps"]:
            t=(cap["start"]+cap["end"])/2.
            row=page.evaluate("""t=>{window.seek(t);
              let a=document.querySelector('#cap').getBoundingClientRect();
              let b=document.querySelector('#title').getBoundingClientRect();
              let c=document.querySelector('#cap'),h=document.querySelector('#title');
              return {left:a.left,right:a.right,bottom:a.bottom,title_bottom:b.bottom,
                caption_overflow:c.scrollHeight>c.clientHeight+1,title_overflow:h.scrollWidth>h.clientWidth+1}}""",t)
            if row["left"]<95 or row["right"]>925 or row["bottom"]>1420 or row["title_bottom"]>450 or row["caption_overflow"] or row["title_overflow"]:
                raise RuntimeError("Caption or title out of mobile safe zone: "+str(row))
            layout.append(row)
        for n in range(6):
            t=.6 if n==0 else (data["cuts"][n]+data["cuts"][n+1])/2
            page.evaluate("t=>window.seek(t)",t)
            p=OUT/f"scene_{n+1:02}.jpg";page.screenshot(path=str(p),type="jpeg",quality=89)
            stills.append(p)
        sheet=Image.new("RGB",(900,1104),"#e4e5e8")
        for i,p in enumerate(stills):
            im=Image.open(p);im.thumbnail((300,533));x=i%3*300;y=i//3*552
            sheet.paste(im,(x,y+19))
            ImageDraw.Draw(sheet).text((x+5,y+2),f"SCENE {i+1}",fill="black")
        sheet.save(OUT/"contact_six.jpg",quality=90)
        if JOB["mode"] in ("pilot","full_silent"):
            # Art only: never synthesize an unauthorized voice or add legacy outro.
            dur=min(7.0,data["total"]) if JOB["mode"]=="pilot" else data["total"]
            frames=math.ceil(dur*30)
            mp4=OUT/("motion_pilot_NO_AUDIO.mp4" if JOB["mode"]=="pilot" else "visual_BODY_NO_AUDIO.mp4")
            cmd=["ffmpeg","-v","error","-nostdin","-y","-f","image2pipe","-vcodec","mjpeg",
             "-framerate","30","-i","-","-c:v","libx264","-preset","fast",
             "-crf","20","-threads","2","-pix_fmt","yuv420p","-r","30",
             "-colorspace","bt709","-color_primaries","bt709","-color_trc","bt709",str(mp4)]
            proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
            try:
                for k in range(frames):
                    page.evaluate("t=>window.seek(t)",k/30)
                    proc.stdin.write(page.screenshot(type="jpeg",quality=88))
                proc.stdin.close()
                if proc.wait(): raise RuntimeError("ffmpeg encoder failed")
            except BaseException:
                proc.kill();raise
            ff(["ffmpeg","-v","error","-xerror","-i",mp4,"-f","null","-"])
        browser.close()
        if errors:raise RuntimeError("Browser JS error: "+str(errors[:4]))
    (OUT/"preflight.json").write_text(json.dumps({
     "id":CFG["id"],"mode":JOB["mode"],"run_id":os.environ.get("GITHUB_RUN_ID"),
     "video_duration_provisional":data["total"],"safe_caption_check":"PASS",
     "six_real_stills_generated":True,"voice":"NOT_GENERATED",
     "approved_outro":"NOT_ATTACHED",
     "one_short_only":True,"no_youtube_writes":True,
     "quality":"VISUAL_ONLY_NOT_READY","owner_review":"PENDING"
    },ensure_ascii=False,indent=2)+"\n")
    print("POPCORN_VISUAL_ONLY",JOB["mode"],"6 stills",flush=True)
if __name__=="__main__":
 main()
