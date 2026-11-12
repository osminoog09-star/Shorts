#!/usr/bin/env python3
"""Фонк-трек кодом + читка по тактам (своя процедурная музыка, AGENTS §11).

usage: python tools/track/make_track.py VOICES_DIR OUT_DIR [--plan tools/track/razdva.json]
VOICES_DIR — папка с v01.wav … (моно, любой SR; приватный голос, в Git не класть).
Пишет OUT_DIR/<id>.wav (44.1 кГц стерео), <id>_beat.wav (минус без голоса) и report.json с замерами.
Голос: без смены высоты; только обрезка тишины, подгонка темпа atempo (≤ plan.max_tempo) и эффекты.
"""
import argparse, json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100


def db(x):
    return 20 * np.log10(max(float(x), 1e-9))


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


def sos(kind, freq, order=2):
    return signal.butter(order, freq, kind, fs=SR, output="sos")


def filt(x, kind, freq, order=2):
    return signal.sosfilt(sos(kind, freq, order), x)


def env_exp(n, decay):
    return np.exp(-np.arange(n) / (decay * SR))


class Song:
    def __init__(self, bpm, bars, seed=7):
        self.bpm, self.bars = bpm, bars
        self.beat = 60.0 / bpm
        self.step = self.beat / 4            # 16-я
        self.bar = self.beat * 4
        self.n = int((bars * self.bar + 2.0) * SR)
        self.rng = np.random.default_rng(seed)

    def t(self, bar, step=0.0):
        return int((bar * self.bar + step * self.step) * SR)

    def add(self, buf, pos, x, gain=1.0):
        if pos >= len(buf) or pos < 0:
            return
        e = min(len(buf), pos + len(x))
        buf[pos:e] += x[: e - pos] * gain


def cowbell(freq, dur=0.32):
    n = int(dur * SR); t = np.arange(n) / SR
    x = signal.square(2 * np.pi * freq * t) + 0.8 * signal.square(2 * np.pi * freq * 1.48 * t)
    x = signal.sosfilt(signal.butter(2, [freq * 0.9, min(freq * 4.5, 9000)], "bandpass", fs=SR, output="sos"), x)
    e = 0.75 * env_exp(n, 0.045) + 0.25 * env_exp(n, 0.16)
    return np.tanh(2.2 * x * e) * 0.5


def bass808(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = freq * (1 + 2.2 * np.exp(-t / 0.018))            # удар: быстрый спад высоты
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph)
    e = np.minimum(1, t / 0.003) * np.exp(-t / (dur * 0.55))
    e[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    return np.tanh(3.2 * x * e) * 0.9                     # гармоники — чтобы было слышно на телефоне


def kick():
    n = int(0.16 * SR); t = np.arange(n) / SR
    f = 48 + 190 * np.exp(-t / 0.022)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07)
    return x


def clap(rng):
    n = int(0.24 * SR)
    x = signal.sosfilt(signal.butter(2, [900, 3800], "bandpass", fs=SR, output="sos"), rng.standard_normal(n))
    e = np.zeros(n)
    for off in (0, 0.011, 0.023):
        k = int(off * SR); e[k:] += env_exp(n - k, 0.012)
    e += 0.6 * env_exp(n, 0.09)
    return np.tanh(x * e * 1.6) * 0.6


def hat(rng, decay=0.022):
    n = int(0.09 * SR)
    return filt(rng.standard_normal(n), "highpass", 7500, 4) * env_exp(n, decay) * 0.35


def pad(freqs, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0.0, 0.007):
            x += signal.sawtooth(2 * np.pi * f * (1 + det) * t)
    x = filt(x, "lowpass", 850, 4) / (3 * len(freqs))
    a = int(0.05 * SR)
    x[:a] *= np.linspace(0, 1, a); x[-a:] *= np.linspace(1, 0, a)
    return x * (0.8 + 0.2 * np.sin(2 * np.pi * 5.5 * t))


def riser(rng, dur):
    n = int(dur * SR); t = np.arange(n) / n
    x = rng.standard_normal(n)
    out = np.zeros(n); blk = 2048
    zi = None
    for i in range(0, n, blk):                             # фильтр, открывающийся вверх
        fc = 400 + 9000 * (i / n) ** 2
        s = signal.butter(2, [fc * 0.7, min(fc * 1.4, 18000)], "bandpass", fs=SR, output="sos")
        seg = x[i:i + blk]
        if zi is None:
            zi = signal.sosfilt_zi(s) * 0
        seg, zi = signal.sosfilt(s, seg, zi=zi)
        out[i:i + len(seg)] = seg
    return out * t ** 2 * 0.5


