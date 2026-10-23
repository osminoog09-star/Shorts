"""Звуки для ролика про GPT и Кодекс."""
import sys, wave
import numpy as np

SR = 44100
OUT = sys.argv[1]
rng = np.random.default_rng(11)


def save(name, x):
    x = np.clip(x, -1, 1)
    with wave.open(f"{OUT}/{name}.wav", "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((x * 32767 * 0.9).astype(np.int16).tobytes())


def env(n, a, d):
    tt = np.arange(n) / SR
    return np.minimum(tt / a, 1) * np.exp(-tt / d)


def add(buf, x, at):
    i = int(at * SR); j = min(len(buf), i + len(x))
    if i < len(buf): buf[i:j] += x[: j - i]


# лоу-фай бит 30 с, 92 bpm, обрыв на 24-27 с
DUR, BPM = float(sys.argv[2]), 92
beat = 60 / BPM
mus = np.zeros(int(SR * DUR))
chords = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 349.2]]
for b in range(int(DUR / beat)):
    at = b * beat
    if float(sys.argv[3]) <= at < float(sys.argv[4]):
        continue
    n = int(SR * 0.3); tt = np.arange(n) / SR
    if b % 4 in (0, 2) or (b % 8 == 7):
        fk = 45 + 90 * np.exp(-tt * 28)
        add(mus, np.sin(2 * np.pi * np.cumsum(fk) / SR) * env(n, 0.002, 0.13) * 0.9, at)
    if b % 4 in (1, 3):
        m = int(SR * 0.18)
        add(mus, rng.normal(0, 1, m) * env(m, 0.001, 0.05) * 0.35, at)
    for k in (0, 0.5):
        m = int(SR * 0.04)
        add(mus, np.diff(np.concatenate([[0], rng.normal(0, 1, m)])) * env(m, 0.001, 0.012) * 0.12, at + k * beat)
    if b % 4 == 0:
        ch = chords[(b // 4) % 4]
        m = int(SR * beat * 4); tt = np.arange(m) / SR
        pad = sum(np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(4 * np.pi * fr * tt) for fr in ch)
        add(mus, pad * env(m, 0.08, 1.4) * 0.05, at)
        bass = np.sin(2 * np.pi * ch[0] / 2 * tt) * env(m, 0.01, 0.8) * 0.25
        add(mus, bass, at)
mus = np.convolve(mus, np.ones(5) / 5, "same")
save(sys.argv[5], mus * 0.85)
print("ok")
