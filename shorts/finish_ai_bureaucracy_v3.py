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


def overlapping_caption_frames():
    data = (ROOT / "shorts/ai_bureaucracy/film/assets/voice/timeline.js").read_text()
    voice = json.loads(data.removeprefix("window.VO = ").strip().rstrip(";"))
    seg = {s["id"]: s for s in voice["segs"]}
    hidden = [(seg["d05"]["words"][0]["s"] - 0.05, seg["s04"]["start"] - 0.14),
              (seg["d07"]["start"] - 0.2, seg["d08"]["start"] - 0.18),
              (seg["s05"]["start"] - 0.05, 51.105)]
    return [i for i in range(1531)
            if not any(a <= i / 30 < b for a, b in hidden)
            and sum(c["t0"] - 0.03 <= i / 30 < c["t1"] for c in voice["caps"]) > 1]


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
    bad_frames = overlapping_caption_frames()
    for i, (start, end) in enumerate(KEEP):
        duration = end - start
        local_bad = [n - round(start * 30) for n in bad_frames if start <= n / 30 < end]
        # Remove the single corrupt overlap frame; CFR fills its existing time
        # slot with an adjacent clean frame. Audio and all timestamps stay fixed.
        selection = "+".join(f"eq(n\\,{n})" for n in local_bad)
        repair = f",select='not({selection})',fps=30" if local_bad else ""
        filters += [
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS{repair},"
            f"scale=in_color_matrix=bt601:out_color_matrix=bt709:out_range=tv[v{i}]",
            f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
            f"afade=t=in:d=0.005,afade=t=out:st={duration-0.005:.6f}:d=0.005[a{i}]"
        ]
    filters.append("".join(f"[v{i}][a{i}]" for i in range(len(KEEP)))
                   + f"concat=n={len(KEEP)}:v=1:a=1[v][a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(source),
         "-filter_complex", ";".join(filters), "-map", "[v]", "-map", "[a]",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-threads", "2",
         "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-b:a", "320k",
         "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
         str(body)])
    output = work / "ai_bureaucracy_claude_v3.mp4"
    run([sys.executable, str(ROOT / "tools/assemble_with_outro.py"),
         str(body), "-o", str(output), "--audio-bitrate", "320k", "--preset", "fast"])
    with (work / "check.json").open("w") as f:
        run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/check.py"),
             str(output), "--platform", "shorts", "--json"], stdout=f)
    run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/look.py"),
         str(output), "--tiles", "3x2", "--overwrite", "-o", str(work / "final_verified_v3.jpg")])
    (work / "edit.json").write_text(json.dumps({
        "source": str(source), "keep_seconds": KEEP, "story_seconds": 45.0,
        "replaced_overlap_source_frames": bad_frames,
        "removed": ["Через минуту у них уже совещание",
                    "Жду час. Тишина. И тут пишет начальник"],
        "outro_method": "tools/assemble_with_outro.py",
        "personal_listening": "NOT_VERIFIED", "publish_date": None
    }, ensure_ascii=False, indent=2) + "\n")
    print(output, flush=True)


if __name__ == "__main__":
    main()

