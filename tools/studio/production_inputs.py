#!/usr/bin/env python3
"""Validate privileged workflow_dispatch render parameters before shell/checkout/path use."""
import argparse
import json
import math
import os
import re
from pathlib import Path

SLUG = re.compile(r"[a-z0-9][a-z0-9_-]{0,63}\Z")
AUDIO = re.compile(r"audio/[a-zA-Z0-9_/-]{1,120}\.(?:wav|mp3|m4a|aac)\Z")


def validate_input(data, root=Path("."), require_timeline=False):
    project = data.get("project", "")
    short = data.get("short", "")
    audio = data.get("audio", "")
    if not SLUG.fullmatch(project):
        raise ValueError("invalid project name (only slug)")
    if short and not SLUG.fullmatch(short):
        raise ValueError("invalid Short id")
    if not AUDIO.fullmatch(audio) or ".." in Path(audio).parts:
        raise ValueError("invalid audio path")
    folder = root / "longform" / project
    if not folder.is_dir():
        raise ValueError("unknown longform project")
    if not (folder / audio).is_file():
        raise ValueError("missing project audio")
    if not short and require_timeline:
        cue = folder / "audio" / "cues.json"
        if not cue.is_file():
            raise ValueError("no verified cues.json; cannot start longform render")
        try:
            duration = float(json.loads(cue.read_text(encoding="utf-8"))["duration"])
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            raise ValueError("bad duration in cues.json") from None
        if not math.isfinite(duration) or duration < 1260 or duration > 14400:
            raise ValueError("longform cues must describe 21min to 4h of content")
    chunks_raw = str(data.get("chunks", "20"))
    fps_raw = str(data.get("fps", "30"))
    if not chunks_raw.isdigit() or not 1 <= int(chunks_raw) <= 32:
        raise ValueError("chunks must be between 1 and 32")
    if fps_raw not in ("24", "25", "30", "60"):
        raise ValueError("FPS must be 24/25/30/60")
    n = int(chunks_raw)
    base_run = str(data.get("base_run", "")).strip()
    if base_run and (not base_run.isdigit() or len(base_run) > 20):
        raise ValueError("base_run must be a numeric run ID")
    only = str(data.get("only", "")).strip()
    if only:
        ids = only.split(",")
        if not base_run:
            raise ValueError("partial rerender requires a base_run")
        if any(not x.isdigit() or int(x) >= n for x in ids):
            raise ValueError("invalid chunk index")
        idx = [int(x) for x in ids]
        if len(set(idx)) != len(idx):
            raise ValueError("duplicate chunk index")
    else:
        idx = list(range(n))
    return {"project": project, "short": short, "audio": audio,
            "chunks": n, "fps": int(fps_raw), "base_run": base_run,
            "idx": idx}


def cli():
    p = argparse.ArgumentParser()
    p.add_argument("--require-timeline", action="store_true")
    p.add_argument("--output")
    args = p.parse_args()
    data = {key: os.environ.get("M1LASH_" + key.upper(), default)
            for key, default in {
                "project": "", "short": "", "audio": "", "chunks": "20",
                "fps": "30", "base_run": "", "only": ""}.items()}
    try:
        result = validate_input(data, require_timeline=args.require_timeline)
    except ValueError as exc:
        raise SystemExit(f"NO-GO: {exc}")
    if args.output:
        with Path(args.output).open("a", encoding="utf-8") as f:
            for key in ("project", "short", "audio", "chunks", "fps", "base_run"):
                f.write(f"{key}={result[key]}\n")
            f.write("idx=" + json.dumps(result["idx"], separators=(",", ":")) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    cli()
