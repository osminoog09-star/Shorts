import numpy as np, soundfile as sf, json
from scipy import signal
SR = 44100
import json as _j, os as _os
WARP = _j.load(open('audio/warp.json')) if _os.path.exists('audio/warp.json') else None
def toNew(x):
    if not WARP: return x
    A = WARP['anchors']
    if x <= A[0][0]: return x - A[0][0] + A[0][1]
    for i in range(len(A) - 1):
        if x <= A[i + 1][0]: k = (x - A[i][0]) / (A[i + 1][0] - A[i][0]); return A[i][1] + k * (A[i + 1][1] - A[i][1])
    return x - A[-1][0] + A[-1][1]
DUR = 31.5
N = int(DUR * SR)
rng = np.random.default_rng(3)
def T(n): return np.arange(n) / SR
def env(n, a=.005, d=.2, curve=4):
    t = T(n); e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) * curve / max(d, 1e-4)); return e
def place(buf, x, at, g=1.0):
    i = int(toNew(at) * SR); j = min(len(buf), i + len(x))
    if i < 0 or i >= len(buf): return
    buf[i:j] += x[:j - i] * g
def bp(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi / (SR / 2), .99)], 'band'); return signal.lfilter(b, a, x)
def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'low'); return signal.lfilter(b, a, x)
def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)

# ---------------- SFX ----------------
def whoosh(dur=.35, up=True):
    n = int(dur * SR); x = rng.standard_normal(n); t = T(n)
    lo, hi = bp(x, 250, 1200), bp(x, 1500, 6000); k = np.linspace(0, 1, n) if up else np.linspace(1, 0, n)
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return (lo * (1 - k) + hi * k) * e * 1.6
def thud(f0=70, dur=.35, g=1):
    n = int(dur * SR); t = T(n); f = f0 * (1 + 1.5 * np.exp(-t * 30))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12)
    x += lp(rng.standard_normal(n), 900) * np.exp(-t * 40) * .6
    return x * g
def clang(f0=520, dur=1.0):
    n = int(dur * SR); t = T(n); x = np.zeros(n)
    for k, (r, a, d) in enumerate([(1, 1, 5), (2.76, .6, 7), (5.4, .4, 10), (8.9, .25, 14), (1.5, .5, 6)]):
        x += a * np.sin(2 * np.pi * f0 * r * t + k) * np.exp(-t * d)
    x += hp(rng.standard_normal(n), 2000) * np.exp(-t * 60) * .8
    return x * .5 + thud(90, dur, .7)[:n]
def pluck(f, dur=.5, bright=.5):
    n = int(dur * SR); p = int(SR / f); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = bright * buf[i % p] + (1 - bright) * .5 * (buf[i % p] + buf[(i + 1) % p]) * .996 if False else .5 * (buf[i % p] + buf[(i + 1) % p]) * .995
    return out
def chime(f=1760, dur=.8):
    n = int(dur * SR); t = T(n)
    return (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.01 * t) + .3 * np.sin(2 * np.pi * f * 3 * t)) * np.exp(-t * 6) * np.minimum(1, t / .003) * .5
def sparkle_sfx():
    out = np.zeros(int(.7 * SR))
    for i, f in enumerate([2093, 2637, 3136, 4186]): place(out, chime(f, .5) * .5, i * .05)
    return out
def tick(): n = int(.04 * SR); t = T(n); return hp(rng.standard_normal(n), 3000) * np.exp(-t * 200) * .8 + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 150) * .4
def pop(f=600):
    n = int(.12 * SR); t = T(n); fr = f * (1 + 2 * t * 10); return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 40)
def boing(f=220, dur=.5):
    n = int(dur * SR); t = T(n); fr = f * (1 + .35 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3)) * (1 + t)
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 5) * .6
def tweet():
    out = np.zeros(int(1.2 * SR))
    for i in range(4):
        n = int(.1 * SR); t = T(n); fr = 3200 + 900 * np.sin(2 * np.pi * 30 * t)
        place(out, np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(np.pi * t / .1) * .25, i * .25)
    return out
def scribble(dur=.18):
    n = int(dur * SR); t = T(n); return bp(rng.standard_normal(n), 1500, 6000) * (0.5 + .5 * np.sin(2 * np.pi * 30 * t)) * np.sin(np.pi * t / dur) * .5
def riser(dur=2.8):
    n = int(dur * SR); t = T(n); f = 200 * (2 ** (t / dur * 2.5))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 + bp(rng.standard_normal(n), 800, 5000) * .3 * (t / dur)
    return x * (t / dur) ** 2
def waves(dur):
    n = int(dur * SR); t = T(n); x = lp(rng.standard_normal(n), 700, 2)
    return x * (0.5 + .5 * np.sin(2 * np.pi * t / 4.5) ** 2) * .5
def heartbeat():
    out = np.zeros(int(.8 * SR)); place(out, thud(55, .3, .8), 0); place(out, thud(50, .3, .6), .22); return out


