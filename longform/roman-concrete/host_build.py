#!/usr/bin/env python3
"""1) voice.wav — только голос Димы по таймлайну фильма (для Rhubarb);
2) после lipsync.sh: studio/src/host_long.json — окна ведущего (вступление, начало глав, финал) + виземы."""
import json, subprocess, sys
import numpy as np
SR = 16000; VO = 0.6
TL = json.load(open('timeline.json')); D = TL['duration']; ST = {s['id']: s for s in TL['scenes']}
if sys.argv[1] == 'voice':
    buf = np.zeros(int(D * SR) + SR)
    for s in TL['scenes']:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f"../../media/tts/roman_concrete/{s['id']}.mp3", '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        x = np.frombuffer(raw, dtype=np.float32); a = int((s['start'] + VO) * SR); buf[a:a + len(x)] += x[:len(buf) - a]
    pcm = (np.clip(buf, -1, 1) * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', 'audio/voice_only.wav'], input=pcm.tobytes(), check=True)
    print('voice ok', D)
else:
    vis = json.load(open(sys.argv[2]))['visemes']
    CH = ['s03', 's04c', 's06', 's09', 's10c', 's12', 's13', 's13c']
    wins = [{'a': ST['s02']['start'] + 0.3, 'b': ST['s02']['start'] + ST['s02']['dur'] - 0.4, 'poses': [[0, 'talk'], [6, 'point'], [12, 'talk'], [20, 'point']]}]
    for c in CH: wins.append({'a': ST[c]['start'] + 0.4, 'b': ST[c]['start'] + 6.6, 'poses': [[0, 'talk'], [3, 'point']]})
    s14 = ST['s14']; wins.append({'a': s14['start'] + 0.3, 'b': s14['start'] + s14['dur'] - 0.2, 'poses': [[0, 'talk'], [8, 'point'], [16, 'talk'], [s14['dur'] - 8, 'laugh']]})
    json.dump({'fps': 30, 'duration': round(D, 3), 'visemes': vis, 'windows': [{'a': round(w['a'], 2), 'b': round(w['b'], 2), 'poses': w['poses']} for w in wins]}, open('../../studio/src/host_long.json', 'w'))
    print('windows', len(wins), 'host seconds', round(sum(w['b'] - w['a'] for w in wins), 1))
