"""Анализ Wardogs 22–23.11.2026: расшифровка мика/Discord (whisper small) + громкость игры по 0,5 с.
Глобальное время = секунды от начала первого файла; смещения монотонные (учтены паузы записи OBS)."""
import json, os, subprocess, datetime as dt
from pathlib import Path
import numpy as np
import torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
os.environ["PATH"] = os.path.join(os.path.dirname(torch.__file__), "lib") + ";" + os.environ["PATH"]

W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22"); (W / "wav").mkdir(parents=True, exist_ok=True)
R = Path(r"C:\Users\osmin\Videos\Gameplay\Recordings")
NAMES = [
    "Вардокс/Game_2026-11-22_02-25-17",
    "Вардокс/Game_2026-11-22_17-18-27", "Вардокс/Game_2026-11-22_18-18-27", "Вардокс/Game_2026-11-22_20-14-07",
    "Вардокс/Game_2026-11-22_20-37-42", "Вардокс/Game_2026-11-22_21-37-43", "Вардокс/Game_2026-11-22_22-37-43",
    "Вардокс/Game_2026-11-22_22-51-52", "Вардокс/Game_2026-11-22_23-51-53", "Вардокс/Game_2026-11-23_00-51-54",
    "Вардокс/Game_2026-11-23_01-00-56", "Вардокс/Game_2026-11-23_02-00-56",
    "Game_2026-11-23_13-51-42", "Game_2026-11-23_14-10-32", "Game_2026-11-23_14-42-58",
]
FILES = [R / (n + ".mkv") for n in NAMES]

def ts(f): return dt.datetime.strptime(f.stem[5:], "%Y-%m-%d_%H-%M-%S")
def dur(f): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout)
T0 = ts(FILES[0])

def ext(src, track, out, sr=16000):
    if not out.exists():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-map", f"0:a:{track}", "-ac", "1", "-ar", str(sr), str(out)], check=True)

from faster_whisper import WhisperModel
model = WhisperModel(r"C:\M1lash\models\faster-whisper-small", device="cuda", compute_type="float16")

index, segs, loud = [], [], []
prev_end = 0.0
for f in FILES:
    d = dur(f)
    off = max((ts(f) - T0).total_seconds(), prev_end + 5.0)
    prev_end = off + d
    index.append(dict(file=str(f), off=off, dur=d, wall=str(ts(f))))
    print("==", f.name, round(off), round(d), flush=True)
    for track, who in ((2, "mic"), (3, "discord")):
        wav = W / "wav" / f"{f.stem}_{who}.wav"; ext(f, track, wav)
        it, _ = model.transcribe(str(wav), language="ru", vad_filter=True, beam_size=5, condition_on_previous_text=False)
        for s in it:
            if s.no_speech_prob > 0.6 or len(s.text.strip()) < 2: continue
            segs.append(dict(who=who, t=round(off + s.start, 2), e=round(off + s.end, 2), text=s.text.strip(), lp=round(s.avg_logprob, 2)))
    gw = W / "wav" / f"{f.stem}_game.wav"; ext(f, 1, gw, sr=8000)
    a = np.memmap(gw, dtype=np.int16, mode="r", offset=44).astype(np.float32) / 32768
    n = len(a) // 4000
    rms = 20 * np.log10(np.sqrt((a[: n * 4000].reshape(n, 4000) ** 2).mean(1)) + 1e-9)
    loud += [(round(off + i * 0.5, 1), round(float(v), 1)) for i, v in enumerate(rms)]
    # промежуточное сохранение, чтобы обрыв не терял работу
    json.dump(dict(t0=str(T0), files=index), open(W / "index.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(segs, open(W / "transcript.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

json.dump(loud, open(W / "loud.json", "w"))
with open(W / "transcript.txt", "w", encoding="utf-8") as o:
    for s in sorted(segs, key=lambda s: s["t"]):
        o.write(f"{int(s['t']//3600)}:{int(s['t']%3600//60):02d}:{s['t']%60:04.1f} [{s['who'][0]}] {s['text']}\n")
print("done", len(segs))
