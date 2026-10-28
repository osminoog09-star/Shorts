# HANDOFF — Genie 4 radar, 2026-10-28

Owner: GPT-6 research-only agent. Branch: `research/genie4-20261028-radar` (NOT merged). This file deliberately does not edit main `HANDOFF.md` to avoid conflicts with Claude/Codex active production.

## Done
- Read current main AGENTS.md, CODEX_NOTICE.md, STRATEGY.md, HANDOFF.md, style-library.md, quality-upgrades.md, movie_edit README and MYSTERY_SHORTS_TEMPLATE.md; checked existing scheduled/produced topics from HANDOFF and reports/style_experiment.
- Verified 12 news candidates, identified 4 strongly source-supported and several provisional; links and dates in `reports/research/2026-10-28-genie4-radar-production.md`.
- Prepared complete 8-shot Genie 4 Shorts production manifest with exact original Russian lines, overlays, planned shot timing, voice ID, source/license policy, metadata: `shorts/genie4_20261028/production.json`.
- Prepared a 24:30 longform outline; updated requirement from main: new long videos **at least 21:00**, not 10–15 minutes.
- Confirmed no duplicated Genie 4 production in current main HANDOFF; earlier AI news 28.10 is about OpenAI/NVIDIA/Anthropic and must not be overwritten.
- Attempted installing `edge-tts` in local runner; pip could not reach package index (DNS error). No generated DmitryNeural audio; **do not substitute Piper/Liam**. No MP4 produced, no final QA claimed.
- vidIQ search failed with insufficient credits (refresh Nov 23); do not cite VPH/view data.

## Next actions, in order
1. Ask owner for S7-D25 vs S3-D25 vs S9-D3; if no reply by GitHub deadline, use CODEX_NOTICE style queue and record style experiment.
2. On internet-enabled runner install edge-tts, synthesize all spoken segments with `ru-RU-DmitryNeural` at same settings including CTA; inspect voice manifest and listen.
3. Re-time shots and captions to real TTS word boundaries; run Rhubarb `tools/lipsync.sh`, use approved PiP host (not an invented replacement).
4. Create eight original illustrated/3D scenes; mark them as artistic reconstruction of Google Genie 4 (not product capture). Music must have original composition proof or verified license; do not reuse archived Liam outro.
5. Render 1080x1920 30fps, full-bleed. ffprobe, full ffmpeg decode, frame inspection 0/1/mid/climax/CTA/end, audio listening, peak/ducking, subtitle spelling/safe margins, fact/source recheck.
6. Check actual live Metricool/YouTube slot; don't reserve 28.10 already busy slots; do not upload without owner authorization.
7. Expand 24:30 longform brief to full original voiceover script, then 21-minute gate and QA. Claude Roman Concrete in progress; do not edit its files.

## Release status
**NO-GO / production package only.** No actual `dima_ru.mp3`, no `dima_visemes.json`, no MP4, no YouTube ID, no live slot verification. All source links are in the report. Public branch contains no film clips and no unlicensed footage.


## 28.10 — Implementation attempt (GPT-6, follow-up)
- Created the real Python production renderer: `shorts/genie4_20261028/render_genie4.py` and push-triggered `.github/workflows/genie4-experimental-render.yml`. It uses eight existing shots, procedural original S7-D25 visuals, and the approved `studio/src/HostCorner.tsx`, with refreshed Rhubarb visemes and proper FFmpeg QA if an approved voice becomes available. No unlicensed Google demo, no archived Liam outro, no YouTube publishing. Branch only.
- GitHub Actions [run 40692002156](https://github.com/osminoog09-star/Shorts/actions/runs/40692002156): failed fast due Python syntax; fixed in commit `f67d9786c15bd47c5b9e6eac5529a17ac0ff7cd9`.
- GitHub Actions [run 40692195247](https://github.com/osminoog09-star/Shorts/actions/runs/40692195247): dependencies installed, actual Edge TTS execution attempted. **NO-GO**: three retries of `ru-RU-DmitryNeural` yielded `NoAudioReceived('No audio was received. Please verify that your parameters are correct.')`. Full TTS, lipsync and MP4 were therefore correctly NOT claimed. Offline Piper/Liam fallback expressly prohibited by AGENTS/CODEX_NOTICE.
- Added `preview_genie4.py` and `.github/workflows/genie4-visual-only.yml` to produce a visibly labeled NON-RELEASE 20-second original animation proof, with no audio, no avatar and no lip-sync, so it cannot be mistaken for the completed Shorts. Preview result must be verified separately.
- Do not schedule or post. When approved `ru-RU-DmitryNeural` becomes available, rerun production and inspect 8 voice segments, visemes, video/audio frames and rights before release; do not assume any successful rendering from this report.