def crash(rng):
    n = int(1.6 * SR)
    return filt(rng.standard_normal(n), "highpass", 5000, 2) * env_exp(n, 0.45) * 0.3


def semis(base, s):
    return base * 2 ** (s / 12)


MEL = [  # (шаг 16-й, полутон от C#5) на 4 такта
    [(0, 0), (3, 0), (6, 3), (8, 0), (11, 0), (14, 7), (15, 5)],
    [(0, 0), (3, 0), (6, 3), (8, 0), (10, -2), (12, -4), (14, -2)],
    [(0, 0), (3, 0), (6, 3), (8, 0), (11, 0), (14, 7), (15, 8)],
    [(0, -4), (3, -4), (6, -2), (8, 0), (11, 3), (12, 2), (14, 0)],
]
ROOTS = [0, 0, -4, -2]                    # C#, C#, A, B
BASS = [[0, 3, 6, 10], [0, 3, 6, 10, 14], [0, 3, 6, 10], [0, 3, 8, 11, 14]]
CHORD = {0: (0, 3, 7), -4: (0, 4, 7), -2: (0, 4, 7)}


def build_beat(song, sections):
    """sections: {bar: {'drums':bool,'hats':bool,'mel':gain,'bass':bool}}"""
    n = song.n
    drums, bassb, mel, padb, fx = (np.zeros(n) for _ in range(5))
    duck = np.ones(n)
    k, cl = kick(), clap(song.rng)
    c5, c2 = 554.37, 69.30
    for bar in range(song.bars):
        sec = sections[bar]; i = bar % 4; root = ROOTS[i]
        if sec["mel"] > 0:
            for st, sm in MEL[i]:
                song.add(mel, song.t(bar, st), cowbell(semis(c5, sm)), sec["mel"])
        if sec["pad"] > 0:
            fr = [semis(138.59, root + s) for s in CHORD[root]]
            song.add(padb, song.t(bar), pad(fr, song.bar), sec["pad"])
        if sec["bass"]:
            hits = BASS[i]
            for j, st in enumerate(hits):
                nxt = hits[j + 1] if j + 1 < len(hits) else 16
                dur = (nxt - st) * song.step * 0.98
                glide = 12 if (st == 14) else 0            # восьмушка вверх в конце такта
                song.add(bassb, song.t(bar, st), bass808(semis(c2, root + glide), dur))
                song.add(drums, song.t(bar, st), k, 0.9)
                p = song.t(bar, st); m = int(0.18 * SR)
                if p + m < n:
                    duck[p:p + m] = np.minimum(duck[p:p + m], 0.45 + 0.55 * np.linspace(0, 1, m) ** 1.5)
        if sec["drums"]:
            for st in (4, 12):
                song.add(drums, song.t(bar, st), cl)
        if sec["hats"]:
            for st in range(0, 16, 2):
                song.add(drums, song.t(bar, st), hat(song.rng), 0.9 if st % 4 == 0 else 0.55)
            if bar % 2 == 1:                               # дробь 32-ми в конце такта
                for q in range(8):
                    song.add(drums, song.t(bar, 12 + q * 0.5), hat(song.rng, 0.012), 0.35 + 0.06 * q)
        if sec.get("riser"):
            song.add(fx, song.t(bar), riser(song.rng, song.bar))
        if sec.get("crash"):
            song.add(fx, song.t(bar), crash(song.rng))
    mus = (mel * 0.95 + padb * 0.5) * duck
    return drums, bassb, mus, fx


def stereo(drums, bassb, mus, fx):
    d = int(0.011 * SR)
    mr = np.concatenate([np.zeros(d), mus[:-d]])           # лёгкая ширина мелодии
    left = drums * 0.8 + bassb * 0.48 + mus * 0.9 + mr * 0.25 + fx
    right = drums * 0.8 + bassb * 0.48 + mus * 0.25 + mr * 0.9 + fx
    return np.stack([left, right], axis=1)


