# M1lash Studio 2.0 — architecture and evidence-led research
Research 28 October 2026. Sources linked below. Proposed tools are NOT assumed installed or independently security-certified.

## Non-negotiable channel rules
- All NEW longform releases >=21:00 (1260s), preferably 23–28 minutes of substance, with 4–5 story acts and no meaningless padding. This rule is on MAIN; SHORTS, internal previews and trailers stay separate. Any older references to 10–15 minutes are obsolete.
- RU main author and CTA: Dima (Edge ru-RU-DmitryNeural); Sveta (ru-RU-SvetlanaNeural) is optional second speaker. No automatic voice fallback, no reuse of historical Liam or Piper outros. Alternate TTS remains TEST ONLY until approved with known lawful voice provenance.
- A real full-length release requires script -> sources -> voice -> animatic -> original scene assets -> render -> technical QA -> visual/auditory QA -> rights QA -> owner approval. Passing a decoder is not artistic success.
- Publishing/Metricool existing queue unchanged; no self-authorized uploads or automatic release from tool evaluation.

## Studio architecture
1. Editorial & news: idea -> 2 independent sources per important factual claim -> concise evidence ledger with dates -> claim classification (verified / attributed / disputed / opinion).
2. Scriptwriting: long 21–28m into 4–5 acts with real content and retention hooks, Shorts self-contained beginning/payoff; each narrative event tied to visual.
3. Prompt and style lab: immutable S1–S9 official variants; new independent X01–X10 EXPERIMENTAL styles in prompts/m1lash/registry.json. Existing channel style tests remain unchanged. No named living artist imitation, no copying protected characters.
4. Voice lab: canonical Edge Dima/Sveta; candidate Qwen3-TTS 0.6B/1.7B (Russian, Apache-2.0) and Chatterbox Multilingual V3 (RU/EN, MIT). Do not acquire proprietary voice clones or bypass original voice licensing. Model installation staged off-main with fixed versions, safety review and no YouTube tokens. TTS audio manifests include engine/model hash, speaker, segment, text, sample rate, true audio hash, alignment and provenance.
5. Visual engine: Remotion reusable compositor (existing studio); Motion Canvas TypeScript explanatory vector motion; Blender original physical models/rigs for character anatomy and engineering; OpenToonz/Krita manual 2D; Three.js existing engineering scenes. AI video (Wan2.2/ComfyUI) only for specially justified short B-roll, after node/weights license and model scans. No "prompt alone gives reliable rigged actor" assumption.
6. Post: FFmpeg concat/mix/loudnorm, Rhubarb timing for animation and whisper.cpp for subtitle/voice transcription validation; independent listening and spelling of names/dates.
7. QA and reproducibility: media preflight, PySceneDetect shots, reference evidence, QA JSON defect log, source-to-video hash, representative previews, human per-scene and last-30-sec inspection; artistic/technical >=8/10 separately. 21min duration gate is separate from 8/10 gate.
8. Publishing/learning: reviewed private YouTube upload only with explicit approval, immutable file digest, confirmed real-time slot; analytics at comparable ages 48h/7d, retention/AVD/CTR/subscriber conversion; original metadata and thumbnail A/B, update style experiment only with data.

## Production recipes
- TECH_LONG 23–28m: 00:00–02:30 highest-stakes promise, 02:30–08:00 context and first demonstration, 08:00–14:00 mechanism and evidence, 14:00–21:00 deeper test/contradiction, 21:00–25:00 answer/consequences/CTA. Timing adapts to actual audio and story; never stretch.
- NEWS_SHORT: 35–60 sec vertical, one central conflict, 2+ sources, large readable unique illustrations, Dima narration and tested outro. No fake "AI escaped" headlines.
- ANIMATED_SKETCH: approve a hero 3 views, 6 expressions, 4 poses, visible hand-object contact and phonetic lip sync BEFORE rendering whole story. The 44s S1 V4 pilot's 3/10 anatomy shows why.
- MOVIE_SHORT: rights/claim and license gate, original commentary; hiding a film name from title does not prevent Content ID or license requirements.
- EN: separate script quality check and allowed voice; do not extrapolate English US audience merely from English metadata.

## Infrastructure and safety
- Use individual, removable venv/project environments, immutable dependencies and locks, SHA256. Never pip curl | sh, don't install unknown ComfyUI custom nodes, don't trust_remote_code on unreviewed models, prefer safetensors, restrict model and video decoding to low-privilege workers with no credentials/network when possible.
- GitHub Action staging has already run safe PySceneDetect 0.7.2 scan + wheelhouse install + real MP4 scene test. This only supports that package at that date, not broad security of other tools.
- On 12GB VRAM: small voice models FIRST; run only one GPU workload at a time and test peak memory. 21min video is rendered per scene/act and streamed/composed, not as a monolithic expensive GPU render.
- Do not check any large model weights, licensed audio, personal voice references, private keys, or copyrighted cinema clips into public GitHub.
- Two tiers: GitHub Actions for tests/CPU renders, user's future local NVIDIA GPU machine for heavy TTS, Blender, generative B-roll. Free GitHub minutes and storage are not unlimited.

## Timeline by dependency rather than promises
A. Policy and QA 21min rule, voice NO-GO, safe package staging (already in repo).
B. Sample 15–30sec TTS model benchmark with owner-approved reference(s), no production voice switch until judged.
C. Reusable 3-view character + full phonetic lip sync, 30–60s pilot >=8/10 before expanding.
D. 23–28min complete long documentary via original voice/scripts and per-scene rendering, then independent full-video audit.
E. Publishing safety, real analytics and weekly learning loop.

## Official references
- Qwen code and license: https://github.com/QwenLM/Qwen3-TTS ; model: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base
- Chatterbox code/license: https://github.com/resemble-ai/chatterbox ; publisher: https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages
- Motion Canvas: https://github.com/motion-canvas/motion-canvas
- Blender: https://www.blender.org/ ; Krita commercial license: https://krita.org/en/about/license/
- YouTube monetization/originality: https://support.google.com/youtube/answer/1311392
- YouTube synthetic disclosure changes: https://support.google.com/youtube/blog/424874071/updates-to-ai-content-disclosure-and-labels
- Internal style and policy: skills/vizavi-motion/references/style-library.md , AGENTS.md , STRATEGY.md
