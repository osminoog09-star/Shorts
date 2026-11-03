#!/usr/bin/env python3
"""Chigur V15: six rendered 3D stills + an eight-second motion pilot.

Review-only graphics with synthetic silent track. NO copyrighted film frames,
NO actor lines, no original movie sound, no full movie and never a publishable MP4.
Runs in the existing motion-render.yml preflight route.
"""
import base64
import json
import os
import subprocess
from pathlib import Path
from shutil import rmtree
import requests
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"motion-output"
OUT.mkdir(exist_ok=True)
LIB=ROOT/"shorts/chigur_three.min.js"
if not LIB.is_file():
    r=requests.get("https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",timeout=60)
    r.raise_for_status()
    LIB.write_bytes(r.content)
SCENES=[
    "longform/chigur/graphics/three_stage_v7.js",
    "longform/chigur/graphics/three_stage_v11.js",
    "longform/chigur/graphics/three_stage_v14_atmosphere.js",
    "longform/chigur/graphics/three_stage_v12_motion.js",
    "longform/chigur/graphics/three_stage_v12_overlay.js",
    "longform/chigur/graphics/three_stage_v15_actions.js",
]
frames=OUT/"chigur_v15_pilot_frames"
frames.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":960,"height":540},device_scale_factor=1)
    errors=[]
    page.on("pageerror",lambda err: errors.append(str(err)))
    page.set_content('<html><body style="margin:0;background:#070a10"><canvas id="scene"></canvas></body></html>')
    page.add_script_tag(path=str(LIB))
    for path in SCENES:
        page.add_script_tag(path=str(ROOT/path))
    page.wait_for_function("window.ready===true&&!!window.chigurV15Info",timeout=30000)
    for i in range(6):
        png=page.evaluate("(t)=>window.frame(t)",i*6+3.1)
        file=OUT/f"chigur_v15_scene_{i+1:02}.png"
        file.write_bytes(base64.b64decode(png.split(",",1)[1]))
        if file.stat().st_size<50000:raise RuntimeError(f"V15 bad 3D still {file.name}")
        print("STILL",file.name,file.stat().st_size,flush=True)
    # Shot A 4s: physical coin. Shot B 4s: a door opens, threat unseen.
    for n in range(240):
        t=n/30 if n<120 else 6+(n-120)/30
        png=page.evaluate("(t)=>window.frame(t)",t)
        (frames/f"f{n:04d}.png").write_bytes(base64.b64decode(png.split(",",1)[1]))
    if errors:raise RuntimeError("Playwright error: "+" | ".join(errors))
    browser.close()
pilot=OUT/"chigur_v15_coin_and_door_8sec_NO_MOVIE_NO_DIALOGUE.mp4"
subprocess.run(["ffmpeg","-hide_banner","-nostdin","-y","-v","error",
                "-framerate","30","-i",str(frames/"f%04d.png"),
                "-f","lavfi","-i","anullsrc=r=48000:cl=stereo",
                "-t","8.0","-vf","scale=1920:1080:flags=lanczos",
                "-c:v","libx264","-preset","veryfast","-crf","20",
                "-r","30","-pix_fmt","yuv420p",
                "-c:a","aac","-b:a","96k","-movflags","+faststart",str(pilot)],check=True)
subprocess.run(["ffmpeg","-hide_banner","-v","error","-xerror","-i",str(pilot),"-f","null","-"],check=True)
probe=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_entries",
                    "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
                    "-of","json",str(pilot)]))
v=[s for s in probe["streams"] if s["codec_type"]=="video"]
a=[s for s in probe["streams"] if s["codec_type"]=="audio"]
if not (len(v)==1 and len(a)==1 and v[0]["width"]==1920 and v[0]["height"]==1080
        and v[0]["r_frame_rate"]=="30/1" and abs(float(probe["format"]["duration"])-8)<.2):
    raise RuntimeError("INVALID V15 pilot streams")
if (frames/"f0000.png").read_bytes()==(frames/"f0119.png").read_bytes():
    raise RuntimeError("Coin has no motion")
if (frames/"f0120.png").read_bytes()==(frames/"f0239.png").read_bytes():
    raise RuntimeError("Door has no motion")
print("V15_PREVIEW_DECODE_PASS",pilot.stat().st_size,flush=True)
rmtree(frames)
(OUT/"chigur_v15_evidence.json").write_text(json.dumps({
    "version":"V15","script":"longform/chigur/graphics/three_stage_v15_actions.js",
    "stills":6,"motion_seconds":8,"movie_footage":False,
    "movie_dialogue":False,"qa":"technical_decode_only",
    "human_visual_inspection":"NOT_YET","intended_for_upload":False,
    "source_rights":"own_threejs_reconstruction_not_a_film_clip"
},indent=2)+"\n")
marker=ROOT/"reports/research/chigur_v15_pilot_run.json"
marker.write_text(json.dumps({"run_id":os.environ.get("GITHUB_RUN_ID"),"stage":"V15",
  "status":"six_stills_and_8sec_pilot_generated_visual_qa_pending",
  "full_movie_assembled":False},indent=2)+"\n")
