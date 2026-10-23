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


# набор текста: 1.2 с щелчков
buf = np.zeros(int(SR * 1.2))
tpos = 0.0
while tpos < 1.1:
    n = int(SR * 0.03)
    c = rng.normal(0, 1, n) * env(n, 0.0005, 0.004) * rng.uniform(0.3, 0.7)
    add(buf, c, tpos)
    tpos += rng.uniform(0.05, 0.11)
save("type", buf)

# сообщение (дзинь)
tt = np.arange(int(SR * 0.5)) / SR
x = np.sin(2 * np.pi * 880 * tt) * env(len(tt), 0.002, 0.08) + np.sin(2 * np.pi * 1320 * tt) * env(len(tt), 0.002, 0.12) * (tt > 0.07)
save("ding", x * 0.5)

# отправка (свуп вверх)
tt = np.arange(int(SR * 0.18)) / SR
f = 400 + 2200 * tt / 0.18
save("send", np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.003, 0.08) * 0.5)

# ошибка (бззт)
tt = np.arange(int(SR * 0.45)) / SR
x = np.sign(np.sin(2 * np.pi * 110 * tt)) * 0.35 * env(len(tt), 0.003, 0.3)
save("error", x)

# тревожный аларм
tt = np.arange(int(SR * 1.2)) / SR
f = 700 + 300 * np.sign(np.sin(2 * np.pi * 4 * tt))
save("alarm", np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 * np.minimum(1, (1.2 - tt) * 5))

# мусорка (шурх + стук)
n = int(SR * 0.5)
x = np.convolve(rng.normal(0, 1, n), np.ones(20) / 20, "same") * env(n, 0.01, 0.12) * 2
tt = np.arange(n) / SR
x += np.sin(2 * np.pi * 140 * tt) * env(n, 0.001, 0.05) * (tt > 0.25)
save("trash", x)

# лоу-фай бит 30 с, 92 bpm, обрыв на 24-27 с
DUR, BPM = 30.0, 92
beat = 60 / BPM
mus = np.zeros(int(SR * DUR))
chords = [[261.6, 329.6, 392.0, 493.9], [220.0, 261.6, 329.6, 392.0], [174.6, 220.0, 261.6, 329.6], [196.0, 246.9, 293.7, 349.2]]
for b in range(int(DUR / beat)):
    at = b * beat
    if 26.0 <= at < 28.3:
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
save("music_code", mus * 0.85)
print("ok")
