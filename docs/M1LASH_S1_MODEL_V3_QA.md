# M1lash S1 Model V3 — distinct angle geometry audit (2026-10-28)

Generated real local artifacts: `M1lash_S1_MODEL_V3_REAL_TURN.mp4` (6.000s, 960×540, 24 FPS, H.264, 91398 bytes), `MODEL_GATE_V3_3x6.png` (18 panels), `build_v3.py` (chat download). Full `ffmpeg -xerror` decode PASS. This repository additionally includes independent reusable front/3/4/profile head geometry in `tools/m1lash_character_rig/head_turnaround.py`. The Python video builder depends on earlier `build.py` in the downloadable project; not yet a standalone repo render pipeline.

## Specific improvement
V2 used `scaleX` to make a fake profile. V3 hand-authoring has distinctly different head outline, protruding nose, single visible eye and ear for profile; 3/4 view uses unequal eye sizes and asymmetrical contour. Six emotional mouth/eye configurations displayed for each view, 3 × 6.

## Independent criticism / hard gate
- Front/3quarter/profile HEAD topologies differ (technical design objective achieved).
- Torso, arms and legs **remain front-facing** even in profile: view-continuity artistic FAIL.
- Facial features are still very simple and expressions largely mouth-dependent; character appeal about 4/10, expression differentiation 4/10.
- 3/4 face is too similar to front; hands still crude, no detailed back-side costume geometry.
- Motion demo uses hard cuts among drawn poses, not continuous natural head rotation. This is a **turnaround presentation** not a full acting scene.
- Audio: NONE; cannot assert Dmitry or lip-sync.
- Technical file 9/10; artistic 8/10 in all categories NOT MET.

## Lessons
1. A genuine model turnaround requires **BODY and costume** geometries in each angle, not just head.
2. Independent geometry paths beat cheap face scale transforms, but 18 drawings are not proof of artistic quality.
3. Allow actual sculpted side-profile ear/nose/jaw; maintain character identity and proportion grid.
4. Next technical target: new body view construction plus rig interpolation in actual action, not pose-to-pose jump cuts; model gate before long scene.
