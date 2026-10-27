#!/usr/bin/env python3
"""Generate all AI news narration via ru-RU-DmitryNeural and NO fallback.

Read exact news lines from the approved motion storyboard; retain text
and durations for deterministic resync against the existing final cut.
"""
import ast, asyncio, json, os, random, time
from pathlib import Path
import edge_tts
from mutagen.mp3 import MP3

VOICE = "ru-RU-DmitryNeural"
SRC=Path("tools/ai_scandals_s7d25.py")
tree=ast.parse(SRC.read_text(encoding="utf-8"))
assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=="NEWS" for x in n.targets))
news=ast.literal_eval(assignment.value)
out=Path("dmitry-news-voice")
out.mkdir(parents=True,exist_ok=True)
manifest=[]
sem=asyncio.Semaphore(2)

async def synth(i,row):
    text=row[3]
    dst=out/f"segment_{i:02d}.mp3"
    last=None
    async with sem:
        for attempt in range(22):
            try:
                dst.unlink(missing_ok=True)
                await edge_tts.Communicate(text,voice=VOICE,rate="+0%",pitch="+0Hz").save(str(dst))
                if not dst.exists() or dst.stat().st_size < 6000:raise RuntimeError("Too small")
                info=MP3(str(dst)).info
                if not 2 <= info.length <= 60:raise RuntimeError(f"Bad TTS duration {info.length}")
                print("OK",i,round(info.length,2),"seconds",dst.stat().st_size,"bytes",flush=True)
                manifest.append({"index":i,"text":text,"file":dst.name,"voice":VOICE,"duration":round(info.length,3),"byte_length":dst.stat().st_size})
                return
            except Exception as exc:
                last=exc
                print("retry",i,attempt,repr(exc),flush=True)
                dst.unlink(missing_ok=True)
                await asyncio.sleep(min(14,3+attempt//2)+random.random()*1.2)
        raise RuntimeError(f"Dmitry segment {i} unavailable after retries: {last}")

async def main():
    assert len(news)==7
    await asyncio.gather(*(synth(i,row) for i,row in enumerate(news)))
    manifest.sort(key=lambda e:e["index"])
    assert len(manifest)==7 and all(x["voice"]==VOICE for x in manifest)
    (out/"manifest.json").write_text(json.dumps({"voice":VOICE,"segments":manifest},ensure_ascii=False,indent=2),encoding="utf-8")
    print("ALL SEVEN SEGMENTS COMPLETE — DMITRY ONLY",flush=True)
asyncio.run(main())
