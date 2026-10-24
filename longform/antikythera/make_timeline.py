#!/usr/bin/env python3
"""timeline.json: порядок сцен и длительности (0.6 вход + голос + 1.1 хвост; финал +3 с)."""
import json, subprocess
ORDER = ['s01', 's02', 'n1', 's03', 's04', 'n2', 's05', 's06', 'n3', 's07', 'n4', 's08', 's09', 'n5', 's10', 's11', 'n6', 'n7', 'n8', 'n9', 's12']
FIXED = {'s01': 17.7}  # у хука своя шторка
out = []; t = 0.0
for sid in ORDER:
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'../../media/tts/antikythera/{sid}.mp3'], capture_output=True, text=True).stdout)
    dur = FIXED.get(sid, round(0.6 + d + 1.1, 2))
    if sid == 's12': dur = round(0.6 + d + 3.8, 2)
    out.append({'id': sid, 'start': round(t, 3), 'dur': dur, 'voice': d}); t += dur
json.dump({'duration': round(t, 3), 'scenes': out}, open('timeline.json', 'w'), indent=1)
print('total', round(t, 1), 's =', int(t // 60), 'min', round(t % 60))
for s in out: print(s['id'], s['start'], s['dur'])
