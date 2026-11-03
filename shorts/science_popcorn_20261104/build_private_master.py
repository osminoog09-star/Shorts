#!/usr/bin/env python3
"""Private final build for ONE M1lash popcorn Short (not a YouTube uploader).

Only consumes true Denis-Qwen offline voice + timed words. Never uses old
provisional captions, Dima, the archived outro, or any other Short's assets.
No private WAV, master video or owner reference is written to public Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
SPEC=json.loads((HERE/"spec.json").read_text(encoding="utf8"))
APPROVAL=json.loads((ROOT/"tools/outro/approved.json").read_text(encoding="utf8"))
ASSET=APPROVAL["assets"]["vertical"]
APPROVED_SHA=ASSET["sha256"]
EXPECTED_ID="science_popcorn_20261104"
EXPECTED_SPEAKER="denis"
EXPECTED_VOICE="denis-qwen3tts-reference-v1"
EXPECTED_ENGINE="qwen3-tts-local"
OUTRO_DEST=ROOT/"media/outro/m1lash_outro_denis_v3_vertical.mp4"

def fail(why: str):
    raise RuntimeError("NO-GO POPCORN: "+why)

def protect_private(path: Path):
    p=path.resolve()
    if p==ROOT or ROOT in p.parents:
        fail("private output is inside public git worktree")
    return p

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(cmd, capture=False):
    r=subprocess.run([str(x) for x in cmd],capture_output=capture,text=capture,check=True)
    return r.stdout if capture else None

def duration(path):
    return float(json.loads(run(["ffprobe","-v","error","-show_entries",
      "format=duration","-of","json",path],capture=True))["format"]["duration"])

def gate_basics():
    if SPEC["id"]!=EXPECTED_ID or SPEC["kind"]!="short":fail("wrong project ID")
    if len(SPEC["scenes"])!=6 or any(len(x["voice"])!=2 for x in SPEC["scenes"]):
        fail("expected six scenes/twelve lines")
    if [s["n"] for s in SPEC["scenes"]]!=list(range(1,7)):
        fail("scene order wrong")
    if SPEC["voice"]["voice_id"]!=EXPECTED_VOICE or SPEC["voice"]["engine"]!=EXPECTED_ENGINE:
        fail("script is not configured for owner's voice")
    if SPEC["outro"]["sha256"]!=APPROVED_SHA or APPROVAL["version"]!="denis-v3-music80":
        fail("outro fingerprint differs from approved manifest")
    if not (HERE/"film.html").is_file():fail("no popcorn HTML")

def validate_actual(timeline: dict, story: Path, voice_folder: Path):
    """Strict invariants before using private voice or rendering a frame."""
    if timeline.get("id")!=EXPECTED_ID or timeline.get("theme")!="popcorn":
        fail("wrong film or unrelated timeline")
    if timeline.get("actual_audio") is not True:
        fail("provisional/fake timing forbidden")
    if timeline.get("voice_id")!=EXPECTED_VOICE or timeline.get("engine")!=EXPECTED_ENGINE:
        fail("voice identity mismatch; Dima fallback forbidden")
    segs=timeline.get("segments",[])
    if len(segs)!=12:fail("expected 12 authenticated Denis segments")
    expected=[line for scene in SPEC["scenes"] for line in scene["voice"]]
    for i,(segment,phrase) in enumerate(zip(segs,expected),start=1):
        if segment.get("text")!=phrase:fail(f"line {i} differs from script")
        if segment.get("speaker")!=EXPECTED_SPEAKER or segment.get("voice_id")!=EXPECTED_VOICE or segment.get("engine")!=EXPECTED_ENGINE:
            fail(f"line {i} is not real Denis/Qwen audio")
        wav=Path(segment.get("source_file") or "")
        if not wav.is_file() or not wav.suffix.lower()==".wav":
            fail(f"line {i} lacks original WAV")
        protect_private(wav)
        if voice_folder not in wav.resolve().parents:
            fail(f"line {i} WAV not in expected private voice folder")
        # The recorded voice ID is not evidence by itself: require a SHA-bound
        # receipt created by the owner's offline Qwen synthesizer per WAV.
        receipt=wav.with_suffix(".provenance.json")
        if not receipt.is_file():fail(f"line {i} missing immutable Denis WAV provenance")
        original=json.loads(receipt.read_text(encoding="utf8"))
        if original.get("wav_sha256")!=sha(wav):
            fail(f"line {i} WAV hash disagrees with Qwen checkpoint")
        for key,value in (("voice_id",EXPECTED_VOICE),("engine",EXPECTED_ENGINE),
                          ("speaker",EXPECTED_SPEAKER),("text",phrase)):
            if original.get(key)!=value:fail(f"line {i} Qwen provenance {key} mismatch")
        if segment.get("scene")!=(i+1)//2:fail(f"scene {i} mapping incorrect")
        if not isinstance(segment.get("start"),(int,float)) or not isinstance(segment.get("end"),(int,float)):
            fail(f"invalid segment time {i}")
        if segment["end"]<=segment["start"]:fail(f"empty speech segment {i}")
        if i>1 and segment["start"]<segs[i-2]["end"]:
            fail("overlapping speech segments")
    if not story.is_file() or story.stat().st_size<10_000:
        fail("story audio absent")
    protect_private(story)
    total=duration(story)
    if not 30<=total+float(APPROVAL["duration"])<=59:
        fail(f"final duration {total+float(APPROVAL['duration']):.2f} outside 30-59 s")
    if abs(total-float(timeline.get("total",0)))>0.12:
        fail("timeline length does not match genuine audio")
    cuts=timeline.get("cuts",[])
    if len(cuts)!=7 or any(cuts[i]>=cuts[i+1] for i in range(6)):
        fail("six ordered shot boundaries missing")
    if abs(cuts[-1]-total)>.12 or cuts[0]!=0:
        fail("shot bounds do not span actual voice")
    caps=timeline.get("caps",[])
    if not caps:fail("true word timestamps missing")
    for i,c in enumerate(caps):
        if not isinstance(c.get("words"),list) or not c["words"]:
            fail(f"caption {i} has no words")
        start,end=c.get("start"),c.get("end")
        if not isinstance(start,(int,float)) or not isinstance(end,(int,float)):
            fail(f"caption {i} invalid time")
        if start<0 or end>total+.05 or start>=end:
            fail(f"caption {i} outside genuine voice")
        if end-start<.7:fail(f"caption {i} too fast to read (<0.7sec)")
        if i>0 and start<caps[i-1]["start"]:
            fail("caption order not monotone")
    return total

def install_verified_outro(private_source: Path):
    private_source=protect_private(private_source)
    if not private_source.is_file() or sha(private_source)!=APPROVED_SHA:
        fail("private vertical outro SHA does not equal approval")
    if OUTRO_DEST.is_file():
        if sha(OUTRO_DEST)!=APPROVED_SHA:
            fail("existing outro inside checkout has mismatched hash; will not overwrite")
    else:
        # Destination is gitignored private content; fail closed if .gitignore changed.
        if (ROOT/".git").exists():
            q=subprocess.run(["git","check-ignore","-q",
                str(OUTRO_DEST.relative_to(ROOT))],cwd=ROOT)
            if q.returncode!=0:fail("approved Denis outro is NOT gitignored")
        OUTRO_DEST.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(private_source,OUTRO_DEST)
    if sha(OUTRO_DEST)!=APPROVED_SHA:fail("outro copy integrity failed")

def render_synced(timeline, voice_dir: Path, out: Path):
    from playwright.sync_api import sync_playwright
    gate_basics()
    out=protect_private(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():fail("would overwrite an existing private master")
    fps=int(SPEC["frame"]["fps"])
    frames=math.ceil(float(timeline["total"])*fps)
    with sync_playwright() as p:
        chrome=shutil.which("chromium") or shutil.which("google-chrome")
        if not chrome:fail("Chromium not available for deterministic HTML graphics")
        browser=p.chromium.launch(executable_path=chrome,headless=True,
            args=["--no-sandbox","--allow-file-access-from-files","--disable-dev-shm-usage"])
        page=browser.new_page(viewport={"width":1080,"height":1920},device_scale_factor=1)
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.goto((HERE/"film.html").as_uri())
        page.evaluate("() => document.fonts.ready")
        page.evaluate("d=>window.setTimeline(d)",timeline)
        for cap in timeline["caps"]:
            t=(cap["start"]+cap["end"])*.5
            q=page.evaluate("""t=>{window.seek(t);
              const c=document.getElementById('cap'),h=document.getElementById('title'),
                a=c.getBoundingClientRect(),b=h.getBoundingClientRect();
              return {x:a.x,right:a.right,bottom:a.bottom,titleBottom:b.bottom,
                capOverflow:c.scrollHeight>c.clientHeight+1,titleOverflow:h.scrollWidth>h.clientWidth+1}}""",t)
            if q["x"]<95 or q["right"]>925 or q["bottom"]>1420 or q["titleBottom"]>450 or q["capOverflow"] or q["titleOverflow"]:
                fail("caption/title crosses mobile safe zone")
        proc=subprocess.Popen(["ffmpeg","-hide_banner","-v","error","-nostdin","-y",
          "-f","image2pipe","-vcodec","mjpeg","-framerate",str(fps),"-i","-",
          "-c:v","libx264","-preset","fast","-crf","19","-threads","2",
          "-pix_fmt","yuv420p","-r",str(fps),"-movflags","+faststart",str(out)],
          stdin=subprocess.PIPE)
        try:
            for i in range(frames):
                page.evaluate("t=>window.seek(t)",i/fps)
                proc.stdin.write(page.screenshot(type="jpeg",quality=89))
            proc.stdin.close()
            if proc.wait()!=0:fail("FFmpeg video encoder failed")
        except BaseException:
            proc.kill();raise
        browser.close()
        if errors:fail("Browser JavaScript rendering errors")
    run(["ffmpeg","-hide_banner","-v","error","-xerror","-i",out,"-f","null","-"])

def build(a):
    gate_basics()
    private=protect_private(Path(a.private_output))
    voice=protect_private(Path(a.private_voice))
    timeline_path=voice/"denis_true_timeline_PRIVATE.json"
    if not timeline_path.is_file():
        fail("VOICE_BLOCKED: genuine Qwen+Whisper timing absent, cannot use old silent video's placeholder timestamps")
    timeline=json.loads(timeline_path.read_text(encoding="utf8"))
    story=voice/"denis_story_NO_OUTRO.wav"
    real_length=validate_actual(timeline,story,voice)
    install_verified_outro(Path(a.approved_outro))
    graphics=private/"popcorn_true_synced_NO_AUDIO.mp4"
    render_synced(timeline,voice,graphics)
    body=private/"popcorn_body_DENIS_ONLY.mp4"
    if body.exists():fail("body already exists; avoid accidental replacement")
    run(["ffmpeg","-v","error","-nostdin","-y",
       "-i",graphics,"-i",story,"-map","0:v:0","-map","1:a:0",
       "-c:v","copy","-c:a","aac","-b:a","192k","-ar","48000",
       "-ac","2","-af","aresample=async=1:first_pts=0",
       "-shortest",body])
    if abs(duration(body)-real_length)>.12:fail("voice and body duration diverged")
    final=private/"M1lash_Popcorn_Denis_v3_PRIVATE_REVIEW.mp4"
    if final.exists():fail("final already exists; never overwrite")
    run([sys.executable,ROOT/"tools/assemble_with_outro.py",body,
        "-o",final,"--preset","fast","--crf","18","--max-seconds","59"])
    qa_check=private/"popcorn_check.json"
    with qa_check.open("w") as fh:
        subprocess.run([sys.executable,ROOT/"skills/ext/ffmpeg-skill/scripts/check.py",
            str(final),"--platform","shorts","--json"],stdout=fh,check=True)
    run([sys.executable,ROOT/"skills/ext/ffmpeg-skill/scripts/look.py",
        final,"--tiles","3x2","--output",private/"popcorn_final_contact.jpg"])
    run(["ffmpeg","-v","error","-xerror","-i",final,"-f","null","-"])
    report=dict(id=EXPECTED_ID,status="PRIVATE_TECHNICAL_QA_NOT_OWNER_APPROVED",
      presenter="denis",voice_id=EXPECTED_VOICE,engine=EXPECTED_ENGINE,
      outro_sha=APPROVED_SHA,speech_segments=12,
      subtitles="actual offline Whisper word timestamps",source="private Qwen WAV",
      duration=duration(final),sha256=sha(final),
      owner_listening="PENDING",published=False,uploaded=False,
      public_git_contains_personal_voice=False)
    (private/"popcorn_release_review_PRIVATE.json").write_text(
       json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps(report,ensure_ascii=False))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-voice",required=True,help="Private directory containing genuine 12 Denis WAVs, true timeline and story")
    p.add_argument("--approved-outro",required=True,help="Private Denis v3 vertical MP4 matching approved SHA256")
    p.add_argument("--private-output",required=True,help="Private directory OUTSIDE public repo")
    a=p.parse_args()
    try:
        build(a)
    except (RuntimeError,ValueError,FileNotFoundError) as e:
        print(str(e),file=sys.stderr)
        return 3
    return 0
if __name__=="__main__":
    sys.exit(main())
