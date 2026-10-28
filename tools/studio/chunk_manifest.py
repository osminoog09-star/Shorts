#!/usr/bin/env python3
"""Fail-closed ordered chunk manifest, avoiding shell glob, missing chunks and -shortest truncation."""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path

NAME = re.compile(r"chunk_(\d{3})\.mp4\Z")


def probe_seconds(path, *, media="format"):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True, check=True, timeout=45)
    value = float(json.loads(result.stdout)["format"]["duration"])
    if not math.isfinite(value) or value <= 0:
        raise ValueError("invalid duration in " + str(path))
    return value


def validate_chunks(directory, audio, count, *, check_media=True):
    directory, audio = Path(directory), Path(audio)
    if not isinstance(count, int) or count < 1 or count > 32:
        raise ValueError("expected 1–32 chunks")
    if not directory.is_dir() or not audio.is_file():
        raise ValueError("chunk directory or final audio missing")
    files = sorted(x for x in directory.iterdir() if x.is_file())
    expected = [directory / ("chunk_%03d.mp4" % i) for i in range(count)]
    if files != expected:
        raise ValueError("chunk filenames missing, duplicated, unexpected, or wrong index; abort")
    if any(f.stat().st_size < 2048 for f in files):
        raise ValueError("empty/tiny chunk")
    if check_media:
        total = sum(probe_seconds(p) for p in files)
        actual_audio = probe_seconds(audio)
        if abs(total - actual_audio) > 1.5:
            raise ValueError(
                f"video chunks total {total:.3f}s != audio {actual_audio:.3f}s; "
                "prevent silent or truncated tail")
    return expected


def make_concat(files, destination):
    destination = Path(destination)
    lines = ["ffconcat version 1.0"]
    for path in files:
        # filenames from strict numeric manifest; resolve full local path
        safe = str(path.resolve()).replace("\\", "\\\\").replace("'", "'\\''")
        lines.append("file '" + safe + "'")
    destination.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--chunks", required=True)
    p.add_argument("--audio", required=True)
    p.add_argument("--expect", required=True, type=int)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    files = validate_chunks(args.chunks, args.audio, args.expect)
    make_concat(files, args.out)
    print(f"Chunk order and A/V duration verified: {len(files)} items")


if __name__ == "__main__":
    main()
