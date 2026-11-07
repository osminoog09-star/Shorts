#!/usr/bin/env python3
"""Mix for «Дикая природа: пылесос». Runs on Denis's PC (voices are private, never committed).

voices/<id>.wav (Denis, Qwen3-TTS ICL) at script times + procedural SFX (own) + CC-BY music bed
(Kevin MacLeod «Investigations»). Music RMS = 0.08 of active-speech voice RMS, continuous, fade in/out only.
Writes: <out>/mix.wav (48 kHz stereo), <out>/mix_report.json, and ./voices/dur.json (subtitle timing for scene.js).
usage: py -3.11 mix.py <voices_dir> <music.mp3> <out_dir>
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR, DUR = 48000, 38.5
HERE = Path(__file__).resolve().parent
LINES = {'v1': .2, 'v2': 3.55, 'v3': 9.85, 'v4': 13.3, 'v5': 18.2, 'v6': 23.9, 'v7': 29.3, 'v8': 32.7}  # must match scene.js
# lines re-synthesized as short pieces (ASR fix 07.11): played back to back with a pause, one subtitle id
CHAINS = {'v5': (['v5a', 'v5b'], .2), 'v7': (['v7a', 'v7b'], .35)}
rng = np.random.default_rng(11)


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
    f = np.geomspace(max(f0, 1), max(f1, 1), n); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) if kind == 'sin' else (np.sign(np.sin(ph)) * .5 if kind == 'sq' else 2 * (ph / (2 * np.pi) % 1) - 1)
    if decay: x *= np.exp(-t * decay)
    return (x * env(n)).astype(np.float32)


def lp(x, a):
    from scipy.signal import lfilter
    return lfilter([a], [1, a - 1], x).astype(np.float32)


def noise(dur, a=0.2, decay=0.0):
    n = int(dur * SR); y = lp(rng.standard_normal(n).astype(np.float32), a)
    if decay: y *= np.exp(-np.arange(n) / SR * decay)
    return y * env(n) / (np.abs(y).max() + 1e-9)


def ov(*xs):
    n = max(len(x) for x in xs); o = np.zeros(n, np.float32)
    for x in xs: o[:len(x)] += x
    return o


def bank():
    b = {}
    b['twitch'] = ov(tone(900, 1400, .08, decay=30) * .4, noise(.08, .5, decay=40) * .2)               # servo snap at 0.4 s
    b['scan'] = tone(2200, 2200, .06, decay=40) * .25                                                   # lidar ping
    b['motor'] = ov(noise(5.3, .02) * .5, tone(170, 175, 5.3, 'saw') * .05)                              # creeping motor
    b['whoosh'] = noise(.45, .18) * np.sin(np.linspace(0, np.pi, int(.45 * SR))).astype(np.float32) * .7
    b['grab'] = ov(noise(.5, .5, decay=8) * .5, tone(140, 90, .3, 'saw', decay=10) * .25)              # brush chews the sock
    b['drag'] = noise(2.8, .06) * .35
    b['purrlow'] = noise(1.4, .01) * (0.6 + .4 * np.sin(np.arange(int(1.4 * SR)) / SR * 2 * np.pi * 24)).astype(np.float32) * .5
    b['swoosh'] = noise(.22, .45) * np.sin(np.linspace(0, np.pi, int(.22 * SR))).astype(np.float32) * .6  # paw shoots out
    tug = np.zeros(int(8.2 * SR), np.float32)                                                          # wheel strain + squeaks
    tug += noise(8.2, .03) * .25
    for i in range(14):
        x = tone(1300 + 300 * (i % 3), 900, .12, decay=12) * .12; o = int((.3 + i * .57) * SR); tug[o:o + len(x)] += x[:len(tug) - o]
    b['tug'] = tug
    al = np.zeros(int(5.0 * SR), np.float32)                                                           # robot alarm (wee-woo)
    for i in range(10):
        x = tone(880 if i % 2 == 0 else 660, 880 if i % 2 == 0 else 660, .25, 'sq') * .12; o = int(i * .25 * SR); al[o:o + len(x)] += x
    b['alarm'] = al
    ch = np.zeros(int(1.0 * SR), np.float32)
    for i, f in enumerate([523.3, 659.3, 784.0]):
        x = tone(f, f, .5, decay=5) * .25; o = int(i * .09 * SR); ch[o:o + len(x)] += x
    b['chime'] = ch                                                                                     # speaker wakes
    b['click'] = noise(.03, .9, decay=120) * .7                                                         # kettle switch
    b['boil'] = noise(1.6, .05) * (0.5 + .5 * np.sin(np.arange(int(1.6 * SR)) / SR * 2 * np.pi * 9)).astype(np.float32) * .3
    b['hop'] = tone(500, 320, .07, decay=30) * .3
    b['growl'] = noise(1.3, .012) * (0.7 + .3 * np.sin(np.arange(int(1.3 * SR)) / SR * 2 * np.pi * 31)).astype(np.float32) * .7
    b['thwack'] = ov(tone(160, 60, .3, decay=14) * .9, noise(.12, .5, decay=35) * .7)
    b['spin'] = ov(tone(300, 900, 1.6, 'saw', decay=1.2) * .08, noise(1.6, .1, decay=1.5) * .2)
    b['clang'] = ov(tone(1250, 1240, .7, decay=6) * .25, tone(1870, 1860, .5, decay=8) * .15, noise(.05, .7, decay=60) * .4)
    b['thud'] = ov(tone(110, 50, .35, decay=12) * .8, noise(.1, .3, decay=30) * .4)
    b['clink'] = tone(2600, 2500, .25, decay=18) * .2
    b['boing'] = tone(240, 170, .45, decay=6) * (1 + .5 * np.sin(np.arange(int(.45 * SR)) / SR * 2 * np.pi * 18)).astype(np.float32) * .35
    b['sad'] = ov(tone(660, 520, .3, decay=3) * .15, np.pad(tone(520, 392, .5, decay=3) * .15, (int(.32 * SR), 0)))
    b['purr'] = noise(5.6, .008) * (0.55 + .45 * np.sin(np.arange(int(5.6 * SR)) / SR * 2 * np.pi * 26)).astype(np.float32) * .55
    return b


SFX_AT = [('twitch', .4), ('scan', .7), ('scan', 2.2), ('motor', 3.6), ('scan', 6.8), ('whoosh', 9.25), ('grab', 9.55),
          ('drag', 9.9), ('purrlow', 13.2), ('swoosh', 14.4), ('tug', 14.8), ('alarm', 18.05), ('chime', 19.6), ('hop', 20.6),
          ('hop', 21.2), ('hop', 21.8), ('click', 21.4), ('boil', 21.6), ('growl', 23.0), ('whoosh', 27.75), ('thwack', 27.95),
          ('spin', 28.0), ('clang', 28.35), ('thud', 28.8), ('thud', 29.15), ('clink', 28.75), ('whoosh', 31.45), ('boing', 32.1),
          ('sad', 32.4), ('purr', 32.6)]


def main():
    vdir, music, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]); out.mkdir(parents=True, exist_ok=True)
    N = int(DUR * SR); voice = np.zeros(N, np.float32); fx = np.zeros(N, np.float32); active = np.zeros(N, bool); durs = {}
    def piece(name):
        x = load(vdir / f'{name}.wav')
        nz = np.where(np.abs(x) > .01)[0]
        if len(nz): x = x[max(0, nz[0] - int(.03 * SR)): nz[-1] + int(.08 * SR)]
        return x / (np.sqrt(np.mean(x[np.abs(x) > .01] ** 2)) + 1e-9) * .12
    used = {}
    for vid, t0 in LINES.items():
        parts, gap = CHAINS.get(vid, ([vid], 0))
        if not all((vdir / f'{p}.wav').exists() for p in parts): parts = [vid]
        x = np.concatenate([np.concatenate([piece(p), np.zeros(int(gap * SR), np.float32)]) if i < len(parts) - 1 else piece(p) for i, p in enumerate(parts)])
        used[vid] = parts
        o = int(t0 * SR); e = min(N, o + len(x)); voice[o:e] += x[:e - o]; active[o:e] |= np.abs(x[:e - o]) > .01
        durs[vid] = round(len(x) / SR, 3)
    order = sorted(LINES, key=LINES.get)
    for a, b in zip(order, order[1:]):
        if LINES[a] + durs[a] > LINES[b] - .1: print(f'WARN overlap {a}->{b}: ends {LINES[a] + durs[a]:.2f} > next {LINES[b]:.2f}')
    if LINES[order[-1]] + durs[order[-1]] > DUR - .3: print('WARN last line runs past body end')
    B = bank()
    for name, t0 in SFX_AT:
        x = B[name]; o = int(t0 * SR); e = min(N, o + len(x)); fx[o:e] += x[:e - o] * .5
    fx += noise(DUR, .02) * .003                                                                       # room tone
    mus = load(music)[:N]
    if len(mus) < N: mus = np.pad(mus, (0, N - len(mus)))
    mus *= env(N, 1.0, 2.5)
    vr = np.sqrt(np.mean(voice[active] ** 2)); mus *= (.08 * vr) / (np.sqrt(np.mean(mus ** 2)) + 1e-9)
    ratio = float(np.sqrt(np.mean(mus ** 2)) / vr)
    mix = voice + fx + mus; pk = np.abs(mix).max(); mix *= min(1.0, .89 / pk)
    st = np.stack([mix, mix], 1).astype(np.float32)
    (out / 'mix.f32').write_bytes(st.tobytes())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', str(out / 'mix.f32'), '-c:a', 'pcm_s16le', str(out / 'mix.wav')], check=True)
    (out / 'mix.f32').unlink()
    (HERE / 'voices').mkdir(exist_ok=True); (HERE / 'voices' / 'dur.json').write_text(json.dumps(durs, indent=1))
    rep = {'voice_pieces': used, 'music_to_voice_rms': round(ratio, 3), 'peak_before_norm': float(pk), 'durations': durs, 'music': music.name, 'sfx': [n for n, _ in SFX_AT]}
    (out / 'mix_report.json').write_text(json.dumps(rep, ensure_ascii=False, indent=1)); print(rep)


if __name__ == '__main__':
    main()
