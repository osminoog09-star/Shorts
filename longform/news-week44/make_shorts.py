#!/usr/bin/env python3
"""Вертикальные нарезки из длинного: хук (новая реплика Димы) → кусок фильма → аутро Димы (CTA).
python3 make_shorts.py → shorts/<имя>.json + audio/short_<имя>.m4a (нужен audio/news_mix.wav и media/tts/news_week44_shorts)."""
import json, subprocess
from pathlib import Path
import numpy as np
HERE = Path(__file__).parent; T = HERE.parents[1] / 'media/tts/news_week44_shorts'; MM = HERE.parents[1] / 'media/music'
SR = 48000
SHORTS = {
 'heist': {'hook': ('aH', 55.0, [{'t': 'СЕРВЕРЫ ДЛЯ ИИ'}, {'t': 'НА $13 МЛН', 'bg': '#e8706a', 'c': '#fff'}, {'t': 'ИСЧЕЗЛИ НА ТРАССЕ'}]),
           'seg': (82.55, 110.0), 'outro': ('aO', 232.0), 'bed': 'Spy Glass.mp3'},
 'hack':  {'hook': ('bH', 520.6, [{'t': 'ИИ-АГЕНТЫ'}, {'t': 'ВЗЛОМАЛИ', 'bg': '#e8706a', 'c': '#fff'}, {'t': 'СОЗДАТЕЛЕЙ ИИ'}]),
           'seg': (552.15, 590.0), 'outro': ('bO', 650.0), 'bed': 'Hidden Agenda.mp3'},
}
def dur(p): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)]))
def load(p, ss=0.0, t=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', str(p), '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.check_output(cmd), np.float32).reshape(-1, 2).copy()
def put(buf, x, at):
    i = int(at * SR); n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n]
(HERE / 'shorts').mkdir(exist_ok=True)
long_mix = HERE / 'audio/news_mix.wav'
for name, s in SHORTS.items():
    hid, hat, lines = s['hook']; oid, oat = s['outro']
    hd = dur(T / f'{hid}.mp3') + 0.55; od = dur(T / f'{oid}.mp3') + 1.6
    a, b = s['seg']; sd = b - a
    total = round(hd + sd + od, 3)
    pieces = [{'kind': 'hook', 'dur': round(hd, 3), 'longAt': hat, 'lines': lines},
              {'kind': 'seg', 'from': a, 'to': b},
              {'kind': 'outro', 'dur': round(od, 3), 'longAt': oat, 'sub': round(dur(T / f'{oid}.mp3') * 0.55, 2)}]
    json.dump({'duration': total, 'pieces': pieces}, open(HERE / f'shorts/{name}.json', 'w'), ensure_ascii=False, indent=1)
    buf = np.zeros((int(total * SR) + SR, 2), np.float32)
    v = load(T / f'{hid}.mp3'); put(buf, v, 0.15)
    seg = load(long_mix, a, sd); f = int(0.25 * SR); seg[:f] *= np.linspace(0, 1, f)[:, None]; seg[-f:] *= np.linspace(1, 0, f)[:, None]; put(buf, seg, hd)
    vo = load(T / f'{oid}.mp3'); put(buf, vo, hd + sd + 0.2)
    bed = load(MM / s['bed'], 0, hd + 1) * 0.16; put(buf, bed, 0)
    bed2 = load(MM / 'Clean Soul.mp3', 0, od) * 0.16; put(buf, bed2 * np.linspace(1, 0.2, len(bed2))[:, None] ** 0.5, hd + sd)
    buf = buf[:int(total * SR)]; buf /= max(1.0, np.abs(buf).max() / 0.9)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', str(HERE / f'audio/short_{name}.m4a')], input=buf.tobytes(), check=True)
    # голос Димы для липсинка ведущего (хук + сегмент только реплики Д + аутро) — для простоты: хук и аутро
    vb = np.zeros(int(total * 16000) + 16000, np.float32)
    for fn, at in [(T / f'{hid}.mp3', 0.15), (T / f'{oid}.mp3', hd + sd + 0.2)]:
        x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(fn), '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']), np.float32); i = int(at * 16000); vb[i:i + len(x)] += x[:len(vb) - i]
    tl = json.load(open(HERE / 'timeline.json'))
    for c in tl['chapters']:
        for l in c['lines']:
            st = c['start'] + l['s']
            if l['sp'] == 'D' and st < b and st + l['vdur'] > a:
                x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(HERE.parents[1] / f"media/tts/news_week44/{l['id']}.mp3"), '-ac', '1', '-ar', '16000', '-f', 'f32le', '-']), np.float32)
                off = st - a; x = x[int(max(0, -off) * 16000):]; i = int((hd + max(0, off)) * 16000); n = min(len(x), int((hd + sd) * 16000) - i)
                if n > 0: vb[i:i + n] += x[:n]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', '16000', '-ac', '1', '-i', '-', str(HERE / f'audio/short_{name}_voice.wav')], input=vb.tobytes(), check=True)
    print(name, 'total', total, 'hook', round(hd, 2), 'seg', round(sd, 2), 'outro', round(od, 2))
