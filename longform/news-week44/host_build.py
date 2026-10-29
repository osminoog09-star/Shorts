#!/usr/bin/env python3
"""1) voice: audio/voice_only.wav — только реплики Димы (для Rhubarb; у Светы рот ведущего закрыт);
2) host <visemes.json>: studio/src/host_long.json — окна ведущего: вступление, первая реплика Димы в каждой главе, финал."""
import json, subprocess, sys
import numpy as np
SR = 16000
TL = json.load(open('timeline.json')); D = TL['duration']
TTS = '../../media/tts/news_week44/'
if sys.argv[1] == 'voice':
    buf = np.zeros(int(D * SR) + SR)
    for c in TL['chapters']:
        for l in c['lines']:
            if l['sp'] != 'D': continue
            raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f"{TTS}{l['id']}.mp3", '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
            x = np.frombuffer(raw, dtype=np.float32); a = int((c['start'] + l['s']) * SR); buf[a:a + len(x)] += x[:len(buf) - a]
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', 'audio/voice_only.wav'], input=pcm.tobytes(), check=True)
    print('voice ok', D)
else:
    vis = json.load(open(sys.argv[2]))['visemes']
    wins = []
    for c in TL['chapters']:
        if c['id'] in ('c0', 'c9'):
            a = c['start'] + 0.3; b = c['start'] + c['dur'] - 0.4
            wins.append({'a': a, 'b': b, 'poses': [[0, 'talk'], [4, 'point'], [9, 'talk'], [max(10, b - a - 7), 'laugh' if c['id'] == 'c9' else 'talk']]})
        else:
            d = next((l for l in c['lines'] if l['sp'] == 'D'), None)
            if d: a = c['start'] + d['s'] - 0.3; wins.append({'a': a, 'b': a + min(9.0, d['vdur'] + 0.8), 'poses': [[0, 'talk'], [3.5, 'point']]})
    json.dump({'fps': 30, 'duration': round(D, 3), 'visemes': vis, 'windows': [{'a': round(w['a'], 2), 'b': round(w['b'], 2), 'poses': w['poses']} for w in wins]}, open('../../studio/src/host_long.json', 'w'))
    print('windows', len(wins), 'host seconds', round(sum(w['b'] - w['a'] for w in wins), 1))
