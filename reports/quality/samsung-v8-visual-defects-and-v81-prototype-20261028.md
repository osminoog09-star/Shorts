# Samsung V8 visual audit from 6 user screenshots — 2026-10-28

**Unchanged approved title:** «Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?»

## Screenshots and P0/P1 root causes
1. Repeated internal stage badges `E01 / 01 из 03` and `E02 / 03 из 03` at top-right in new research scenes. **P0 viewer-facing debug output**. Remove entirely, not reword to another code.
2. Country stop badges `010/159`, `015/159` at top-right on baseline map scene. **P1 distracting build-style counter**. Replace by occasional genuinely useful chapter markers; no permanent progress number.
3. Philippines 015/159: the map visually emphasizes Borneo, New Guinea and Australia while the named Philippines is small/partly at top. Myanmar 010/159 too wide. Country camera must be evaluated by screen composition and land visibility, not only valid centroid.
4. Baseline country card `КИТАЙ` appears with story overlay still saying `ЯПОНИЯ · ПРОДАЖИ GALAXY`. **P0 semantic mismatch**. For a cross-market comparison, show both countries explicitly and the specific source; otherwise never retain a previous country's story panel after camera transition.
5. Added research cards consist of three near-static screenshots for ~40-50s of narration; generic side-by-side text panels lead to boredom. **P0 storytelling mismatch**. Replace with real licensed photography where facts talk about hardware, factory/ship/delivery where facts talk about production/logistics, meaningful 3-step diagrams where facts explain channels. Aim for new meaningful visual beat every 5–8 seconds; zoom alone is insufficient for 10/10.
6. Old story photoless cards make a phone explanation look like a geography lesson; add documentary B-roll and descriptive, license-correct object labels.

## Actual changes completed in cloud prototype V8.1 (NOT full film)
- The existing V8 full cut is ~1477.317s (24:37), H.264/AAC, not overwritten. It includes 26 original and 17 genuinely voiced extra stories; 3 originally drafted stories were not present in the prior V8 final, so don't claim all 20 are already in film.
- New Python source `Samsung_V8_21plus/create_storyboards_v81.py` built **60 new 1920x1080 storyboard panels** for all 20 drafted stories. Viewer-facing `E##` and stage numerals are removed; stage types are map, real photographed objects/production (when appropriate), and subject-specific 3-step fact diagram. Images have qualifying restrictions on-screen.
- Real source assets obtained through the GitHub workflow [samsung-v8-visual-assets.yml](../../.github/workflows/samsung-v8-visual-assets.yml); 5 downloaded and license verified: authentic Galaxy A51 2020 by EDG 543 CC BY 4.0; Samsung SGH-C207 2007 public domain; typical non-Samsung assembly line CC0; smartphone use CC0; generic fishing nets CC0. 2 intended files (ship, smartphone screen) failed 429 and were **not** substituted with unknown photos.
- New **89.03s actual MP4 preview** combines research chapters E02 Japan and E03 Vietnam with approved original Dima/Sveta voices, both 1920x1080 in source and mobile 720p copy. New preview does not show editor badges; 6 camera shots per chapter, ~7.3–7.5 seconds each. Full FFmpeg -xerror decode PASS. Verified exact output exists locally as `/mnt/data/M1lash_Samsung_V81_NEW_VISUAL_SAMPLE_MOBILE.mp4`.
- The preview improves variety but remains a **prototype**, not a finished 24-minute V8.1. Reusing a photo in a nearby cut is still inferior to a true six-asset documentary scene and should be improved further.

## Rights and factual safety
- Samsung Global Newsroom published Terms of Use say content cannot broadly be republished for commercial use without permission; no copyrighted newsroom photos auto-imported.
- CC BY 4.0 A51 photo must credit EDG 543 and license in video description. CC0 images need no attribution but recommended.
- Generic assembly-line photo is an iPhone pre-production line; **must be marked as generic illustration, NOT Samsung factory in Vietnam or Noida**.
- Old 2007 Samsung device is not first 1988 phone. A51 2020 is not proof of current Japanese availability. Photo is illustration, source/official-shop document provides claim.
- Never turn unknown official sales into «не продаётся»; 159 countries continue to be sourced from the same registry.

## Remaining before V8.1 release
Rebuild 17 E-chapter clips from new plan, then the 26 original map chapters to remove `###/159`, correct Japan/Korea/China overlay/cue and poor framing (Philippines, Myanmar). Keep exact voice and country timeline; no scripted fake anecdotes. Visually inspect all story/map changes, original photos with source captions, silent overlaps, and run full-duration + full decode on the **new** 21+ minute MP4. Do not claim the old V8 is fixed or 10/10 until this is complete.

**Status: AUDIT COMPLETE; NEW VISUAL PROTOTYPE AND 89s MP4 READY; FULL V8.1 MASTER NOT YET ASSEMBLED.**
