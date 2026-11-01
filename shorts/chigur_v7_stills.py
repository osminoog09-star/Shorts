#!/usr/bin/env python3
# Six review stills from Three.js, no movie media.
from pathlib import Path
import base64,subprocess,requests
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'motion-output'; ART.mkdir(exist_ok=True)
LIB=ROOT/'shorts/chigur_three.min.js'
if not LIB.is_file():
    response=requests.get('https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js',timeout=60)
    response.raise_for_status()
    LIB.write_bytes(response.content)
src=ROOT/'longform/chigur/graphics/three_stage_v7.js'
with sync_playwright() as pw:
    browser=pw.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl'])
    page=browser.new_page(viewport={'width':960,'height':540})
    errors=[]
    page.on('pageerror',lambda err:errors.append(str(err)))
    page.set_content('<body style="margin:0"><canvas id="scene"></canvas></body>')
    page.add_script_tag(path=str(LIB))
    page.add_script_tag(path=str(src))
    page.wait_for_function('window.ready===true',timeout=30000)
