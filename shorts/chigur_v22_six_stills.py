#!/usr/bin/env python3
"""Chigur V22: SIX different Three.js physical-action stills, NOT the film.

Preflight ONLY. It cannot create narration, film audio, private media or upload.
Runs under the existing motion-render.yml to verify visuals before motion pilot.
"""
from pathlib import Path
import hashlib
import json
import base64
import requests
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"motion-output"
OUT.mkdir(exist_ok=True)
LIB=ROOT/"shorts/chigur_three.min.js"
if not LIB.exists():
    r=requests.get("https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js",timeout=60)
    r.raise_for_status()
    LIB.write_bytes(r.content)
SOURCES=[
    "three_stage_v7.js",
    "three_stage_v11.js",
    "three_stage_v14_atmosphere.js",
    "three_stage_v12_motion.js",
    "three_stage_v15_actions.js",
    "three_stage_v21_editorial.js",
    "three_stage_v22_action.js",
]
SC=ROOT/"longform/chigur/graphics"
SHOTS=[
    {"id":"coin","scene_id":0,"chapter_title":"МОНЕТА НЕ РЕШАЕТ","index":0,"seconds":6},
    {"id":"door","scene_id":1,"chapter_title":"ДВЕРЬ И ТИШИНА","index":17,"seconds":6},
    {"id":"signal","scene_id":2,"chapter_title":"СИГНАЛ ПРИБЛИЖАЕТСЯ","index":20,"seconds":6},
    {"id":"refusal","scene_id":3,"chapter_title":"ОНА ОТКАЗЫВАЕТСЯ","index":22,"seconds":6},
    {"id":"briefcase","scene_id":4,"chapter_title":"ЦЕНЫ НЕТ","index":11,"seconds":6},
    {"id":"road","scene_id":5,"chapter_title":"КОНЕЦ ВСЕЙ ЛОГИКИ","index":25,"seconds":6},
]
results=[]
with sync_playwright() as pw:
    browser=pw.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--disable-dev-shm-usage"])
    page=browser.new_page(viewport={"width":1280,"height":720})
    errors=[]
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.set_content('<html><body style="margin:0"><canvas id="scene"></canvas></body></html>')
    page.add_script_tag(path=str(LIB))
    for name in SOURCES:
        page.add_script_tag(path=str(SC/name))
    page.wait_for_function("window.chigurV22ActionReady===true",timeout=30000)
    for shot in SHOTS:
        payload=page.evaluate("([s,t])=>window.frameV21(s,t,'image/png')",[shot,3.3])
        dest=OUT/("chigur_v22_"+shot["id"]+"_stills_ONLY.png")
        dest.write_bytes(base64.b64decode(payload.split(",",1)[1]))
        if dest.stat().st_size<24000:
            raise RuntimeError("Blank/too-small frame: "+str(dest))
        results.append({
            "scene":shot["id"],"scene_id":shot["scene_id"],
            "relative_path":dest.name,
            "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "bytes":dest.stat().st_size,"sample_at_s":3.3
        })
        print("V22 STILL",shot["id"],dest.stat().st_size,flush=True)
    browser.close()
    if errors:raise RuntimeError("V22 Three.js runtime failure: "+" | ".join(errors))
(OUT/"chigur_v22_six_still_gate.json").write_text(
    json.dumps({"status":"6_physical_stills_not_art_approved",
                "film_frames":False,"film_audio":False,"voice":False,
                "human_visual_review":"PENDING","motion_pilot":"NOT_STARTED",
                "results":results},ensure_ascii=False,indent=2)+"\n",
    encoding="utf8"
)
print("Six V22 stills emitted for actual human visual evaluation; not final.")
