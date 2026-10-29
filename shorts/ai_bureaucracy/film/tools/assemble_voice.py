#!/usr/bin/env python3
"""Сборка дорожки речи для «Я нанял ИИ, чтобы меньше работать».

Вход: ../tts/<id>.mp3 + <id>.json (Edge TTS из workflow TTS, голоса Дима/Света).
Что делает:
  * сжимает только паузы тишины (>0.30 с → PAUSE с), слова и скорость голоса не меняются;
  * раскладывает реплики по порядку с паузами GAP;
  * пишет assets/voice/voice.wav (48 кГц), assets/voice/dima.wav (только Дима — для Rhubarb),
    assets/voice/timeline.js (window.VO: реплики, слова, титры) и ../tts/manifest.json (паспорт голосов).
Запуск: python3 tools/assemble_voice.py   (из папки film)
"""
import json, re, subprocess, wave, array
from pathlib import Path

FILM = Path(__file__).resolve().parent.parent
TTS = FILM.parent / 'tts'
OUT = FILM / 'assets' / 'voice'
OUT.mkdir(parents=True, exist_ok=True)
SR = 48000
PAUSE = 0.26          # длина сжатой паузы внутри реплики
LEAD, TAIL = 0.02, 0.10

# id, пауза ДО реплики (с), сцена
ORDER = [
    ('d01', 0.30), ('d02', 0.18), ('s01', 0.22), ('d03', 0.34), ('s02', 0.18), ('s03', 0.30),
    ('d04', 0.34), ('d05', 0.22), ('s04', 0.30), ('d06', 0.40), ('d07', 0.16), ('d08', 0.55),
    ('s05', 0.22),
    ('d09', 1.05),   # концовка: после последней шутки — переход к ведущему
]
END_TAIL = 1.35      # музыка после последнего слова CTA

def decode(mp3):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(mp3), '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return array.array('h', raw)

