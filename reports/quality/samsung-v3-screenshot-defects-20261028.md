# Samsung Full V3: screenshot-based defect register (2026-10-28)

## Scope and immutable baseline
User submitted seven screenshots: `1000026475.jpg`, `1000026477.jpg`, `1000026479.jpg`, `1000026481.jpg`, `1000026483.jpg`, `1000026485.jpg`, `1000026487.jpg` (screens 033–036, 038, 041, 044 / 159). This note intentionally does **not** claim the defects are fixed. More screenshots expected. Preserve approved video title and Russian Dmitry/Svetlana track.

## Root cause audit (confirmed in local /mnt/data/Samsung_Full_2026/v3/render_v3.py)
1. **P0 Missing country geometry**. The program constructs `shapes[c]` from `countryinfo.CountryInfo().all()[...]['geoJSON']['features']`. Cross-check of all **159 ISO2** rows in `facts_v3.csv` reveals **15 with zero polygon features**: BB, GB, RS, ME, BH, MV, MM, SG, WS, TO, KI, FM, PW, NR, TV. These include UK, Serbia, Montenegro, Myanmar, Singapore and 9 small islands. Centroid for each may exist, so a flag marker and counter still appear without any corresponding country silhouette. This explains Tuvalu, Nauru, Palau, Micronesia empty-water frames. Must fix data **before** rerender. Map marker ≠ land polygon, and success of 159 counter ≠ visual coverage.
2. **P0 Unsynchronized voice/map progression**. `segment` schedules every country in a narration chapter by `t0=starts[i]+cdur*k/len(xs)` irrespective of when the spoken country appears. At 038/159 the spoken text discusses Turkmenistan while map labels Uzbekistan; at 041/159 the speaker asks about upcoming Iran while map shows Turkmenistan. No arbitrary timing slices: anchor to actual TTS word boundaries, including voice-to-map delayed transitions. Narrative callback should not increment counter twice.
3. **P1 Locator graphics not geographically explanatory**. `screen_point()` targets a country centroid; then `alpha_over(sprite,sx+ox,sy+oy)` offsets the flag from that centroid without a drawn connecting line. For microstates with no polygon it visually resembles a ball floating over ocean attached to an empty ring; long travel lines for previous stops add misleading strokes. Use stable proximity/leader-line collision layout and larger island inset views, zoom at least enough to see land; never draw a status face at a place where the model has no corresponding land geometry unless clearly labeled inset.
4. **P1 Overlay occlusion**. Iran story overlay `show_story()` occupies right part of map; countryball is rendered before overlay and becomes partly concealed. Need subject-aware panel placement (left/right) or reframe map; ensure country outline, main marker, and anchor all remain visible. Keep story panel out of subtitle and key label safe areas.
5. **P1 Broken phrase captions**. `subslots` groups narration into blocks of exactly 7 tokens (`for k in range(0,len(entries),7)`), not by natural phrases, yielding abrupt fragments such as 'крест только потому, что государство крошечное или' and 'И Туркменистан. Через Афганистан переходим к Ирану' across inconsistent country cards. Split at punctuation/clauses, 2–6 useful words, two lines maximum, using verified word-boundary times.
6. **P2 Low apparent resolution/overbearing UI**. Renderer draws source at only **960×540** and then scales to 1920×1080; fonts, water contours and flags have visible pixel-level softness and can look like a game debug overlay rather than a documentary. Design native 1920×1080 atlas/text; allocate key story card only when narration demands; otherwise avoid a permanent 159-counter UI dominating screen.
7. **P2 Missing contrast/variety**. Multiple consecutive microstate frames show almost indistinguishable dark ocean with no country highlight. Group small island stops into purposeful regional inset/flyover and use actual land outlines and strong contextual labels while preserving 159-country itinerary. No lengthy empty-ocean holds.
8. **P2 Inconsistent story wording/UI**. Iran card alternates English FREE/PAID and Russian explanation in a fully Russian documentary; 'ИСТОЧНИКИ: SAMSUNG / ДОКУМЕНТЫ' is too generic to validate a fact. Use Russian micro-labels 'БЕСПЛАТНО'/'ПЛАТНО' with exact source/date in author fact register, concise onscreen date and attribution.
9. **NOT a renderer defect**: the large black bands above/below narrow landscape picture in user's portrait gallery screenshot and the small anime mini-player are phone/app UI, not proof of black fields or anime injected in the exported MP4. Check original decoded full-frame MP4 separately before claiming a video black bar defect.

## Visual examples mapped from user's screenshots
- 033/159 TV: country outline absent, marker floating in dark water.
- 034/159 NR: absent country silhouette, long diagonal stroke to isolated point.
- 035/159 PW: national flag icon exists but actual island not outlined/spotlighted.
- 036/159 FM: almost entire canvas empty ocean, long horizontal stroke with no geography.
- 038/159 UZ: word timing already reaches TM; map one stop behind the speech.
- 041/159 TM: narrator asks Iran-related question while current card remains TM.
- 044/159 IR: documented Galaxy Store story panel hides main character; camera frames unrelated land more prominently.

## Must-pass validation gates before calling V4 '7/10'
- ISO2 polygon coverage **159/159**, or explicit user-approved inset substitute for microstates; no silent geometry omissions. Verify all 15 above.
- Verify word-boundary timestamps by sample around 033–044 and at least 3 later regional transitions; country changes only on narration cue, no mismatched labels/stories.
- Overlay layout occlusion tests across story cards. Main country remains perceptible. Correct pin-line correspondence.
- Phone playback QA using the actual original video frame (not portrait gallery screenshot) at zoom 1:1; native resolution and text legibility.
- Confirm dialogue remains DmitryNeural/SvetlanaNeural; no fact invention, keep 159 unique-country counting and unknown status separate from absence.
- User will submit more screenshot evidence; append new records here, don't overwrite or close prematurely.

Status: **OPEN; defects reproduced from source and screenshots, no new MP4 rendered by this audit.**
