"""Анализ записи 2026-11-17: расшифровка микрофона/дискорда + профиль громкости игры по секундам.
Глобальное время = секунды от начала первого файла (13:05:40)."""
import json, os, subprocess, sys, datetime as dt
from pathlib import Path
import numpy as np
import os, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
os.environ["PATH"] = os.path.join(os.path.dirname(torch.__file__), "lib") + ";" + os.environ["PATH"]

REC = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings")
W = Path(os.environ.get("GAME_WORK", r"C:\M1lash\Работа\game_2026-11-17")); (W / "wav").mkdir(parents=True, exist_ok=True)
FILES = sorted(REC.glob(os.environ.get("GAME_GLOB", "Game_2026-11-17_*.mkv")))  # маска файлов OBS одной сессии
T0 = dt.datetime.strptime(FILES[0].stem[5:], "%Y-%m-%d_%H-%M-%S")

def ext(src, track, out, sr=16000):
    if not out.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", f"0:a:{track}", "-ac", "1", "-ar", str(sr), str(out)], check=True)

from faster_whisper import WhisperModel
model = WhisperModel(r"C:\M1lash\models\faster-whisper-small", device="cuda", compute_type="float16")

index, segs, loud = [], [], []
for f in FILES:
    off = (dt.datetime.strptime(f.stem[5:], "%Y-%m-%d_%H-%M-%S") - T0).total_seconds()
    index.append(dict(file=str(f), off=off))
    print("==", f.name, off, flush=True)
    for track, who in ((2, "mic"), (3, "discord")):
        wav = W / "wav" / f"{f.stem}_{who}.wav"; ext(f, track, wav)
        it, _ = model.transcribe(str(wav), language="ru", vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for s in it:
            if s.no_speech_prob > 0.6 or len(s.text.strip()) < 2: continue
            segs.append(dict(who=who, t=round(off + s.start, 2), e=round(off + s.end, 2), text=s.text.strip(), lp=round(s.avg_logprob, 2)))
    # громкость игры (дорожка Game) по 0.5 с
    gw = W / "wav" / f"{f.stem}_game.wav"; ext(f, 1, gw, sr=8000)
    a = np.memmap(gw, dtype=np.int16, mode="r", offset=44).astype(np.float32) / 32768
    n = len(a) // 4000
    rms = 20 * np.log10(np.sqrt((a[: n * 4000].reshape(n, 4000) ** 2).mean(1)) + 1e-9)
    loud += [(round(off + i * 0.5, 1), round(float(v), 1)) for i, v in enumerate(rms)]

json.dump(dict(t0=str(T0), files=index), open(W / "index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(segs, open(W / "transcript.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(loud, open(W / "loud.json", "w"))
with open(W / "transcript.txt", "w", encoding="utf-8") as o:
    for s in sorted(segs, key=lambda s: s["t"]):
        o.write(f"{int(s['t']//3600)}:{int(s['t']%3600//60):02d}:{s['t']%60:04.1f} [{s['who'][0]}] {s['text']}\n")
print("done", len(segs))
