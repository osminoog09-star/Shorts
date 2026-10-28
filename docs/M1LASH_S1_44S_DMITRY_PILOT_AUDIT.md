# M1lash S1 first complete voiced code pilot — 2026-10-28

## Finished file and reproducible source in conversation
- `M1lash_S1_44s_DMITRY_CODE_PILOT.mp4`: 43.8333 s, 960×540, 18fps, H.264 + AAC, ~1.2MB.
- `m1lash_s1_44s_pilot.py`: exact executable render script (conversation download), reuses local `m1lash_s1_ink_v2.py` primitives. Requires `m1lash_ai_office_dmitry_voice.zip`, with `voice_00.mp3` (43.824s) and original word timestamps.
- Reference speech is *the whole first scene* of the office story: the director gathers staff, activates the all-AI button, 42 resignations print, coffeemachine speaks, director asks to increase volume. **No 20s truncation.**
- 11 action-matched scenes: meeting (0–5.7), new era (5.7–9.5), boss reaction (9.5–13.3), speech (13.3–19.6), accountant (19.6–23.2), button (23.2–25.45), darkness (25.45–27.15), printer (27.15–30.3), coffee (30.3–35.2), unplug (35.2–38.8), volume-up (38.8–43.824).
- Final file ffmpeg `-xerror` full decode **PASS**, video 43.833s and audio 43.824s (drift 0.009s).
- Contact sheet `M1lash_S1_44s_CONTACT_SHEET.jpg` created sampling 12 story timestamps. In first review, card overlapped boss and text crossed action; scene positions and text corrected and re-rendered.

## Artistic self-audit — NO-GO, target >=8/10 each not met
- Dramaturgical match to original narration: **6/10** — actions correspond roughly to narrative beats, but some cuts/props are still schematic.
- Shot coverage: **6/10**, 11 meaningful compositions; many reuse same windows and stage.
- Character art: **3/10**, simple geometric models with repeated faces and round hands.
- Anatomy: **3/10**, primitive hands and unnatural contact.
- Character acting: **3/10**, weak weight shifts and lip movement.
- Office setting: **4/10**, two compositions but flat and low-detail.
- Audio integrity: **8/10 for voice presence and complete line**, but lip-sync **not passed** (no phoneme-driven mouth).
- Video technical integrity: **9/10**: entire file decodes; final audio ends within 0.01s of video.
- Output 960×540 at 18fps is a technical preview, not production 1080p/24fps.
- Deliberately NO artist release approval; no YouTube upload.

## Major learning
This is the *first larger coherent, voiced* pilot after repeated silent microtests. It fixes missing voice and incomplete thought, but confirms the underlying character-model weakness is the dominant bottleneck. Do NOT return to single-hand V9 experiments. Replace character/robot model and office art **as a bundle** for all 11 shots, then full 1080p motion + lip-sync QA. The exact renderer, prior S1 base, approved voice ZIP, assets manifest and this report must be committed as a reproducible package before claiming repository completeness.
