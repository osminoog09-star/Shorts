# M1lash Voice Lab — independent free TTS benchmark, not release audio

The owner-approved production voice stays ru-RU-DmitryNeural for Dima and ru-RU-SvetlanaNeural for Sveta. Qwen3-TTS (Apache-2.0) and Chatterbox Multilingual V3 (MIT) are TEST CANDIDATES only. Model license is distinct from voice reference rights. Voice cloning requires owner's own recordings or explicit voice-holder consent. Do not copy or synthesize a third-party celebrity or a platform voice without permission.

## Candidate shortlist (research 28 October 2026)
- Edge TTS: current baseline. Specific expected IDs and word timing via existing scripts/voice_cast.py. Online, may fail.
- Qwen3-TTS-12Hz-0.6B-Base: official HF model ~2.52GB repository, model.safetensors approx 1.83GB; Russian supported, can do few-second reference voice cloning. Test only with authorized original voice. Official GitHub https://github.com/QwenLM/Qwen3-TTS and HF https://huggingface.co/Qwen/Qwen3-TTS-12Hz-0.6B-Base
- Qwen3-TTS-12Hz-1.7B-Base: larger model, benchmark after 0.6B, no assertion of real-time on 12GB without measurement.
- Chatterbox Multilingual V3: official MIT multilingual, RU/EN supported, 0.5B. Distinguish V3 model from old V2 defaults. https://github.com/resemble-ai/chatterbox
- F5-TTS weights with noncommercial licensing should NOT be production default without separate license clearance.

## Fair 10-clip test
1. Clear 10–20s narrator opening: exact spoken technical terms ("нейросеть", "агент", "компьютерное зрение").
2. Names/dates: OpenAI, NVIDIA, Антропик, 28 октября 2026.
3. 15s emotionally neutral factual exposition, one 15s suspense segment, one ironic punchline.
4. 2-voice test: separate Dima and Sveta segments, no unauthorized voice cloning.
5. 20s uninterrupted rapid speech to measure clipping, repetition, skipped words.
6. Long section test 100–150 words with correct pauses and sentence boundaries.
7. English segment only for separate EN-channel candidate (no automatic RU voice substitution).
8. Every test saves text.txt, audio.wav, aligned transcript, manifest.json, hashes, versions and GPU peak MB.
9. Automatic whisper.cpp transcription to estimate character/word error rates; manually check proper names. This is not MOS, emotion or real voice match.
10. Blind listener (files shuffled without model names) rates naturalness, pronunciation, emotion, pace, fatigue on 1–5 scale and notes concrete timestamps.

## GO/NO-GO
- Research audio is not an official Dima/Sveta release even if it sounds good. New narrator adoption requires specific owner approval and a reviewed reference voice.
- FAIL if words hallucinate/vanish, pronunciation of claims changes meaning, clip has speaker drift, musical artifacts, voice rights unclear, license unclear, or GPU memory unknown.
- Compare voice alternatives on identical text, loudness, loudness normalization and final mix. No claims of measured quality without exported audio and actual blind listening.
- Download weights in local isolated environment with pinned revision, verified source + license + file digest, scan dependencies and no token exposure; do not commit weights or voice samples to public repo.
