#!/usr/bin/env python3
"""M1lash: detect three-second quiet windows lacking film dialogue.

Heuristic: this cannot determine whether a shot is creatively justified.
Use before attaching the approved outro; the outro itself is not analyzed.
"""
import json
import math
import re
import subprocess


def integrated_lufs(path, start, duration):
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-ss", f"{start:.3f}",
           "-t", f"{duration:.3f}", "-i", str(path), "-vn",
           "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
           "-f", "null", "-"]
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(f"FFmpeg failed measuring {path}: {p.stderr[-400:]}")
    m = re.search(r'\{[^{}]*"input_i"[^{}]*\}', p.stderr, re.S)
    if not m:
        raise RuntimeError("FFmpeg did not report loudness")
    value = json.loads(m.group(0))["input_i"]
    try:
        return float(value)
    except (ValueError, TypeError):
        return -math.inf


def dead_windows(path, words, total_seconds, *, window=3.0, hop=1.5,
                 low_lufs=-30.0, minimum_seconds=3.0):
    """Return quiet periods (start,end,min_lufs) with no speech timestamps.

    An editor may explicitly waive an intentionally dramatic quiet passage
    after inspecting the picture and documenting its timecode.
    """
    if total_seconds < window:
        return []
    stamps = []
    t = 0.0
    while t <= total_seconds - window + 1e-5:
        end = t + window
        has_words = any(st < end and en > t for st, en, *_ in words)
        if not has_words:
            level = integrated_lufs(path, t, window)
            if level < low_lufs:
                stamps.append((t, end, level))
        t = round(t + hop, 3)
    intervals = []
    for st, en, level in stamps:
        if intervals and st <= intervals[-1][1] + 1e-6:
            prev = intervals[-1]
            intervals[-1] = (prev[0], max(prev[1], en), min(prev[2], level))
        else:
            intervals.append((st, en, level))
    return [(round(s, 2), round(e, 2), round(level, 1)) for s, e, level in intervals
            if e-s >= minimum_seconds]
