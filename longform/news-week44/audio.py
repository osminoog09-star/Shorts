#!/usr/bin/env python3
"""Процедурная музыка (комикс-фанк) + SFX + сведение с голосом.

python3 audio.py mix cues.json out.wav
cues.json: {"duration": сек, "voice": [{"file":..., "at": сек}], "sfx": [{"name":..., "at": сек, "gain": 1}],
            "music": {"bpm": 112, "sections": [{"at": 0, "style": "intro"}, ...]}}
"""
import json
import subprocess
import sys

import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, d=0.2, s=0.0, r=0.05, total=None):
    total = total or n / SR
    t = np.arange(n) / SR
    e = np.where(t < a, t / max(a, 1e-6), np.exp(-(t - a) / max(d, 1e-6)) * (1 - s) + s)
    rel = np.clip((total - t) / max(r, 1e-6), 0, 1)
    return e * rel


def note_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


# ───────── инструменты ─────────
def marimba(f, d=0.45, v=0.5):
    t = t_(d)
    x = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 30) + 0.15 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t * 60)
    return x * env(len(t), 0.002, 0.18) * v


def pluck(f, d=0.35, v=0.5):
    n = int(SR * d); p = max(2, int(SR / f))
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]
        buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out * v


def bass(f, d=0.3, v=0.6):
    t = t_(d)
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.3 + np.sin(2 * np.pi * f * t)
    # простой ФНЧ
    y = np.convolve(x, np.ones(24) / 24, mode='same')
    return y * env(len(t), 0.004, 0.25, 0.3, 0.05) * v


def kick(v=0.9):
    t = t_(0.35)
    f = 50 + 120 * np.exp(-t * 25)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * v


def snare(v=0.5):
    t = t_(0.22)
    n = rng.uniform(-1, 1, len(t))
    n = n - np.convolve(n, np.ones(6) / 6, mode='same')
    return (n * np.exp(-t * 22) + 0.4 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)) * v


def hat(v=0.18, open_=False):
    t = t_(0.25 if open_ else 0.06)
    n = rng.uniform(-1, 1, len(t))
    n = n - np.convolve(n, np.ones(3) / 3, mode='same')
    return n * np.exp(-t * (14 if open_ else 70)) * v


def glock(f, d=0.8, v=0.25):
    t = t_(d)
    x = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 8)
    return x * np.exp(-t * 4) * v


def pad(fs, d, v=0.08):
    t = t_(d)
    x = sum(np.sin(2 * np.pi * f * t + i) + 0.3 * np.sin(2 * np.pi * f * 2.003 * t) for i, f in enumerate(fs))
    a = np.clip(t / 0.4, 0, 1) * np.clip((d - t) / 0.4, 0, 1)
    return x * a * v


