#!/usr/bin/env python3
"""Six literal 3D storyboard stills, before the motion pilot. PRIVATE REVIEW."""
import base64
import subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright
import requests

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/"motion-output"
ART.mkdir(exist_ok=True)
OUT=ROOT/"videos/chigur_three_storyboard_PRIVATE_REVIEW.mp4"
LIB=ROOT/"shorts/chigur_three.min.js"
if not LIB.is_file():
    url="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
    response=requests.get(url,timeout=45)
    response.raise_for_status()
    LIB.write_bytes(response.content)

print('storyboard setup')
