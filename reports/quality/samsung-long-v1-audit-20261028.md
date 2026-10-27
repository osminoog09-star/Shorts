# Samsung full film V1 — critical audit and V2 rebuild brief
Date: 2026-10-28 · project: M1lash / Samsung world map · approved title unchanged:
**«Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?»**
Target: Russian, 16:9, 1920×1080/30, DmitryNeural + SvetlanaNeural, >=100 unique countries (currently 159). Shorts V6 remains unchanged.

## Verified technical baseline (local finished MP4 + renderer)
- Runtime 698.433 s (11:38), 20,953 decoded video frames; 1920×1080 H.264/AAC.
- Renderer generated just **1,092 JPG stills**, expanded by variable-duration ffconcat holds into 20,953 video frames. The theoretical repeated-frame proportion is **~94.8%** (not a measurement of audience retention). This is not frame-by-frame 30 fps camera animation.
- 159 distinct country ISO2 stops (route_159.json), 26 narration chapters; 9 actual geographic regions in facts.csv.
- facts.csv has 156 'retail_status=not confirmed', 3 specific historical/restriction records (RU, IR, KP). **All 159 map_binary entries are 'unclassified'.**
- Renderer independently hardcodes CONFIRMED_RETAIL = {KR,JP,IN,SG,ID,AU,PL,DE,FR,GB,EE,ZA,MX,US,CA} and displays these in green **despite the CSV not recording country-level retail proof**. Resolve in factual database; never infer retail from Knox support or newsroom.
- Renderer hardcodes flag stripes for ~12 countries. The majority show generic country code tokens rather than their real flags.
- Subtitle snippet() slices words into equally sized beats, regardless of actual speech timing. Not aligned to word timestamps; potential phrase clipping/truncation.
- Actual voice-based scene starts: **North Korea 01:50, Iran 03:35, Russia 05:08**. The strongest hook (Russia supply/sales paradox) is buried five minutes into the film. Bring its visually supported paradox into 00:00–00:05 as a teaser; preserve its later full regional appearance and do not double-count the country.
- Repeated static title banner, dialogue panel, 26 'chapters' UI for only 9 geographic regions; large blank/ocean framing on Pacific stops.
- Positives: complete 159-country route, distinguish Russia shipments vs Iran Galaxy Store vs Korea sanctions, clean 1080p export, both Russian voices, readable broad strokes of map.

## V2 priority fixes (strict order)
**P0 — editorial truth and visual status consistency (release blocker)**
1. Keep 159-row route and region grouping. Build immutable per-country evidence entry with ISO2, market definition (official Galaxy handset retail vs support vs third-party import), exact evidence URL, observed date, evidence quote/summary, confidence, last_verified.
2. NEVER=historically proven never, not 'currently absent' or 'not found'. Halt red crosses unless absence at date supported; yellow event icon for historical restriction separate from current retail result.
3. Runtime map reads only approved facts data, not a parallel hardcoded CONFIRMED_RETAIL list. Render QA checks assert source-linked green/red and counts match registry; keep unknown neutral, never mark verified falsely. List actual verified counts after sourcing, no made-up numbers.
4. Audit official country storefronts and historical reports for featured stops (at minimum RU, IR, KP, KR, JP, CN, IN, AU, DE, GB, EE, ZA, MX, US, CA); third-party sellers do not prove Samsung direct distribution.

**P1 — true map animation, not held slides (largest impact)**
5. Animate position, zoom, rotation and map fills at EVERY output frame (30 fps); no ffconcat still-slide approach. Smooth land-to-land camera travel, inset maps for tiny islands, easing, speed-aware route; no empty oceans for 6 sec.
6. Render flag face markers accurately from per-country flag assets; main reactive 'countryball' only for 5–8 featured stories; minor stops show 20–35px pin/flag. Eyes blink, expression changes tied to supported event; keep country silhouettes readable.
7. Country status appears immediately on arrival, a specific event (shipment arrow blocked, paid app purchase locked) appears only at the pertinent narration word. No long hangs after the line.

