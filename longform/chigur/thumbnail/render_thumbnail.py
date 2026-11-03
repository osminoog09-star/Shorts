#!/usr/bin/env python3
"""Render approved 'ВЫБОРА НЕТ?' Chigur thumbnail using HTML/CSS + Playwright.

Local authorized film reference image ONLY. Never commit original movie frame
or generated movie thumbnail to public git; upload thumbnail privately after QA.
"""
import argparse,base64
from pathlib import Path
from playwright.sync_api import sync_playwright

ap=argparse.ArgumentParser()
ap.add_argument("--image",required=True,help="local original movie frame, JPEG")
ap.add_argument("--out",required=True)
a=ap.parse_args()
pic=Path(a.image)
if not pic.exists() or pic.suffix.lower() not in (".jpg",".jpeg"):
    raise ValueError("Expected local JPEG still")
url="data:image/jpeg;base64,"+base64.b64encode(pic.read_bytes()).decode("ascii")
html="""<!doctype html><html lang="ru"><meta charset="utf-8"><style>
*{box-sizing:border-box}
body,html{width:1280px;height:720px;margin:0;overflow:hidden;background:#05070d;color:#fff}
.bg{position:absolute;inset:-10%;background:url('""" +url+ """') 64% 58%/cover no-repeat;
filter:brightness(.94) saturate(.79) contrast(1.13)}
.gradient{position:absolute;inset:0;
background:linear-gradient(90deg,rgba(4,7,12,.96),rgba(5,9,15,.86) 26%,
rgba(5,9,15,.36) 55%,rgba(0,0,0,.02)),linear-gradient(0deg,rgba(0,0,0,.75),transparent 30%)}
.vignette{position:absolute;inset:0;box-shadow:inset 0 0 120px 60px rgba(0,0,0,.42)}
.brand{position:absolute;left:62px;top:62px;color:#e9c293;font:bold 29px system-ui;letter-spacing:4px}
.rule{position:absolute;left:62px;top:128px;width:82px;height:7px;background:#e9a85a}
.title{position:absolute;left:57px;top:233px;width:780px;white-space:nowrap;
font:1000 132px/.98 system-ui,Arial;letter-spacing:-5px;text-shadow:0 8px 23px rgba(0,0,0,.63)}
.title span{display:block}.title span:last-child{color:#f2ae65;font-size:157px;margin-top:13px}
.footer{position:absolute;left:66px;bottom:56px;letter-spacing:4px;
font:900 24px system-ui;color:#e0e7ef}
</style><body>
<div class="bg"></div><div class="gradient"></div><div class="vignette"></div>
<div class="brand">АНТОН ЧИГУР</div><div class="rule"></div>
<div class="title"><span>ВЫБОРА</span><span>НЕТ?</span></div>
<div class="footer">M1LASH · КИНОРАЗБОР</div>
</body></html>"""
out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
with sync_playwright() as pw:
 browser=pw.chromium.launch(args=["--no-sandbox","--disable-dev-shm-usage"])
 page=browser.new_page(viewport={"width":1280,"height":720},device_scale_factor=1)
 page.set_content(html)
 page.screenshot(path=str(out))
 browser.close()
print("PRIVATE thumbnail only",out,out.stat().st_size)
