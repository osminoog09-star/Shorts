# M1lash S1 44-second pilot V3 — batch revision and independent audit

2026-10-28. The full source is downloadable in the chat as `m1lash_s1_pilot_v3_production.py`; NOT committed in this PR, hence repo reproducibility gate remains open.

## Actual tested MP4
`M1lash_S1_44s_DMITRY_REWORK_V3.mp4`: 43.83333 s, 960×540, **24 FPS**, H.264+AAC, 1,214,283 bytes. Voice source remains original complete Dmitry `voice_00.mp3` extracted from approved zip. `ffmpeg -xerror` decode video+audio: PASS. Contact sheet sampled 11 timed shots `M1lash_S1_V3_AUDIT_CONTACT.jpg`.

## Changes to the whole 11-shot scene
- V2 employee was literally `boss(...,.82)` with a sweater rectangle over it. V3 **replaces it with independent drawing code**: altered facial structure, hair, vest, legs/arms, startled eyes, papers and asymmetric hand positions.
- 20→24fps, narration 43.8s kept without clipping.
- The dark interstitial now depicts a system-activation icon and label instead of a bare 'click' word.
- Adjusted ending caption to relate to the ongoing director situation.

## Inspected frame findings and hard NO-GO
- Director and employee differ more now but share same primitive head/hand design language; appeal still low.
- Office uses the SAME windows and table in nearly every shot, despite 11 chapter cuts; this is not genuine visual variety.
- Real decoded frame 1s: scene label overlaps the illustrated presentation placard.
- Frame 6s: robot partly behind the oversized label card; visual hierarchy wrong.
- Frame 24s: supposed button shot is actually a wide static boss with a huge red rectangle; **NO finger-button physical contact depicted**.
- Frame 29s and 33s: schematic printer and coffeemachine, characters absent; action/mouthsync limited.
- Near frame 42s: volume panel overlaps robot, and ending is not a standalone CTA or meaningful completed visual action.
- Lip-sync is NOT phoneme driven; no voice-aligned mouth shapes.
- Technical delivered preview, not target release 1080p.

## Editorial scores (subjective, verified only by sampled stills and technical decode)
Story correspondence 6/10; shot diversity 5/10; visual characters 4/10; anatomy/physical acting 3/10; background detail 4/10; narration continuity 8/10; lip-sync 1/10; technical decode 9/10. Release threshold >=8 across ALL: NOT MET.

## Essential next batch
**Stop adding captions & new micro-gestures to this PIL renderer.** Replace all character/robot models with consistent illustrated assets (or a more capable rig), add 2 true office layouts, animate fully legible physical actions, proof lip-sync and 1080p final output. Must audit every shot including end and align action to actual voice words, not arbitrary durations. Commit the full source/audio provenance rather than QA-only reports.
