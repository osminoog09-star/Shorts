#!/usr/bin/env python3
"""timeline.json из chapters.json + длительностей озвучки (или оценки, если mp3 ещё нет: --mock).
Глава: заставка INTRO с → реплики с паузами GAP → хвост TAIL. В конце — финальный хвост END."""
import json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).parent; TTS = HERE.parents[1] / 'media/tts/news_week44'
job = {l['id']: l for l in json.load(open(HERE.parents[1] / 'jobs/tts/news_week44.json'))['lines']}
chs = json.load(open(HERE / 'chapters.json'))
MOCK = '--mock' in sys.argv
INTRO = {'c0': 0.35}; INTRO_DEF = 2.6; GAP_SAME, GAP_SWITCH = 0.22, 0.34; TAIL = 1.0; END = 4.0
def vdur(lid):
    p = TTS / f'{lid}.mp3'
    if MOCK or not p.exists():
        if not MOCK: print('MISSING', lid)
        return round(len(job[lid]['text']) / 13.2, 2)
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)]))
out, t = [], 0.0
for ci, c in enumerate(chs):
    intro = INTRO.get(c['id'], INTRO_DEF); s = intro; lines = []
    for k, lid in enumerate(c['lines']):
        sp = 'S' if job[lid].get('voice') else 'D'; d = vdur(lid)
        nxt = c['lines'][k + 1] if k + 1 < len(c['lines']) else None
        gap = (GAP_SWITCH if nxt and ('S' if job[nxt].get('voice') else 'D') != sp else GAP_SAME) if nxt else (END if ci == len(chs) - 1 else TAIL)
        lines.append({'id': lid, 'sp': sp, 's': round(s, 3), 'vdur': round(d, 3), 'dur': round(d + gap, 3)}); s += d + gap
    out.append({'id': c['id'], 'n': ci, 'title': c['title'], 'start': round(t, 3), 'dur': round(s, 3), 'intro': intro, 'lines': lines}); t += s
json.dump({'duration': round(t, 3), 'chapters': out}, open(HERE / 'timeline.json', 'w'), ensure_ascii=False, indent=1)
print('total', round(t, 1), 's =', int(t // 60), 'min', round(t % 60), '(mock)' if MOCK else '')
