"""Finish the existing host-free render: 45 s story + unchanged approved rev4.
Requires an actual V2 MP4; does not render scenes, regenerate speech or publish.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEEP = [(0.0, 10.1), (12.5, 33.0), (36.5, 50.9)]


def run(args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=True)
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_format", "-show_streams",
        "-of", "json", str(source)
    ]))
    video = next(s for s in probe["streams"] if s["codec_type"] == "video")
    if (video["width"], video["height"]) != (1080, 1920):
        raise ValueError("Expected the actual 1080x1920 host-free V2 master")
    if float(probe["format"]["duration"]) < 51.03:
        raise ValueError("Source does not contain the complete original story")
    body = work / "body_45s.mp4"
    filters = []
    for i, (start, end) in enumerate(KEEP):
        duration = end - start
        filters += [
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]",
            f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.005,afade=t=out:st={duration-0.005:.6f}:d=0.005[a{i}]"
        ]
    filters.append("".join(f"[v{i}][a{i}]" for i in range(len(KEEP)))
                   + f"concat=n={len(KEEP)}:v=1:a=1[v][a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(source),
         "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
         "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "320k",
         str(body)])
    output = work / "ai_bureaucracy_claude_v3.mp4"
    run([sys.executable, str(ROOT / "tools/assemble_with_outro.py"),
         str(body), "-o", str(output), "--audio-bitrate", "320k", "--preset", "fast"])
    with (work / "check.json").open("w") as f:
        run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/check.py"),
             str(output), "--platform", "shorts", "--json"], stdout=f)
    run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/look.py"),
         str(output), "--tiles", "3x2", "-o", str(work / "final_look.jpg")])
    (work / "edit.json").write_text(json.dumps({
        "source": str(source), "keep_seconds": KEEP, "story_seconds": 45.0,
        "removed": ["Через минуту у них уже совещание",
                    "Жду час. Тишина. И тут пишет начальник"],
        "outro_method": "tools/assemble_with_outro.py",
        "personal_listening": "NOT_VERIFIED", "publish_date": None
    }, ensure_ascii=False, indent=2) + "\n")
    print(output, flush=True)


if __name__ == "__main__":
    main()
