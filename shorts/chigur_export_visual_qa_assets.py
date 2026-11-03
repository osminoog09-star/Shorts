#!/usr/bin/env python3
"""Read-only export of Chigur V15 authored visual sources and exact ffmpeg QA toolchain.

Runs via existing motion-render.yml. Output: ephemeral private Actions artifact.
Absolutely no movie media, secrets, real actor clips, or complete proprietary MP4s.
"""
from pathlib import Path
from shutil import copy2,copytree
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"motion-output"
OUT.mkdir(exist_ok=True)
ASSETS=[
 "longform/chigur/graphics/three_stage_v7.js",
 "longform/chigur/graphics/three_stage_v11.js",
 "longform/chigur/graphics/three_stage_v14_atmosphere.js",
 "longform/chigur/graphics/three_stage_v12_motion.js",
 "longform/chigur/graphics/three_stage_v12_overlay.js",
 "longform/chigur/graphics/three_stage_v15_actions.js",
 "longform/chigur/graphics/shot_plan_v15.json",
 "longform/chigur/graphics/new_graphics_ranges.json",
 "shorts/chigur_v15_story_pilot.py",
 "tools/assemble_with_outro.py"
]
for name in ASSETS:
 p=ROOT/name
 if not p.is_file():raise RuntimeError("Missing source "+name)
 dst=OUT/"source_bundle"/name
 dst.parent.mkdir(parents=True,exist_ok=True)
 copy2(p,dst)
exact=ROOT/"skills/ext/ffmpeg-skill/scripts"
if not (exact/"check.py").is_file() or not (exact/"look.py").is_file():raise RuntimeError("missing QA")
copytree(exact,OUT/"source_bundle/skills/ext/ffmpeg-skill/scripts",dirs_exist_ok=True)
(OUT/"source_bundle/MANIFEST.json").write_text(json.dumps({
 "kind":"Chigur V15 source QA export", "contains_movie":False,
 "contains_licensed_film_dialogue":False,"complete_movie_output":False,
 "sources":ASSETS,"production_stage":"private visual prototype"
},ensure_ascii=False,indent=2)+"\n")
print("V15 source QA bundle prepared; no movie media exported",flush=True)
