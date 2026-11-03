"""Repair only two overlay windows in Claude's existing film; 45 s body + rev4."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from finish_ai_bureaucracy_v3 import ROOT, KEEP, run

work = ROOT / "motion-output/ai_bureaucracy_v3"
work.mkdir(parents=True, exist_ok=True)
run(["git", "submodule", "update", "--init", "--depth", "1", "skills/ext/huashu-motion"], cwd=ROOT)
chrome = shutil.which("google-chrome") or shutil.which("chromium")
if not chrome:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        chrome = p.chromium.executable_path
run(["node", str(ROOT / "shorts/ai_bureaucracy/preflight_hostfree.mjs"), "--patches"],
    cwd=ROOT, env=dict(os.environ, OM_CHROME=chrome, M1LASH_FRAMES_OUTPUT=str(work)))
frames = work / "frames"
if len(list(frames.glob("*.jpg"))) != 291:
    raise RuntimeError("Expected exactly 141 + 150 patch frames")
patch = work / "patches.mp4"
run(["ffmpeg", "-v", "error", "-y", "-framerate", "30", "-i",
     str(frames / "%05d.jpg"), "-c:v", "libx264", "-preset", "fast",
     "-crf", "17", "-threads", "2", "-vf", "scale=out_color_matrix=bt709:out_range=tv",
     "-pix_fmt", "yuv420p", "-colorspace", "bt709", "-color_primaries", "bt709",
     "-color_trc", "bt709", str(patch)])
source = ROOT / "videos/ai_bureaucracy_claude_ru.mp4"
# Picture windows preserve all original animation except the obsolete host.
picture = [(1, 0, 4.7), (0, 4.7, 10.1), (0, 12.5, 33),
           (0, 36.5, 42.5), (1, 4.7, 9.7), (0, 47.5, 50.9)]
filters = []
for i, (stream, start, end) in enumerate(picture):
    filters.append(f"[{stream}:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
filters.append("".join(f"[v{i}]" for i in range(6)) + "concat=n=6:v=1:a=0[v]")
for i, (start, end) in enumerate(KEEP):
    duration = end - start
    filters.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS,"
                   f"afade=t=in:d=0.005,afade=t=out:st={duration-0.005:.6f}:d=0.005[a{i}]")
filters.append("[a0][a1][a2]concat=n=3:v=0:a=1[a]")
body = work / "body_45s.mp4"
run(["ffmpeg", "-v", "error", "-y", "-i", str(source), "-i", str(patch),
     "-filter_complex_threads", "2", "-filter_complex", ";".join(filters),
     "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast",
     "-crf", "18", "-threads", "2", "-pix_fmt", "yuv420p", "-r", "30",
     "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709",
     "-c:a", "aac", "-b:a", "320k", str(body)])
out = ROOT / "videos/ai_bureaucracy_claude_v3.mp4"
run([sys.executable, str(ROOT / "tools/assemble_with_outro.py"), str(body),
     "-o", str(out), "--audio-bitrate", "320k", "--preset", "fast"])
# Preserve an actual candidate even if the strict final gate rejects it.
shutil.copy2(out, work / out.name)
shutil.copy2(str(out) + ".qa.json", work / "assembly.json")
with (work / "check.json").open("w") as f:
    run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/check.py"),
         str(out), "--platform", "shorts", "--json"], stdout=f)
run([sys.executable, str(ROOT / "skills/ext/ffmpeg-skill/scripts/look.py"),
     str(out), "--tiles", "3x2", "-o", str(work / "final_look.jpg")])
(work / "edit.json").write_text(json.dumps({
    "method": "291 replacement frames + existing Claude export",
    "keep_seconds": KEEP, "picture_windows": picture, "story_seconds": 45,
    "outro": "official rev4 via assemble_with_outro.py",
    "personal_listening": "NOT_VERIFIED", "publish_date": None
}, ensure_ascii=False, indent=2) + "\n")
shutil.rmtree(frames)
body.unlink(missing_ok=True)
patch.unlink(missing_ok=True)
