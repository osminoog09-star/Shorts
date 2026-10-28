# Handoff — Waddle World news Short (28.10.2026 evening)

Owner: M1lash; editor: GPT-6 research radar. **Status: NO-GO / visual-only animatic; no publication.** Branch `radar/2026-10-28-evening-waddle` created from current main; no files or scheduled posts of other agents touched.

## Produced and saved
- Fact-check, 12 news candidates, source URLs, 51-second full RU script, storyboard, metadata, 24-minute Hera longform research brief and two movie-edit rights assessments: [evening radar](../../reports/radar/2026-10-28-evening.md).
- [production.json](production.json): nine scenes, audio voice manifest `ru-RU-DmitryNeural`, source_file null, no fake audio claims.
- [timeline.srt](timeline.srt): exact planned spoken text, estimated timings (not word-synced).
- Local, user-accessible production package ZIP with original Pillow/FFmpeg scene renderer, 9-frame contact sheet, QA JSON, 51s 1080x1920/12fps H264 silent animatic. The local ZIP/MP4 are conversation artifacts and **NOT** committed to GitHub; no GitHub download link is claimed for them. SHA256 animatic `8d17c6011da9f69edc327c7763f4f6180f713c35229e87a0f525b59351770721`. Full decode PASS. 9 visual stills inspected. No audio, no host, no lipsync.

## Required to proceed
1. Generate entire spoken script + exact CTA via **Microsoft Edge TTS ru-RU-DmitryNeural** (no Piper/Liam fallback), retain source audio and segment manifest.
2. Apply the existing approved `studio/src/HostCorner.tsx` (unchanged design), calculate new Rhubarb visemes from final audio, remove visual placeholder.
3. Restructure scene pacing to actual TTS word boundaries; tighten visual quality and reduce large empty areas; 30fps 1080x1920 final. Validate safe captions and all critical frames.
4. Music rights: original composition or verify NCS Laeko current license before including; add credits.
5. FFmpeg full decode + ffprobe video/audio + listening/lipsync review + visual check. **Do not call the animatic a release.**
6. Metricool calendar: 28.10 10:00 ID 405847304 and 16:00 ID 405064835 both show ERROR `You have reached your Metricool account limit`; YouTube publication **unconfirmed**. Verify in YouTube Studio before any re-upload; do not occupy third slot or alter other agents' posts.

## Editorial decisions
New lead is Waddle World, not repeated morning OpenAI/NVIDIA/Anthropic news nor Genie 4. Date of Waddle app-store appearance late September, **coverage** 28 October; don't claim launched today. Selected style **S5-D2** (next untested in GitHub queue), with alternatives S3-D25 and S8-D25. 24-minute Hera longform must satisfy `scripts/qa/longform_duration_gate.py` only after a real video is produced. No copyright-cleared movie clips exist.
