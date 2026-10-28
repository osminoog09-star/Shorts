# Samsung Full V6 — native-detail geographic rebuild (2026-10-28)

**Approved title unchanged:** «Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?»

## Implemented and independently inspected before full render
- Natural Earth official public-domain 1:10m national outlines obtained by GitHub Actions: [workflow](../../.github/workflows/samsung-v6-geo-all.yml). Extracted **all 159 country features**, using ISO3 cross-check, not ambiguous ISO2 aliases. No duplicated/missing countries or dateline exceptions in rendered polygon selection.
- New native-resolution (1920×1080) animated map layer projects geography at **12 pixels per longitude/latitude degree** from a 4320×2160 world atlas; 30fps camera motion and original story overlays preserved. Distinguish from V5's whole image rendered at 960×540 and upscaled: the **map coastline and borders**, not all legacy UI typography, now get true Full-HD detail.
- Every polygon checked for country anchor placement: **two off-land points fixed** in Gambia (GM) and Trinidad and Tobago (TT). All other 157 fell inside their corresponding Natural Earth polygons.
- First-pass route data: **159 distinct ISO2**, 9 geographic regions (each 12+), 42 documented Samsung official national storefront offers, 117 unknown retail statuses. No invented prohibited/NEVER states. All colors read from existing audited V5 source.
- 159 first-country cues: 119 original spoken word-boundary cues, 28 legitimate visual passes, 12 previously estimated L20 cues. Narration remains original Russian DmitryNeural and SvetlanaNeural.
- 8 storyboard frames sampled before full build (South Korea, Japan, Nauru, Iran, Eastern Europe, Mediterranean, Peru, finale). Actual V5/V6 same-timestamp contrast composed; sharper native coastlines visible.

## Known limits
- Some intro/title/subtitle/panel graphics are inherited from V5 logical 960×540 and enlarged; do not claim 100% vector-native full 1080 artwork.
- L20 South America and L24 ending word metadata estimated, not independently forced aligned; still an editorial limitation.
- Evidence of 42 local storefront offers does not prove that 117 unknown countries are absent or historically NEVER. Verify any fresh claims independently.
- This branch **does not contain large MP4 binaries**. A downloadable artifact must be verified in the active ChatGPT container; YouTube publication is not performed.

## Release gates
Full film V6 expected 698.433 seconds, 20953 frames, 1920×1080 H.264 30fps + original AAC voices, plus phone 720p. Before claiming final: 14 chunks need exact frame counts (13×1500 + 1453), concat + remux full voice, full FFmpeg decode both files, ending sentence present, random frames checked from actual output, score reported as editorial not viewer retention.

## Process
Under development in authorized cloud: `/mnt/data/Samsung_V6_WORK/Samsung_Full_2026/v6`. This is NOT a path on the user's computer. New README, source code, original voices, 10m shapes and detailed QA are archived as a separate project ZIP after delivery.

## Final verified local export — 2026-10-28

- **Full HD file created:** `/mnt/data/SAMSUNG_FULL_V6_HD.mp4`, 396,039,113 bytes, 1920×1080 H.264/AAC 30fps, **20,953 frames**, duration **698.433333 seconds**; **full FFmpeg -xerror video+audio decode PASS**.
- **Phone file created:** `/mnt/data/SAMSUNG_FULL_V6_MOBILE.mp4`, 31,056,141 bytes, 1280×720 H.264/AAC 30fps, **20,953 frames**, duration **698.440998 seconds**; **full FFmpeg -xerror video+audio decode PASS**.
- Sampled and inspected **16 frames extracted from the finished Full HD MP4**, including 0s hook, South Korea, Japan, Pacific, Iran, Russia, Europe, Africa, South America, United States/Canada and the 690s final world view. Contact sheet: `SAMSUNG_FULL_V6_CONTACT.jpg` in downloadable source ZIP.
- Source QA: 159 unique ISO2, 9 geographic groups with >=12 countries, 159/159 verified ISO3-matched detailed shape features, **GM and TT markers reanchored**, 42 documented Samsung official-store offers, 117 **unclassified**; 119 spoken country cues, 28 visual first passes, **12 estimated** cues.
- Both final MP4s are **review cuts**, **not uploaded to YouTube**. Some animated UI/captions are inherited from V5's 960x540 logic and upscaled; it is the geographic background that has native Full HD precision. Subtitle timestamps for L20 South America and L24 finale remain estimates. A full manual normal-speed watch/listen has not been certified by QA scripts.
- **Internal subjective score ~7.5/10 overall; geographic drawing ~8.5/10, technical integrity 8.5/10. Do not claim user-verified 8/10.** Next material upgrade is voice-to-story pacing and more country-specific source evidence.
