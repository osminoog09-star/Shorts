# Genie 4 — M1lash V4 redesign and audit (2026-10-28)

Owner rated V3 5/10; the user specifically asked to **improve the entire video**. Preserve the approved talking host.

## Real work delivered
- Replaced repeated full-screen city/HUD template with **eight distinct code-rendered animated 2.5D S7 scenes**: world-from-prompt, interactive city, gradual weather change, spatial sound, research-only laboratory, physically broken world (floating car and fractured ground), developer workstation, city/space CTA.
- Exactly one short title or statement on-screen at a time; no persistent large headline + subhead + source panel + caption boxes. Keep sources in YouTube description.
- **Original approved host unchanged**: GitHub Actions run 40697188817 (Rhubarb lip-sync), reused as transparent alpha overlay. No editing face/clothes/presentation/voice. 720x1280 working composite and final Lanczos upscaling preserve the original final footprint at ~x20 y1060, 420x500.
- **Actual approved Dima**: original source MP3 from run 40696423671, `ru-RU-DmitryNeural`; no Piper/Liam.
- Speech scene cuts at detected actual silences (seconds): `0,4.045,11.471,18.829,23.738,31.967,39.019,47.568,58.536`. Unlike V3, not estimated from per-scene word counts.
- New quiet **original procedural** transition swooshes, plus the established original procedural backing track; no unlicensed music.
- 13 phrase-level Russian SRT entries in a separate file rather than multiplying on-screen captions; still not a verified word-for-word forced alignment.

## Verified current-turn outputs
Generated and verified exact files in the conversation working container, not the GitHub repository:
- `/mnt/data/M1lash_Genie4_V4_FullHD.mp4` H264/AAC, 1080x1920, 58.566667 s, 36,712,822 bytes, SHA256 `d55a821d873feda6463310ce943d1c2c915b7ea4cab510dd55df28ed005113ea`.
- `/mnt/data/M1lash_Genie4_V4_Mobile.mp4` H264/AAC, 720x1280, 58.566667 s, 20,732,903 bytes, SHA256 `c38f057e2081960d7cc656111811d30d315317dc0763eead9b8026ae651720d0`.
- `/mnt/data/M1lash_Genie4_V4_Code_QA_and_Mobile.zip` contains `render_v4.py` source, mobile MP4, SRT, original SFX WAV, 16-frame QA contact sheet and JSON report.
- Full FFmpeg decode pass on **both** MP4s; 16 representative frames inspected. No title/host collision on inspected frames; audio present, mean -21.6 dBFS and peak -4.9 dBFS; H264/AAC.
- Original Python scene renderer was developed in current-turn container, *not* committed as source to this repo. The ZIP is the source-of-truth for the actual V4 code. Do not claim it is in GitHub until imported.

## Quality gate / lessons for all future M1lash code video
1. One information layer per scene; no repeated opaque HUDs, long captions, persistent decorative progress bars, source boxes or duplicate title overlays.
2. Never modify an approved host/voice after user says keep it unchanged. Reserve its original rectangle early.
3. Render 8 meaningfully distinct scenes instead of the same city backdrop with changing headlines. Changes in subject require new scene objects, foreground actions and camera placement.
4. Sync cuts to the actual source voice's sentence pauses. Never distribute shot timing by text length when audio source is already available.
5. CTA text should match what Dima is saying at that moment (subscribe → thanks → audience question).
6. Conduct before/after 16-frame sample QA plus full decode, measure audio, release only after owner's artistic inspection. Passing FFmpeg does not mean 8/10.
7. Heavy ProRes RGBA overlays may make a full-HD ffmpeg render prohibitively slow: one tested fast workflow is pre-downscaling the original host alpha with qtrle to 280x333, compositing at 720p, then final Lanczos 1080p export. The final host rectangle must remain the same visually; this is a *performance-only* intermediary, not a change in avatar.

**Release status**: V4 private review. Never auto-publish. User's explicit artistic rating still needed, 8/10 is NOT claimed. Original platform demo footage has not been used. All visuals are editorial reconstructions, not real Genie 4 output.
