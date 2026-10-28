# M1lash S1 44-second narrated pilot V4 — QA

Created in conversation 2026-10-28. Local file: M1lash_S1_44s_DMITRY_REWORK_V4.mp4 (43.824 seconds, 960x540 24fps H.264/AAC, 3,180,809 bytes). Uses original complete 43.824s voice_00.mp3 by Dmitry from user-approved archive. Entire decoded audio/video passed ffmpeg -xerror.

Full reproducible code supplied as conversation ZIP M1lash_S1_V4_SOURCE.zip (base_v3.py and render_v4.py). Note: source ZIP not committed in this PR, so GitHub source integration remains open.

Changed 4 storyboard shots in the complete 11-shot pilot, not random cosmetic filters: a new conference-room composition, two robots entering office, physical hand/button insert, end screen with increasing volume and M1lash strip. Other 7 shots still inherit the V3 code.

Contact sheet M1lash_S1_V4_KEYFRAMES.jpg samples 2s,7s,24s,42.8s,43.7s:
- Frame 24s clearly shows a hand approaching the physical button; however finger art is still primitive and not a convincing press.
- 7s shows differentiated robot composition, but people and robots remain simplified.
- At 42.8s panel obscures robot body; outro has branding but composition is unpolished.
- 2s meeting is different spatial staging, but reused employee models look nearly identical.

Self-review: character appeal ~4/10; hands/anatomy ~3/10; acting ~3/10; stage variety ~6/10; scenery ~5/10; scene-to-voice ~6/10; voice completeness 8/10; phoneme lip-sync NOT PASS; technical decode 9/10. Artistic gate >=8/10 each **NO-GO**. These are editorial ratings, not verified viewer scores.

Learning: improving narrative coverage can coexist with poor on-model characters. Replacing 4 shots is not a full visual overhaul. Detect actual occlusions in last second, not just AV duration match. The next production block must remake canonical character rigs and staging across ALL remaining 7 shots; separately solve lip sync, visible contact, end-panel geometry, before claiming new quality level.
