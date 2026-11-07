"""Свои процедурные SFX (без чужих сэмплов → без проблем с правами)."""
import numpy as np, soundfile as sf
from pathlib import Path
SR = 48000
out = Path(r"C:\M1lash\Работа\game_2026-11-07\sfx"); out.mkdir(exist_ok=True)
rng = np.random.default_rng(7)
t = lambda d: np.arange(int(SR * d)) / SR

def env(n, a=0.005, r=0.2):
    e = np.ones(n); na = int(SR * a); nr = int(SR * r)
    e[:na] = np.linspace(0, 1, na); e[-nr:] *= np.linspace(1, 0, nr) ** 2
    return e

def lp(x, k):  # простой однополюсный ФНЧ
    y = np.zeros_like(x); a = k
    for i in range(1, len(x)): y[i] = y[i - 1] + a * (x[i] - y[i - 1])
    return y

def save(name, x, peak=0.89):
    x = x / (np.abs(x).max() + 1e-9) * peak
    sf.write(out / f"{name}.wav", np.stack([x, x], 1).astype("float32"), SR)

# whoosh: шум с нарастающим/спадающим ФНЧ
d = 0.45; n = int(SR * d); nz = rng.standard_normal(n)
cut = np.sin(np.linspace(0, np.pi, n)) ** 2
y = np.zeros(n)
for i in range(1, n): y[i] = y[i - 1] + (0.02 + 0.25 * cut[i]) * (nz[i] - y[i - 1])
save("whoosh", y * cut)

# boom: саб-удар с падающей частотой + щелчок
tt = t(1.2); f = 110 * np.exp(-tt * 6) + 38
ph = 2 * np.pi * np.cumsum(f) / SR
b = np.sin(ph) * np.exp(-tt * 3.2) + 0.35 * np.tanh(3 * np.sin(ph)) * np.exp(-tt * 6)
b[:300] += rng.standard_normal(300) * np.linspace(1, 0, 300) * 0.8
save("boom", np.tanh(1.6 * b))

# ding: колокольчик (звание/убийство)
tt = t(1.0)
dg = sum(a * np.sin(2 * np.pi * fr * tt) * np.exp(-tt * dk) for fr, a, dk in [(1318, 1, 4), (2637, .4, 7), (3951, .2, 9), (1975, .25, 5)])
save("ding", dg * env(len(tt), 0.002, 0.3), 0.6)

# scratch: «зажевало пластинку» — пила с волнообразным питчем
tt = t(0.55); f = 420 + 380 * np.sin(2 * np.pi * 7 * tt) * np.exp(-tt * 1.5) - 300 * tt
ph = 2 * np.pi * np.cumsum(np.maximum(f, 60)) / SR
sc = (2 * ((ph / (2 * np.pi)) % 1) - 1) + 0.3 * rng.standard_normal(len(tt))
save("scratch", lp(sc, 0.25) * env(len(tt), 0.003, 0.15), 0.7)

# fail: грустный тромбон-спуск «ва-ва-ва-ваааа» (синтез)
notes = [(311, .35), (294, .35), (277, .35), (262, 1.2)]
seg = []
for i, (fr, dd) in enumerate(notes):
    tt = t(dd); vib = 1 + (0.012 * np.sin(2 * np.pi * 5.5 * tt) if i == 3 else 0)
    ph = 2 * np.pi * np.cumsum(fr * vib) / SR
    s = sum(np.sin(k * ph) / k ** 1.1 for k in range(1, 9))
    seg.append(lp(s, 0.18) * env(len(tt), 0.02, 0.08 if i < 3 else 0.5))
save("fail", np.concatenate(seg), 0.55)

# riser: восходящий шум+тон перед моментом
tt = t(1.4); f = 200 * 2 ** (tt * 2.4)
ph = 2 * np.pi * np.cumsum(f) / SR
r = (np.sin(ph) * 0.5 + lp(rng.standard_normal(len(tt)), 0.15)) * (tt / tt[-1]) ** 2
save("riser", r, 0.6)

# tick: щелчок таймера/счётчика
tt = t(0.06); save("tick", np.sin(2 * np.pi * 2200 * tt) * np.exp(-tt * 90), 0.5)
print(sorted(p.name for p in out.iterdir()))
