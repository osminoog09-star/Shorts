"""Генерация музыки и звуков для шорта (numpy -> wav)."""
import sys, wave
import numpy as np

SR = 44100
OUT = sys.argv[1]
rng = np.random.default_rng(7)


def save(name, x):
    x = np.clip(x, -1, 1)
    x = (x * 32767 * 0.9).astype(np.int16)
    with wave.open(f"{OUT}/{name}.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(x.tobytes())


def t(sec):
    return np.arange(int(SR * sec)) / SR


def env(n, a=0.005, d=0.2):
    tt = np.arange(n) / SR
    return np.minimum(tt / a, 1) * np.exp(-tt / d)


def kick():
    tt = t(0.35)
    f = 50 + 120 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, 0.12)


def hat():
    n = int(SR * 0.05)
    x = rng.normal(0, 1, n)
    x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.001, 0.015) * 0.25


def snare():
    n = int(SR * 0.2)
    tt = np.arange(n) / SR
    return (rng.normal(0, 1, n) * 0.5 + np.sin(2 * np.pi * 190 * tt)) * env(n, 0.001, 0.06) * 0.5


def tone(freq, sec, wave_="saw", d=0.15):
    tt = t(sec)
    ph = (freq * tt) % 1
    x = (2 * ph - 1) if wave_ == "saw" else np.sign(np.sin(2 * np.pi * freq * tt))
    return x * env(len(tt), 0.005, d)


def add(buf, x, at):
    i = int(at * SR)
    j = min(len(buf), i + len(x))
    if i < len(buf):
        buf[i:j] += x[: j - i]


# ---------- музыка 25 c, 128 bpm ----------
DUR, BPM = 25.0, 128
beat = 60 / BPM
mus = np.zeros(int(SR * DUR))
bass_notes = [55.0, 55.0, 65.41, 49.0]  # A1 A1 C2 G1
arp = [440, 523.25, 659.25, 783.99, 659.25, 523.25]
nb = int(DUR / beat)
for b in range(nb):
    at = b * beat
    # провал на 18-22 c: тишина и сломанный бит
    if 18.0 <= at < 21.6:
        continue
    add(mus, kick() * 0.9, at)
    if b % 2 == 1:
        add(mus, snare() * 0.6, at)
    add(mus, hat(), at + beat / 2)
    bn = bass_notes[(b // 4) % 4]
    add(mus, tone(bn, beat * 0.9, "saw", 0.25) * 0.25, at)
    if 5.5 <= at < 18:
        for k in range(2):
            add(mus, tone(arp[(b * 2 + k) % 6], beat / 2, "sq", 0.06) * 0.05, at + k * beat / 2)
# простое сглаживание
mus = np.convolve(mus, np.ones(6) / 6, mode="same")
save("music", mus * 0.8)

# ---------- SFX ----------
# whoosh
n = int(SR * 0.6)
x = rng.normal(0, 1, n)
sweep = np.sin(np.linspace(0, np.pi, n)) ** 2
x = np.convolve(x, np.ones(30) / 30, mode="same") * sweep * 3
save("whoosh", x)

# pop (звезда)
tt = t(0.18)
f = 900 + 1400 * np.exp(-tt * 25)
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.001, 0.05) * 0.8)

# chime (магия)
tt = t(1.2)
x = sum(np.sin(2 * np.pi * fr * tt) * np.exp(-tt * (2 + i)) for i, fr in enumerate([1046, 1318, 1568, 2093]))
save("chime", x * 0.25)

# tick
tt = t(0.04)
save("tick", np.sin(2 * np.pi * 2500 * tt) * env(len(tt), 0.0005, 0.008))

# boom
tt = t(1.4)
f = 35 + 80 * np.exp(-tt * 6)
x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.003, 0.5)
x += np.convolve(rng.normal(0, 1, len(tt)), np.ones(80) / 80, mode="same") * env(len(tt), 0.002, 0.25) * 2
save("boom", x * 0.9)

# вакуум (гравитация) — нисходящий свип
tt = t(1.3)
f = 600 * np.exp(-tt * 2.2) + 60
x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(tt / 0.1, 1) * np.exp(-tt * 1.2)
save("suck", x * 0.6)

# провал (wah wah wah waaah)
x = np.zeros(int(SR * 2.4))
for i, (fr, dd) in enumerate([(392, 0.45), (370, 0.45), (349, 0.45), (330, 1.0)]):
    tt = t(dd)
    vib = 1 + (0.02 * np.sin(2 * np.pi * 6 * tt) if i == 3 else 0)
    ph = np.cumsum(fr * vib) / SR
    s = (np.sin(2 * np.pi * ph) + 0.4 * np.sin(4 * np.pi * ph)) * np.minimum(tt / 0.02, 1) * np.exp(-tt * 1.5)
    add(x, s * 0.4, i * 0.45)
save("fail", x)

# скретч пластинки
tt = t(0.35)
f = 800 * np.abs(np.sin(2 * np.pi * 5 * tt)) + 100
x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3 + rng.normal(0, 0.2, len(tt))
save("scratch", x * env(len(tt), 0.002, 0.2))
print("ok")
