# Звук movie-edit: диалог по монтажу + лицензионный трек (CC BY) с дакингом + удары/нарастания + голос ведущего в финале.
# Ключевые моменты берутся из edit.py: PUNCH (удары), KEY_DROP (музыка пропадает), KEY_HIT (главный удар).
# Финал: outro_voice.wav + outro.json {duration, like, tap}.
import subprocess, sys
import numpy as np
from edit import *

SR = 48000
out = sys.argv[1]
TRACK = sys.argv[2]
OFF = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] != 'auto' else None
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', SRC, '-vn', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
src = np.frombuffer(raw, np.float32).reshape(-1, 2)

# --- диалог по монтажу
parts = []
fade = int(0.03 * SR)
for a, b in SEGMENTS:
    p = src[int(a * SR):int(b * SR)].copy()
    ramp = np.linspace(0, 1, fade)[:, None]
    p[:fade] *= ramp; p[-fade:] *= ramp[::-1]
    parts.append(p)
dlg = np.concatenate(parts)
import json
OUTRO = json.load(open('outro.json'))
OUT_T = OUTRO['duration']
VO_OFF = len(dlg) / SR
import wave
def rdw(f, ch=1):
    w = wave.open(f); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() == 2: a = a.reshape(-1, 2).mean(1)
    if w.getframerate() != SR:
        a = np.interp(np.arange(int(len(a) * SR / w.getframerate())) * w.getframerate() / SR, np.arange(len(a)), a)
    return a
vo = rdw('outro_voice.wav')
dlg = np.concatenate([dlg, np.zeros((int(OUT_T * SR), 2), np.float32)])
i0 = int(VO_OFF * SR); dlg[i0:i0 + len(vo)] += (vo * 1.6)[:, None]
for sfx, at, g in [('ding.wav', OUTRO['like'], 0.5), ('chime.wav', OUTRO['tap'], 0.5)]:
    x = rdw('/home/claude/shorts/studio/public/' + sfx); j = int((VO_OFF + at) * SR)
    dlg[j:j + len(x)] += (x * g)[:len(dlg) - j, None]
N = len(dlg)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

def env_at(points):  # кусочно-линейная огибающая [(t, v)]
    xs, ys = zip(*points)
    return np.interp(t, xs, ys)

from scipy.signal import lfilter
def lp(x, k):  # однополюсный НЧ-фильтр
    return lfilter([k], [1, k - 1], x)

E = edit_time
T = total()
mus = np.zeros(N)

def boom(at, amp=1.0, dur=1.6, f0=120, f1=38):
    i0 = int(at * SR); n = min(int(dur * SR), N - i0)
    if n <= 0: return
    tt = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-tt * 14)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt * 2.6)
    click = rng.standard_normal(n) * np.exp(-tt * 60) * 0.35
    mus[i0:i0 + n] += amp * (s + lp(click, 0.3))

def heartbeat(at, amp=0.6):
    boom(at, amp * 0.8, 0.5, 90, 45)
    boom(at + 0.2, amp * 0.55, 0.5, 80, 42)

def swell(end, dur=1.6, amp=0.5):  # обратный «вдох» шума перед ударом
    i1 = int(end * SR); i0 = max(0, i1 - int(dur * SR))
    n = i1 - i0
    x = rng.standard_normal(n)
    k = np.linspace(0.02, 0.35, n)
    y = np.empty(n); acc = 0.0
    for j in range(n):
        acc += k[j] * (x[j] - acc); y[j] = acc
    mus[i0:i1] += y * np.linspace(0, 1, n) ** 3 * amp * 3

for p in PUNCH:
    if p != KEY_HIT:
        boom(E(p), 0.8)
swell(E(KEY_HIT), 1.0, 0.6)
boom(E(KEY_HIT), 1.4, 2.8, 140, 34)

mus = np.tanh(mus * 1.2) * 0.32
trk = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', TRACK, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                    capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
EDIT = T
if OFF is None:  # самый «нарастающий» кусок трека длиной с монтаж
    h = SR // 2; mm = trk.mean(1)[: len(trk) // h * h]; m = np.sqrt((mm ** 2).reshape(-1, h).mean(1))
    L = int(EDIT * 2); best, OFF = -9, 0
    for i in range(0, len(m) - L - 30, 2):
        w = m[i:i + L]; a, b = w[:L // 3].mean(), w[-L // 3:].mean()
        sc = np.log(b / (a + 1e-6) + 1e-6) - abs(np.log(w.mean() / (m.mean() + 1e-6))) * 0.5
        if sc > best: best, OFF = sc, i / 2
print('offset', OFF)
seg = trk[int(OFF * SR): int(OFF * SR) + N]
if len(seg) < N: seg = np.concatenate([seg, np.zeros((N - len(seg), 2), np.float32)])
seg = seg / (np.sqrt((seg ** 2).mean()) + 1e-6) * 0.046            # уровень подложки (+15% к 0.035 после loudnorm)
# огибающая трека: пропадает перед ключевым моментом, возвращается с ударом, тише в финале под голос
g = env_at([(0, 0.0), (0.6, 1.0), (E(KEY_DROP) - 0.2, 1.0), (E(KEY_DROP), 0.0), (E(KEY_HIT) - 0.05, 0.0), (E(KEY_HIT) + 0.05, 1.25), (T, 1.0), (T + 0.6, 0.55), (T + OUT_T - 1.2, 0.55), (T + OUT_T, 0.0)])
# дакинг под речь
v = np.abs(dlg.mean(1)); k = SR // 20
env = np.convolve(v, np.ones(k) / k, 'same'); env = np.convolve(env, np.ones(k * 4) / (k * 4), 'same')
duck = 1 - 0.6 * np.clip(env / (np.percentile(env, 90) + 1e-6), 0, 1)
music = seg * (g * duck)[:, None] + np.stack([mus, mus], 1)
mix = dlg * 1.0 + music
pcm = mix.astype(np.float32).tobytes()
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-',
                '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-c:a', 'aac', '-b:a', '192k', out],
               input=pcm, check=True)
print('audio', N / SR)