# ---------- голос ----------
def load_voice(path):
    sr, x = wavfile.read(str(path))
    x = x.astype(np.float64)
    if x.ndim > 1:
        x = x.mean(axis=1)
    x /= 32768.0 if np.abs(x).max() > 1.5 else 1.0
    if sr != SR:
        g = np.gcd(SR, sr)
        x = signal.resample_poly(x, SR // g, sr // g)
    return x


def frames_db(x, hop=0.01):
    h = int(hop * SR); m = len(x) // h
    e = np.sqrt(np.mean(np.square(x[: m * h].reshape(m, h)), axis=1) + 1e-12)
    return 20 * np.log10(e / (np.abs(x).max() + 1e-9)), h


def trim(x, thr=-38):
    d, h = frames_db(x)
    idx = np.where(d > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] * h - int(0.015 * SR)); b = min(len(x), (idx[-1] + 1) * h + int(0.05 * SR))
    y = x[a:b].copy(); f = int(0.008 * SR)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y


def split_mid(x, thr=-32):
    """Две половины строки по самой длинной паузе в середине (30–72 %)."""
    d, h = frames_db(x); m = len(d)
    lo, hi = int(m * 0.30), int(m * 0.72)
    best, cur = None, None
    for i in range(lo, hi):
        if d[i] < thr:
            cur = [i, i] if cur is None else [cur[0], i]
            if best is None or cur[1] - cur[0] > best[1] - best[0]:
                best = cur[:]
        else:
            cur = None
    if best is None or best[1] - best[0] < 5:               # паузы < 60 мс нет
        return None
    mid = (best[0] + best[1]) // 2 * h
    return trim(x[:mid]), trim(x[mid:])


def atempo(x, factor):
    if abs(factor - 1) < 0.01:
        return x
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "a.wav", Path(td) / "b.wav"
        wavfile.write(str(a), SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(a), "-af", "atempo=%.4f" % factor,
                        "-ar", str(SR), "-ac", "1", str(b)], check=True)
        return load_voice(b)


def compress(x, thr_db=-20, ratio=4.0, att=0.004, rel=0.09):
    e = np.abs(x); out = np.zeros_like(x); g = 0.0
    a, r = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    lvl = np.zeros_like(x)
    for i, v in enumerate(e):                              # огибающая
        g = a * g + (1 - a) * v if v > g else r * g + (1 - r) * v
        lvl[i] = g
    over = np.maximum(20 * np.log10(lvl + 1e-9) - thr_db, 0)
    out = x * 10 ** (-over * (1 - 1 / ratio) / 20)
    return out


def voice_fx(x):
    x = filt(x, "highpass", 110, 2)
    x = x / (np.abs(x).max() + 1e-9) * 0.8
    x = compress(x)
    x = x + 0.35 * filt(x, "highpass", 3200, 1)            # разборчивость
    x = np.tanh(1.6 * x) / np.tanh(1.6)                    # лёгкая сатурация, высота не меняется
    return x / (np.abs(x).max() + 1e-9)