BPM = 132  # dotted-quarter = beat; eighth = 60/BPM/... use eighth duration
E8 = 60 / BPM / 2 * 1.0  # eighth note seconds (6/8 feel)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def saw_pad(f, dur, g=.2):
    n = int(dur * SR); t = T(n); vib = 1 + .004 * np.sin(2 * np.pi * 5.5 * t)
    ph = np.cumsum(f * vib) / SR; x = 2 * (ph % 1) - 1 + .6 * (2 * ((ph * 1.005) % 1) - 1)
    x = lp(x, 1400); e = np.minimum(1, t / .06) * np.minimum(1, (dur - t) / .08)
    return x * e * g
plk_cache = {}
# ---- whimsical comedic underscore (replaces jig) ----
music = np.zeros(N)
BEAT = 60 / 104
def pizz(m, dur=.45, g=1.0):
    k = ('pz', m, round(dur, 2))
    if k not in plk_cache:
        x = pluck(midi(m), dur); n = len(x); t = T(n)
        x = bp(x, 180, 3500) * np.exp(-t * 7) + bp(rng.standard_normal(n), 1500, 5000) * np.exp(-t * 300) * .15
        plk_cache[k] = x / (np.max(np.abs(x)) + 1e-9)
    return plk_cache[k] * g
def glock(m, dur=1.2, g=1.0):
    n = int(dur * SR); t = T(n); f = midi(m)
    x = (np.sin(2 * np.pi * f * t) + .35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + .15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12))
    return x * np.exp(-t * 3.5) * np.minimum(1, t / .002) * .5 * g
def reed(m, dur=.22, g=1.0):
    n = int(dur * SR); t = T(n); f = midi(m); ph = (f * t) % 1
    x = lp(np.sign(np.sin(2 * np.pi * ph)) * .6 + (2 * ph - 1) * .4, 900)
    return x * np.minimum(1, t / .015) * np.exp(-t * 6) * np.minimum(1, (dur - t) / .03) * .5 * g
def strings(ms, dur, g=1.0):
    n = int(dur * SR); t = T(n); x = np.zeros(n)
    for m in ms:
        for d in (-.004, 0, .005):
            ph = np.cumsum(midi(m) * (1 + d) * (1 + .003 * np.sin(2 * np.pi * 5 * t))) / SR; x += 2 * (ph % 1) - 1
    x = lp(x / (len(ms) * 3), 1100); e = np.minimum(1, t / .5) * np.minimum(1, (dur - t) / .5)
    return x * e * g
# progressions (root, chord tones) in midi
DM = [(38, (62, 65, 69)), (43, (62, 67, 71)), (38, (62, 65, 69)), (45, (61, 64, 67))]   # Dm G Dm A7
DMAJ = [(38, (62, 66, 69)), (43, (62, 67, 71)), (45, (61, 64, 69)), (38, (62, 66, 69))]  # D G A D
motif = [(0, 74), (.5, 77), (1, 81), (2, 79), (2.5, 77), (3, 76)]  # glock line over 1 bar
def playful(t0, t1, prog, g=1.0, glock_on=True, stabs=True):
    t = t0; bar = 0
    while t < t1 - .05:
        root, ch = prog[bar % 4]
        place(music, pizz(root, .5, .9), t, g); place(music, pizz(root + 7, .5, .7), t + 2 * BEAT, g)
        if stabs:
            for bt in (1, 3): 
                for m in ch: place(music, pizz(m - 12, .3, .28), t + bt * BEAT, g)
        if glock_on and bar % 2 == 0:
            for (bt, m) in motif:
                mm = m if prog is DM else m + (1 if m % 12 in (5,) else 0)
                if t + bt * BEAT < t1: place(music, glock(mm, 1.0, .35), t + bt * BEAT, g)
        t += 4 * BEAT; bar += 1
def sneak(t0, t1, g=1.0):
    steps = [38, 38, 41, 40, 39, 38, 36, 37]
    t = t0; i = 0
    while t < t1 - .05:
        place(music, reed(steps[i % 8] + 12, .2, .8), t, g); place(music, pizz(steps[i % 8], .35, .6), t, g)
        t += BEAT * (1 if i % 2 == 0 else 1); i += 1


def hiss(dur, g=1.0):
    n = int(dur * SR); t = T(n); x = bp(rng.standard_normal(n), 900, 5000)
    return x * np.minimum(1, t / .2) * np.minimum(1, (dur - t) / .2) * .5 * g
def motor(dur, f=95, g=1.0):
    n = int(dur * SR); t = T(n); ph = np.cumsum(f * (1 + .03 * np.sin(2 * np.pi * 7 * t))) / SR
    x = lp(2 * (ph % 1) - 1, 700) * .5 + bp(rng.standard_normal(n), 300, 2500) * .25
    return x * np.minimum(1, t / .15) * np.minimum(1, (dur - t) / .2) * g
