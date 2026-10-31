#!/usr/bin/env python3
"""«Очеловечивание» голосов Димы и Светы (решение Дениса 31.10). Голос НЕ меняется (AGENTS §3):
тот же edge-tts / Azure voice_id, мы только меняем подачу и обработку.

1. Текст режется на предложения; у каждого свой небольшой разброс темпа/высоты
   (вопрос — чуть выше, восклицание — бодрее, длинная фраза — медленнее). Разброс детерминирован
   (хэш текста), поэтому повторная сборка даёт тот же звук и кэш работает.
2. Между предложениями — естественные паузы разной длины + еле слышный «вдох» перед новой мыслью.
3. Обработка: срез гула, тёплый низ, мягче «ш/с» (de-esser), лёгкая компрессия, маленькая комната,
   громкость -16 LUFS и тихий «воздух» комнаты вместо цифровой тишины.

Тайминги слов (для субтитров/липсинка) пересчитываются со сдвигом по реальным длительностям.
Включается полем "humanize": true в jobs/tts/<job>.json (по умолчанию для новых джобов — true).
"""
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

SENT = re.compile(r"[^.!?…]+(?:[.!?…]+|$)")
PAUSE = {".": 0.34, "!": 0.30, "?": 0.38, "…": 0.55}
POST = ("highpass=f=70,"
        "equalizer=f=180:t=q:w=0.9:g=2,"
        "equalizer=f=3400:t=q:w=1.2:g=-1.5,"
        "deesser=i=0.35:m=0.5:f=0.5,"
        "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=140:makeup=1.5,"
        "aecho=0.85:0.82:23|41:0.10|0.06,"
        "loudnorm=I=-16:TP=-1.5:LRA=9")


def sentences(text):
    parts = [p.strip() for p in SENT.findall(text.replace("...", "…")) if p.strip()]
    return parts or [text.strip()]


def _jitter(s, salt, lo, hi):
    h = int(hashlib.sha1((salt + s).encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return lo + (hi - lo) * h


def _pct(v):
    v = int(round(v))
    return f"{'+' if v >= 0 else ''}{v}%"


def _hz(v):
    v = int(round(v))
    return f"{'+' if v >= 0 else ''}{v}Hz"


def prosody(sentence, base_rate="+0%", base_pitch="+0Hz"):
    """Темп и высота для одного предложения."""
    r = int(base_rate.rstrip("%") or 0)
    p = int(base_pitch.rstrip("Hz") or 0)
    words = len(sentence.split())
    r += _jitter(sentence, "r", -4, 3)
    p += _jitter(sentence, "p", -3, 3)
    end = sentence.rstrip()[-1:] if sentence.strip() else "."
    if end == "?":
        p += 4
    if end == "!":
        r += 3
        p += 2
    if words >= 14:
        r -= 3
    if words <= 3:
        r -= 2
    return _pct(r), _hz(p)


def gap_after(sentence):
    end = sentence.rstrip()[-1:]
    return PAUSE.get(end, 0.28) + _jitter(sentence, "g", -0.05, 0.06)


def _dur(path):
    out = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                   "-of", "default=nw=1:nk=1", str(path)])
    return float(out.strip() or 0)


def _run(args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def silence(path, sec, breath=False):
    """Пауза с тихим «воздухом»; при breath=True в конце паузы — короткий мягкий вдох."""
    if breath and sec >= 0.3:
        b = 0.22
        _run(["-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.0016:d={sec:.3f}:r=24000",
              "-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.05:d={b}:r=24000",
              "-filter_complex",
              f"[1]bandpass=f=1300:w=1800,afade=t=in:d=0.12,afade=t=out:st={b-0.09:.2f}:d=0.09,"
              f"volume=-6dB,adelay={int((sec-b-0.02)*1000)}|{int((sec-b-0.02)*1000)}[br];"
              f"[0][br]amix=inputs=2:normalize=0,aformat=sample_rates=24000:channel_layouts=mono",
              "-c:a", "pcm_s16le", str(path)])
    else:
        _run(["-f", "lavfi", "-i", f"anoisesrc=c=pink:a=0.0016:d={sec:.3f}:r=24000",
              "-ac", "1", "-c:a", "pcm_s16le", str(path)])


def assemble(pieces, out_mp3):
    """pieces: [(wav_or_mp3, gap_after_sec, breath_before_next)] → out_mp3 с обработкой POST.
    Возвращает список смещений начала каждого куска (сек)."""
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        seq, offsets, t = [], [], 0.0
        for i, (src, gap, breath) in enumerate(pieces):
            w = td / f"p{i}.wav"
            # убираем цифровую тишину по краям фразы, чтобы паузы были нашими
            _run(["-i", str(src), "-af",
                  "silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.02,"
                  "areverse,silenceremove=start_periods=1:start_threshold=-50dB:start_silence=0.04,areverse,"
                  "aformat=sample_rates=24000:channel_layouts=mono", "-c:a", "pcm_s16le", str(w)])
            offsets.append(t)
            seq.append(w)
            t += _dur(w)
            if i < len(pieces) - 1:
                s = td / f"s{i}.wav"
                silence(s, gap, breath)
                seq.append(s)
                t += _dur(s)
        lst = td / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in seq), encoding="utf-8")
        raw = td / "raw.wav"
        _run(["-f", "concat", "-safe", "0", "-i", str(lst), "-c:a", "pcm_s16le", str(raw)])
        _run(["-i", str(raw), "-af", POST + ",aformat=sample_rates=24000:channel_layouts=mono",
              "-c:a", "libmp3lame", "-b:a", "160k", str(out_mp3)])
        return offsets, td


async def humanized(one, text, voice, rate, pitch, mp3, meta, extra):
    """Синтез по предложениям через ту же функцию one() (edge-tts), сборка и обработка."""
    sents = sentences(text)
    words, pieces = [], []
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        parts = []
        for i, s in enumerate(sents):
            r, p = prosody(s, rate, pitch)
            pm, pj = td / f"{i}.mp3", td / f"{i}.json"
            await one(s, voice, r, p, pm, pj)
            parts.append((pm, json.loads(pj.read_text(encoding="utf-8")), r, p))
        for i, (pm, pjd, r, p) in enumerate(parts):
            nxt_long = i + 1 < len(sents) and len(sents[i + 1].split()) >= 6
            pieces.append((pm, gap_after(sents[i]), nxt_long))
        offsets, _ = assemble(pieces, mp3)
        # сдвиг таймингов: start куска − начало речи в исходном mp3 (тишину по краям срезали)
        for (pm, pjd, r, p), off in zip(parts, offsets):
            ws = pjd.get("words") or []
            lead = ws[0]["start"] if ws else 0.0
            for w in ws:
                words.append({"w": w["w"], "start": round(off + max(0.0, w["start"] - lead), 3),
                              "end": round(off + max(0.0, w["end"] - lead), 3)})
        data = json.loads(parts[0][1] and json.dumps(parts[0][1]))
    data.update({"text": text, "words": words, "rate": rate, "pitch": pitch, "humanize": True,
                 "prosody": [{"s": s, "rate": r, "pitch": p} for s, (_, _, r, p) in zip(sents, parts)],
                 "post": POST, "source_file": str(mp3), **extra})
    Path(meta).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
