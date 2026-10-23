"""Озвучка «Притворись ботом»: голоса, пикание мата, шумы, таймлайны, музыка."""
import os as _os
ROOT_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import json, os, re, subprocess, sys, wave
import numpy as np

ROOT = ROOT_DIR
VOICES = _os.path.join(ROOT_DIR, "voices")
FPS, SR = 30, 44100
TITLE, GAP, END = 56, 6, 70

ROBO = "aecho=0.7:0.6:9|17:0.4|0.25,flanger=delay=2:depth=2:speed=6,highpass=f=150"
CAST = {
    "ru": {
        "n": ("rh", "aleksandr-hq", "atempo=1.06"),
        "nr": ("rh", "aleksandr-hq", "atempo=0.92," + ROBO),
        "nw": ("rh", "aleksandr-hq", "atempo=1.25,highpass=f=300,volume=0.8"),
        "hr": ("rh", "artemiy", "asetrate=44100*0.94,aresample=44100,atempo=1.12," + ROBO),
        "col": ("rh", "pavel", "asetrate=44100*1.05,aresample=44100,atempo=1.0," + ROBO),
        "guard": ("rh", "vitaliy", "asetrate=44100*0.85,aresample=44100,atempo=1.25," + ROBO),
        "boss": ("rh", "mikhail", "asetrate=44100*0.82,aresample=44100,atempo=1.15,aecho=0.8:0.7:40:0.3," + ROBO),
        "old": ("rh", "yuriy", "atempo=0.9"),
        "colh": ("rh", "pavel", "atempo=0.95"),
        "plumb": ("rh", "vitaliy", "atempo=1.0"),
        "agent": ("rh", "anna", "atempo=1.0,aecho=0.6:0.5:7:0.3,highpass=f=120"),
        "coffee": ("rh", "evgeniy-rus", "asetrate=44100*0.72,aresample=44100,atempo=1.1,aecho=0.8:0.85:60|120:0.4|0.25"),
    },
    "en": {
        "n": ("piper", "en-us-ryan-high", "atempo=1.05"),
        "nr": ("piper", "en-us-ryan-high", "atempo=0.92," + ROBO),
        "nw": ("piper", "en-us-ryan-high", "atempo=1.2,highpass=f=300,volume=0.8"),
        "hr": ("rh", "alan", "asetrate=44100*0.94,aresample=44100,atempo=1.1," + ROBO),
        "col": ("rh", "bdl", "asetrate=44100*1.05,aresample=44100," + ROBO),
        "guard": ("piper", "en-us-ryan-medium", "asetrate=44100*0.85,aresample=44100,atempo=1.2," + ROBO),
        "boss": ("rh", "evgeniy-eng", "asetrate=44100*0.82,aresample=44100,atempo=1.15,aecho=0.8:0.7:40:0.3," + ROBO),
        "old": ("rh", "bdl", "asetrate=44100*0.9,aresample=44100,atempo=0.95"),
        "colh": ("rh", "alan", "atempo=0.95"),
        "plumb": ("piper", "en-us-ryan-medium", "atempo=1.0"),
        "agent": ("rh", "slt", "atempo=1.0,aecho=0.6:0.5:7:0.3,highpass=f=120"),
        "coffee": ("rh", "alan", "asetrate=44100*0.72,aresample=44100,atempo=1.1,aecho=0.8:0.85:60|120:0.4|0.25"),
    },
}