def beep(f=1400, dur=.12): n = int(dur * SR); t = T(n); return np.sign(np.sin(2 * np.pi * f * t)) * .25 * np.minimum(1, (dur - t) / .02)
def slurp(dur=.9):
    n = int(dur * SR); t = T(n); f = 900 * (1 - .8 * t / dur)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * .3 * np.sin(np.pi * t / dur) + bp(rng.standard_normal(n), 400, 3000) * .3 * np.sin(np.pi * t / dur)
def scrape(dur=.9): n = int(dur * SR); t = T(n); return bp(rng.standard_normal(n), 2000, 7000) * (0.6 + .4 * np.sin(2 * np.pi * 40 * t)) * np.exp(-t * 1.5) * .5
sfx = np.zeros(N)
for w in (3.4, 11.0, 22.6): place(sfx, whoosh(.36), w - .22, .4)
for c in (6.6, 14.6, 25.6): place(sfx, thud(80, .2, .5), c, .4)
# 1 hook
place(sfx, hiss(2.8), .3, .45); place(sfx, pop(520), 1.3, .4)
for i in range(6): place(sfx, thud(150, .08, .3), .15 + i * .35, .45)
place(sfx, beep(1800, .06), 2.6, .25); place(sfx, beep(1800, .06), 2.8, .25)
# 2 reveal
place(sfx, chime(196, 1.4), 3.65, .5); place(sfx, beep(900, .1), 4.3, .4); place(sfx, beep(700, .18), 4.45, .4)
place(sfx, hiss(2.2, 1.2), 3.9, .5); place(sfx, slurp(.9), 4.9, .7); place(sfx, pop(380), 5.75, .6); place(sfx, thud(60, .3, .7), 5.75, .5)
# 3 chase
place(sfx, motor(4.4, 110), 6.6, .55); place(sfx, pop(560), 7.4, .4)
for i in range(26): place(sfx, thud(130 + (i % 2) * 25, .07, .35), 6.65 + i * .165, .5)
# 4 obstacle
place(sfx, motor(1.3, 120), 11.0, .4); place(sfx, whoosh(.5), 11.6, .45); place(sfx, scrape(.9), 12.1, .5)
place(sfx, clang(420), 13.0, .7); place(sfx, thud(55, .5, .9), 13.0, .7); place(sfx, tweet(), 13.15, .5)
# 5 tug of war
place(sfx, pop(500), 14.9, .4); place(sfx, heartbeat(), 15.2, .4); place(sfx, heartbeat(), 15.9, .45)
place(sfx, riser(3.0), 16.6, .6); place(sfx, hiss(3.0, 1.5), 16.6, .55); place(sfx, pop(620), 17.9, .4)
# 6 pop
place(sfx, pop(300), 19.6, .9); place(sfx, thud(50, .6, 1), 19.6, .8); place(sfx, boing(240, .5), 19.75, .5)
place(sfx, whoosh(.6, False), 19.8, .45); place(sfx, thud(70, .35, .8), 20.8, .7); place(sfx, sparkle_sfx(), 21.1, .4)
# 7 win
for i in range(8): place(sfx, beep(2000 if i % 2 else 1600, .08), 22.9 + i * .16, .3)
place(sfx, sparkle_sfx(), 22.95, .35); place(sfx, pop(700), 23.2, .4)
# 8 twist
place(sfx, motor(1.7, 100), 25.6, .5); place(sfx, clang(700, .6) * .4, 27.4, .5)
for i in range(5): place(sfx, scribble(), 27.6 + i * .2, .45)
place(sfx, boing(180, .5), 29.4, .5); place(sfx, beep(1200, .1), 29.7, .35); place(sfx, beep(1500, .14), 29.85, .35)

music = np.zeros(N)
playful(0, 3.4, DM, .7, glock_on=False)
sneak(3.4, 6.6, .9); place(music, strings((50, 56, 62), 3.2, .3), 3.4)
playful(6.6, 14.6, DM, .9, glock_on=True)
place(music, strings((50, 57, 62), 5.0, .4), 14.6); sneak(14.6, 19.6, .6)
for k, m in enumerate([62, 65, 69, 72, 74, 77, 81]): place(music, glock(m, .9, .3), 17.0 + k * .36)
playful(19.6, 25.6, DMAJ, .9)
place(music, strings((50, 56, 62), 6.0, .35), 25.6); sneak(25.6, 29.4, .7)
for m in (38, 41, 44, 47): place(music, pizz(m, 1.0, .7), 29.4); place(music, glock(m + 36, 1.4, .3), 29.4)
music = lp(music, 6000)
mix = music * .35 + sfx * .8
out = np.stack([mix, mix], 1)
fl = int(.6 * SR); out[-fl:] *= np.linspace(1, 0, fl)[:, None]
out = out / np.max(np.abs(out)) * .89
sf.write('audio/mix.wav', out, SR)
print('done', out.shape)
