#!/usr/bin/env python3
"""Ведущий в углу (16:9): окна по timeline.json + виземы Rhubarb из голоса Димы → studio/src/host_long.json и host_windows.json.
Окна: вся s02 и s14, первые ~5 с у начала глав. Запуск: cd longform/roman-concrete && python3 make_host.py"""
import json, subprocess, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent; REPO = ROOT.parents[1]
FPS = 30; VO = 0.6
CHAPTERS = ['s03', 's04c', 's06', 's09', 's10c', 's12', 's13', 's13c']

tl = json.loads((ROOT / 'timeline.json').read_text())
sc = {s['id']: s for s in tl['scenes']}
D = tl['duration']; N = int(round(D * FPS)) + 1
vis = ['X'] * N
wins = []


def words(sid):
    return json.loads((REPO / f'media/tts/roman_concrete/{sid}.json').read_text())['words']


def wt(sid, w, fb):
    for x in words(sid):
        if x['w'].lower().strip('«»,.!?:;—').startswith(w):
            return VO + x['start']
    return fb


def lips(sid):
    out = Path('/tmp') / f'vis_{sid}.json'
    subprocess.run([str(REPO / 'tools/lipsync.sh'), str(REPO / f'media/tts/roman_concrete/{sid}.mp3'), str(out)], check=True, capture_output=True)
    v = json.loads(out.read_text())['visemes']
    f0 = int(round((sc[sid]['start'] + VO) * FPS))
    for i, c in enumerate(v):
        if 0 <= f0 + i < N: vis[f0 + i] = c


s = sc['s02']; lips('s02')
wins.append({'a': round(s['start'] + 0.25, 2), 'b': round(s['start'] + s['dur'] - 0.4, 2), 'poses': [[0, 'talk'], [round(wt('s02', 'сегодня', 3), 2), 'point'], [round(wt('s02', 'сегодня', 3) + 3, 2), 'talk'], [round(wt('s02', 'мифа', 18) - 0.2, 2), 'laugh'], [round(wt('s02', 'поехали', 22), 2), 'point']]})
for sid in CHAPTERS:
    s = sc[sid]; lips(sid)
    wins.append({'a': round(s['start'] + 0.45, 2), 'b': round(s['start'] + 5.8, 2), 'poses': [[0, 'talk'], [2.6, 'point']]})
s = sc['s14']; lips('s14')
wins.append({'a': round(s['start'] + 0.25, 2), 'b': round(s['start'] + s['dur'] - 0.2, 2), 'poses': [[0, 'talk'], [round(wt('s14', 'как', 8) - s['start'] * 0 , 2), 'shrug'], [round(wt('s14', 'следующей', 15), 2), 'point'], [round(wt('s14', 'подпишись', 22), 2), 'point'], [round(wt('s14', 'спасибо', 27), 2), 'laugh']]})
# позы задаются во времени окна (от a)
for w in wins:
    sid = None
for w, sid in zip(wins, ['s02'] + CHAPTERS + ['s14']):
    base = w['a'] - sc[sid]['start']
    w['poses'] = [[0, w['poses'][0][1]]] + [[round(max(0.0, p - base), 2), n] for p, n in w['poses'][1:]]
data = {'fps': FPS, 'duration': round(D, 3), 'visemes': ''.join(vis), 'windows': wins}
(REPO / 'studio/src/host_long.json').write_text(json.dumps(data, ensure_ascii=False))
(ROOT / 'host_windows.json').write_text(json.dumps([{'a': w['a'], 'b': w['b'], 'fa': int(round(w['a'] * FPS)), 'fb': int(round(w['b'] * FPS)), 'file': f'host/win_{i:02d}.webm'} for i, w in enumerate(wins)], indent=1))
print('windows', len(wins), 'host seconds', round(sum(w['b'] - w['a'] for w in wins), 1))
