#!/usr/bin/env python3
"""Pronunciation fixes for TTS (Claude, 07.11): «Оумуамуа» was read differently every time («О мама», «Омомо»).
A test of 6 spellings: «Оу-муа-муа» is read the same every time. Subtitles keep the real spelling (text), only `say` changes.
Order: chapters.py → extra_shots.py → edu.py → pron.py. Prints the beat ids whose voice must be regenerated (delete their WAVs)."""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAY = {'Оумуамуа': 'Оу-муа-муа', 'Буква I.': 'Буква И.'}
changed = []
for p in sorted((HERE / 'levels').glob('*.json')):
    j = json.loads(p.read_text(encoding='utf-8'))
    for b in j['beats']:
        base = b.get('say', b['text']); new = base
        for a, c in SAY.items(): new = new.replace(a, c)
        if new != base:
            b['say'] = new; changed.append((j['id'], b['id']))
            b['alias'] = list(dict.fromkeys(b.get('alias', []) + [new.replace('Оу-муа-муа', 'Оу Муа Муа')]))
    p.write_text(json.dumps(j, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(json.dumps(changed, ensure_ascii=False))
if '--delete' in sys.argv:
    W = Path(r'C:\M1lash\Работа\oumuamua\voice')
    for c, b in changed: (W / c / f'{b}.wav').unlink(missing_ok=True)
    print('deleted', len(changed))
