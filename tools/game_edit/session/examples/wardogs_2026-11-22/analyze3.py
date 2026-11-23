"""Повторная расшифровка мика/Discord с усилением по gains.json (тихие дорожки whisper-VAD пропускал).
Пишет transcript.json / transcript.txt (старые -> *_v1)."""
import json, os, shutil
from pathlib import Path
import numpy as np, soundfile as sf
import torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
os.environ["PATH"] = os.path.join(os.path.dirname(torch.__file__), "lib") + ";" + os.environ["PATH"]
from faster_whisper import WhisperModel

W = Path(r"C:\M1lash\Работа\wardogs_2026-11-22")
IDX = json.load(open(W / "index.json", encoding="utf-8"))["files"]
G = json.load(open(W / "gains.json", encoding="utf-8"))
for n in ("transcript.json", "transcript.txt"):
    if (W / n).exists() and not (W / (n + "_v1")).exists(): shutil.copy(W / n, W / (n + "_v1"))
model = WhisperModel(r"C:\M1lash\models\faster-whisper-small", device="cuda", compute_type="float16")
segs = []
for x in IDX:
    f, off = x["file"], x["off"]; stem = Path(f).stem
    print("==", stem, flush=True)
    for who in ("mic", "discord"):
        g = G[f][who]; raw = G[f]["raw"][who][0]
        if raw <= -69: continue  # дорожка пустая
        a, sr = sf.read(str(W / "wav" / f"{stem}_{who}.wav"), dtype="float32")
        a = np.clip(a * g, -1, 1)
        it, _ = model.transcribe(a, language="ru", vad_filter=True, beam_size=5, condition_on_previous_text=False)
        n0 = len(segs)
        for s in it:
            if s.no_speech_prob > 0.6 or len(s.text.strip()) < 2: continue
            segs.append(dict(who=who, t=round(off + s.start, 2), e=round(off + s.end, 2), text=s.text.strip(), lp=round(s.avg_logprob, 2)))
        print("  ", who, "gain", g, "->", len(segs) - n0, flush=True)
    json.dump(segs, open(W / "transcript.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
with open(W / "transcript.txt", "w", encoding="utf-8") as o:
    for s in sorted(segs, key=lambda s: s["t"]):
        o.write(f"{int(s['t']//3600)}:{int(s['t']%3600//60):02d}:{s['t']%60:04.1f} [{s['who'][0]}] {s['text']}\n")
print("done", len(segs))
