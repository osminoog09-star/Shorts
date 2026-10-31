"""Voice and timings for genuine 21+ minute Heron V3. No cached Liam fallback."""
import asyncio
import json
import math
import subprocess
import wave
from pathlib import Path
import edge_tts

R = Path(__file__).resolve().parent
V = R / "v3"
S = json.loads((V / "script_v3.json").read_text(encoding="utf-8"))
assert len(S) == 44, "NO-GO: missing story sections"
VOICE = "ru-RU-DmitryNeural"
A = R / "audio_v3"
A.mkdir(exist_ok=True)
TIME_STRETCH = 1.20  # same as verified Heron V2 narration
FPS = 30

async def synth(i, sentence):
    mp3 = A / f"{i:02}.mp3"
    meta = A / f"{i:02}.json"
    if mp3.exists() and meta.exists() and mp3.stat().st_size > 1024:
        old = json.loads(meta.read_text(encoding="utf-8"))
        if old.get("text") == sentence and old.get("voice_id") == VOICE:
            return old
    words = []
    mp3.unlink(missing_ok=True)
    meta.unlink(missing_ok=True)
    # Generation errors are fatal. Do not substitute another narrator.
    try:
        speaker = edge_tts.Communicate(sentence, VOICE, rate="+0%", pitch="+0Hz", boundary="WordBoundary")
    except TypeError:
        speaker = edge_tts.Communicate(sentence, VOICE, rate="+0%", pitch="+0Hz")
    with mp3.open("wb") as output:
        async for msg in speaker.stream():
            if msg["type"] == "audio":
                output.write(msg["data"])
            elif msg["type"] == "WordBoundary":
                words.append({"w": msg["text"], "start": msg["offset"]/1e7,
                              "end": (msg["offset"]+msg["duration"])/1e7})
    assert mp3.stat().st_size > 1024, f"NO-GO: missing Dmitry audio for scene {i}"
    data = {"speaker":"dima", "voice_id":VOICE, "engine":"edge-tts",
            "rate":"+0%", "pitch":"+0Hz", "text":sentence, "words":words,
            "source_file":mp3.name}
    meta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

async def main():
    result = []
    current = 0.0
    for i, scene in enumerate(S):
        data = None
        for trial in range(4):
            try:
                data = await synth(i, scene["text"])
                break
            except Exception:
                if trial == 3: raise
                await asyncio.sleep(6 * (trial+1))
        assert data and data["voice_id"] == VOICE and data["speaker"] == "dima"
        wav = A / f"{i:02}.wav"
        subprocess.run(["ffmpeg","-y","-v","error","-i",str(A/f"{i:02}.mp3"),
                        "-af",f"aresample=44100,atempo={TIME_STRETCH},loudnorm=I=-17:TP=-3:LRA=9",
                        "-ar","44100","-ac","1",str(wav)],check=True)
        with wave.open(str(wav)) as w:
            speech = w.getnframes()/w.getframerate()
        if speech < 4: raise RuntimeError(f"NO-GO: suspiciously short voice in scene {i}")
        d = math.ceil((speech+1.4)*FPS)/FPS
        cues = []
        words = data.get("words",[])
        for j in range(0,len(words),11):
            group = words[j:j+11]
            cues.append({"start":group[0]["start"]/TIME_STRETCH,
                         "end":group[-1]["end"]/TIME_STRETCH,
                         "text":" ".join(w["w"] for w in group)})
        result.append({**scene, "index":i,"start":current,"speech":speech,
                       "dur":d,"file":f"audio_v3/{i:02}.wav","cues":cues,
                       "voice_id":VOICE,"speaker":"dima"})
        current += d
        print(f"Scene {i+1}/{len(S)}: {scene['title']}, {speech:.1f}s", flush=True)
    if not 1260 <= current <= 1800:
        raise SystemExit(f"NO-GO: actual spoken duration {current:.1f}s outside 21:00–30:00. Rewrite editorially; do not pad or speed artificially.")
    (R/"timeline.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    count = 64
    tasks = [{"clip":"main","part":i,"parts":count,"frames":round(current*FPS)} for i in range(count)]
    (V/"matrix.json").write_text(json.dumps({"include":tasks}))
    (V/"duration_report.json").write_text(json.dumps({
        "scene_count":len(S),"words":sum(len(s["text"].split()) for s in S),
        "measured_narration_seconds":current, "voice":VOICE, "artificial_padding":False,
        "status":"AUDIO_DONE_VIDEO_NOT_YET_RENDERED"},ensure_ascii=False,indent=2))
    print(f"V3 real spoken runtime = {current:.2f}s ({current/60:.2f}m) / {count} render shards")

if __name__=="__main__":
    asyncio.run(main())
