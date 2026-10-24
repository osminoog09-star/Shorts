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


async def one(text, voice, rate, pitch, mp3, meta):
    try:
        com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
    except TypeError:
        com = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    words = []
    with open(mp3, "wb") as f:
        async for ch in com.stream():
            if ch["type"] == "audio":
                f.write(ch["data"])
            elif ch["type"] == "WordBoundary":
                words.append({"w": ch["text"], "start": ch["offset"] / 1e7,
                              "end": (ch["offset"] + ch["duration"]) / 1e7})
    meta.write_text(json.dumps({"text": text, "words": words}, ensure_ascii=False, indent=1), encoding="utf-8")


async def main(job_path: str):
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    out = Path("media/tts") / Path(job_path).stem
    out.mkdir(parents=True, exist_ok=True)
    for ln in job["lines"]:
        mp3 = out / f"{ln['id']}.mp3"
        meta = out / f"{ln['id']}.json"
        if mp3.exists() and meta.exists() and json.loads(meta.read_text(encoding="utf-8")).get("text") == ln["text"]:
            continue
        for attempt in range(5):
            try:
                await one(ln["text"], ln.get("voice", job["voice"]), ln.get("rate", job.get("rate", "+0%")),
                          ln.get("pitch", job.get("pitch", "+0Hz")), mp3, meta)
                print("ok", ln["id"]); break
            except Exception as ex:  # noqa: BLE001
                print("retry", ln["id"], attempt, repr(ex)); mp3.unlink(missing_ok=True)
                await asyncio.sleep(4 + attempt * 6)
        await asyncio.sleep(1.5)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        asyncio.run(main(p))
