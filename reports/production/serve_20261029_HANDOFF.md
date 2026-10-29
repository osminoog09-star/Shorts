# Serve Robotics S4-D25 — handoff 2026-10-29
## What exists
- Editorial production script: reports/radar/2026-10-29-morning/SERVE_PRODUCTION.md on radar/2026-10-29-morning-serve.
- 46-second silent animatic in conversation artifact, NOT the final release; no approved host or lip sync.
- This branch: scripts/serve_20261029_dima.py (ten segments, exact Microsoft Edge ru-RU-DmitryNeural, no fallback).
- This branch: .github/workflows/serve-20261029-voice.yml (voice-only artifact, no publication).
- This branch: scripts/qa/serve_20261029_release_gate.py (fail-closed checks).
## Blocking work
1. Run workflow through GitHub Actions; the connector cannot dispatch workflows and a workflow newly introduced on a feature branch may not auto-trigger. Do not claim a run ID until confirmed.
2. Download the artifact, inspect voice manifest and listen to ALL segments, especially CTA.
3. Render a new S4-D25 full-bleed animated video with approved HostCorner. Generate phoneme/viseme alignment from the actual Dima speech; do not use arbitrary amplitude mouth movement as proof of sync.
4. Produce final audio/video MP4; QA 1080x1920, ffmpeg full decode, subtitles, crop, frame inspection, music licenses, factual captions, listening. Create work/serve_20261029/lipsync_review.json only AFTER manual review, with booleans approved_host, reviewed_audio, reviewed_lipsync.
5. Run python scripts/qa/serve_20261029_release_gate.py FINAL.mp4; no YouTube upload, no scheduling.
## Current status
VOICE NOT CONFIRMED. FINAL MP4 NOT CREATED. NO-GO. No publication or calendar edits.
