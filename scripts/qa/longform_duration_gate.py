#!/usr/bin/env python3
"""M1lash full-film release gate: validate *measured streams*, not just MP4 metadata.

Duration/stream health is not a quality, originality, voice-identity or rights certificate.
Shorts and internal pilots must not call this full-film gate.
"""
import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

MIN_SECONDS = 1260.0
MAX_SECONDS = 4 * 3600.0
MAX_DRIFT = 0.75


def _seconds(obj, label, issues):
    try:
        value = float(obj)
    except (ValueError, TypeError):
        issues.append(label + " duration absent/invalid")
        return None
    if not math.isfinite(value) or value <= 0:
        issues.append(label + " duration non-finite/non-positive")
        return None
    return value


def validate(probe):
    issues = []
    fmt = probe.get("format") or {}
    seconds = _seconds(fmt.get("duration"), "container", issues)
    streams = probe.get("streams") or []
    video = next((x for x in streams if x.get("codec_type") == "video"), None)
    audio = next((x for x in streams if x.get("codec_type") == "audio"), None)
    if not video:
        issues.append("video stream absent")
    if not audio:
        issues.append("audio stream absent")
    if seconds is not None:
        if seconds < MIN_SECONDS:
            issues.append(f"container shorter than 21:00 ({seconds:.3f}s)")
        if seconds > MAX_SECONDS:
            issues.append("container duration outside supported 4h safety bound")
    for name, stream in (("video", video), ("audio", audio)):
        if stream is None:
            continue
        stream_seconds = _seconds(stream.get("duration"), name, issues)
        if stream_seconds is not None:
            if stream_seconds < MIN_SECONDS:
                issues.append(f"{name} shorter than 21:00 ({stream_seconds:.3f}s)")
            if seconds is not None and abs(stream_seconds - seconds) > MAX_DRIFT:
                issues.append(f"{name} and container disagree by {abs(stream_seconds-seconds):.3f}s")
    if video is not None:
        width, height = video.get("width"), video.get("height")
        if not isinstance(width, int) or not isinstance(height, int) or width < 1920 or height < 1080 or width <= height:
            issues.append("full film must be landscape >=1920x1080")
        if video.get("codec_name") not in (None, "h264"):
            issues.append("full film video codec must be H.264")
    if audio is not None and audio.get("codec_name") not in (None, "aac"):
        issues.append("full film audio codec must be AAC")
    return {
        "pass": not issues,
        "seconds": round(seconds, 3) if seconds is not None else None,
        "minimum_seconds": MIN_SECONDS,
        "issues": issues,
        "limitations": "Technical container/stream gate, NOT a content, visual, audio listening, originality or rights audit."
    }


def inspect_file(movie):
    movie = Path(movie)
    if not movie.is_file() or movie.suffix.lower() != ".mp4" or movie.stat().st_size < 2048:
        raise ValueError("final MP4 missing, too small or wrong extension")
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=codec_type,codec_name,duration,width,height",
         "-of", "json", str(movie)],
        capture_output=True, text=True, timeout=60, check=True)
    data = validate(json.loads(result.stdout))
    with movie.open("rb") as f:
        data["sha256"] = hashlib.file_digest(f, "sha256").hexdigest()
    data["file_bytes"] = movie.stat().st_size
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("movie")
    p.add_argument("--report", help="save technical JSON report")
    args = p.parse_args()
    try:
        result = inspect_file(args.movie)
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        result = {"pass": False, "issues": [f"probe failed: {type(e).__name__}"]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.report:
        path = Path(args.report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if not result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
