#!/usr/bin/env python3
"""Edit only body footage for three already approved movie Shorts.

Output MP4 bodies intentionally EXCLUDE the approved M1lash outro and Dima's
spoken film title. Assemble finals ONLY with tools/assemble_with_outro.py.
003: replace 2.0 s repeat portrait with an existing live-band/reaction cutaway with NO burned-in caption;
     retain unbroken original film sound.
005: the original 9 s empty pause was ALREADY removed in V26, so do not
     cut it a second time; remove a remaining 0.733 s silent reaction.
006: the original 35-43 s sea passage was ALREADY removed in V24; tighten
     an additional 1.900 s empty sea passage before the return to action.
Movie files NEVER enter GitHub. This script uses owner-provided local inputs.
"""
import argparse
import json
import subprocess
from pathlib import Path

# The exact 30fps timecodes used for the approved-source private QA exports.
EDITS = {
    "003": {"source": "body_v24.mp4", "video_parts": [(0, 28.466666667),
            (21.0, 23.0), (30.466666667, 39.0)], "audio_keep": True},
    "005": {"source": "body_v26.mp4", "video_parts": [(0, 9.233333333),
            (9.966666667, 23.3)], "audio_keep": False},
    "006": {"source": "body_v24.mp4", "video_parts": [(0, 31.966666667),
            (33.866666667, 35.333333333)], "audio_keep": False},
}

def render(short_id, root, output):
    config = EDITS[short_id]
    src = root / short_id / config["source"]
    if not src.is_file():
        raise FileNotFoundError(src)
    output.parent.mkdir(parents=True, exist_ok=True)
    fragments = []
    for idx, (start, end) in enumerate(config["video_parts"]):
        fragments.append(f"[0:v]trim=start={start:.9f}:end={end:.9f},"
                         f"setpts=PTS-STARTPTS,fps=30,setsar=1[v{idx}]")
        if not config["audio_keep"]:
            fragments.append(f"[0:a]atrim=start={start:.9f}:end={end:.9f},"
                             f"asetpts=PTS-STARTPTS,aresample=48000[a{idx}]")
    count = len(config["video_parts"])
    if config["audio_keep"]:
        # 003 changes the picture to a meaningful, same-film stage reaction.
        # The instructor's film dialogue/sfx continue uninterrupted.
        fragments.append("".join(f"[v{i}]" for i in range(count))
                         + f"concat=n={count}:v=1:a=0[v]")
        fragments.append("[0:a]atrim=start=0:end=39,asetpts=PTS-STARTPTS,"
                         "aresample=48000[a]")
    else:
        fragments.append("".join(f"[v{i}][a{i}]" for i in range(count))
                         + f"concat=n={count}:v=1:a=1[v][a]")
    command = ["ffmpeg", "-hide_banner", "-nostdin", "-y", "-v", "warning",
               "-i", str(src), "-filter_complex", ";".join(fragments),
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
               "-threads", "3", "-preset", "ultrafast", "-crf", "18",
               "-pix_fmt", "yuv420p", "-r", "30",
               "-c:a", "aac", "-b:a", "224k", "-ar", "48000",
               "-ac", "2", "-movflags", "+faststart", str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode or "Non-monotonic" in result.stderr:
        raise RuntimeError(result.stderr[-1500:])
    probe = subprocess.check_output(["ffprobe", "-v", "error",
                                     "-show_entries", "format=duration",
                                     "-of", "json", str(output)])
    actual = float(json.loads(probe)["format"]["duration"])
    expected = sum(b-a for a,b in config["video_parts"])
    if abs(actual - expected) > .10:
        raise RuntimeError(f"body duration {actual} differs from {expected}")
    print(f"BODY {short_id}: {actual:.3f}s {output}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-root", type=Path, required=True,
                    help="private folder containing 003/005/006 body_*.mp4")
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("ids", nargs="*", choices=sorted(EDITS), default=sorted(EDITS))
    args = ap.parse_args()
    for identifier in args.ids:
        render(identifier, args.source_root,
               args.output_dir / f"{identifier}_story_body_V45.mp4")
