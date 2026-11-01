# 01.11.2026 · M1lash: actually recovered missing authentic Russian film clips, two new Shorts & proof excerpts

**FACTUAL STATUS:** New physical media artifacts verified in the active runtime. **Two PRIVATE complete Shorts + three real 16:9 movie clip proofs created; NO update made to cinematic long master REV11** (latest 286MB final master absent from current runtime; only old REV7 exists). No YouTube upload, queue readiness, schedule or publication. Copyright permissions for movie/dubbing are NOT independently established.

## Extraction source provenance — short excerpts only, no full films

Source transfer successful after RuTube options JSON 404, via OK public video pages:

| Material | Source URL | Original extracted portion | GitHub Actions run / artifact | Speech |
|---|---|---|---|---|
| Ex Machina / Ava red blackout | https://ok.ru/video/16284243071436 | 30:05–31:55 (109.011sec excerpt) | [41272309173](https://github.com/osminoog09-star/Shorts/actions/runs/41272309173) / 13070096727 | [ASR 41272501723](https://github.com/osminoog09-star/Shorts/actions/runs/41272501723): `ru 0.98135`, `ru 0.97109`, real dialogue “Он тебе не друг”, “Не верь ни единому его слову” |
| No Country driver / Anton | https://m.ok.ru/video/9392943141311 | 03:30–05:50 (140sec excerpt) | [41272692788](https://github.com/osminoog09-star/Shorts/actions/runs/41272692788) / 13070052528 | [ASR 41273154882](https://github.com/osminoog09-star/Shorts/actions/runs/41273154882): `ru 0.9638`, `ru 0.91723`, real dialogue “Пожалуйста, выйдите из машины, сэр”, “Замрите, пожалуйста” |
| No Country tracking receiver / motel | https://m.ok.ru/video/9392943141311 | 44:40–46:45 (125sec excerpt) | [41272313789](https://github.com/osminoog09-star/Shorts/actions/runs/41272313789) / 13070325354 | Exact tracker device shown at source t80–120 with **original movie audio preserved**; waveform/spectrogram show periodic tonal sound, but no subjective hearing confirmation of precise beep |
| No Country Carla Jean end | https://m.ok.ru/video/9392943141311 | 1:47:30–1:51:10 (220sec excerpt) | [41273269553](https://github.com/osminoog09-star/Shorts/actions/runs/41273269553) / 13069849250 | [ASR 41273494411](https://github.com/osminoog09-star/Shorts/actions/runs/41273494411): `ru 0.98056/0.96563/0.97984`; [word-align 41273807923](https://github.com/osminoog09-star/Shorts/actions/runs/41273807923) transcribes exact “Орёл? Или решка?” source 178.63–181.79 and “Нет. Не буду выбирать” 194.35–198.97 |

**Rejected source**: https://m.ok.ru/video/9938467687032 successfully downloaded via run 41272311134 but video was **gas station scene**, NOT driver; no use and not claimed as correct.

## Actually built deliverables in working container

The ZIP `M1lash_2_NEW_RUSSIAN_SHORTS_AND_3_FILM_PROOFS_20261101_PRIVATE.zip`, **104,719,611 bytes**, SHA256 `37672be2ffe49606f0adfb995794c7a1ded23de18fd75d3e89ce95b6d1f6e07e`, ZIP CRC `testzip()=None`, has FIVE MP4 + `manifest.json` and `READ_ME_FIRST_RU.txt`.

| File | Runtime / resolution | SHA256 | Status |
|---|---|---|---|
| `M1lash_ExMachina_Ava_AUTHENTIC_RU_MYSTERY_V2_PRIVATE_REVIEW.mp4` | 43.633sec, 1080×1920 | `71a80cf1c73ef9c04b828a7b74f05bdb706bc5c3f4afe3d3a5a97f9090d3dfa9` | TRUE RU movie dialogue, face-aware reframe, RU subtitle timings, approved vertical outro 6.6s, last words Dima reveal |
| `M1lash_Chigur_Carla_AUTHENTIC_RU_MYSTERY_V12_PRIVATE_REVIEW.mp4` | 45.8sec, 1080×1920 | `75495faec3c81bb857a5fd3ed2dad9f47a7eded6a4d2802fd903e97ef5e7dd70` | TRUE RU movie dialogue (source t178.4–214.6), word-aligned captions with Carla **refusal**, 6.6s approved outro, Dima final title only |
| `CHIGUR_DRIVER_RU_30s_EDIT_INSERT.mp4` | 30sec, 1920×1080 | `5909e06ec09c925614c61c2f2097f50d5ebd901e49f46d87aaec738e5e74fe79` | Genuine RU driver actor clip, to edit into long |
| `CHIGUR_TRACKER_ORIGINAL_BEEP_25s_EDIT_INSERT.mp4` | 25sec, 1920×1080 | `8479e9d4247ad7dd8df4885c0a188f772e890d160bbd91db2fe20bf8841f10c0` | Actual tracker with original movie sound, confirm beep manually |
| `CHIGUR_CARLA_REAL_RU_SOURCE_36s_EDIT_INSERT.mp4` | 36sec, 1920×1080 | `26613665f8a64cb052328d3ebfe0d872f1dff9b42cfe4ee24f17d3572ebde635` | Confirmed RU Carla actor speech, source for long, not an individual mystery Short |

Every one of **5 real media files** passed `ffmpeg -v error -xerror -map 0:v:0 -map 0:a:0 -f null -` and FFprobe; video contact-sheet checked. V1 Ex Machina initially had subtitles offset due PTS concat: **REJECT**. Resolved in V2 body via `[v]setpts=PTS-STARTPTS` **after** `concat` and **before** ASS overlays, plus cropped per speaking face rather than frozen center. Carla uses new dubbed source instead of user recording `1000027021.mp4` with `eng` stream metadata, to avoid claiming RU from an untested original. **Do not say old owner's Carla recording was ASR-confirmed:** only the new OK clip was confirmed.

All movie/audio source scenes are for editorial private review, not licensed by mere public webpage availability. Approval gates: manual full listening, subtitles, owner approval, distribution/reuse rights and possible copyright Content ID actions. **Do not upload/ schedule yet.**

## The long film is NOT finished

Long Chigur `07_CHIGUR_LONG_EDITORIAL_FILM_BROLL_REV11_PRIVATE.mp4` is recorded in previous HANDOFF 31.10 as existing 286,240,957-byte, 597.312sec master. The current working runtime did NOT mount that path (nor `REV8`); only older `M1lash_Chigur_Analysis_Carla_Sync_REV7_PRIVATE.mp4` exists. To avoid reverting the 14 cinematic B-roll corrections of latest REV11, we **did not write over it or pretend the 3 extracted clips are integrated**. Next editor should restore the actual REV11 master file from owner's download/private artifact, then match three replacement scene frames and insert genuine RU actor audio/sound with objective sync, without covering Dima narration. The ZIP holds all three exact sound/video proofs as separate files and technical hashes. The originally missing clips are now actually sourced; no further recording/download from owner is needed for these scenes.

Scripts in current runtime: `/mnt/data/m1lash_autosource/build_carla_ru_short.py`, `edit_machina_v3.py` and `finalize_machina.py`, generated media under `/mnt/data/m1lash_output/`. These script paths are local-run data, NOT tracked GitHub source.

