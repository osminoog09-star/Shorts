# Samsung V7 — delivery QA and honest release status (2026-10-28)

**Approved Russian title unchanged:** «Где в мире НЕ продаётся Samsung? Какие страны отказались от Galaxy в 2026 году?». Eleven-minute-thirty-eight-second long film, Russian original DmitryNeural and SvetlanaNeural. Shorts V6 and earlier full video versions were not altered; nothing published on YouTube.

## Delivered actual outputs in the authorized ChatGPT cloud runtime

- Full HD: `/mnt/data/M1lash_Samsung_V7_FullHD.mp4` — **381,461,258 bytes**, **1920×1080**, H.264 + AAC, **30 FPS**, **20,953 video frames**, container duration ~**698.454s** (11:38), **full video+audio FFmpeg -xerror decode PASS**.
- Phone: `/mnt/data/M1lash_Samsung_V7.mp4` — **56,258,901 bytes**, **1280×720**, H.264 + AAC, **30 FPS**, **20,953 frames**, duration **698.433s**, **full video+audio FFmpeg -xerror decode PASS**.
- ZIP fallback: `/mnt/data/M1lash_Samsung_V7_DOWNLOAD.zip` — contains the exact phone MP4; **ZipFile.testzip() PASS**.
- Project source ZIP: `/mnt/data/M1lash_Samsung_V7_SOURCE.zip` — **9,523,553 bytes**, **82 files**, ZIP CRC test PASS. Includes code, editable ASS subtitles, map country/ISO references, original 26 voice chapters, interactive source table, YouTube metadata, QA and three thumbnails; DOES NOT copy unlicensed font binaries.
- Corrected final exported-frame contact sheet: `Samsung_V7_FINAL/V7_FINAL_CONTACT.jpg`; three 1280×720 thumbnail candidates `thumb_a.jpg` / `thumb_b.jpg` / `thumb_c.jpg`; `fact_check_v7.html` factual evidence page.

These are verified private ChatGPT sandbox outputs, NOT public HTTPS files or committed repository binaries. No YouTube upload.

## Actually verified render and speech continuity

- 159 unique ISO2 countries in 9 regions; detailed Natural Earth country polygon matching 159/159, with Gambia and Trinidad/Tobago anchor corrections preserved from V6.
- 42 country-specific official Galaxy storefront offer records; **117 retail country statuses explicitly unclassified**, NOT assumed absent. 0 supported historical NEVER cases. Russia March 2022 shipment suspension vs retail resale; Iran February 2020 paid Galaxy Store limitation, and DPRK sanctions/2024 controversy retained as separate dated events.
- V7 adds a native-resolution **1920×1080 overlay** (rather than upscaled 960×540 captions) with 26 host identifiers, 17 factual/editorial beat cards, and **350** short synchronized caption phrases from normalized word-boundary matching. **0 unexpected single-word subtitle flashes** after merging 23 broken fragments from first assembly.
- Opaque replacement lower third: 4 sampled caption-box alpha points **255/255/255/255** so previous V6 hard-burned subtitles do not ghost. Verified in Iran scene (time ~225s) extracted from latest final video.
- Original voices were **not** resynthesized. Only gentle loudness mastering around -16 LUFS from previous ~-20 LUFS to improve listening. Real normalized speech waveform similarity between original V6 audio and mastered V7 at **100s: 0.99923**, **310s: 0.99756**, **650s: 0.99745**, zero measured lag (16kHz PCM), i.e. original voice delivery/word order preserved. AAC hashes naturally change with mastering; never claim byte-identical AAC after mixing.
- Final authoritative machine report `V7_FINAL_QA.json` status **TECHNICAL_PASS_WITH_EDITORIAL_LIMITS**, critical_errors **[]**, full HD decode **true**, mobile decode script exit **0**. Count and format verified with FFprobe. Source archive CRC test PASS. 13 final full-resolution frame samples across 2s to 690s inspected.

## Known remaining editorial limitations (block an unqualified claim of 10/10)

1. Original voice word timestamps for L20 South America and L24 conclusion remain ESTIMATED, not forced-aligned by a real speech aligner. Script/text matched, but sub-word auditory lip precision is not certified for those chapters.
2. Of 159 countries, current official Galaxy retail status is only directly source-recorded for 42. The 117 unknown values are not market absence. No reliable comprehensive NEVER list; title is a viewer's question, not a proven claim of absence.
3. V7 upgrades the graphic and caption layer while preserving the 26 original spoken chapters and most pacing/plot; it is a significant readability improvement but NOT a completely new film with bespoke acting and 159 unique vignettes.
4. No real YouTube audience data, complete certified human playback, or demonstrated viewer score. Internal editorial improvement may be ~8/10 in legibility/technical quality, but **10/10 cannot be guaranteed or truthfully asserted** from production telemetry.
5. Final V7 HD/phone are publish-review cuts, not automatically scheduled on YouTube.

## Non-repetition requirements

- Read `skills/vizavi-motion/references/geography-map-video-qa.md` and `skills/vizavi-motion/references/documentary-longform.md` before editing.
- Always render a 20s smoke test, then full output; test alpha 255 for replaced hard-burned captions and no single-word captions; check original voice waveform preservation after mastering; full decode/frame counts; enforce source-layer vs map consistency.
- Maintain a full self-contained source project, actual saved output, ZIP fallback and honest sandbox versus public HTTPS links. Do not relabel estimated timing as verified.

**Final internal verdict:** TECHNICAL PASS; editorial release REVIEW; confirmed 10/10: NOT ESTABLISHED.