def readw(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768


def savew(p, x):
    with wave.open(p, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def tts(lang, who, text, out):
    eng, voice, fx = CAST[lang][who]
    raw = out + ".raw.wav"
    if eng == "rh":
        subprocess.run(["RHVoice-test", "-p", voice, "-o", raw], input=text.encode(), check=True, capture_output=True)
    else:
        subprocess.run(["python3", "-m", "piper", "-m", f"{VOICES}/{voice}.onnx", "-f", raw], input=text.encode(), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", raw, "-af",
                    f"aresample={SR},{fx},silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-15:TP=-1.5",
                    "-ar", str(SR), "-ac", "1", out], check=True)
    os.remove(raw)
    return readw(out)


def bleep(sec=0.42):
    t = np.arange(int(SR * sec)) / SR
    return np.sin(2 * np.pi * 1000 * t) * 0.32 * np.minimum(1, np.minimum(t, sec - t) / 0.01)


def say(lang, who, text, out):
    parts = re.split(r"\[(?:бип|beep)\]", text)
    chunks = []
    for i, p in enumerate(parts):
        p = p.strip(" ,")
        if re.search(r"\w", p):
            chunks.append(tts(lang, who, p, out))
        if i < len(parts) - 1:
            chunks.append(np.zeros(int(SR * 0.05)))
            chunks.append(bleep())
            chunks.append(np.zeros(int(SR * 0.05)))
    x = np.concatenate(chunks)
    savew(out, x)
    return x


SRC = sys.argv[1] if len(sys.argv) > 1 else "bot_series"
TLN = sys.argv[2] if len(sys.argv) > 2 else "bot_tl"
EPS = json.load(open(f"{ROOT}/src/{SRC}.json"))
ONLY = set(sys.argv[3].split(",")) if len(sys.argv) > 3 else None
try:
    res = json.load(open(f"{ROOT}/src/{TLN}.json"))
except Exception:
    res = {}
for ep in EPS:
    if ONLY and ep["id"] not in ONLY:
        continue
    res[ep["id"]] = {}
    for lang in ("ru", "en"):
        d = f"{ROOT}/public/bot/{ep['id']}/{lang}"
        os.makedirs(d, exist_ok=True)
        cur, lines, mouth = TITLE, {}, []
        for ln in ep["lines"]:
            if ln["who"] == "fx":
                lines[ln["id"]] = {"start": cur, "end": cur + ln["dur"], "who": "fx", "file": None}
                cur += ln["dur"] + GAP
                continue
            fn = f"bot/{ep['id']}/{lang}/{ln['id']}.wav"
            x = say(lang, ln["who"], ln["text"][lang], f"{ROOT}/public/{fn}")
            nfr = int(np.ceil(len(x) / SR * FPS))
            lines[ln["id"]] = {"start": cur, "end": cur + nfr, "who": ln["who"], "file": fn}
            if ln["who"] in ("n", "nr", "nw"):
                hop = SR // FPS
                env = [float(np.sqrt(np.mean(x[i * hop:(i + 1) * hop] ** 2) + 1e-9)) for i in range(nfr)]
                mx = max(env) or 1
                mouth += [0] * (cur - len(mouth))
                mouth += [round(min(1, e / mx * 1.4), 3) for e in env]
            cur += nfr + GAP
        total = cur + END
        mouth += [0] * (total - len(mouth))
        res[ep["id"]][lang] = {"lines": lines, "total": total, "mouth": mouth[:total]}
        subprocess.run(["python3", f"{ROOT}/tools/music.py", f"{ROOT}/public", str(total / FPS + 0.5), "999", "999", f"music_bot_{ep['id']}_{lang}"], check=True, capture_output=True)
        print(ep["id"], lang, round(total / FPS, 1), "s")
json.dump(res, open(f"{ROOT}/src/{TLN}.json", "w"))

# доп. звуки
rng = np.random.default_rng(5)
t = np.arange(int(SR * 1.5)) / SR
f = 70 + 25 * np.sin(2 * np.pi * 3 * t) + 15 * np.sin(2 * np.pi * 7.3 * t)
g = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / 1.5) ** 0.6
g += np.convolve(rng.normal(0, 1, len(t)), np.ones(200) / 200, "same") * 2 * np.sin(np.pi * t / 1.5)
savew(f"{ROOT}/public/growl.wav", g * 0.8)
t = np.arange(int(SR * 1.6)) / SR
cr = np.zeros_like(t)
for k in range(5):
    s0 = k * 0.32
    m = (t > s0) & (t < s0 + 0.12)
    cr += np.sin(2 * np.pi * 4300 * t) * m * (0.5 + 0.5 * np.sin(2 * np.pi * 60 * t)) * 0.25
savew(f"{ROOT}/public/crickets.wav", cr)
t = np.arange(int(SR * 0.35)) / SR
th = np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 20)) * t) * np.exp(-t * 12) + np.convolve(rng.normal(0, 1, len(t)), np.ones(40) / 40, "same") * np.exp(-t * 25)
savew(f"{ROOT}/public/thud.wav", th * 0.9)
t = np.arange(int(SR * 0.5)) / SR
st = np.convolve(rng.normal(0, 1, len(t)), np.ones(15) / 15, "same") * np.exp(-t * 18) * 2 + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 15)
savew(f"{ROOT}/public/stamp.wav", st * 0.8)
t = np.arange(int(SR * 0.25)) / SR
savew(f"{ROOT}/public/servo.wav", np.sign(np.sin(2 * np.pi * (300 + 600 * t / 0.25) * t)) * 0.12 * np.sin(np.pi * t / 0.25))
print("sfx ok")
