# 01.11 · Chigur cinematic 3D V13/V14: staging audit

## V13: rendered and inspected, NO-GO
- Actions run **41327670440**, artifact **13092121882**, six 960×540 PNG from `shorts/chigur_v13_stills.py`, saved `/mnt/data/chigur_V13_private_QA.zip`; contact `/mnt/data/chigur_V13_contact.jpg` opened visually.
- №02: hallway gained practical lights and a looming figure, but the figure is explicitly a cylinder/sphere mannequin: **fails** the studio ban on mannequin-like proxy people.
- №04: animated hand created in 3D but **entirely off screen** in QA stopframe; still just coin+chair+paper, so the intended emotional action is not visible. No artistic PASS.
- №06: haze and setting improved marginally, car reads as a toy; need less frontal hero lighting and stronger silhouette/physical action.
- №01/03/05 mostly unchanged from V12, meaningful detail but not 28 varied narrative scenes.

## V14: fix issued, pending review
- `longform/chigur/graphics/three_stage_v14_atmosphere.js`: mannequin replaced with physically cast soft doorway shadow (3D plane and alpha canvas texture), moving arm reframed to visible right-foreground, corrected `poses[3]` camera target. No film frames, no PIL art.
- `shorts/chigur_v14_stills.py`, `jobs/motion/chigur_v14_six_stills.json`: starts shared motion-render workflow with 6 PNG gate. **Await** `reports/research/chigur_v14_run.json` and independent screenshot inspection before claiming improvement.

## Film constraints
- Long REV19: **28 legacy PIL intervals not touched**, no full 1080p MP4 revision. V12 six-second motion pilot is genuine movement but aesthetically weak: `reports/research/2026-11-01_CHIGUR_V12_MOTION_PILOT_QA.md`.
- Exact next step: get V14 screenshot artifact, inspect hand visibility and human-proxy absence. If visually stronger, pilot an action that advances story in 5–10 seconds and compare with rev4 outro. Do not present source-only/CI green as ready.
