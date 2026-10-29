#!/usr/bin/env python3
"""Наложение ведущего (прозрачные webm-окна из host/) на готовый фильм: python3 overlay_host.py film.mp4 out.mp4"""
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
src, out = sys.argv[1], sys.argv[2]
wins = json.loads((ROOT / 'host_windows.json').read_text())
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', src]
for w in wins:
    cmd += ['-itsoffset', str(w['fa'] / 30), '-c:v', 'libvpx-vp9', '-i', str(ROOT / w['file'])]
fl = []; cur = '0:v'
for i, w in enumerate(wins):
    nxt = f'v{i}'
    fl.append(f"[{cur}][{i + 1}:v]overlay=0:0:eof_action=pass:enable='between(t,{w['fa'] / 30 - 0.05:.3f},{w['fb'] / 30 + 0.1:.3f})'[{nxt}]")
    cur = nxt
cmd += ['-filter_complex', ';'.join(fl), '-map', f'[{cur}]', '-map', '0:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '21', '-maxrate', '3200k', '-bufsize', '6400k',
        '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'copy', '-movflags', '+faststart', out]
subprocess.run(cmd, check=True)
print('overlay ok', out)