def silences(mp3):
    r = subprocess.run(['ffmpeg', '-i', str(mp3), '-af', 'silencedetect=noise=-40dB:d=0.18', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([0-9.]+)', r)]
    en = [float(x) for x in re.findall(r'silence_end: ([0-9.]+)', r)]
    return list(zip(st, en))

def words_of(meta, dur):
    """Слова с таймингами. Если Edge отдал только границы предложений — делим по длине букв."""
    out = []
    for w in meta['words']:
        toks = w['w'].split()
        if len(toks) == 1:
            out.append({'w': toks[0], 's': w['start'], 'e': w['end']})
            continue
        L = sum(len(t) + 1 for t in toks); t0 = w['start']; span = w['end'] - w['start']
        acc = 0
        for t in toks:
            a = t0 + span * acc / L; acc += len(t) + 1
            out.append({'w': t, 's': a, 'e': t0 + span * acc / L})
    return out

segs, voice, dima = [], array.array('h'), array.array('h')
cursor = 0.0
manifest = []
for sid, gap in ORDER:
    mp3, meta = TTS / f'{sid}.mp3', json.loads((TTS / f'{sid}.json').read_text())
    pcm = decode(mp3); dur = len(pcm) / SR
    sil = silences(mp3)
    # интервалы, которые оставляем (в исходном времени)
    speech_start = next((e for s, e in sil if s <= 0.01), 0.0)
    speech_end = next((s for s, e in sil if e >= dur - 0.02 and s > 0.05), dur)
    keep, cut_map = [], []
    a = max(0.0, speech_start - LEAD)
    for s, e in sil:
        if s <= 0.01 or e >= dur - 0.02:
            continue
        if e - s > PAUSE + 0.04:
            mid_keep = PAUSE / 2
            keep.append((a, s + mid_keep)); a = e - mid_keep
    keep.append((a, min(dur, speech_end + TAIL)))
    # перенос времени: исходное → сжатое
    def remap(t):
        acc = 0.0
        for k0, k1 in keep:
            if t < k0:
                return acc
            if t <= k1:
                return acc + (t - k0)
            acc += k1 - k0
        return acc
    out = array.array('h')
    for k0, k1 in keep:
        out.extend(pcm[int(k0 * SR):int(k1 * SR)])
    # 5-мс фейды на стыках, чтобы не было щелчков
    n = len(out); f = int(0.005 * SR)
    for i in range(min(f, n)):
        out[i] = int(out[i] * i / f); out[n - 1 - i] = int(out[n - 1 - i] * i / f)
    cursor += gap
    start = cursor
    pad = int(round(start * SR)) - len(voice)
    voice.extend([0] * max(0, pad)); dima.extend([0] * max(0, pad))
    voice.extend(out)
    speaker = 'dima' if meta['voice_id'] == 'ru-RU-DmitryNeural' else 'sveta'
    dima.extend(out if speaker == 'dima' else array.array('h', [0]) * len(out))
    clen = len(out) / SR
    ws = [{'w': w['w'], 's': round(start + remap(w['s']), 3), 'e': round(start + remap(w['e']), 3)} for w in words_of(meta, dur)]
    # отображаемые слова берём из исходного текста (с пунктуацией и кавычками)
    toks = [t for t in meta['text'].split() if re.search(r'\w', t)]
    if len(toks) == len(ws):
        for w, t in zip(ws, toks):
            w['w'] = t
    else:
        print('WARN token mismatch', sid, len(toks), len(ws))
    segs.append({'id': sid, 'who': speaker, 'start': round(start, 3), 'end': round(start + clen, 3),
                 'speechEnd': round(start + remap(speech_end), 3), 'text': meta['text'], 'words': ws})
    manifest.append({'id': sid, 'speaker': speaker, 'voice_id': meta['voice_id'], 'engine': meta['engine'],
                     'rate': meta['rate'], 'pitch': meta['pitch'], 'source_file': f'shorts/ai_bureaucracy/tts/{sid}.mp3',
                     'repo_source': f'media/tts/ai_bureaucracy_claude/{sid}.mp3', 'placed_at': round(start, 3),
                     'kept_source_intervals': [[round(a, 3), round(b, 3)] for a, b in keep],
                     'processing': 'только сжатие пауз тишины и 5-мс фейды; скорость/высота не менялись'})
    cursor = start + clen

total = cursor + END_TAIL
pad = int(round(total * SR)) - len(voice)
voice.extend([0] * pad); dima.extend([0] * pad)

def write(path, pcm):
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
write(OUT / 'voice.wav', voice); write(OUT / 'dima.wav', dima)

# ---- титры: короткие фразы, ≤ 3–4 слова, по знакам препинания ----
KEY = {'одно', 'слово', 'нейросети', 'команду', 'совещание', 'точкой', 'точке', 'эйчара', 'сорок', 'Юрист',
       'тона', 'совещаниям', 'копию', 'Тишина', 'руководитель', 'девять', 'меньше', 'подчинённых', 'Шеф',
       'да', 'Подпишись', 'лайк', 'работать'}
caps = []
for sg in segs:
    if sg['id'] == 'd09':
        continue   # в концовке текст CTA показывает сама карточка
    chunk = []
    for i, w in enumerate(sg['words']):
        chunk.append(w)
        brk = re.search(r'[.,:?!—»]$', w['w']) or len(chunk) >= 3 or sum(len(x['w']) for x in chunk) > 17
        nxt = sg['words'][i + 1] if i + 1 < len(sg['words']) else None
        if nxt and nxt['w'] in ('—',):
            brk = False
        if brk or nxt is None:
            text = ' '.join(x['w'] for x in chunk)
            hl = [re.sub(r'[^\wё-]', '', x['w'], flags=re.I) for x in chunk if re.sub(r'[^\wё]', '', x['w'], flags=re.I) in KEY]
            caps.append({'t0': chunk[0]['s'], 't1': (nxt['s'] if nxt else max(sg['speechEnd'] + 0.15, chunk[0]['s'] + 0.7)), 'text': text,
                         'who': sg['who'], 'hl': hl})
            chunk = []
for i in range(len(caps) - 1):            # без «дырок» внутри реплики, но и без наложений
    caps[i]['t1'] = round(min(caps[i]['t1'], caps[i + 1]['t0']), 3)

(OUT / 'timeline.js').write_text('window.VO = ' + json.dumps({'total': round(total, 3), 'segs': segs, 'caps': caps},
                                 ensure_ascii=False) + ';\n', encoding='utf-8')
(TTS / 'manifest.json').write_text(json.dumps({'job': 'ai_bureaucracy_claude', 'segments': manifest,
                                   'total_seconds': round(total, 3)}, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'total {total:.2f}s')
for s in segs:
    print(f"{s['id']} {s['who']:5} {s['start']:6.2f}–{s['end']:6.2f}  {s['text'][:60]}")
