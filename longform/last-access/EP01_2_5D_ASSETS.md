# «Последний допуск»: 2.5D production asset index

**Date:** 2026-10-27 (Europe/Tallinn). **Episode:** 01 «Лишний пассажир». **Master prompt/shotlist:** [EP01_2_5D_30_SHOT_PROMPTS.md](EP01_2_5D_30_SHOT_PROMPTS.md). **Style:** mature illustrated graphic novel based on original S3-D25 (not the bright sticker style). **Status:** reference key art / opening-stills created; complete 13:30 2.5D episode NOT created.

## Individual canonical references (separate PNG assets)

| Name | Image | Generation ID |
|---|---|---|
| MARA (captain) | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225435_84fb1a87-b3ed-4bd5-812a-df176ff0cb12.png) | `84fb1a87-b3ed-4bd5-812a-df176ff0cb12` |
| LEV (engineer) | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225436_0231b846-007c-4882-8c68-d1995e1f196e.png) | `0231b846-007c-4882-8c68-d1995e1f196e` |
| KERN (non-humanoid emblem) | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225436_700f7618-06f1-40f8-af14-06e9c2cd98dc.png) | `700f7618-06f1-40f8-af14-06e9c2cd98dc` |
| POROG (rescue ship) | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225435_0fb26f8e-bcad-4674-a7e4-af22c637b4a2.png) | `0fb26f8e-bcad-4674-a7e4-af22c637b4a2` |

## Four separate opening scene illustrations (16:9)

These are reference-conditioned using the canonical MARA image, not generated blindly. They are **static images**; motion exists only once a video renderer composes shots with movement, masking and atmosphere.

| Shot | Name | Image | Generation ID |
|---|---|---|---|
| 01 | Mara faces emergency bulkhead P‑4 | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225616_beb822ca-f5fe-4391-aaa2-393f6f92c7ec.png) | `beb822ca-f5fe-4391-aaa2-393f6f92c7ec` |
| 02 | KERN says Mara died 18 hours earlier | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225615_db8d015c-dd86-4f9a-bb22-42036d094d94.png) | `db8d015c-dd86-4f9a-bb22-42036d094d94` |
| 03 | Three hands pressed to locked glass | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225615_818926b1-09be-4b72-859d-8d6a91d3a703.png) | `818926b1-09be-4b72-859d-8d6a91d3a703` |
| 04 | Bioscanner/registry discrepancy | [PNG](https://d8j0ntlcm91z4.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/hf_20261026_225615_acbaa80a-4ca7-43c4-99d1-28a2f6527155.png) | `acbaa80a-4ca7-43c4-99d1-28a2f6527155` |

## Video proof: 70-second illustrated opening scene (27.10.2026)

- Rendered through GitHub Actions `Last Access 2.5D illustrated opening preview`, verified successful [run #40419021359](https://github.com/osminoog09-star/Shorts/actions/runs/40419021359).
- [Download the 70s preview artifact](https://github.com/osminoog09-star/Shorts/actions/runs/40419021359/artifacts/12696521513) (ZIP with MP4, Russian subtitle SRT, ffprobe and QA stills; artifact retention 30 days).
- The preview uses the four newly generated original stills, eight motivated moving crops, a separate drifting atmosphere layer, **new shortened Cyrillic subtitle timing**, exact canon 311/312 HUD, and the first 70 seconds of the prior confirmed Russian audio mix.
- Technical QA: 70.000s, H.264, 1280×720, 24fps, AAC 44.1kHz; FFmpeg decode PASS and sampled frames at 3, 14, 35, 53, 67 seconds reviewed. Subtitles corrected from the first export, becoming appreciably smaller, and character close-ups remain readable.
- **Not the final animation**. Actor mouth/eye movement, independently extracted foregrounds/backgrounds, full 120+ scene frames, final character continuity audits and human full-length listening are still pending. Keep watermark `ПРОБА 2.5D`. Do **not publish as Episode 1**; no YouTube or Metricool actions were taken.
- The renderer stays reproducible as `render_2_5D_opening_preview.sh` plus GitHub workflow; its external media URLs should be checked if rerunning months later.

## QA and continuity

- **Canon:** The sensor registers **312 living signals**, ship registry lists **311 confirmed records**. KERN has *no human face*; its icon is abstract. MARA 38, asymmetric black bob, steel-gray eyes, dark teal/navy uniform with one copper shoulder stripe. The remote engineer LEV 29 wears olive-gray utility clothing.
- More images are needed for front/side character turnarounds, in-between pose changes, foreground/background alpha masks and 26 remaining story beats. Do not claim the entire episode is complete.
- Previous 3D pilot [13:30 MP4](https://d2ol7oe51mr4n9.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/1c018130-74ee-47d9-bcf3-65917c6371e3.mp4) is an **audio reference/previous visual draft**. It must not be uploaded as if it is the new 2.5D product.
- All character art and shot art should undergo consistency check before locking as canon. Never include AI-generated text in on-screen numbers; composite digits and Cyrillic in editor.
- The preview render pipeline under this directory is **a camera/atmospheric motion test over four stills**, not full multi-plane 2.5D character animation. Further layer splitting is required before full production.
