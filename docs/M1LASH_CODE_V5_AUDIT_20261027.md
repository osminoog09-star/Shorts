# M1lash CODE V5 — self-audit (2026-10-27)

Artifact created locally: M1lash_CODE_V5_DIRECTOR_ACTING_TEST.mp4, 10.000 s, 960x540, 24fps, H.264, programmatic SVG/CairoSVG procedural frames, **no source image frames and no camera pans**. Reproducible local source: m1lash_v5_procedural.py (download from chat; NOT checked into GitHub). Decode with ffmpeg -xerror: PASS. Audio: **none**, intentionally silent motion-only test.

What actually improved: three meaningful distinct compositions (boss at desk, close press, worker and robot); keyframed easing; independent brows/blinks, head expression and button depression; more detailed jacket, hair and eyes. This is not a cinematic-quality animation.

## Observed visual problems (actual decoded frames at 2.3 and 4.8 seconds)
- Boss pose: arm stretched oddly with blunt fist, no convincing wrist/fingers; button looks oversized, monitor background remains flat. MODEL_GATE NO-GO.
- Contact close-up: fingertip overlaps button and button moves downward, but sleeve/forearm shape is giant unnatural tapered blob; palm and finger joints not believable. CONTACT_GATE NO-GO.
- No dialogue-driven lipsync, no convincing animated body weight, generic static backdrop; actor motion not enough. ACTING_GATE NO-GO.
- **Audio gate not tested** because this test deliberately has no soundtrack; do not call a silent video the final episode.

## Provisional editorial score / 10
Character appeal 3, anatomy 2, hand contact 3, natural acting 3, environment 3, camera staging 5, technical codec 9, speech/lipsync N/A. **8/10 on all categories NOT MET.**

## Concrete next production criteria
1. Rebuild character rig into layers: torso / upper arm / elbow / wrist / palm / five distinct fingers, body rotation and fabric-over-elbow geometry.
2. Separate world-space target (button position) from screen-space characters and use IK with constraints, but require a visual hand/finger contact test. Show a real hand with index finger curved and button depression.
3. Body weight shift and step/brace pose must happen before press; arm must not extend beyond plausible reach.
4. 3/4 face and profile must match frontal model sheet, six expressions with brow + eyelid + jaw differences.
5. Character-design pass BEFORE 10+ seconds of animation. Model must read as attractive without moving.
6. Test dialogue-sync against **original Dmitry audio** and full dramatic phrase when moving beyond silent motion prototype.
7. Check shots 2s before and after contacts in MP4, verify last frame/sound and overall decode. If any P1 gate fails, do not publish.
