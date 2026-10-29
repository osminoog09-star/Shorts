#!/usr/bin/env python3
"""Озвучка через edge-tts (запускается в GitHub Actions, где есть интернет).

Вход: jobs/tts/<name>.json
  {"voice": "ru-RU-DmitryNeural", "rate": "+0%", "pitch": "+0Hz",
   "lines": [{"id": "s01", "text": "..."}, ...]}
Выход: media/tts/<name>/<id>.mp3 и <id>.json (границы слов в секундах)
"""
import asyncio
import json
import sys
from pathlib import Path

import edge_tts
from voice_cast import APPROVED, validate_job


async def one(text, voice, rate, pitch, mp3, meta, boundary="WordBoundary"):
    # boundary влияет только на метаданные таймингов, голос тот же (не fallback голоса)
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


async def main(job_path: str):
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    lines = validate_job(job)  # fail BEFORE writing any new audio
    out = Path("media/tts") / Path(job_path).stem
    out.mkdir(parents=True, exist_ok=True)
    for ident, text, voice, rate, pitch in lines:
        mp3 = out / f"{ident}.mp3"
        meta = out / f"{ident}.json"
        if mp3.is_file() and mp3.stat().st_size >= 1024 and meta.is_file():
            try:
                old = json.loads(meta.read_text(encoding="utf-8"))
                if (old.get("text") == text and old.get("voice_id") == voice
                        and old.get("engine") == "edge-tts" and old.get("rate") == rate
                        and old.get("pitch") == pitch):
                    print("cached", ident, voice, flush=True)
                    continue
            except (ValueError, OSError):
                pass
        for attempt in range(8):
            try:
                mp3.unlink(missing_ok=True)
                meta.unlink(missing_ok=True)
                mode = "WordBoundary" if attempt < 2 else "SentenceBoundary"
                await asyncio.wait_for(one(text, voice, rate, pitch, mp3, meta, mode), 90)
                print("ok", ident, voice, flush=True)
                break
            except Exception as ex:  # noqa: BLE001
                print("retry", ident, attempt, repr(ex), flush=True)
                mp3.unlink(missing_ok=True)
                meta.unlink(missing_ok=True)
                if attempt == 7:
                    raise RuntimeError(f"NO-GO: {voice} unavailable for {ident}; no fallback") from ex
                await asyncio.sleep(min(20, 4 + attempt * 3))
        await asyncio.sleep(1.5)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        asyncio.run(main(p))