def reverb_ir(rng, dur=0.9):
    n = int(dur * SR)
    ir = rng.standard_normal((n, 2)) * env_exp(n, 0.22)[:, None]
    ir[: int(0.012 * SR)] = 0
    return signal.sosfilt(signal.butter(2, [350, 6000], "bandpass", fs=SR, output="sos"), ir, axis=0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("voices"); ap.add_argument("out")
    ap.add_argument("--plan", default=str(Path(__file__).with_name("razdva.json")))
    a = ap.parse_args()
    plan = json.loads(Path(a.plan).read_text(encoding="utf-8"))
    song = Song(plan["bpm"], plan["bars"], plan.get("seed", 7))
    sections = {}
    for bar in range(song.bars):
        sec = {"drums": False, "hats": False, "bass": False, "mel": 0.0, "pad": 0.0}
        for rule in plan["sections"]:
            if rule["from"] <= bar < rule["to"]:
                sec.update({k: v for k, v in rule.items() if k not in ("from", "to", "name")})
        sections[bar] = sec
    for bar in plan.get("risers", []):
        sections[bar]["riser"] = True
    for bar in plan.get("crashes", []):
        sections[bar]["crash"] = True
    beat = stereo(*build_beat(song, sections))

    vox = np.zeros(song.n); vox_wide = np.zeros((song.n, 2)); report = {"lines": []}
    max_len = song.bar * plan.get("fill", 0.93); max_tempo = plan.get("max_tempo", 1.3)
    cache = {}
    for item in plan["vocals"]:
        vid = item["id"]
        if vid not in cache:
            raw = trim(load_voice(Path(a.voices) / (vid + ".wav")))
            parts = split_mid(raw) or (raw,)
            done = []
            for p in parts:
                limit = max_len if len(parts) == 2 else max_len * 2
                fct = min(max(len(p) / SR / limit, 1.0), max_tempo)
                done.append(voice_fx(trim(atempo(p, fct))))
                report["lines"].append({"id": vid, "part": len(done), "sec": round(len(p) / SR, 2),
                                        "tempo": round(fct, 3), "fits": len(done[-1]) / SR <= limit + 0.05})
            cache[vid] = done
        for j, p in enumerate(cache[vid]):
            pos = song.t(item["bar"] + j)
            song.add(vox, pos, p)
            if item.get("double"):                         # хук: дабл по краям
                d = int(0.017 * SR)
                song.add(vox_wide[:, 0], pos + d, p, 0.5); song.add(vox_wide[:, 1], pos + 2 * d, p, 0.5)
    # задержка на восьмую с точкой и короткий ревер
    dly = int(song.step * 3 * SR)
    echo = np.zeros(song.n); echo[dly:] = filt(vox, "bandpass", [500, 3500])[:-dly] * 0.22
    echo[2 * dly:] += filt(vox, "bandpass", [500, 3500])[: -2 * dly] * 0.09
    wet = signal.fftconvolve(np.stack([vox, vox], 1), reverb_ir(song.rng), mode="full", axes=0)[: song.n]
    wet *= 0.10 / (np.abs(wet).max() + 1e-9) * np.abs(vox).max() * 6
    vst = np.stack([vox + echo * 0.8, vox + echo], 1) + vox_wide + wet * 0.5

    # баланс: голос на plan.vocal_over_beat дБ громче минуса на участках речи
    act = np.abs(signal.sosfiltfilt(sos("lowpass", 8, 2), np.abs(vox))) > 0.03
    b_rms, v_rms = rms(beat[act].mean(axis=1)), rms(vox[act])
    vgain = b_rms * 10 ** (plan.get("vocal_over_beat", 3.0) / 20) / (v_rms + 1e-9)
    # минус чуть приседает под голосом (плавно, без качки)
    under = 1 - plan.get("duck", 0.22) * np.clip(signal.sosfiltfilt(sos("lowpass", 4, 2), act.astype(float)), 0, 1)
    mix = beat * under[:, None] + vst * vgain
    # фейды и мастер
    fo = int(plan.get("fade_out", 3.0) * SR); end = song.t(song.bars)
    mix[end - fo:end] *= np.linspace(1, 0, fo)[:, None] ** 1.5; mix = mix[:end]
    beat_only = beat[:end].copy(); beat_only[end - fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5

    def master(x):
        x = signal.sosfilt(sos("highpass", 28, 2), x, axis=0)
        x = x / (np.percentile(np.abs(x), 99.7) + 1e-9) * 0.80
        x = np.tanh(1.25 * x) / np.tanh(1.25)
        return x / (np.abs(x).max() + 1e-9) * 0.89           # ≈ −1 dBFS
    mix, beat_only = master(mix), master(beat_only)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    name = plan["id"]
    wavfile.write(str(out / (name + ".wav")), SR, (mix * 32767).astype(np.int16))
    wavfile.write(str(out / (name + "_beat.wav")), SR, (beat_only * 32767).astype(np.int16))
    act = act[:end]
    report.update({"id": name, "bpm": song.bpm, "bars": song.bars, "duration": round(end / SR, 2),
                   "peak_db": round(db(np.abs(mix).max()), 2), "rms_db": round(db(rms(mix)), 2),
                   "voice_minus_beat_db": round(db(v_rms * vgain) - db(b_rms), 2),
                   "voice_active_share": round(float(act.mean()), 3),
                   "all_fit": all(l["fits"] for l in report["lines"]),
                   "voice": "denis-qwen3tts-reference-v1, без смены высоты; темп ≤ %.2f" % max_tempo,
                   "music": "процедурная, tools/track/make_track.py (своя, AGENTS §11)"})
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "lines"}, ensure_ascii=False))
    for l in report["lines"]:
        print("LINE", l)
    if not report["all_fit"]:
        print("::warning::часть строк длиннее такта даже после ускорения — проверить на слух")


if __name__ == "__main__":
    sys.exit(main())
