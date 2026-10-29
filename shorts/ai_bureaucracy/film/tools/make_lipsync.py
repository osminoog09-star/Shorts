#!/usr/bin/env python3
"""Виземы Rhubarb для ведущего (только дорожка Димы) + огибающая громкости для ботов.
Запуск из папки film после assemble_voice.py:
  RHUBARB_DIR=/tmp/rhubarb bash ../../../tools/lipsync.sh assets/voice/dima.wav assets/voice/dima_visemes.json
  python3 tools/make_lipsync.py
"""
import json, subprocess, array
from pathlib import Path
F = Path(__file__).resolve().parent.parent / 'assets' / 'voice'
vis = json.loads((F / 'dima_visemes.json').read_text())['visemes']
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(F / 'voice.wav'), '-ac', '1', '-ar', '48000', '-f', 's16le', '-'],
                     capture_output=True, check=True).stdout
pcm = array.array('h', raw); n = len(pcm) // 1600
env = []
for i in range(n):
    seg = pcm[i * 1600:(i + 1) * 1600]
    env.append(round(min(1.0, (sum(x * x for x in seg) / len(seg)) ** 0.5 / 6000), 2))
(F / 'lipsync.js').write_text('window.VIS = ' + json.dumps(vis) + ';\nwindow.ENV = ' + json.dumps(env) + ';\n')
print(len(vis), 'viseme frames,', len(env), 'env frames')
