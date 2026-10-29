#!/usr/bin/env python3
"""Склейка озвучки + таймлайн слов для кинетической типографики (S6-D25).
python3 build.py → voice.wav, timeline.json"""
import json, re, subprocess, difflib
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
TTS = HERE.parents[1] / "media" / "tts" / "ai_blackmail"
IDS = ["s01", "s02", "s03", "s04", "s05", "s06", "s07"]
GAP = {"s01": 0.3, "s02": 0.25, "s03": 0.25, "s04": 0.35, "s05": 0.3, "s06": 0.3}
LEAD, TAIL = 0.12, 1.8
TEMPO = 1.1  # ускорение голоса (Shorts ≈ 1 мин)
WORK = HERE / "work"; WORK.mkdir(exist_ok=True)
_model = None

def align(wav, text):
    """Тайминги слов: whisper (word_timestamps) → сопоставление со словами текста."""
    global _model
    from faster_whisper import WhisperModel
    if _model is None: _model = WhisperModel(str(Path.home() / "wm/small"), device="cpu", compute_type="int8")
    a = np.frombuffer(subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(wav), "-ac", "1", "-ar", "16000", "-f", "f32le", "-"]), np.float32)
    segs, _ = _model.transcribe(a, language="ru", word_timestamps=True, initial_prompt=text)
    hw = [w for sg in segs for w in sg.words]
    norm = lambda x: re.sub(r"[^\wё]", "", x.lower().replace("ё", "е"))
    tw = re.findall(r"[\w-]+", text)
    A, B = [norm(x) for x in tw], [norm(w.word) for w in hw]
    res = [None] * len(tw)
    for blk in difflib.SequenceMatcher(None, A, B, autojunk=False).get_matching_blocks():
        for k in range(blk.size): res[blk.a + k] = (hw[blk.b + k].start, hw[blk.b + k].end)
    # непойманные слова — интерполяция между соседями
    for i in range(len(tw)):
        if res[i] is None:
            j = i
            while j < len(tw) and res[j] is None: j += 1
            s0 = res[i - 1][1] if i else (hw[0].start if hw else 0)
            e0 = res[j][0] if j < len(tw) else (hw[-1].end if hw else s0 + 0.3 * (j - i))
            step = max(0.05, (e0 - s0) / (j - i))
            for k in range(i, j): res[k] = (s0 + (k - i) * step, s0 + (k - i + 1) * step)
    miss = sum(1 for x in A if x not in B)
    return [{"w": w, "start": r[0], "end": r[1]} for w, r in zip(tw, res)], miss

def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))

words, scenes, parts, t = [], [], [], LEAD
for sid in IDS:
    meta = json.loads((TTS / f"{sid}.json").read_text())
    src = WORK / f"{sid}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(TTS / f"{sid}.mp3"), "-af", f"atempo={TEMPO}", "-ar", "48000", str(src)], check=True)
    if meta.get("boundary", "WordBoundary") == "WordBoundary" and len(meta["words"]) >= 3:
        meta["words"] = [dict(w, start=w["start"] / TEMPO, end=w["end"] / TEMPO) for w in meta["words"]]
    else:
        meta["words"], miss = align(src, meta["text"]); print(sid, "aligned by whisper, unmatched", miss)
    d = dur(src)
    scenes.append({"id": sid, "s": round(t, 3), "e": round(t + d, 3)})
    for w in meta["words"]:
        words.append({"w": w["w"], "s": round(t + w["start"], 3), "e": round(t + w["end"], 3), "sc": sid})
    parts.append((src, t))
    t += d + GAP.get(sid, 0)
total = round(t + TAIL, 2)

# голос в один wav: каждую фразу ставим на её время
inputs, filt = [], []
for i, (p, st) in enumerate(parts):
    inputs += ["-i", str(p)]
    ms = int(st * 1000)
    filt.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms}[a{i}]")
filt.append("".join(f"[a{i}]" for i in range(len(parts))) + f"amix=inputs={len(parts)}:normalize=0,apad,atrim=0:{total}[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]", "-ac", "2", str(HERE / "voice.wav")], check=True)
json.dump({"dur": total, "scenes": scenes, "words": words}, open(HERE / "timeline.json", "w"), ensure_ascii=False, indent=0)
print("dur", total, "words", len(words))
