# Samsung full — mandatory 21+ minute release compliance, 2026-10-28

**Approved title unchanged:** «Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?»

**Binding rule confirmed** from main branch AGENTS.md, STRATEGY.md, CODEX_NOTICE.md, and documentary-longform skill as of 2026-10-28:
- Any NEW complete long-form M1lash video MUST be >= 21:00 = 1260 seconds; recommended 23–28 minutes.
- No padding by silence, repeating shots or content, slow motion, meaningless sound/music.
- All new release candidates must pass `python scripts/qa/longform_duration_gate.py VIDEO.mp4` AND content/geography QA. Pilot cuts and Shorts are exempt only if they are not presented as full long-form releases.
- Primary narrator `ru-RU-DmitryNeural`; supporting second narrator `ru-RU-SvetlanaNeural`. Russian-only.
- Do not retroactively edit already published videos; V7 is unpublished review cut.

## Current status — HARD NO-GO

V7 exported files are 11:38.454 (698.454 seconds, verified by local ffprobe, 1920x1080 H.264 + AAC). It FAILS the new minimum by **561.546 seconds (9:21.546)**, even if its codec/frames pass. Do not label as 'long-form release ready' and do not upload under this label. Retain V7 as immutable visual/audio reference and project base. Prior claims of 7–10/10 quality do not override duration gate.

## Content-led rebuild into true long-form, target 24:00–26:00

The gap to target 24:00 from current measured duration is ~741.546 seconds, but do not add precisely this much mechanically; calculate duration only from accepted final voiced scenes. Start from the approved 159 unique-country, 9-region route and current verified factual ledger. Do not invent unknown historical NEVER claims. Expand evidence across under-researched countries, source official country-specific Samsung buy pages and specific historical reportage, 2 independent sources for factual interpretations.

Story arcs to research and build as *new content*, not repeats:
1. **Direct storefront versus resale** — visually demonstrate proof hierarchy with 3-5 country examples (official purchase CTA, local pricing, actual independent dealer, third-party imports). Difference between existence of phone and direct distribution.
2. **South Korea + Japan + India** — product/channel differences and dated milestones only when directly supported by primary sources.
3. **China + South-East Asia** — market presence versus sales volume, model differences, several verified country store pages; evidence not inferred from neighbors.
4. **Pacific microstates** — where documentation is sparse, show real detailed inset and explain limits; do not say absence; distribute across geographically contiguous regional stops.
5. **Iran** — dated paid-app restrictions do not imply handset ban; direct document reference and illustrative store-flow animation.
6. **Russia** — March 2022 suspension versus later independent import; date-specific documented import/range, exact source and counter semantics.
7. **Europe + Nordics** — 6+ distinct official local sites and why supported model/warranty/product offers vary (only supported documented facts); short humorous reversals without stereotypes.
8. **Africa** — verified concrete official offers in selected countries; separate evidence from blanket assumptions.
9. **Americas** — verified product prices/country sites and market channels; preserve Peru/Bolivia etc timing by actual WordBoundary, not estimates.
10. **Final answer** — separate verified YES, confirmed current NO (if any evidence), restrictions, and unknown; historical NEVER only if literal lifetime evidence exists; clear answer and CTA to subscribe/comment.

## P0 QC before any new complete MP4

- The spoken-script and visual cue sheet is rebuilt from new exact TTS word boundaries, especially missing L20 and L24. No estimated timelines in *new* release.
- 159 code/ISO3 and actual 10m polygons validated; flags on land after camera transform; source-specific status with dates; no store-vs-sanctions conflation.
- 23–28 mins requires enough **original, sourced** dialogue for real speaking rate; never reuse V7's video on loop or stretch clips. Avoid endless 'unknown' cards; each region should give payoffs and differentiated visuals.
- Full native 1080 drawing and typography, no ghost or one-word flashing subtitle lines, no incorrect historical text; graphical safety zones and presenter presence.
- Duration gate run on final Full HD *actual* MP4, with machine-readable report plus full decoder, frame count, audio/visual human review; no preemptive 10/10 declaration.
- Two Shorts funnels remain separate from 21+ constraint and follow channel slots.

**Status:** research and editorial rebuild required; V8 >=21:00 has NOT been rendered or released. Work here is plan/gate correction only.

## ADDENDUM: verified V8 full-length delivery on 2026-10-28 (supersedes prior pre-production NO-GO status for V8 only)

The earlier paragraphs in this same document apply to **V7** and the V8 pre-production state, NOT this newly rendered V8. The current **V8 FullHD was assembled and tested successfully**:
- **Final 21+ FullHD**: `/mnt/data/M1lash_Samsung_Full_21plus_V8.mp4`, exact `ffprobe` duration **1477.317 s** = 24 min 37.317 sec, 1920×1080, H.264 30fps, AAC audio (audio ~1477.317 s, video ~1477.233 s), container 690,024,043 bytes. File exists in the authorized cloud model runtime, **not uploaded to GitHub**.
- Passed repository-equivalent `scripts/qa/longform_duration_gate.py`: `pass:true, minimum_seconds:1260.0, issues:[]`. Full FFmpeg video+audio decoder `-xerror` completed **exit 0**, see cloud `/mnt/data/Samsung_V8_21plus/qa/full_decode_exit.txt` and `longform_21_gate.json`.
- **43 original, sequential chapters**: 26 pre-existing V7 narrated scenes plus **17 entirely new, factual storyboarded, Edge-TTS original-voice sections**, geographically inserted throughout the same 159-country first pass. Added section IDs **E01-E11, E13, E15-E19**. The other 3 planned chapters (E00, E12, E14) were **explicitly deferred** due to Edge TTS `NoAudioReceived` errors and are not replaced by silence/looping/fake voices. No time stretch, slowed video or meaningless padding to reach threshold.
- New research source: `jobs/tts/samsung_v8_new_research.json` contains **20 researched paragraphs** and 28 unique original declared URLs. Actually included 17 stories, drawing on 25 unique direct sources recorded in cloud `sources_v8.txt`. Not every claim independently fact-checked against two independent institutions; author editorial review remains before publication.
- Russian narration preserves `ru-RU-DmitryNeural` and `ru-RU-SvetlanaNeural`, not re-voiced with other voice engines. Real `WordBoundary` metadata for newly inserted lines; inherited V7 L20/L24 estimated cue limitations remain.
- 159 unique country entries in nine groups, original 42 confirmed national Samsung Galaxy storefront offers; 117 retail statuses **unknown, never assumed absent**. No historical NEVER invented.
- Twelve preview frames were actually extracted from final FullHD MP4 at 00:10 through 24:20, including map scenes, Asia, Russia/Iran region, Europe, Africa, America and world finale. Contact sheet `/mnt/data/Samsung_V8_21plus/qa/contact_v8_21plus.jpg`.
- Editable source project ZIP `/mnt/data/M1lash_Samsung_V8_EDITABLE_PROJECT.zip` packed 255 files (~18.5 MB) including new script, 60 original 1920×1080 infographic stills, original and new voice MP3, word-boundary metadata, Natural Earth data, source URLs, video assembly scripts, cue audit and chapters. Zip CRC `testzip() PASS`. Private cloud artifact path is not an external public download URL.

**Current status V8: duration + technical decode PASS; editorial human release review still pending; no YouTube publication or guaranteed artistic 10/10.**
