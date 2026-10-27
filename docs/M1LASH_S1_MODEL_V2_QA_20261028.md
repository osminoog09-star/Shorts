# M1lash S1 Model V2 · 28.10.2026

## Rendered and verified locally
- Real procedural video: `M1lash_S1_MODEL_V2_ACTION_TEST.mp4`, 6.000s, 960x540, 24fps H.264, FFmpeg full video decode PASS.
- Original code: `m1lash_model_v2/build.py` (downloadable via chat); all frames rendered from CairoSVG SVG paths, no imported stills, no camera motion as a substitute.
- Six-panel PNG `MODEL_GATE_SHEET.png`, produced from procedural code: front neutral, 3/4 smug, profile angry, front shock, 3/4 sad, front laugh.
- Voice: **no audio**. Technical test only, not finished content.

## Honest independent model gate
- Art/character appeal **4/10**: improved intentional costume silhouette vs basic primitives, but still too infantile/stylized for approved art.
- Anatomy/hands **3/10**: crude fingers/mittens and odd arm pivot geometry.
- View consistency **2/10**: 3/4 and side were simulated by scaling the frontal head, not a real rotation. Profile visibly narrows face improperly. **DO NOT CLAIM PROPER THREE-ANGLE MODEL SHEET.**
- Facial expressions **4/10**: some brows/mouth variety, but emotion changes rely too much on one mouth position and frontal features.
- Acting/motion **3/10**: arm/eyes animate independently but no leg/weight shift, natural button contact is not established.
- Environment **4/10**; technical decode **9/10**, sound NOT TESTED.
- 8/10 per category: **NOT MET; ARTISTIC NO-GO**.

## Root causes and next iteration
1. Create a genuine multi-view head topology with separate contour, nose projection, eye placement, ear and hairstyle for frontal/3/4/profile; NEVER use scaleX as the stand-in for perspective.
2. Make attractive 5-finger hands and independent cuff/wrist meshes; compare hands in close shot before scene render.
3. Freeze all rig animation until standalone still MODEL_GATE passes: readable front/profile/3-4 + 6 natural emotions.
4. Only after model gate animate a 3–6s physical action with touch/press/recoil and coherent balance; compare actual MP4.
5. Reproducible scripts must be committed verbatim in GitHub for full project portability; this PR stores review, while complete code is available as a chat file rather than falsely claiming it has already been committed.

## Technical caveat
The six poses are six combinations of view and emotion, NOT three views each with six emotions. Next sheet should separate these dimensions into a 3x6 matrix.
