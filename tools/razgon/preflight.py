#!/usr/bin/env python3
"""M1lash Razgon archive preflight and voice-provenance gate. Does not execute the plugin."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
from zipfile import ZipFile

PINNED = {
    "3376259460a0d6efb11dd808d5cb9e4b0fcdfdd5503e6e5ef6eb4991f48e2812": "original",
    "6e0f93ec10e24299ee4841acf661b985715e468b0bd0abf395cd1b15160cf3ec": "m1lash-patched",
}
PREFIX = "skills/make-2d-video/kit/"
REQUIRED = ["package.json", "render.mjs", "engine/core.js", "engine/player.js",
            "engine/motion.js", "audio/mix.py", "tools/new_project.py"]


def inspect(archive):
    digest = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest not in PINNED:
        raise ValueError("Archive checksum not approved: " + digest)
    with ZipFile(archive) as z:
        names = set()
        total = 0
        for m in z.infolist():
            name = m.filename
            pp = PurePosixPath(name)
            if pp.is_absolute() or ".." in pp.parts or "\\" in name or "\x00" in name:
                raise ValueError("Unsafe archive path: " + repr(name))
            if name in names:
                raise ValueError("Duplicate archive entry: " + name)
            names.add(name)
            if stat.S_ISLNK(m.external_attr >> 16):
                raise ValueError("Symlink not allowed: " + name)
            total += m.file_size
            if m.file_size > 20_000_000 or total > 80_000_000:
                raise ValueError("Excessive uncompressed archive size")
        missing = [PREFIX + name for name in REQUIRED if PREFIX + name not in names]
        if missing:
            raise ValueError("Missing kit files: " + ", ".join(missing))
        manifest = json.loads(z.read(".claude-plugin/plugin.json"))
        if manifest.get("name") != "razgon-2d-studio" or manifest.get("version") != "0.3.0":
            raise ValueError("Unexpected plugin manifest")
        return {"sha256": digest, "variant": PINNED[digest],
                "entries": len(names), "uncompressed_bytes": total}


def install(archive, parent):
    dest = Path(parent).resolve() / "razgon-2d-studio"
    if dest.exists():
        raise ValueError(f"Refusing to overwrite existing project: {dest}")
    inspect(archive)
    dest.mkdir(parents=True)
    with ZipFile(archive) as z:
        for item in z.infolist():
            if item.is_dir() or not item.filename.startswith(PREFIX):
                continue
            subpath = item.filename[len(PREFIX):]
            path = dest / subpath
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(z.read(item))
    return dest


def check_voice(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    segs = data.get("segments", [])
    if not isinstance(segs, list) or not segs:
        raise ValueError("NO-GO: voice segments missing")
    ids = {"dima": "ru-RU-DmitryNeural", "sveta": "ru-RU-SvetlanaNeural"}
    for idx, s in enumerate(segs):
        who = s.get("speaker")
        if who not in ids or s.get("voice_id") != ids[who]:
            raise ValueError(f"NO-GO: voice segment {idx} is not approved")
        if not all(s.get(key) for key in ("engine", "source_file", "rate")):
            raise ValueError(f"NO-GO: missing voice provenance in segment {idx}")
        if s.get("role") in ("narration", "cta") and who != "dima":
            raise ValueError(f"NO-GO: principal/CTA voice must be Dima at segment {idx}")
    if not any(s.get("speaker") == "dima" and s.get("role") == "narration" for s in segs):
        raise ValueError("NO-GO: principal narration by Dima is missing")
    if not any(s.get("speaker") == "dima" and s.get("role") == "cta" for s in segs):
        raise ValueError("NO-GO: CTA by Dima is missing")
    return {"segments": len(segs), "voice_gate": "PASS"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", type=Path)
    p.add_argument("--install-parent", type=Path)
    p.add_argument("--voice-manifest", type=Path)
    args = p.parse_args()
    if args.install_parent and not args.archive:
        p.error("--install-parent requires --archive")
    if not (args.archive or args.voice_manifest):
        p.error("provide --archive or --voice-manifest")
    if args.archive:
        print(json.dumps(inspect(args.archive), indent=2))
    if args.install_parent:
        print("Installed into", install(args.archive, args.install_parent))
    if args.voice_manifest:
        print(json.dumps(check_voice(args.voice_manifest), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError) as e:
        raise SystemExit(str(e))