**P2 — retention and story**
8. Keep approved publication title unchanged. Hook 0–5s: Galaxy appears in Russia despite Samsung's March 2022 shipment suspension, with a visual closed official route vs third-party import (not a total sales ban). Reach first country of full geographic pass by second sentence.
9. Distinct payoffs every 20–35s: Russia import channel vs company shipment, Iran paid Galaxy Store vs phones, genuine official shopping channels in Japan/India/US/etc, sanctions nuance for North Korea, scale differences in islands.
10. Preserve 159 unique visits in cohesive 9 regions (>=10 each); accelerate routine countries with contextual group moves, not 26 equally weighted narration panels. 159 countries can be counted visually without reading all 159 aloud. Never sacrifice route coverage to shorten edit.
11. Keep narrative varied: question -> proof -> map action -> joke -> immediate onward flight. Avoid repeatedly saying 'не подтверждено' for dozens of countries; note method once, then show neutral status unobtrusively.
12. Make finale actually answer what is and isn't established; unresolved 'never' is an honest discovery, not a made-up count.

**P3 — art/audio and accessibility**
13. 75–85% of visual area available for map; title banner disappears after opening; narration faces smaller and animated, lower-third only when someone speaks; status UI compact and legible on phones/TVs.
14. Replace one-colour dark cyan static map with region-specific color accents and shallow parallax; 3 distinct shot types (wide map, focused country, explanatory infographic/evidence screenshot). Avoid distracting excessive neon. Maintain S7-D25 family from Shorts V6.
15. Use source-linked date callouts for historical events; valid flag shapes/territories map ISO alignment; do not treat disputed territories as additional distinct countries without declared system.
16. Sync subtitles from actual word boundaries, max 1–2 short lines; no arbitrary proportional segmentation. Voice should be dynamic, dialogue lively not alternating huge monologues. Duck original licensed-safe background music under speech, add purposeful whooshes/check pings with restrained peaks.

## Proposed pacing (11–14 minutes, not fixed before WAV)
0:00–0:25 visual paradox + first fact; 0:25–1:30 South/East Asia; 1:30–3:00 South/Southeast Asia; 3:00–4:05 Pacific; 4:05–5:25 Middle East/Central Asia; 5:25–7:05 Eastern Europe/Russia; 7:05–8:20 Western Europe; 8:20–9:45 Africa; 9:45–11:15 Americas; 11:15–12:10 payoff and channel outro. Adjust to actual audio and 159 unique visits; all 9 actual regional groups must have >=10.
Opening example only (NOT an approved final rewrite):
Dmitry: «Samsung остановил поставки в Россию — но почему Galaxy там всё ещё продают?»
Svetlana: «Сначала Южная Корея. Проверим страны по очереди — и найдём, где действительно нет официальных продаж».
At end of second line South Korea already has its base status shown.

## QA / release gates
- 159 unique ISO2 stop events; repeated story callbacks don't increment; 9 contiguous region groups with >=10 distinct countries.
- Status sourced; no hardcoded contradictory colors; green/red counters derive from same verified registry with unknown excluded.
- Motion genuinely frame-by-frame across travel; sampled every 0.5 s for freeze/flicker/occlusion, with 30fps export and visual check on phone.
- Exact timing from synthesized WAV/MP3 including ending, no missing/fake lines, no sentence cut on regional boundaries, synced captions verified.
- Check all title and subtitle safe zones, flags, region names, dates and historical claim wording.
- Author QA gate target >=8/10 separately for hook, factual integrity, animation, visual design, voices/sound, subtitles, pacing, payoff. Do NOT call V2 finished just for passing codec probe.
- Compare YouTube Studio intro 30-second retention, spikes/dips, CTR after actual upload against relevant baseline; do not invent audience metrics before publication.

No overwrite of approved V1 or Shorts V6 without separate requested production update.
