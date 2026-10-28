# Samsung Full V4 — audited review cut (2026-10-28)

**Approved title unchanged:** «Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?»

**Status: REVIEW CUT, YouTube unpublished, not yet an 8/10 release.** V1/V2/V3 and Shorts V6 retained unchanged. Runtime cloud root: `/mnt/data/Samsung_Full_2026/v4` (not user's desktop). The V4 project/source ZIP, mobile MP4 and Full HD MP4 exist as chat artifacts, **not uploaded to GitHub**; do not invent public video links.

## Measured output
- V4 HD: H.264/AAC, 1920×1080, 30fps, 698.4333s, 20953 frames across 14 chunks (13×1500 + 1453), ~270 MiB.
- V4 mobile: H.264/AAC, 1280×720, 30fps, 698.4333s, 20953 frames, ~57 MiB. Entire mobile decoder PASS; HD sampled at 26 points and encoding metadata validated, full HD decoder interrupted by execution limit and hence not claimed as full PASS.
- Same Russian DmitryNeural/SvetlanaNeural audio as V3; no re-voicing or invented replacement.
- 159 unique ISO2 in 9 regions, 0 duplicate progress increments. Actual geo shape coverage 148/159 from CountryInfo + Natural Earth. Remaining **11** BB BH FM KI MV NR PW SG TO TV WS are honest precise geographical locator-insets, not invented polygons. 0 blank/missing representations, 0 off-land centroid for existing polygons, 0 mid-stop target offscreen. Serbia invalid polygon explicitly repaired via shapely buffer(0); GB, ME and MM silhouettes restored using Natural Earth data.
- All flag markers have X offset=0 relative to their map anchor, maximum 18 source px vertical; 0 fake trailing route lines; Iran story panel no longer hides main character. Country-title visible in ROI.
- 159 first-pass country cues: **117** actual Edge TTS WordBoundary, **12** explicitly estimated L20 South America cues, **30** visually visited unspoken stops. 2 callbacks to already-seen countries do not increment count. No equal-duration chapter slicing.
- 42 source-backed Samsung national smartphone storefronts (NO added 2026-10-28 from Samsung Norway official purchase page), 117 unknown retail statuses. No negative/NEVER inferred from missing data.
- Subtitle batches shortened by semantic/named-country boundaries. Missing V3 L20/L24 transcripts repaired; timestamp sources for these remain estimated, not verified; per-region human audible alignment still needed.

## Independent defects found and fixed in V4 test loop
1. Short marker connector still placed Portuguese flag in Spain; changed to exact same X and vertical-only 18px locator; retested at 093/159.
2. Intro card claimed a Russia supply fact before narration introduced it; replaced with worldwide Samsung question to match first spoken sentence.
3. Iran's lone country card disappeared into overview after two seconds while narrator remained on Iran; removed premature overview for single-country chapters.
4. Missing word metadata led to **Australia fallback subtitle text in L20/L24**, now reconstructed from actual scripts, with estimated timings clearly labeled.
5. Original RS latlng outside repaired polygon; fixed invalid geo polygon repair and reran across all 159; zero off-land active anchors after repair.
6. FFmpeg -shortest caused 20952 instead of 20953 video frames. Removed -shortest, checked video 698.4333s and mobile 20953/20953.
7. Long mobile reencode was cut at minute ~7 by tool runtime; transcoded in 3 exact source-length chunks and concat-copy, mobile entire decode PASS.

## Outstanding release blockers
- True detailed coastlines or map insets for 11 micro/island states; locator-only is honest but insufficient for requested donor-level visual polish.
- Rebuild/verify real L20 and L24 word boundaries against current WAV rather than syllabic estimates; 30 unnamed country visits are visual (valid), not word-cued (do not mislabel).
- Draw graphics and text at native 1920×1080 rather than rendering 960×540 and upscaling; present Full HD codec doesn't imply native geometry resolution.
- Thorough factual refresh of unverified 117 markets, NOT labeling them absent.
- More varied designed cinematographic country stories to achieve actual user-judged 8/10, final human watch/listen to full HD.

## Future release gates
Apply `skills/vizavi-motion/references/geography-map-video-qa.md` and `scripts/qa/map_release_gate.py`; require honest PASS across geography, timing, anchors, UI occlusions, proof sources, cue count, audio/endpoints. Technical codec success alone is never 8/10.
