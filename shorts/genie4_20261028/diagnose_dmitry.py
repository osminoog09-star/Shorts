#!/usr/bin/env python3
"""Non-publishing diagnostic for the approved Microsoft voice. No audio fallback."""
import asyncio
import importlib.metadata
from pathlib import Path
import edge_tts
async def check(text, suffix):
    dest=Path("work/genie4/diag_"+suffix+".mp3"); dest.parent.mkdir(parents=True,exist_ok=True)
    chunks=0; words=0
    try:
        c=edge_tts.Communicate(text, "ru-RU-DmitryNeural",rate="+0%")
        with dest.open("wb") as fp:
            async for event in c.stream():
                if event["type"]=="audio":
                    fp.write(event["data"]);chunks+=1
                elif event["type"]=="WordBoundary":words+=1
        size=dest.stat().st_size
        print(f"RESULT {suffix} bytes={size} audio_chunks={chunks} words={words}",flush=True)
        if size<1024:raise ValueError("Audio too small")
    except Exception as e:
        print(f"FAILED {suffix} {type(e).__name__}: {str(e)[:500]}",flush=True)
        dest.unlink(missing_ok=True)
async def main():
    print("EDGE_TTS_VERSION",importlib.metadata.version("edge-tts"))
    print("EDGE_TTS_FILE",edge_tts.__file__)
    import edge_tts.constants as co
    print("GEC_VERSION",getattr(co,"SEC_MS_GEC_VERSION",None))
    await check("Привет! Это голос Димы для канала Милашь.","short")
    await check("ИИ создаёт интерактивный мир. Это тест озвучки канала.", "medium")
asyncio.run(main())
