#!/usr/bin/env python3
"""Read-only, offline ASR verification of existing M1lash review Shorts.

The ASR transcript is evidence, not proof of human listening or approval.
Never uploads videos, modifies audio, or schedules YouTube.
"""
import argparse
import difflib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS = ROOT / "shorts" / "next_four_20261103" / "spec.json"
OUTPUT_DIR = ROOT / "reports" / "research" / "qa" / "next_four_20261103"


def normalized(text):
    text = (text or "").lower().replace("ё", "е")
    text = re.sub(r"[^\w\s]+", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def word_similarity(expected, recognized):
    return round(difflib.SequenceMatcher(
        None, normalized(expected).split(), normalized(recognized).split()
    ).ratio(), 3)


def extract_story(video, target, keep_seconds):
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-i", str(video), "-vn", "-t", f"{keep_seconds:.3f}",
        "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(target)
    ], check=True)


def ffprobe(video):
    p = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height",
        "-of", "json", str(video)
    ], capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def analyze(model, spec, video, outro_seconds):
    meta = ffprobe(video)
    duration = float(meta["format"]["duration"])
    streams = meta["streams"]
    video_streams = [s for s in streams if s["codec_type"] == "video"]
    audio_streams = [s for s in streams if s["codec_type"] == "audio"]
    if not video_streams or not audio_streams:
        raise RuntimeError(f"{video}: missing video/audio")
    if video_streams[0].get("width") != 1080 or video_streams[0].get("height") != 1920:
        raise RuntimeError(f"{video}: not 1080x1920")
    if not 30 <= duration <= 59:
        raise RuntimeError(f"{video}: unexpected duration {duration}")
    story_seconds = duration - outro_seconds
    expected_lines = [line["text"] for line in spec["lines"]]
    expected = " ".join(expected_lines)
    with tempfile.TemporaryDirectory(prefix="m1lash-asr-") as scratch:
        wav = Path(scratch) / "story.wav"
        extract_story(video, wav, story_seconds)
        parts, info = model.transcribe(str(wav), language="ru", beam_size=5,
                                       vad_filter=False, condition_on_previous_text=False)
        segments = [{"start": round(p.start, 2), "end": round(p.end, 2),
                     "text": p.text.strip()} for p in parts]
    recognized = " ".join(p["text"] for p in segments)
    similarity = word_similarity(expected, recognized)
    last_similarity = word_similarity(expected_lines[-1], " ".join(
        p["text"] for p in segments if p["start"] >= max(0, story_seconds - 12)
    ))
    # Preserve negation: a missing 'не' can reverse the meaning.
    exp_no = normalized(expected).split().count("не")
    got_no = normalized(recognized).split().count("не")
    flags = []
    if similarity < 0.72:
        flags.append("ASR_TRANSCRIPT_DIFFERENCE")
    if last_similarity < 0.52:
        flags.append("PAYOFF_END_ASR_UNCERTAIN")
    if got_no < exp_no:
        flags.append("NEGATION_MAY_BE_MISSING")
    if not segments:
        flags.append("NO_SPEECH_RECOGNIZED")
    return {
        "id": spec["id"], "source_file": str(video.relative_to(ROOT)),
        "duration_seconds": round(duration, 3),
        "story_seconds": round(story_seconds, 3),
        "expected_voice_id": spec["voice"],
        "voice_identity_listening_verified": False,
        "engine_verified_from_audio": False,
        "expected_text": expected,
        "recognized_text": recognized,
        "segments": segments,
        "text_similarity": similarity,
        "payoff_similarity": last_similarity,
        "expected_negations": exp_no, "recognized_negations": got_no,
        "flags": flags,
        "automatic_asr_result": "NO_OBVIOUS_ISSUE" if not flags else "REVIEW_REQUIRED",
        "personal_listening": "NOT_VERIFIED",
        "owner_audio_approved": False,
        "next_action": "Give final MP4 to owner for uninterrupted listening; never auto-upload/schedule."
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True)
    args = parser.parse_args()
    job = Path(args.job)
    if job.parent.as_posix() != "jobs/audioqa" or job.suffix != ".json":
        raise ValueError("Job path must be in jobs/audioqa/*.json")
    config = json.loads((ROOT / job).read_text(encoding="utf-8"))
    specs = {x["id"]: x for x in json.loads(SPECS.read_text(encoding="utf-8"))["items"]}
    entries = config["videos"]
    if not entries or len(entries) > 4:
        raise ValueError("One to four videos required")
    from faster_whisper import WhisperModel
    model = WhisperModel(config.get("model", "small"), device="cpu", compute_type="int8")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for entry in entries:
        id_ = entry["id"]
        if id_ not in specs:
            raise ValueError(f"Unknown approved short ID {id_}")
        path = Path(entry["file"])
        if path.parent.as_posix() != "videos" or path.suffix != ".mp4":
            raise ValueError(f"Unapproved media path {path}")
        if not (ROOT / path).is_file():
            raise FileNotFoundError(ROOT / path)
        result = analyze(model, specs[id_], ROOT / path, float(config.get("outro_seconds", 6.6)))
        (OUTPUT_DIR / (id_ + "_final_asr.json")).write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        results.append({k: result[k] for k in (
            "id", "source_file", "automatic_asr_result", "text_similarity",
            "payoff_similarity", "flags", "personal_listening"
        )})
        print(id_, result["automatic_asr_result"], "similarity", result["text_similarity"],
              "flags", result["flags"], flush=True)
    summary = {"model": config.get("model", "small"), "source": args.job,
               "results": results, "human_listening_required": True,
               "youtube_upload_performed": False, "schedule_changed": False}
    (OUTPUT_DIR / "final_asr_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
