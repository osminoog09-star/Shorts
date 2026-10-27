# Samsung full film V2 — QA and fact status (2026-10-28)

Approved title remains unchanged: **«Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?»**

**Production result in authorized cloud container** (not yet committed as large MP4):
- Video: 698.433 seconds, 20,953 video frames, real per-frame moving map with interpolated camera, 30 fps. Full HD 1920×1080 H.264/AAC and 720p/mobile.
- Previous V1 used 1,092 JPEG holds for 20,953 output frames. V2 instead computes new map/camera motion for every frame; country flag faces are built from original offline Noto Emoji artwork.
- Existing Russian DmitryNeural and SvetlanaNeural voices preserved from successful GitHub synthesis; timeline and 159-country itinerary preserved, Shorts V6 untouched.
- 159 distinct ISO2 country visits in 9 geographic groups, region sizes 12–23, no duplicate increments.
- Fully grounded status layer from facts_v2.csv: **16 current official Galaxy purchase offer examples** supported by source-specific Samsung country shopping pages; **143 current retail statuses remain unconfirmed**. Three dated/limited events (RU shipment pause 2022, IR paid Galaxy Store 2020, KP sanctions/2024 Olympic case), none represent a proven historical 'NEVER' or global countrywide 2026 ban.
- Script and atlas use the same sourced status layer, no independent set of 15 hardcoded green values. Unsupported negative categories excluded.
- Country-specific timeline subtitles use Edge TTS word metadata for 25 chapters; reconstructed Australia chapter L06 still requires a final manual subtitle check.
- Full decoder FFmpeg validation passed on HD and mobile; sample scenes checked across continents and storyline, including RU, IR, KP and conclusion. 20,953 video packets.

**Internal editorial review ratings, not YouTube audience metrics**: sourcing integrity 7/10 (not sourcing breadth), animation 7/10, flag graphics 7/10, hook/pacing 7/10, voice/mix 7/10, subtitles 7/10 (L06 limitation), technical export 8/10.

**Residual issues**: 143 unverified countries cannot be reported absent; HD has 1920×1080 output size but maps were drawn at 960×540 and enlarged, not native full-resolution map detail; scene variety/human host expression can improve; manual human voice/subtitle review needed before publication. YouTube unpublished.

**Next step**: Expand actual official country-storefront citations; build bespoke story cutaways and upgrade native-resolution map details before 8–9/10 target.
