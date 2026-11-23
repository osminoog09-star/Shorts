"""words.py 0:28:20 0:29:40 [0:35:20 0:36:50 ...] -> пословные таймкоды (глобальные) мик/дискорд."""
import os, sys, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
os.environ["PATH"] = os.path.join(os.path.dirname(torch.__file__), "lib") + ";" + os.environ["PATH"]
import soundfile as sf
from faster_whisper import WhisperModel
from src import W, locate, hms
from pathlib import Path
import json, numpy as np
G = json.load(open(W / "gains.json", encoding="utf-8"))
m = WhisperModel(r"C:\M1lash\models\faster-whisper-small", device="cuda", compute_type="float16")
args = sys.argv[1:]
for a, b in zip(args[::2], args[1::2]):
    a, b = hms(a), hms(b); f, la = locate(a)
    print(f"===== {args[args.index([x for x in args if hms(x)==a][0])]}")
    lines = []
    for who in ("mic", "discord"):
        wav = W / "wav" / f"{Path(f).stem}_{who}.wav"
        x, sr = sf.read(str(wav), start=int(la * 16000), stop=int((la + b - a) * 16000), dtype="float32")
        x = np.clip(x * G[f][who], -1, 1)
        it, _ = m.transcribe(x, language="ru", word_timestamps=True, vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for s in it:
            for w in s.words:
                lines.append((a + w.start, who[0], w.word))
    lines.sort()
    cur, out = None, []
    for t, who, w in lines:
        if cur and cur[1] == who and t - cur[2] < 1.2:
            cur[3] += w; cur[2] = t
        else:
            if cur: out.append(cur)
            cur = [t, who, t, w]
    if cur: out.append(cur)
    for t0, who, t1, txt in out:
        print(f"{int(t0//3600)}:{int(t0%3600//60):02d}:{t0%60:05.2f}-{t1%60:05.2f} [{who}]{txt}")
