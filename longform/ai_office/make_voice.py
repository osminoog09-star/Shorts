#!/usr/bin/env python3
"""M1lash AI Office: Dmitry-only speech with per-sentence timing, no substitutions."""
import asyncio, json, os, random, sys, time
from pathlib import Path
from mutagen.mp3 import MP3
import edge_tts

ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/"episode.json").read_text(encoding="utf-8"))
scenes=data["scenes"]
VOICE="ru-RU-DmitryNeural"
OUTPUT=ROOT/"voice"
OUTPUT.mkdir(parents=True,exist_ok=True)
MAX_RETRIES=22
sem=asyncio.Semaphore(3)

async def synth(i,scene):
    async with sem:
        dest=OUTPUT/f"voice_{i:02d}.mp3"
        meta=OUTPUT/f"words_{i:02d}.json"
        if dest.exists() and meta.exists():
            try:
                info=json.loads(meta.read_text())
                if info.get("text")==scene["text"] and info.get("voice")==VOICE and dest.stat().st_size>10000:
                    return info
            except Exception: pass
        errors=[]
        for attempt in range(MAX_RETRIES):
            words=[]
            try:
                tmp=dest.with_suffix(".tmp.mp3")
                with tmp.open("wb") as f:
                    async for chunk in edge_tts.Communicate(scene["text"],voice=VOICE,rate="+16%",pitch="+0Hz",boundary="WordBoundary").stream():
                        if chunk["type"]=="audio": f.write(chunk["data"])
                        elif chunk["type"]=="WordBoundary":
                            words.append({"text":chunk["text"],"start":round(chunk["offset"]/1e7,3),"duration":round(chunk["duration"]/1e7,3)})
                length=MP3(str(tmp)).info.length
                if tmp.stat().st_size<12000 or length<8 or length>200:raise RuntimeError(f"invalid size/duration {tmp.stat().st_size}/{length}")
                tmp.replace(dest)
                result={"scene_id":scene["id"],"index":i,"title":scene["title"],"text":scene["text"],"duration":round(length,3),"words":words,"voice":VOICE,"file":dest.name}
                meta.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
                print(f"TTS_OK index={i} duration={length:.2f} words={len(words)} bytes={dest.stat().st_size}",flush=True)
                return result
            except Exception as exc:
                errors.append(str(exc))
                tmp=dest.with_suffix(".tmp.mp3");tmp.unlink(missing_ok=True)
                if attempt in (0,3,8,15,21):
                    print(f"TTS_RETRY index={i} attempt={attempt} err={str(exc)[:120]}",flush=True)
                await asyncio.sleep(min(12,2+attempt*.6)+random.random())
        raise RuntimeError(f"Voice {VOICE} failed scene {i} after retries: {errors[-3:]}")

async def main():
    print("DMITRY_EXCLUSIVE",VOICE,"scenes",len(scenes),flush=True)
    voices=await asyncio.gather(*(synth(i,s) for i,s in enumerate(scenes)))
    voices.sort(key=lambda v:v["index"])
    assert len(voices)==len(scenes)
    assert all(v["voice"]==VOICE for v in voices)
    m={"voice":VOICE,"scenes":voices,"total_speech_seconds":sum(v["duration"] for v in voices)}
    (OUTPUT/"manifest.json").write_text(json.dumps(m,ensure_ascii=False,indent=2))
    print(f"VOICE_READY {len(voices)} segments; total_speech_seconds={m['total_speech_seconds']:.2f}",flush=True)

if __name__=="__main__":asyncio.run(main())