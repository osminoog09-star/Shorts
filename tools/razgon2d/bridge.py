#!/usr/bin/env python3
"""Optional Razgon 2D engine adapter for M1lash. No uploading or auto-publishing."""
from __future__ import annotations
import argparse
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE / "kit"
PREFIX = "skills/make-2d-video/kit/"
VOICES = {"dima": "ru-RU-DmitryNeural", "sveta": "ru-RU-SvetlanaNeural"}
MAX_ENTRIES, MAX_UNCOMPRESSED = 128, 30_000_000


def install(archive: Path, dest: Path = KIT) -> None:
    """Safely install only the plugin's kit subtree, never execute the archive."""
    archive, dest = archive.resolve(), dest.resolve()
    if dest.exists():
        raise ValueError(f"Target exists: {dest}. Back it up/remove manually first.")
    with zipfile.ZipFile(archive) as z:
        info = z.infolist()
        if len(info) > MAX_ENTRIES or sum(i.file_size for i in info) > MAX_UNCOMPRESSED:
            raise ValueError("Archive exceeds extraction limits")
        found = {}
        for member in info:
            name = member.filename
            parts = Path(name).parts
            if name.startswith("/") or ".." in parts or "\\" in name:
                raise ValueError(f"Unsafe archive member: {name}")
            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError(f"Symlink not accepted: {name}")
            if not name.startswith(PREFIX) or member.is_dir():
                continue
            sub = name[len(PREFIX):]
            if not sub or sub in found:
                raise ValueError(f"Duplicate/empty kit path: {name}")
            found[sub] = member
        required = ("package.json", "render.mjs", "player.html", "tools/verify_kit.py",
                    "tools/new_project.py", "engine/player.js")
        if any(k not in found for k in required):
            raise ValueError("Incomplete Razgon kit")
        with tempfile.TemporaryDirectory(prefix="razgon_safe_") as tmp:
            stage = Path(tmp) / "kit"
            for name, member in found.items():
                output = stage / name
                output.parent.mkdir(parents=True, exist_ok=True)
                with z.open(member) as source, output.open("wb") as target:
                    shutil.copyfileobj(source, target)
            subprocess.run([sys.executable, str(stage / "tools/verify_kit.py")],
                           check=True, timeout=30)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(stage, dest)
    print(f"Installed verified kit: {dest}")


def voice_gate(manifest: Path) -> None:
    """Check required cast metadata; can't cryptographically prove the voice identity."""
    data = json.loads(manifest.read_text(encoding="utf-8"))
    segments = data.get("segments")
    if not isinstance(segments, list) or not segments:
        raise ValueError("Voice manifest needs nonempty segments")
    found_dima = False
    for n, seg in enumerate(segments, 1):
        role = seg.get("speaker")
        if (role not in VOICES or seg.get("voice_id") != VOICES[role]
                or seg.get("engine") not in ("edge-tts", "Microsoft Edge TTS")
                or not isinstance(seg.get("rate"), str)
                or not seg.get("source_file")):
            raise ValueError(f"Invalid voice segment #{n}: no silent fallback allowed")
        source = (manifest.parent / seg["source_file"]).resolve()
        if not source.is_file():
            raise ValueError(f"Voice segment file missing: {source}")
        found_dima |= role == "dima"
    if not found_dima:
        raise ValueError("Main M1lash narrator Dima is required")


def shots_gate(project: Path) -> None:
    """Reject missing shots and gaps/overlaps before expensive rendering."""
    cfg = json.loads((project / "config.json").read_text(encoding="utf-8"))
    story = json.loads((project / "story/shots.json").read_text(encoding="utf-8"))
    if cfg.get("fps", 0) <= 0 or cfg.get("aspect") not in ("16:9", "9:16"):
        raise ValueError("Invalid project format")
    shots = story.get("shots") or []
    if not shots:
        raise ValueError("No shot timeline")
    last = 0.0
    for n, shot in enumerate(shots, 1):
        start, end = float(shot["start"]), float(shot["end"])
        if abs(start - last) > .025 or end <= start:
            raise ValueError(f"Gap/overlap or invalid timing at shot #{n}")
        last = end
    if abs(last - float(story.get("duration", last))) > .025:
        raise ValueError("Timeline duration mismatch")
    if abs(last - float(cfg.get("duration", last))) > 1.5:
        raise ValueError("Narration and shot timeline durations disagree")


def preflight(project: Path) -> None:
    if not KIT.is_dir():
        raise ValueError("Razgon not installed: use 'install --zip ...' first")
    voice_gate(project / "input/voice_manifest.json")
    shots_gate(project)
    cfg = json.loads((project / "config.json").read_text(encoding="utf-8"))
    if not (project / cfg["voiceover"]).is_file():
        raise ValueError("Missing narration audio")


def qa(project: Path, video: Path, kind: str) -> None:
    preflight(project)
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                        "format=duration:stream=codec_type", "-of", "json", str(video)],
                       capture_output=True, text=True, check=True)
    info = json.loads(r.stdout)
    duration = float(info["format"]["duration"])
    streams = {s["codec_type"] for s in info.get("streams", [])}
    if "video" not in streams or "audio" not in streams:
        raise ValueError("Final MP4 must have both video and audio")
    if kind == "long" and duration < 1260:
        raise ValueError(f"M1lash longform gate failed: {duration:.2f}s < 1260s")
    print(f"TECHNICAL QA PASS: {duration:.2f}s, audio+video ({kind}); human art/rights QC still required")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="action", required=True)
    i = sub.add_parser("install"); i.add_argument("--zip", type=Path, required=True)
    d = sub.add_parser("doctor")
    r = sub.add_parser("render"); r.add_argument("--project", type=Path, required=True)
    r.add_argument("--sheet", action="store_true"); r.add_argument("--from-sec", type=float)
    r.add_argument("--to-sec", type=float)
    q = sub.add_parser("qa"); q.add_argument("--project", type=Path, required=True)
    q.add_argument("--video", type=Path, required=True)
    q.add_argument("--kind", choices=["short", "long", "pilot"], required=True)
    a = p.parse_args()
    try:
        if a.action == "install": install(a.zip)
        elif a.action == "doctor":
            if not KIT.is_dir():
                raise ValueError("Install from zip first")
            subprocess.run([sys.executable, str(KIT / "tools/doctor.py")],
                           check=True, timeout=90)
        elif a.action == "render":
            project = a.project.resolve()
            preflight(project)
            cmd = ["node", str(KIT / "render.mjs"), "--project", str(project)]
            if a.sheet: cmd += ["--sheet"]
            if a.from_sec is not None: cmd += ["--from", str(a.from_sec)]
            if a.to_sec is not None: cmd += ["--to", str(a.to_sec)]
            subprocess.run(cmd, cwd=KIT, check=True)
        else: qa(a.project.resolve(), a.video.resolve(), a.kind)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        p.exit(2, f"NO-GO: {exc}\n")


if __name__ == "__main__":
    main()
