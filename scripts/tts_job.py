#!/usr/bin/env python3
"""Озвучка Димы/Светы (запускается в GitHub Actions, где есть интернет).

Движок: Azure Speech, если заданы AZURE_SPEECH_KEY и AZURE_SPEECH_REGION (решение 30.10.2026),
иначе edge-tts. Голос один и тот же; движок выбирается на весь джоб, внутри ролика не смешивается.
TTS_ENGINE=azure|edge принудительно (azure без ключа -> ошибка, без подмены).
У строки может быть поле "ssml" (разметка внутри <voice>: <break time="300ms"/>, <emphasis>) — только для Azure.

Вход: jobs/tts/<name>.json
  {"voice": "ru-RU-DmitryNeural", "rate": "+0%", "pitch": "+0Hz",
   "lines": [{"id": "s01", "text": "..."}, ...]}
Выход: media/tts/<name>/<id>.mp3 и <id>.json (границы слов в секундах)
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from voice_cast import APPROVED, validate_job
import tts_azure
import voice_humanize


async def one(text, voice, rate, pitch, mp3, meta, boundary="WordBoundary"):
    # boundary влияет только на метаданные таймингов, голос тот же (не fallback голоса)
    import edge_tts  # noqa: PLC0415
    try:
        com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary=boundary)
    except TypeError:
        com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    words = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] in ("WordBoundary", "SentenceBoundary"):
                words.append({"w": ch["text"], "start": ch["offset"] / 1e7,
                              "end": (ch["offset"] + ch["duration"]) / 1e7})
    if not mp3.is_file() or mp3.stat().st_size < 1024:
        raise RuntimeError(f"NO-GO: no usable TTS audio for {voice}")
    meta.write_text(json.dumps({"text": text, "words": words, "voice_id": voice,
                                "speaker": APPROVED[voice], "engine": "edge-tts",
                                "rate": rate, "pitch": pitch, "boundary": boundary,
                                "source_file": str(mp3)}, ensure_ascii=False, indent=1), encoding="utf-8")


def pick_engine() -> str:
    want = os.environ.get("TTS_ENGINE", "auto").lower()
    if want == "azure":
        if not tts_azure.available():
            raise RuntimeError("NO-GO: TTS_ENGINE=azure, but AZURE_SPEECH_KEY/REGION are not set")
        return tts_azure.ENGINE
    if want == "edge":
        return "edge-tts"
    return tts_azure.ENGINE if tts_azure.available() else "edge-tts"


async def main(job_path: str):
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    lines = validate_job(job)  # fail BEFORE writing any new audio
    ssml_by_id = {ln.get("id"): ln.get("ssml") for ln in job["lines"]}
    humanize = bool(job.get("humanize", True))  # решение Дениса 31.10: живая подача по умолчанию
    engine = pick_engine()
    print("engine", engine, flush=True)
    out = Path("media/tts") / Path(job_path).stem
    out.mkdir(parents=True, exist_ok=True)
    for ident, text, voice, rate, pitch in lines:
        ssml = ssml_by_id.get(ident)
        if ssml and engine != tts_azure.ENGINE:
            raise RuntimeError(f"NO-GO: line {ident} needs SSML, which only Azure supports")
        mp3 = out / f"{ident}.mp3"
        meta = out / f"{ident}.json"
        if mp3.is_file() and mp3.stat().st_size >= 1024 and meta.is_file():
            try:
                old = json.loads(meta.read_text(encoding="utf-8"))
                if (old.get("text") == text and old.get("voice_id") == voice
                        and old.get("engine") == engine and old.get("ssml") == ssml_by_id.get(ident) and old.get("rate") == rate
                        and old.get("pitch") == pitch and bool(old.get("humanize")) == (humanize and engine != tts_azure.ENGINE)):
                    print("cached", ident, voice, flush=True)
                    continue
            except (ValueError, OSError):
                pass
        for attempt in range(8):
            try:
                mp3.unlink(missing_ok=True)
                meta.unlink(missing_ok=True)
                if engine == tts_azure.ENGINE:
                    await asyncio.wait_for(asyncio.to_thread(
                        tts_azure.synth, text, voice, rate, pitch, mp3, meta, APPROVED[voice], ssml), 120)
                else:
                    mode = "WordBoundary" if attempt < 2 else "SentenceBoundary"
                    if humanize:
                        async def _one(t_, v_, r_, p_, m_, j_):
                            await one(t_, v_, r_, p_, m_, j_, mode)
                        await asyncio.wait_for(voice_humanize.humanized(_one, text, voice, rate, pitch, mp3, meta, {}), 240)
                    else:
                        await asyncio.wait_for(one(text, voice, rate, pitch, mp3, meta, mode), 90)
                print("ok", ident, voice, flush=True)
                break
            except Exception as ex:  # noqa: BLE001
                print("retry", ident, attempt, repr(ex), flush=True)
                (out / "_errors.log").open("a", encoding="utf-8").write(f"{ident} attempt {attempt}: {ex!r}\n")
                mp3.unlink(missing_ok=True)
                meta.unlink(missing_ok=True)
                if attempt == 7:
                    raise RuntimeError(f"NO-GO: {voice} unavailable for {ident}; no fallback") from ex
                await asyncio.sleep(min(20, 4 + attempt * 3))
        await asyncio.sleep(1.5)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        asyncio.run(main(p))
