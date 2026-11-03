"""Existing S1-D25 news format: deterministic HTML/SVG, Edge Dima, rev4.
Modes from M1LASH_JOB_PATH: stills -> pilot -> full. No publishing.
PIL is used ONLY to assemble QA contact sheets, never to draw video scenes.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path
import numpy as np
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "shorts/ai_news_20261103"
WORK = ROOT / "motion-output/ai_news_20261103"
WORK.mkdir(parents=True, exist_ok=True)
SPEC = json.loads((ROOT / os.environ["M1LASH_JOB_PATH"]).read_text())
MODE = SPEC.get("mode", "stills")
JOB = json.loads((PROJECT / "news_20261103.json").read_text())
RATE = 48000


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def timeline(actual):
    voice = ROOT / "media/tts/news_20261103"
    if actual:
        run([sys.executable, str(ROOT / "scripts/tts_job.py"),
             str(PROJECT / "news_20261103.json")],
            cwd=ROOT, env=dict(os.environ, TTS_ENGINE="edge"))
    samples = [np.zeros(round(RATE * .15), dtype=np.float32)]
    segments, captions = [], []
    at = .15
    estimates = [4.4, 9.6, 7.2, 4.2, 9.8, 3.6]
    for i, line in enumerate(JOB["lines"]):
        if actual:
            audio = voice / (line["id"] + ".mp3")
            meta = json.loads((voice / (line["id"] + ".json")).read_text())
            if meta["voice_id"] != "ru-RU-DmitryNeural" or meta["engine"] != "edge-tts":
                raise RuntimeError("NO-GO: narration voice/engine changed")
            pcm = np.frombuffer(subprocess.check_output([
                "ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar",
                str(RATE), "-f", "f32le", "-"
            ]), dtype=np.float32)
            duration = len(pcm) / RATE
            words = meta["words"]
            if not words or any(len(w["w"].split()) > 2 for w in words):
                raise RuntimeError("NO-GO: sentence-only timestamps; obtain word ASR before captions")
        else:
            duration = estimates[i]
            tokens = line["text"].split()
            words = [{"w": w, "start": j * duration / len(tokens),
                      "end": (j + 1) * duration / len(tokens)} for j, w in enumerate(tokens)]
            pcm = np.zeros(round(RATE * duration), dtype=np.float32)
        segments.append({"id": line["id"], "start": at, "end": at + duration,
                         "text": line["text"], "voice": "ru-RU-DmitryNeural"})
        pairs = [words[j:j + 2] for j in range(0, len(words), 2)]
        groups, cursor = [], 0
        while cursor < len(pairs):
            group = list(pairs[cursor])
            cursor += 1
            end = pairs[cursor][0]["start"] if cursor < len(pairs) else duration
            while end - group[0]["start"] < .8 and cursor < len(pairs):
                group.extend(pairs[cursor])
                cursor += 1
                end = pairs[cursor][0]["start"] if cursor < len(pairs) else duration
            if end - group[0]["start"] < .8 and groups:
                groups[-1].extend(group)
            else:
                groups.append(group)
        for j, group in enumerate(groups):
            start = at + max(0, group[0]["start"])
            end = at + (groups[j + 1][0]["start"] if j + 1 < len(groups) else duration)
            if end <= start:
                raise RuntimeError("NO-GO: non-monotonic caption timing")
            captions.append({"start": start, "end": end,
                             "words": [w["w"] for w in group]})
        samples.append(pcm)
        gap = .12 if i < len(JOB["lines"]) - 1 else .2
        samples.append(np.zeros(round(RATE * gap), dtype=np.float32))
        at += duration + gap
    body_s = len(np.concatenate(samples)) / RATE
    first, second = segments[1]["end"], segments[3]["end"]
    cuts = [0, first / 2, first, (first + second) / 2,
            second, (second + body_s) / 2, body_s]
    result = {"total": body_s, "cuts": cuts, "caps": captions, "segments": segments,
              "actual_audio": actual}
    if actual:
        if MODE == "full" and not 30 <= body_s <= 45:
            raise RuntimeError(f"NO-GO: story {body_s:.3f}s; revise script, never stretch")
        signal = np.concatenate(samples)
        t = np.arange(len(signal)) / RATE
        # Original quiet procedural plucks; no third-party background song.
        beat = (t * 1.35) % 1
        music = (.006 * np.sin(2 * np.pi * 110 * t)
                 + .004 * np.sin(2 * np.pi * 164.81 * t))
        music += .009 * np.sin(2 * np.pi * 440 * t) * np.exp(-beat * 20)
        rng = np.random.default_rng(20261103)
        for cut in cuts[1:-1]:
            pos = round(cut * RATE)
            count = min(round(.07 * RATE), len(signal) - pos)
            tau = np.arange(count) / RATE
            music[pos:pos + count] += .012 * rng.normal(size=count) * np.exp(-tau * 60)
        mixed = np.clip(signal + music, -.95, .95)
        with wave.open(str(WORK / "narration_score.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(RATE)
            wav.writeframes((mixed * 32767).astype(np.int16).tobytes())
        dst = WORK / "voices"
        dst.mkdir(exist_ok=True)
        for src in voice.glob("*"):
            if src.suffix in (".mp3", ".json"):
                shutil.copy2(src, dst / src.name)
    (WORK / "timeline.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def contacts(images, name):
    from PIL import Image, ImageDraw
    board = Image.new("RGB", (960, 1176), "#202020")
    for i, image in enumerate(images):
        im = Image.open(image).resize((320, 569))
        x, y = (i % 3) * 320, (i // 3) * 588
        board.paste(im, (x, y + 19))
        ImageDraw.Draw(board).text((x + 7, y + 2), image.stem, fill="white")
    board.save(WORK / name, quality=78)


def capture(data, frame_window=None, caption_only=False):
    images = []
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=chrome, headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": 1080, "height": 1920},
                                device_scale_factor=1)
        page.goto((PROJECT / "film/index.html").as_uri())
        page.evaluate("() => document.fonts.ready")
        page.evaluate("data => window.setTimeline(data)", data)
        if min(c["end"] - c["start"] for c in data["caps"]) < .799:
            raise RuntimeError("NO-GO: a caption is shorter than the 0.8-second reading gate")
        layout = []
        for cap in data["caps"]:
            when = (cap["start"] + cap["end"]) / 2
            result = page.evaluate("""t => {
                const state = window.seek(t);
                const box = document.getElementById('caption').getBoundingClientRect();
                const source = document.getElementById('source').getBoundingClientRect();
                return {time:state.time,left:box.left,right:box.right,bottom:box.bottom,
                        sourceTop:source.top,clockRegistered:!!window.__timelines['m1lash-news-20261103']};
            }""", when)
            if (not result["clockRegistered"] or abs(result["time"] - when) > .0001
                    or result["left"] < 95 or result["right"] > 925
                    or result["bottom"] > result["sourceTop"] - 12):
                raise RuntimeError("NO-GO: actual browser caption/clock bounds " + str(result))
            layout.append(result)
        (WORK / "layout_gate.json").write_text(json.dumps({
            "actual_browser_checks": layout, "overlap_failures": 0,
            "registered_paused_clock": True
        }, indent=2))
        for i in range(6):
            a, b = data["cuts"][i:i + 2]
            when = .8 if i == 0 else (a + b) / 2
            page.evaluate("t => window.seek(t)", when)
            path = WORK / f"still_{i+1:02d}_{when:.3f}.jpg"
            page.screenshot(path=str(path), type="jpeg", quality=92)
            images.append(path)
        contacts(images, "stills_contact.jpg")
        if frame_window is not None:
            start, duration = frame_window
            frames = WORK / "frames"
            frames.mkdir(exist_ok=True)
            total = round(duration * 30)
            began = time.monotonic()
            for i in range(total):
                page.evaluate("t => window.seek(t)", start + i / 30)
                shot = {"x": 90, "y": 1090, "width": 850, "height": 254} if caption_only else None
                page.screenshot(path=str(frames / f"{i:05d}.jpg"), type="jpeg", quality=91, clip=shot)
                if i % 100 == 0:
                    print("FRAME", i, "/", total, "elapsed", round(time.monotonic() - began, 1), flush=True)
        browser.close()


def encode(duration, start, output):
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i",
         str(WORK / "frames/%05d.jpg"), "-ss", str(start), "-i",
         str(WORK / "narration_score.wav"), "-map", "0:v", "-map", "1:a",
         "-t", str(duration), "-vf", "scale=in_color_matrix=bt601:out_color_matrix=bt709:out_range=tv",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
         "-pix_fmt", "yuv420p", "-r", "30", "-colorspace", "bt709",
         "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2",
         str(output)])
    run(["ffmpeg", "-v", "error", "-xerror", "-i", str(output), "-f", "null", "-"])




def encode_caption_repair(duration, body):
    """Replace only the 850x254 caption area; retain the existing scene footage."""
    import hashlib
    source = ROOT / "videos/m1lash_ai_news_20261103_ru.mp4"
    if not source.is_file():
        raise RuntimeError("Caption repair needs the existing full master from the previous successful run")
    source_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    overlay = WORK / "caption_overlay.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i",
         str(WORK / "frames/%05d.jpg"), "-t", str(duration), "-vf",
         "scale=in_color_matrix=bt601:out_color_matrix=bt709:out_range=tv",
         "-c:v", "libx264", "-preset", "fast", "-crf", "17", "-threads", "2",
         "-pix_fmt", "yuv420p", "-r", "30", "-colorspace", "bt709",
         "-color_primaries", "bt709", "-color_trc", "bt709", str(overlay)])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-i", str(overlay),
         "-i", str(WORK / "narration_score.wav"), "-filter_complex_threads", "2",
         "-filter_complex", "[0:v][1:v]overlay=90:1090:shortest=1[v]",
         "-map", "[v]", "-map", "2:a", "-t", str(duration),
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
         "-pix_fmt", "yuv420p", "-r", "30", "-colorspace", "bt709",
         "-color_primaries", "bt709", "-color_trc", "bt709",
         "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-ac", "2", str(body)])
    (WORK / "caption_repair.json").write_text(json.dumps({
        "source_master_sha256": source_sha, "overlay_rectangle": [90, 1090, 850, 254],
        "body_seconds": duration, "minimum_caption_seconds":
            min(c["end"] - c["start"] for c in DATA_FOR_REPAIR["caps"]),
        "narration_source": "same cached Edge MP3s; deterministic original score rebuilt",
        "outro_method": "official assembler, never overlay the approved outro"
    }, indent=2))


def save_remote_evidence(data):
    """Commit small inspectable QA assets; works when the chat executor is offline."""
    from PIL import Image
    qa = ROOT / "reports/research/qa"
    qa.mkdir(parents=True, exist_ok=True)
    selected = []
    for source in sorted(WORK.glob("still_*.jpg")):
        name = f"news_20261103_{MODE}_{source.name}"
        target = qa / name
        im = Image.open(source)
        im.resize((720, 1280)).save(target, quality=66, optimize=True)
        selected.append(target)
    for source in [WORK / "stills_contact.jpg", WORK / "pilot_look.jpg",
                   WORK / "final_look.jpg", WORK / "caption_contact.jpg"]:
        if source.is_file():
            target = qa / f"news_20261103_{MODE}_{source.name}"
            shutil.copy2(source, target)
            selected.append(target)
    report = ROOT / f"reports/research/2026-11-03_NEWS_{MODE.upper()}_QA.json"
    report.write_text(json.dumps({
        "mode": MODE, "run_id": os.environ.get("GITHUB_RUN_ID"),
        "body_seconds": data["total"], "actual_audio": data["actual_audio"],
        "timeline": data, "visual_review": "PENDING_MANUAL_INSPECTION",
        "personal_listening": "NOT_VERIFIED", "publish_date": None
    }, ensure_ascii=False, indent=2) + "\n")
    selected.append(report)
    for name in ["check.json", "assembly.json", "pilot_asr.json", "final_asr.json", "layout_gate.json", "caption_repair.json", "artifact_recovery.json"]:
        source = WORK / name
        if source.is_file():
            target = ROOT / f"reports/research/2026-11-03_NEWS_{MODE.upper()}_{name}"
            shutil.copy2(source, target)
            selected.append(target)
    if MODE in ("pilot", "full"):
        selected.extend(sorted((ROOT / "media/tts/news_20261103").glob("*.mp3")))
        selected.extend(sorted((ROOT / "media/tts/news_20261103").glob("*.json")))
    if MODE == "pilot":
        target = ROOT / "videos/news_20261103_PILOT_INTERNAL.mp4"
        shutil.copy2(WORK / "NEWS_PILOT_COMPLETE_PHRASE.mp4", target)
        selected.append(target)
    if MODE == "full" and SPEC.get("save_review_mp4"):
        selected.append(ROOT / "videos/m1lash_ai_news_20261103_ru.mp4")
    run(["git", "config", "user.name", "m1lash-render-bot"], cwd=ROOT)
    run(["git", "config", "user.email", "m1lash-render-bot@users.noreply.github.com"], cwd=ROOT)
    run(["git", "add", "--"] + [str(p.relative_to(ROOT)) for p in selected], cwd=ROOT)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode:
        run(["git", "commit", "-m", f"qa(news): save actual {MODE} evidence for direct inspection"], cwd=ROOT)
        for attempt in range(3):
            run(["git", "pull", "--rebase", "origin", "main"], cwd=ROOT)
            pushed = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=ROOT)
            if pushed.returncode == 0:
                break
        else:
            raise RuntimeError("QA commit could not be pushed; do not claim remote evidence")


def speech_evidence(video, name):
    from faster_whisper import WhisperModel
    pcm = np.frombuffer(subprocess.check_output([
        "ffmpeg", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar",
        "16000", "-f", "f32le", "-"
    ]), dtype=np.float32)
    model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=2)
    segments, info = model.transcribe(pcm, language="ru", beam_size=3,
                                     word_timestamps=True, vad_filter=True,
                                     condition_on_previous_text=False)
    rows = [{"start": s.start, "end": s.end, "text": s.text,
             "words": [{"word": w.word, "start": w.start, "end": w.end}
                       for w in s.words]} for s in segments]
    (WORK / name).write_text(json.dumps({
        "language": info.language, "segments": rows,
        "personal_listening": "NOT_VERIFIED"
    }, ensure_ascii=False, indent=2) + "\n")



if MODE == "recover":
    import hashlib
    import io
    import zipfile
    import requests
    artifact_id = int(SPEC["artifact_id"])
    source_run = int(SPEC["source_run"])
    api = "https://api.github.com/repos/osminoog09-star/Shorts"
    headers = {"Authorization": "Bearer " + os.environ["GITHUB_TOKEN"],
               "Accept": "application/vnd.github+json"}
    info = requests.get(f"{api}/actions/artifacts/{artifact_id}", headers=headers, timeout=30)
    info.raise_for_status()
    record = info.json()
    if int(record["workflow_run"]["id"]) != source_run:
        raise RuntimeError("Unexpected artifact provenance")
    response = requests.get(f"{api}/actions/artifacts/{artifact_id}/zip",
                            headers=headers, timeout=180)
    response.raise_for_status()
    archive = zipfile.ZipFile(io.BytesIO(response.content))
    if archive.testzip() is not None:
        raise RuntimeError("Artifact ZIP CRC failed")
    for entry in archive.infolist():
        path = Path(entry.filename)
        if entry.is_dir():
            continue
        if not path.parts or path.parts[0] != "ai_news_20261103" or ".." in path.parts:
            raise RuntimeError("Unexpected artifact path")
        relative = Path(*path.parts[1:])
        target = WORK / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.read(entry))
    data = json.loads((WORK / "timeline.json").read_text())
    if min(c["end"] - c["start"] for c in data["caps"]) < .799:
        raise RuntimeError("Recovered captions do not satisfy the reading gate")
    candidate = WORK / "m1lash_ai_news_20261103_ru.mp4"
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    output = ROOT / "videos/m1lash_ai_news_20261103_ru.mp4"
    shutil.copy2(candidate, output)
    run(["ffmpeg", "-v", "error", "-xerror", "-i", str(output), "-f", "null", "-"])
    with (WORK / "check.json").open("w") as handle:
        run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/check.py"),
             str(output), "--platform", "shorts", "--json"], stdout=handle)
    (WORK / "artifact_recovery.json").write_text(json.dumps({
        "source_run": source_run, "artifact_id": artifact_id, "zip_crc_passed": True,
        "sha256": digest, "bytes": output.stat().st_size, "rerendered": False,
        "decode_repeated_after_transport": True
    }, indent=2))
    MODE = "full"
    data["artifact_recovery_run"] = os.environ.get("GITHUB_RUN_ID")
    save_remote_evidence(data)
    sys.exit(0)

if MODE == "stills":
    data = timeline(False)
    capture(data)
    (WORK / "status.json").write_text(json.dumps({
        "type": "six_stills_only", "actual_audio": False, "visual_review": "PENDING",
        "ready_video": False
    }, indent=2))
elif MODE in ("pilot", "full"):
    data = timeline(True)
    if MODE == "pilot":
        segment = next(s for s in data["segments"] if s["id"] == "n03")
        start = max(0, segment["start"] - .05)
        duration = math.ceil((segment["end"] + .1 - start) * 30) / 30
        if not 5 <= duration <= 12:
            raise RuntimeError("Pilot must retain one complete 5-12 second spoken phrase")
        capture(data, (start, duration))
        out = WORK / "NEWS_PILOT_COMPLETE_PHRASE.mp4"
        encode(duration, start, out)
        run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/look.py"),
             str(out), "--tiles", "3x2", "-o", str(WORK / "pilot_look.jpg")])
        speech_evidence(out, "pilot_asr.json")
    else:
        duration = math.ceil(data["total"] * 30) / 30
        DATA_FOR_REPAIR = data
        capture(data, (0, duration), caption_only=bool(SPEC.get("caption_only")))
        body = WORK / "body.mp4"
        if SPEC.get("caption_only"):
            encode_caption_repair(duration, body)
        else:
            encode(duration, 0, body)
        out = ROOT / "videos/m1lash_ai_news_20261103_ru.mp4"
        run([sys.executable, str(ROOT / "tools/assemble_with_outro.py"), str(body),
             "-o", str(out), "--audio-bitrate", "320k", "--preset", "fast"])
        shutil.copy2(out, WORK / out.name)
        shutil.copy2(str(out) + ".qa.json", WORK / "assembly.json")
        with (WORK / "check.json").open("w") as f:
            run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/check.py"),
                 str(out), "--platform", "shorts", "--json"], stdout=f)
        run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/look.py"),
             str(out), "--tiles", "3x2", "-o", str(WORK / "final_look.jpg")])
        speech_evidence(out, "final_asr.json")
    shutil.rmtree(WORK / "frames")
else:
    raise ValueError("Unknown approved production mode")

save_remote_evidence(data)
