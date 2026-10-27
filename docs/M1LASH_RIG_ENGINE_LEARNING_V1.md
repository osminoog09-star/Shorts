# M1lash Rig Engine — local zero-cost character animation (prototype)

**Status: TECH DEMO / artistic NO-GO**. Script / source ZIP created in this session, not yet included in repository. Code is supplied as a downloadable artifact from the chat.

Purpose: replace flat stick-figure drawing and whole-image zoom with **articulated 2.5D sprites**. Requires separately illustrated transparent PNG body components, pivots, and hand-authored keyframes. This is not a deep learning or generative video model.

## First verified run — 2026-10-27
- Engine: Python/Pillow + ffmpeg, JSON project with characters, body parts, keyframes, pivot, layer/z-order.
- Supports cubic easing interpolation for x/y/rotation/scale and isolated sprite transforms.
- 3s 640×360@24 fps prototype generated and **decoded fully** without errors (ffprobe 3.000s).
- This prototype uses generated placeholder parts — NOT approved, polished M1lash characters. No misleading claims of cinema-quality actor animation.
- 2 expected next refinements: pivot-aware connected bone parenting rather than independent anchors; realistic eyes, mouths, hands and costumes from approved model sheet as transparent layered art.

## Next version acceptance
1. Real assets for director + employee + robot: silhouette and facial resemblance to approved character art, at least 3 expressions each, separate fingers/hand shapes.
2. Physical contact test: button depression, hand recoil, another character reacting to the event. Watchable **without sound**, no repeated pose at each second.
3. Lip sync aligned to Dmitry's precise original phrase, no 20-second cuts; preserve existing audio.
4. 15–30s animated story clip, 1080p, before/after V3 side by side. No full 14-min render until director GO.
5. Full technical MP4 decode and separate end-of-file audio checks.
6. Evidence-based update to skills with concrete failure modes; do not judge improvement from near-static metric alone.

Use existing `skills/m1lash-animation-production/SKILL.md`, `skills/m1lash-quality-improvement/SKILL.md`, `tools/m1lash_qa/preflight.py`. Never substitute a still with zoom for the user's request for actual animation.
