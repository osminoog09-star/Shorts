#!/usr/bin/env python3
"""Mix for «Забастовка умного дома» (mini). Runs in GitHub Actions only (voices are private).

voices/<id>.wav (Denis m_h*, Домашня m_f*) placed at script times + procedural SFX + CC-BY music bed.
Music RMS is held at <= 0.08 of active-speech voice RMS (AGENTS §4: <= 0.10 for new parts).
Writes: mix.wav (48 kHz stereo), voices/lips.json (mouth open per 1/30 s), mix_report.json.
usage: python mix.py <voices_dir> <music.mp3> <out_dir>
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR, DUR = 48000, 40.0
HERE = Path(__file__).resolve().parent
LINES = {'m_h1': .25, 'm_f1': 3.3, 'm_f2': 8.2, 'm_h2': 11.0, 'm_h3': 19.6, 'm_f3': 22.6, 'm_h4': 27.6, 'm_f4': 35.0}
rng = np.random.default_rng(7)


def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def env(n, a=.005, r=.05):
    e = np.ones(n, np.float32); na, nr = min(n // 2, int(a * SR)), min(n // 2, int(r * SR))
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def tone(f0, f1, dur, kind='sin', decay=0.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.linspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) if kind == 'sin' else np.sign(np.sin(ph)) * .5
    if decay: x *= np.exp(-t * decay)
    return (x * env(n)).astype(np.float32)


def noise(dur, lp=0.2, decay=0.0):
    n = int(dur * SR); x = rng.standard_normal(n).astype(np.float32)
    y = np.zeros_like(x); a = lp; s = 0.0
    for i in range(n):  # one-pole low-pass
        s += a * (x[i] - s); y[i] = s
    if decay: y *= np.exp(-np.arange(n) / SR * decay)
    return y * env(n) / (np.abs(y).max() + 1e-9)


def ov(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n, np.float32)
    for x in xs: o[:len(x)] += x
    return o


def sfx_bank():
    b = {}
    b['pop'] = tone(300, 900, .12, decay=20) * .8                       # sign pops out
    b['boing'] = tone(220, 160, .45, decay=6) * (1 + .5 * np.sin(np.arange(int(.45 * SR)) / SR * 2 * np.pi * 18)) * .35
    b['buzz'] = ov(tone(100, 100, 1.2, 'sq') * .25, noise(1.2, .5) * .08) * .6   # light flicker
    b['motor'] = ov(noise(2.4, .03) * .5, tone(180, 200, 2.4) * .08) * .5         # robovac
    b['whistle'] = ov(tone(1900, 2300, .95) * .35, noise(.95, .6) * .25) * .7       # kettle steam jet
    b['click'] = noise(.03, .9, decay=120) * .7                                  # toaster lever
    b['thwip'] = ov(tone(500, 1400, .18, decay=8) * .5, noise(.18, .3, decay=10) * .3)
    b['bonk'] = ov(tone(180, 90, .25, decay=18) * .9, noise(.08, .4, decay=40) * .5)   # toast hits forehead
    sp = np.zeros(int(1.0 * SR), np.float32)
    for i, f in enumerate([1318.5, 1568.0, 1975.5, 2637.0]):
        x = tone(f, f, .55, decay=6) * .2; o = int(i * .07 * SR); sp[o:o + len(x)] += x
    b['sparkle'] = sp
    b['pour'] = noise(2.4, .08) * .35
    hum = np.zeros(int(3.2 * SR), np.float32)                                     # kettle sings happily
    for i, f in enumerate([784, 988, 1175, 988, 1319]):
        x = tone(f, f * 1.01, .55, decay=1.5) * .12; o = int(i * .6 * SR); hum[o:o + len(x)] += x
    b['sing'] = hum
    b['ching'] = ov(tone(2400, 2600, .4, decay=9) * .3, tone(3600, 3600, .3, decay=12) * .15)
    b['whoosh'] = noise(.5, .15) * np.sin(np.linspace(0, np.pi, int(.5 * SR))).astype(np.float32) * .4
    return b


SFX_AT = [('pop', 1.55), ('boing', 1.6), ('buzz', 4.3), ('motor', 8.0), ('whistle', 13.75), ('click', 17.55),
          ('click', 18.95), ('thwip', 19.0), ('bonk', 19.18), ('whoosh', 22.4), ('sparkle', 30.6), ('pour', 31.2),
          ('sing', 31.3), ('ching', 35.4), ('whoosh', 34.8)]


def main():
    vdir, music, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    N = int(DUR * SR); voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32)
    lips, durs, active = {}, {}, np.zeros(N, bool)
    for vid, t0 in LINES.items():
        x = load(vdir / f'{vid}.wav')
        nz = np.where(np.abs(x) > .01)[0]                       # trim silence
        if len(nz): x = x[max(0, nz[0] - int(.03 * SR)): nz[-1] + int(.08 * SR)]
        x = x / (np.sqrt(np.mean(x[np.abs(x) > .01] ** 2)) + 1e-9) * .12   # equal speech level
        o = int(t0 * SR); e = min(N, o + len(x)); voice[o:e] += x[:e - o]; active[o:e] |= np.abs(x[:e - o]) > .01
        durs[vid] = round(len(x) / SR, 3)
        hop = SR // 30; fr = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]
        m = max(fr) or 1; lips[vid] = [round(min(1, (v / m) ** .7 * 1.15), 3) for v in fr]
    for name, t0 in SFX_AT:
        x = sfx_bank_cache[name]; o = int(t0 * SR); e = min(N, o + len(x)); fx[o:e] += x[:e - o] * .5
    # room tone
    fx += noise(DUR, .02) * .004
    mus = load(music)[:N]
    if len(mus) < N: mus = np.pad(mus, (0, N - len(mus)))
    mus *= env(N, 1.0, 2.0)
    vr = np.sqrt(np.mean(voice[active] ** 2)); mr = np.sqrt(np.mean(mus ** 2)) + 1e-9
    mus *= (.08 * vr) / mr
    ratio = float(np.sqrt(np.mean(mus ** 2)) / vr)
    mix = voice + fx + mus
    pk = np.abs(mix).max(); mix *= min(1.0, .89 / pk)
    st = np.stack([mix, mix], 1)
    # slight stereo width for fx/music
    st[:, 0] += (fx + mus) * .0; st[:, 1] -= 0
    (out / 'mix.f32').write_bytes(st.astype(np.float32).tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(out / 'mix.f32'),
                    '-c:a', 'pcm_s16le', str(out / 'mix.wav')], check=True)
    (out / 'mix.f32').unlink()
    (HERE / 'voices').mkdir(exist_ok=True)
    (HERE / 'voices' / 'lips.json').write_text(json.dumps(lips))
    (HERE / 'voices' / 'dur.json').write_text(json.dumps(durs, indent=1))
    rep = {'music_to_voice_rms': round(ratio, 3), 'peak_before_norm': float(pk), 'durations': durs,
           'music': music.name, 'sfx': [n for n, _ in SFX_AT]}
    (out / 'mix_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1)); print(rep)


sfx_bank_cache = sfx_bank()
if __name__ == '__main__':
    main()
