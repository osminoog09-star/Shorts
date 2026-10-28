#!/usr/bin/env python3
"""M1lash Studio prompt pack: deterministic research/script/visual/audio/QA prompts.
A prompt is a production *brief*, never proof that assets, factual checks or a movie exist.
"""
import argparse
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
REGISTRY=ROOT/"prompts"/"m1lash"/"registry.json"
MIN_LONG=1260

def build(style,topic,format,duration,depth=None):
    if format not in ("short","long"):raise ValueError("format must be short or long")
    if not isinstance(topic,str) or not topic.strip() or len(topic)>240:
        raise ValueError("topic must be nonempty and <=240 characters")
    if not isinstance(duration,int) or duration<=0:raise ValueError("invalid duration")
    if format=="long" and duration<MIN_LONG:
        raise ValueError("all new M1lash long videos require >=1260 seconds")
    if format=="short" and duration>180:
        raise ValueError("Shorts brief too long; use long only if >=1260s")
    catalog=json.loads(REGISTRY.read_text(encoding="utf-8"))["styles"]
    found=next((x for x in catalog if x["id"]==style),None)
    if not found:raise ValueError("unknown experimental style; official S1-S9 live elsewhere")
    d=depth or found["depth"]
    if d not in ("D2","D25","D3"):raise ValueError("invalid depth")
    actual_topic=topic.strip()
    baseline=("Dima = ru-RU-DmitryNeural main narrator and CTA; Sveta = ru-RU-SvetlanaNeural secondary. "
              "No silent Liam/Piper substitution; no reused unverified outro. "
              "Do not fabricate sources, output rights, approvals or completed renders.")
    length_rule=("Every new full film must be >=1260 seconds of meaningful original content, "
                 "prefer 23-28 minutes; 4-5 acts, varied scene actions, no padding. "
                 if format=="long" else
                 "Native vertical 1080x1920; immediate meaningful hook, one story and resolution. ")
    base=f"Topic: {actual_topic}. Format: {format}. Planned duration: {duration}s. Style: {style} ({found['name']}); depth: {d}."
    return {
        "status":"EXPERIMENTAL_PROMPT_BUNDLE_NOT_RENDERED",
        "style_id":style,"format":format,"duration_s":duration,"topic":actual_topic,"depth":d,
        "research_prompt":base+" Research real facts; attach 2 independent sources per material claim, source dates, certainty, licensing. Do not confuse claims with verified findings.",
        "script_prompt":base+" "+length_rule+" Outline the hook, causal narrative, genuine discoveries and conclusion. Annotate every spoken fact with source ID and every passage with estimated seconds. "+baseline,
        "director_prompt":base+" Create distinct original shots, not image slides. Per shot: time, visible action, location, camera, emotion, physical prop contact, light, SFX, evidence and actor pose. For long film use 4-5 acts.",
        "visual_prompt":base+" "+found["visual"]+" Motion: "+found["motion"]+" Avoid: "+found["negative"]+" Characters consistent across shots, text legible, evidence accurate, rights documented. Show what narration actually says.",
        "voice_prompt":base+" "+baseline+" Make a per-line speech manifest with voice ID, engine, text, timestamps, hash, proper-name pronunciation, real word timing and audio approval. Any test TTS is not Dima until owner approval.",
        "qa_prompt":base+" Verify actual MP4 via ffprobe/full decode, duration, stream alignment, timeline, subtitles, scenes, first frame and last 30 sec, sources/licenses, every scene visually and voice auditorily. Any category <8/10 -> NO-GO. Short and long technical profiles differ. "+length_rule,
        "license_notice":"Prompt text is original project documentation; generated assets, third-party weights, stock, voices and music each require individual rights verification."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--style",required=True)
    ap.add_argument("--topic",required=True)
    ap.add_argument("--format",choices=["short","long"],required=True)
    ap.add_argument("--duration",type=int,required=True)
    ap.add_argument("--depth",choices=["D2","D25","D3"])
    ap.add_argument("--output")
    a=ap.parse_args()
    try: result=build(a.style,a.topic,a.format,a.duration,a.depth)
    except ValueError as e:ap.error(str(e))
    text=json.dumps(result,ensure_ascii=False,indent=2)
    if a.output:
        path=Path(a.output);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(text+"\n",encoding="utf-8")
    print(text)

if __name__=="__main__":main()
