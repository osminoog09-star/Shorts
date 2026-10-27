# M1lash V8 — hand and elbow prototype audit

Date: 2026-10-27. Scope: focused 6-second silent action test, **not a complete office-cartoon scene**.

### Deliverables
- `M1lash_V8_ARTICULATED_HAND.mp4` (generated locally; chat download), 6.000 s, 960×540, H.264, no audio.
- `m1lash_v8_articulated.py` (generated locally; chat download). All frames procedurally rendered by Python/CairoSVG — no imported stills or camera pan.
- Contact snapshots: `m1lash_v8_check_{2.5,3.0,3.5,4.25}.png`, available as chat artifacts.

### Tests
- Full FFmpeg decode: PASS.
- Contact at t=2.5: fingertip y310.594, button surface y311, offset -0.406 px.
- Contact at t=3.0: fingertip y321.752, button surface y321.752, offset 0 px.
- Contact at t=3.5: fingertip y323, button surface y323, offset 0 px.
- Contact at t=4.25: fingertip y310.388, button surface y311, offset -0.612 px.
- Button has visibly encoded downstroke and restoration; elbow and cuff are distinct connected shapes.
- IMPORTANT: coordinate pass does NOT certify attractive hand anatomy, collision-free silhouette, meaningful facial acting or commercial quality.

### Artistic QA
Character beauty, acting and full-body animation: NOT EVALUATED / NO-GO in this isolated hand-only study.
Anatomy: remains simplified, notably knuckles and curled non-index fingers; hand shading and foreshortening require art work.
Physical contact: coordinate alignment PASS, visual realistic material compression NOT PASS.
Voice and lip-sync: NOT PRESENT. No claim of 8/10 on all categories.

### Next
Improve hand model with 3D/2.5D anatomy, hand pose gallery, joint limits and surface collision; then restore complete actor, human reaction and verified Dmitry track in 15–30-sec scene. Perform model and acting gates before longform.
