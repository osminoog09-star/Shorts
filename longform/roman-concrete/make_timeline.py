#!/usr/bin/env python3
"""timeline.json: порядок сцен = порядок строк jobs/tts/roman_concrete.json; длительность = 0.6 вход + голос + 1.1 хвост; финал +3.8 с."""
import json, subprocess
ORDER = [l['id'] for l in json.load(open('../../jobs/tts/roman_concrete.json'))['lines']]
out = []; t = 0.0
for sid in ORDER:
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'../../media/tts/roman_concrete/{sid}.mp3'], capture_output=True, text=True).stdout)
    dur = round(0.6 + d + (3.8 if sid == 's14' else 1.1), 2)
    out.append({'id': sid, 'start': round(t, 3), 'dur': dur, 'voice': d}); t += dur
json.dump({'duration': round(t, 3), 'scenes': out}, open('timeline.json', 'w'), indent=1)
print('total', round(t, 1), 's =', int(t // 60), 'min', round(t % 60))
