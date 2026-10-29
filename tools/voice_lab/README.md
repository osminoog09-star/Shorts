# M1lash Voice Lab: free TTS research and reproducible audio checks

Production is ONLY Edge ru-RU-DmitryNeural for Dima (main narrator and CTA) and ru-RU-SvetlanaNeural for Sveta. Voice lab candidates must NEVER replace these in published videos without specific owner approval. Do not clone the proprietary Dima provider voice; if a new local narrator is desired, create a lawful original voice with consent or VoiceDesign, listen and have the owner approve it.

## Researched candidates (not installed)
- Qwen3-TTS 0.6B-Base, Apache 2.0, Russian support. Model card: https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base . Official code: https://github.com/QwenLM/Qwen3-TTS . Official code includes generate_voice_clone and VoiceDesign on a separate 1.7B checkpoint. The 0.6B-Base official HF repository totals ~2.52GB; not appropriate to commit to Git or automatically install in short-lived Actions.
- Chatterbox Multilingual V3, MIT, Russian and English; explicitly select t3_model="v3", as default loads an older model. Official: https://github.com/resemble-ai/chatterbox . Manufacturer docs https://www.resemble.ai/resources/chatterbox-multilingual-v3-tts-with-embedded-watermarking-for-25-languages .
- Edge TTS baseline: already runnable and approved; outages mean NO-GO, not fallback.

## Safe preparation (local NVIDIA PC only after security gate)
1. Create fresh Python venv, record Python/CUDA/Torch versions. Do not connect any YouTube GitHub secrets. Check model weight licenses separately from Python code, verify source/revision and full SHA256 of every downloaded weight.
2. Use official Qwen package docs (never curl|bash or pip from a random fork). Review dependency lock and vulnerability scan with pip-audit first. On device with 12GB VRAM, benchmark 0.6B first and measure peak; no guarantee the 1.7B fits in the same workload.
3. Avoid trust_remote_code=True, unverified remote Python and pickle or arbitrary ComfyUI custom nodes; prefer safetensors where possible. Voice references must be your own recordings or consented.
4. Generate 10 voice samples from docs/M1LASH_TTS_BENCHMARK_20261028.md with a fixed seed where supported. Save original text, exact model hash, audio SHA, parameters, peak VRAM and timestamp.
5. After generation: python tools/voice_lab/wav_audit.py OWN_ORIGINAL_SAMPLE.wav --output work/voice_lab/report.json
6. Listen blind, rate naturalness/clarity/fatigue on 1–5, check transcription of proper names via whisper.cpp, lipsync through Rhubarb if the visual avatar uses real corresponding mouth shapes. A low WAV clipping percentage is not evidence that audio sounds good.

## VoiceDesign option
Qwen3-TTS 1.7B VoiceDesign can create a synthetic, new voice persona by descriptions. Use its generated reference for an independently approved channel character voice; do not imitate or market the voice as a named living actor or a proprietary TTS provider. A new persona is an owner decision; it does not automatically equal the approved Dima.

## Why model binaries not uploaded here
A 2.5GB model file and GPU execution are not free of storage/compute limits, require individual weights/digest verification, and are unnecessary to run the existing production Dima voice. This repository adds safe documentation and objective QA harness; no unreviewed model code has been run in CI.
