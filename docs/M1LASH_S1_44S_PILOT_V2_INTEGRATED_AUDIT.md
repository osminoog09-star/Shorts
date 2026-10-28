# M1lash S1 44s Pilot V2 — integrated code-only production audit (2026-10-28)

## Verified deliverables
- `M1lash_S1_44s_DMITRY_REWORK_V2.mp4`: full episode 43.824 sec, 960×540, 20 fps H.264/AAC, size 1,291,742 bytes, full FFmpeg -xerror decode PASS.
- `m1lash_s1_pilot_v2_production.py`: self-contained local code renderer and sound assembly, available as a downloadable conversation artifact; **not committed in this PR**.
- `M1lash_S1_V2_PRODUCTION_AUDIT.jpg`: 11 actual video timecodes (1, 7, 11, 16, 21, 24, 26, 29, 33, 37, 42). Contact sheet is a representative sample, not full artistic viewing.
- Original complete scene-0 voice stem: `ru-RU-DmitryNeural`, 43.824 seconds, maintained without truncation or replacement.
- 11 original hand-coded shot modes; characters/robot and office environments reauthored in Python/Pillow geometry, not pan-over-static illustrations.

## Actual improvements compared to previous 44s pilot
- More character detail: jacket lapels, necktie, separately drawn arms and legs, facial eyes/brows, hair; robot with articulated limbs and screen.
- Office background reauthored for meeting room and open office, additional cityscape, desks, monitor units, detailed props.
- Re-rendered after visual QA detected labels crossing office furniture: moved two story labels away from action.
- FPS from 18 to 20 in a technical preview. Still **not** 1080p, not a production-quality deliverable.

## Independent editorial audit: NO-GO
- Dramaturgy/story-action alignment: 6/10, some props match dialogue, but blocking lacks natural interactions.
- Character appeal: 4/10. New details help distinguish outfits, yet figures resemble simplified geometric vector mascots; **not approved high-quality ink animation**.
- Anatomy/hands: 3/10. Hands and limbs remain unconvincing, and physical button contact remains unsupported by convincing close-up evidence.
- Acting/natural movement: 3/10. Most figures hold similar poses; blinking and bobbing do not substitute for body acting.
- Staging: 6/10. 11 distinct story beats but few genuine changing camera angles or reactions.
- Environment: 5/10. Two different sets but they share window motifs and flat perspective.
- Audio completeness: 8/10 for original full voice stem; lip-sync: NOT PASSED, no phoneme-driven dialogue.
- Technical video/audio: 9/10; full decode PASS and audio/video ends within 0.03 sec.
- Owner's hard condition >=8/10 in every quality category **NOT MET**.

## New confirmed lessons
1. Integrating more than one weak subsystem is better test coverage than endlessly polishing a hand, but does not magically produce strong character art.
2. A 44-second code-only video is feasible, including full original Dmitry audio; sound continuity is no longer the production blocker.
3. Layout/safe area checks must scan **every** planned shot title against foreground objects, not only first/last frames.
4. Actual character beauty remains the highest-risk P1 blocker: acquire/create one professional model and rig with multiple poses before re-rendering eleven weak figures.
5. Before claiming quality gain, compare identical timestamps/poses and listen to final 30 seconds, not just check codecs.
6. Keep render code plus manifest in GitHub, not QA reports alone; until committed, reproducibility is incomplete.
