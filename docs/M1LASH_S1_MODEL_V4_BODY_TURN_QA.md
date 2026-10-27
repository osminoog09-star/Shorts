# M1lash S1 Model V4 — code body turnaround, 2026-10-28

## Render and verification
Actual output: M1lash_S1_MODEL_V4_BODY_TURN.mp4, **6.000s, 960x540, 24 FPS, 115825 bytes, H.264**. ffmpeg -xerror full decode PASS. Exact local code: m1lash_model_v2/body_v4.py, downloadable in the chat (not falsely claimed to be GitHub committed).
Every frame is rendered in Python/CairoSVG from procedural SVG shapes, with no imported photo or camera-pan substitute.

### Verified change
Head, shoulders, torso, tie, arm targets, hips, legs and feet interpolate over a common turn factor. Compared to V3, the body no longer remains completely fixed front-facing during side head pose.
A mid-turn pose and frame ~106 (4.4s) were inspected as decoded PNG stills.

### Artistic self-audit (NO-GO)
- Consistent body/head yaw animation **5/10**: geometric changes visible but torso still lacks believable silhouette at 3/4/profile.
- Character appeal **4/10**: simplified geometric features, abrupt shape changes during perspective turn.
- Hands and anatomy **3/10**: hands are circles with drawn lines, straight limbs and no fabric deformation.
- Animated motion **4/10**: linked movement but legs do not pivot with hips, no authentic weight shift or natural footfall.
- Office environment **3/10**: largely empty flat windows; no staging context.
- Technical decode **9/10**.
- Narration / lip sync NOT TESTED: silent motion experiment.
- Owner's hard gate 8/10 in EACH relevant category **NOT MET**.

### Newly learned rules
1. Rotating body by narrowing shoulder widths is not a proper side-view reconstruction; side silhouette, arm occlusions, tie perspective and visible/far-side limbs must be genuinely redrawn.
2. Model sheets must validate front/3/4/profile across head **and** shoulders/arms/hands/torso/hips/feet with consistent character identity.
3. Never score 'moving legs' as natural walk without checking ground contact and weight transfer.
4. Next generation must fix silhouette in still poses BEFORE adding time interpolation; do not create V5 based on cosmetic eye or shadow changes.
5. Keep actual render script, proof frames and exact final MP4 together for reproducible learning.
