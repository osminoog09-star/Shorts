#!/usr/bin/env python3
"""Микс: голос + Kevin MacLeod «Hidden Agenda» (CC BY 4.0, с даккингом) + синтезированные SFX по events.json.
python3 audio.py → mix.wav"""
import json, subprocess
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
ROOT = HERE.parents[1]
SR = 48000
tl = json.load(open(HERE / "timeline.json")); ev = json.load(open(HERE / "events.json"))
N = int(tl["dur"] * SR)
rng = np.random.default_rng(7)

def load(p, start=0.0):
    a = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-ss", str(start), "-i", str(p), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]), np.float32).reshape(-1, 2)
    out = np.zeros((N, 2), np.float32); n = min(N, len(a)); out[:n] = a[:n]; return out

voice = load(HERE / "voice.wav")
music = load(ROOT / "media/music/Hidden Agenda.mp3")
sfx = np.zeros((N, 2), np.float32)

def put(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    s = sig[: N - i] * gain
    sfx[i:i + len(s), 0] += s * (1 - pan) ; sfx[i:i + len(s), 1] += s * (1 + pan)

def env(n, a, d):
    e = np.ones(n); ai = int(a * SR); e[:ai] = np.linspace(0, 1, ai) if ai else 1
    e[ai:] = np.exp(-np.arange(n - ai) / (d * SR)); return e

def lp(x, k):  # простой однополюсный ФНЧ
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y

def boom(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 55 * np.exp(-t * 3) + 32
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.28)
    s += lp(rng.standard_normal(n), 0.08) * env(n, 0.001, 0.05) * 0.9
    return s.astype(np.float32)

def whoosh(dur=0.35):
    n = int(dur * SR); x = rng.standard_normal(n)
    k = np.linspace(0.02, 0.35, n); y = np.empty(n); acc = 0
    for i in range(n): acc += k[i] * (x[i] - acc); y[i] = acc
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return (y * e * 0.8).astype(np.float32)

def click(f=2400, dur=0.03):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * env(n, 0.0005, 0.006)).astype(np.float32)

def glitch(dur=0.28):
    n = int(dur * SR); s = np.sign(np.sin(2 * np.pi * 180 * np.arange(n) / SR)) * 0.3
    s *= (rng.random(n // 400 + 1).repeat(400)[:n] > 0.4); s += rng.standard_normal(n) * 0.25
    return (s * env(n, 0.002, 0.15)).astype(np.float32)

def riser(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(200 + 900 * (t / dur) ** 2) / SR) * 0.25 + lp(rng.standard_normal(n), 0.2) * 0.5
    return (s * (t / dur) ** 2).astype(np.float32)

def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (600 + 900 * np.exp(-t * 40)) * t) * env(n, 0.001, 0.03)).astype(np.float32)

B, Wh = boom(), whoosh()
for t in ev["chunks"][1:]: put(Wh, t - 0.12, 0.22, rng.uniform(-0.3, 0.3))
for t in ev["scenes"][1:]: put(whoosh(0.5), t - 0.3, 0.45)
for t in ev["acc"]: put(B, t, 0.75)
for t in ev["glitch"]:
    if t is not None: put(glitch(), t, 0.5)
if ev.get("count") is not None:
    put(riser(1.0), ev["count"] - 1.0, 0.5)
    for i in range(14): put(click(3000 - i * 60), ev["count"] + i * 0.064, 0.35)
for i in range(22): put(click(1500 + rng.uniform(-300, 300), 0.02), ev["type"] + 0.15 + i * 0.07 + rng.uniform(0, 0.03), 0.3)
if ev.get("dots") is not None:
    for i in range(7): put(pop(), ev["dots"] + 0.15 + i * 0.07, 0.4)
for t in ev["pop"]:
    if t is not None: put(pop(), t, 0.45)
put(click(1800, 0.05), ev["click"], 0.8); put(click(900, 0.06), ev["click"] + 0.02, 0.5)

# даккинг музыки под голос
v = np.abs(voice).mean(1); win = int(0.12 * SR)
envv = np.convolve(v, np.ones(win) / win, "same"); envv = envv / (envv.max() + 1e-9)
duck = 1 - 0.55 * np.clip(envv * 4, 0, 1)
t = np.arange(N) / SR
fade = np.clip(t / 0.4, 0, 1) * np.clip((tl["dur"] - t) / 1.5, 0, 1)
mus = music * (0.55 * duck * fade)[:, None]
mix = voice * 1.0 + mus + sfx * 0.9
peak = np.abs(mix).max(); mix = mix / max(1.0, peak / 0.89)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), str(HERE / "mix.wav")], input=mix.astype(np.float32).tobytes(), check=True)
print("mix ok, peak", round(float(peak), 2))
