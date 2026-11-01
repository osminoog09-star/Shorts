#!/usr/bin/env python3
# Six review stills from Three.js, no movie media.
from pathlib import Path
import base64,subprocess,requests
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'motion-output'; ART.mkdir(exist_ok=True)