def put(buf, x, at):
    i = int(at * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    j = min(len(buf), i + len(x))
    s = max(0, i)
    buf[s:j] += x[s - i:j - i]


# ───────── музыка ─────────
PROG = [(48, [60, 64, 67]), (45, [57, 60, 64]), (41, [57, 60, 65]), (43, [59, 62, 67])]  # C Am F G
PROG_TENSE = [(45, [57, 60, 64]), (41, [57, 60, 65]), (38, [57, 62, 65]), (40, [56, 59, 64])]  # Am F Dm E
SCALE = [0, 2, 4, 7, 9]


def music(duration, bpm, sections):
    L = np.zeros(int(SR * (duration + 2)))
    beat = 60 / bpm
    bar = beat * 4
    secs = sorted(sections, key=lambda s: s["at"]) + [{"at": duration, "style": "end"}]
    for si in range(len(secs) - 1):
        st, en, style = secs[si]["at"], secs[si + 1]["at"], secs[si]["style"]
        prog = PROG_TENSE if style in ("tense", "mystery") else PROG
        nbar = int(np.ceil((en - st) / bar))
        for b in range(nbar):
            t0 = st + b * bar
            if t0 >= en:
                break
            root, chord = prog[b % 4]
            if style in ("intro", "mystery"):
                put(L, pad([note_hz(m) for m in chord], min(bar, en - t0) + 0.3, 0.05), t0)
                for k in range(4):
                    if t0 + k * beat < en:
                        put(L, marimba(note_hz(chord[(k * 2) % 3] + 12), 0.4, 0.22), t0 + k * beat)
                if style == "mystery":
                    put(L, glock(note_hz(chord[b % 3] + 24), 1.2, 0.12), t0 + beat * 2.5)
                continue
            if style == "end":
                continue
            drive = 1.0 if style in ("groove", "big") else 0.7
            for k in range(8):  # восьмые
                tt = t0 + k * beat / 2 + (0.03 if k % 2 else 0)  # лёгкий свинг
                if tt >= en:
                    break
                put(L, hat(0.1 * drive), tt)
                if k in (0, 3, 4) or (style == "big" and k == 6):
                    put(L, kick(0.75 * drive), tt)
                if k in (2, 6):
                    put(L, snare(0.32 * drive), tt)
                bn = root - 12 + (7 if k in (3, 7) else 0) + (12 if k == 5 else 0)
                if k in (0, 2, 3, 5, 6):
                    put(L, bass(note_hz(bn + 12), beat * 0.45, 0.35), tt)
                # мелодия маримбы по пентатонике
                if k % 2 == 0 or style == "big":
                    deg = SCALE[(b * 3 + k * 2 + (b // 2)) % 5]
                    put(L, marimba(note_hz(60 + deg + (12 if (b + k) % 7 == 0 else 0)), 0.35, 0.16), tt)
            put(L, pad([note_hz(m) for m in chord], min(bar, en - t0) + 0.2, 0.035), t0)
            if style == "big":
                put(L, glock(note_hz(chord[0] + 24), 0.9, 0.1), t0)
    return L[: int(SR * duration)]


# ───────── SFX ─────────
def sfx(name):
    if name == 'pop':
        t = t_(0.14); f = 400 + 900 * t / 0.14
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 25) * 0.5
    if name == 'boing':
        t = t_(0.5); f = 180 + 120 * np.sin(t * 38) * np.exp(-t * 4) + 80 * t
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 5) * 0.45
    if name == 'whoosh':
        t = t_(0.6); n = rng.uniform(-1, 1, len(t))
        k = (np.sin(np.pi * t / 0.6) ** 2)
        y = np.convolve(n, np.ones(12) / 12, 'same') * k
        return y * 0.9
    if name == 'bam':
        return np.concatenate([kick(1.0)]) * 1.0 + np.pad(snare(0.6), (0, int(SR * 0.35) - int(SR * 0.22)))
    if name == 'splash':
        t = t_(0.9); n = rng.uniform(-1, 1, len(t))
        y = np.convolve(n, np.ones(5) / 5, 'same') * np.exp(-t * 5)
        return y * 0.6 + np.sin(2 * np.pi * (300 - 200 * t) * t) * np.exp(-t * 8) * 0.3
    if name == 'ding':
        return glock(note_hz(88), 1.4, 0.4) + glock(note_hz(95), 1.4, 0.15)
    if name == 'tick':
        t = t_(0.03); return rng.uniform(-1, 1, len(t)) * np.exp(-t * 300) * 0.5
    if name == 'crank':
        out = np.zeros(int(SR * 0.6))
        for i in range(6):
            put(out, sfx('tick') * 0.8, i * 0.1)
        return out
    if name == 'crunch':
        out = np.zeros(int(SR * 0.6))
        for i in range(9):
            t = t_(0.05); put(out, rng.uniform(-1, 1, len(t)) * np.exp(-t * 60) * 0.7, i * 0.06 + rng.uniform(0, 0.02))
        return out
    if name == 'thunder':
        t = t_(2.0); n = rng.uniform(-1, 1, len(t))
        y = np.convolve(n, np.ones(60) / 60, 'same') * 6
        return y * (np.exp(-t * 2) + 0.4 * np.exp(-((t - 0.3) ** 2) * 40)) * 0.9
    if name == 'bubbles':
        out = np.zeros(int(SR * 1.2))
        for i in range(10):
            t = t_(0.08); f = rng.uniform(500, 1100) * (1 + t * 8)
            put(out, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.25, rng.uniform(0, 1.1))
        return out
    if name == 'scan':
        t = t_(1.6); f = 220 + 440 * t / 1.6
        return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + np.sin(2 * np.pi * 60 * t) * 0.1) * np.sin(np.pi * t / 1.6)
    if name == 'beep':
        t = t_(0.12); return np.sin(2 * np.pi * 1320 * t) * 0.25 * np.clip((0.12 - t) / 0.02, 0, 1)
    if name == 'zap':
        t = t_(0.5); return np.sign(np.sin(2 * np.pi * (900 - 1400 * t) * t)) * np.exp(-t * 7) * 0.25
    if name == 'riser':
        t = t_(2.0); n = rng.uniform(-1, 1, len(t))
        return (np.convolve(n, np.ones(8) / 8, 'same') * (t / 2.0) ** 2 * 0.5 + np.sin(2 * np.pi * (200 + 600 * (t / 2) ** 2) * t) * (t / 2) * 0.1)
    if name == 'chord':
        return sum(glock(note_hz(m), 3.0, 0.18) for m in (72, 76, 79, 84)) + pad([note_hz(m) for m in (48, 60, 64, 67)], 3.0, 0.08)
    raise KeyError(name)


def load_audio(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def mix(cfg, out):
    D = cfg['duration']
    n = int(SR * D)
    voice = np.zeros(n)
    for v in cfg.get('voice', []):
        put(voice, load_audio(v['file']) * v.get('gain', 1.0), v['at'])
    m = cfg.get('music')
    if m and m.get('beds'):
        mus = np.zeros(n)
        xf = int(SR * 2.5)
        for bd in m['beds']:
            src = load_audio(bd['file'])
            a0, a1 = int(bd['from'] * SR), min(n, int(bd['to'] * SR))
            L = a1 - a0
            if L <= 0: continue
            reps = int(np.ceil(L / max(1, len(src) - xf))) + 1
            seq = src.copy()
            for _ in range(reps - 1):  # петля с кроссфейдом
                fade = np.linspace(0, 1, xf)
                seq = np.concatenate([seq[:-xf], seq[-xf:] * (1 - fade) + src[:xf] * fade, src[xf:]])
            seq = seq[:L + xf] * bd.get('gain', 1.0)
            env = np.ones(len(seq)); env[:xf] = np.linspace(0, 1, xf); env[-xf:] = np.linspace(1, 0, xf)
            put(mus, seq * env, max(0, bd['from'] - (1.25 if bd['from'] > 0 else 0)))
        mus = mus[:n]
    else:
        mus = music(D, m.get('bpm', 112), m['sections']) if m else np.zeros(n)
    # дакинг музыки под голос
    envv = np.abs(voice)
    k = int(SR * 0.25)
    envv = np.convolve(envv, np.ones(k) / k, 'same')
    duck = 1 - 0.55 * np.clip(envv / 0.05, 0, 1)
    mus = mus[:n] * duck * m.get('gain', 0.5) if m else mus
    fx = np.zeros(n)
    for c in cfg.get('sfx', []):
        put(fx, sfx(c['name']) * c.get('gain', 1.0) * 0.6, c['at'])
    total = voice * 1.0 + mus + fx
    # финальный хвост и лимитер
    fade = int(SR * 1.5)
    total[-fade:] *= np.linspace(1, 0, fade)
    peak = np.max(np.abs(total)) or 1
    total = np.tanh(total / peak * 1.2) * 0.89
    pcm = (total * 32767).astype(np.int16)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', '-ac', '2', out], input=pcm.tobytes(), check=True)


if __name__ == '__main__':
    if sys.argv[1] == 'mix':
        mix(json.load(open(sys.argv[2])), sys.argv[3])
