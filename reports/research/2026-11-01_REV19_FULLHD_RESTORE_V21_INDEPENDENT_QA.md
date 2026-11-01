# 01.11.2026 — M1lash REV19 Full HD restoration and Shorts V20/V21 independent QA

**Status: PRIVATE_REVIEW, NOT READY, NO UPLOAD OR SCHEDULE.**

## Real local outputs
- `M1lash_Chigur_REV19_1080p_PRIVATE_REVIEW.mp4` — 1920×1080 H264/AAC, 681.349333s, 408595504 bytes, SHA256 `fd228f1b7d330aeadba412b1f06be404ea1022c2de81510e178acfb27431a4ef`.
- `M1lash_6_MOVIE_SHORTS_RU_MASTERED_V21_PRIVATE_REVIEW_20261101.zip` — 6 × 1080×1920 H264/AAC (001/005 V21, the rest V20), 170122911 bytes, ZIP SHA256 `fcffb5b271ea4ed2454e9657d516689afd0bf87c870ed42181dfacf8f20abe94`. All 6 individual SHA hashes match ZIP manifest.
- Local auxiliary package `M1lash_REV19_FULLHD_QA_EVIDENCE_20261101.zip` contains audit, contacts for 28 art intervals + 6 Shorts, FFmpeg metadata, hashes and 112 edge samples; never commit copyrighted movie frames to this repository.

## What changed
REV19 is a **1080p picture restoration, NOT a new CGI redesign**. We used actual Full HD REV14 as the base, borrowed only the 28 art intervals (276s) from the available 720p REV18 mobile preview, scaled that art with Lanczos. The untouched film portions retain the Full HD original picture. The separate artist still used vector-like static diagrams; do not claim compliance with AGENTS §10 / `visuals-by-code.md`. Reusable command `scripts/qa/restore_long_from_preview.py` is committed.

## Independent checks
- All **7 final MP4s fully decoded** video+audio via `ffmpeg -xerror`: PASS, empty stderr.
- REV14 / REV19 AAC bitstream identical: `SHA256=a46d57c67d5f7761865f7178c4e288435e7c70556657aee3390aacbc77a79526`.
- 28 graphics contact-frame samples checked visually. 112 boundary samples (four around each interval), simple green/black pixel detectors: 0/112 green-frame flags, 0/112 black-frame flags. Not a full frame-by-frame creative review.
- Shorts integrated LUFS / true peak dBTP: 001 -16.0/-0.2, 002 -19.3/-1.9, 003 -17.9/-1.8, 004 -18.4/-0.9, 005 -18.7/-1.6, 006 -21.8/-1.4. **No audio normalization** per AGENTS §4/§12: approved outro remains untouched; 001 and 004 peak margins need a dedicated film-body mastering review. 006 noticeably quiet and has low-motion ocean around 36–41s.
- Repo's exact `check.py` and `look.py` binaries were **not executed in this isolated environment**. We ran independent ffprobe/decode/EBU meters/contact/edge checks instead; the official §12 gate remains pending.

## OPEN, do NOT mark as ready
1. Long art scenes remain schematic repeated `talk/deal/paths/coin` graphics, not approved premium HTML/Three.js/HyperFrames 3D. Needs human creative pass and a proper 3D rebuild.
2. No complete **human listening** pass of seven files; the two older Carla long segments remain unverified for RU actual voice, plus proof of audible movie cues.
3. Content licensing / Content ID risks are outstanding despite user's risk acceptance.
4. `BAD TIMES — Imael Angel` was NOT embedded: for only Ava and Carla Shorts, attach through official YouTube Shorts Audio Library if available and allowed (or separate sync license), preserve untouched 6.6s outro. No ripped MP3.
5. Official `check.py`/`look.py`, final human review and private upload without date are not done. No `queue.ready`, no public release.

**Lesson:** successful decode/bit-identical audio and a 1080p container do not mean cinematic quality, human listening QA, or release rights. Never use the word 'all finished' until all remaining gates actually pass.
