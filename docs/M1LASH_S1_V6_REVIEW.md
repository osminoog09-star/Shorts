# M1lash S1 Ink V6 — self-audit (2026-10-27)

Generated actual video `M1lash_S1_INK_V6_BETTER_ARM.mp4`: 14.000 sec, 960x540, 24fps, H.264/AAC, local FFmpeg full decode PASS. Audio remains effects-only — **no Dmitry**. Source `m1lash_s1_v6.py` is available from this conversation; code inherits the V5 procedural renderer, then replaces the hand/button macro with new geometry. No imported illustration frames or camera pans.

## What V6 changes
- Replaces the previous giant one-piece sleeve wedge with **separate shoulder-to-elbow and elbow-to-wrist volumes**, independent cuff, palm and fingers; adds elbow seam and button travel.
- Preserves the original storyline, shot order and SFX, so the only meaningful improvement is the contact insert.
- Initial V6 review revealed duplicate on-frame headings left over from the V5 renderer; corrected header masking before final MP4 re-export.

## Technical / artistic QA
- Full video + audio decode: PASS; correct 14s export.
- Hand and costume anatomy: **4/10**, incomplete; while the sleeve is articulated now, it still looks like a stiff long bar and finger gesture is hook-shaped.
- Contact readability: **5/10**; index visibly touches moving button but cinematic fidelity is low.
- Character design: **4/10**; unchanged from weak V5 in much of the video.
- Meaningful movement/acting: **4/10**; too little natural body weight transfer.
- Environment: **4/10**; flat, repeated background.
- Staging: **6/10**; macro shows intent, but there are not enough meaningful variations.
- Narration and lip sync: **2/10**, SFX only.
- Technical: **9/10**.
- Owner's 8/10 in **every** category remains unmet. Artistic NO-GO.

## Verified skill lessons
1. Before export, inspect actual decoded frames from all replaced shots **and the title overlays**. When reusing another renderer, old overlays may remain under new version text.
2. Splitting one flat sleeve wedge into *two flat tapered shapes* does not produce beautiful anatomical motion: silhouette gate needs an attractive arm-and-hand pose with fabric folds and controllable wrist angle.
3. Stop accumulating more layers atop low-quality base characters; when design stays 4/10, prioritise new canonical character model and rig rather than postprocess.
4. Keep SFX vs actual voiced dialogue separate; do not claim lip-sync with no narrator.
