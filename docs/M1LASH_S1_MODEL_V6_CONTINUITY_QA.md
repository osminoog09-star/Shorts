# M1lash S1 Model V6 — Continuous head topology (2026-10-28)

## Actual completed files
- Local MP4: `M1lash_S1_MODEL_V6_CONTINUOUS_TURN.mp4`; 6.000s, 960×540, 24 FPS, 108803 bytes, H.264.
- Exact full video builder: `body_v6.py` (available as conversation downloadable file). Builds on local `body_v4.py` and uses the V5 body path art. This GitHub change stores the reusable head-turn function in `tools/m1lash_character_rig/continuous_head.py`, but NOT a self-contained complete video render command.
- Full FFmpeg decode with `-xerror`: PASS.

## Fix applied
- V5 snapped between three head polygons with inconsistent vertex counts (9,10,12), selected at yaw 0.23 and 0.73.
- V6 normalizes all three heads to **12 corresponding vertices**, morphs front→quarter→profile with smoothstep easing, gradually hides far eye.
- This avoids the previous sudden contour switch by construction. Full motion look is still a rudimentary vector cartoon; there is no evidence of audience or cinematic-quality improvement.

## Editorial review
Topology continuity: improved over V5; tentative 7/10. Character appeal 4/10, anatomy/hands 3/10, natural full-body acting 3/10, environment 3/10, technical MP4 9/10. Audio not tested (silent study). Required owner threshold **>=8/10 on all relevant dimensions is NOT MET**.

## Next root cause
Do not keep polishing contour interpolation. Next step is a genuinely better drawn *static* model body/hands, 3-view costume silhouette and recognisable expressions, plus physically grounded acting and complete Dmitry voiced scene once model gate passes. Avoid automatic cosmetic V7 if this gate remains below 5/10.

## Skill lesson
Make consistent point correspondence a hard prerequisite for animated contour morphs. Require a single reusable source module and test 0/25/50/75/100% yaw plus inspecting the rendered profile. Smooth mathematical morph does not certify attractive anatomy.
