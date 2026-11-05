---
name: denis-voice-ci
description: Самостоятельный запуск личного голоса Дениса Qwen3-TTS 1.7B через GitHub Actions и owner-private Google Drive, сборка с approved Denis v7. Для Claude; без передачи приватных образцов в репозиторий.
---
# Denis voice / Claude · M1lash

**Начать:** `tasks/NOW.md` (GPT/Codex и Claude), `AGENTS.md` §3–4, `skills/m1lash-studio/SKILL.md` и **`tasks/CLAUDE_STUDIO_TRANSFER_2026-11-05.md`**. Приоритет AGENTS.md выше этого навыка.

1. Для автономной озвучки коммить только `jobs/voice/<id>.json`, затем `gh workflow run denis-voice-tts.yml --ref main -f job_path=jobs/voice/<id>.json`. Модель — строго `Qwen/Qwen3-TTS-12Hz-1.7B-Base`; speaker `denis`, voice_id `denis-qwen3tts-reference-v1`, engine `qwen3-tts-local`. Выход в private Google Drive `M1lash/_studio/voice_out/<id>/`, плюс Actions artifact (retention 1 day). После run проверять 3/3 ASR, затем владелец слушает тембр.
2. Сырой голос, текст референса, embedding, токены, закрытый MP4 в PUBLIC repo **никогда** не класть. GitHub хранит только code/skills/jobs + SHA и private Drive file IDs (`tools/voice/approved.json`, `tools/outro/approved.json`).
3. Доступ к private Drive внутри Actions уже настроен: `GDRIVE_REFRESH_TOKEN` + existing `YOUTUBE_OAUTH_CLIENT_ID`/`YOUTUBE_OAUTH_CLIENT_SECRET` либо `YT_CLIENT_ID`/`YT_CLIENT_SECRET`. Claude не получает значения секретов. `scripts/voice_private_io.py` и `scripts/fetch_outro.py` по file IDs скачивают/проверяют SHA и отказывают без подмены голоса.
4. Для movie-Shorts `movie-short.yml` использовать `title_voice_drive_id` и `title_voice_sha256` из private voice_out receipt, с `upload=false`; `scripts/fetch_voice_clip.py` проверяет sibling manifest+ASR и hash, `tools/assemble_with_outro.py` вставляет approved Denis v7. Затем `check.py`, `look.py`, owner review.
5. Известный голосовой run `42092477812` — **FAIL** после 3 сгенерированных WAV из-за отсутствия локального faster-whisper small; позже добавлен predownload PUBLIC model и SoX. Запустить новый test run, убедиться SUCCESS, только тогда давать владельцу аудио на прослушивание. CPU 1.7B ~10 минут/реплика, общий timeout 110 минут. Паузы прочих проектов и запрет YouTube без «ок» неизменны.

Полные пошаговые команды и ссылки на приватные папки: `tasks/CLAUDE_STUDIO_TRANSFER_2026-11-05.md`.

## Проверено Claude 05.11 (факты, не план)
- Run `42105048407` (`jobs/voice/mini_strike_denis.json`, 4 реплики): **SUCCESS**, ASR 4/4 = 1.0, ~35 с на короткую фразу (не 10 мин), весь job ≈ 12 мин с установкой. Длительность берётся из лога `WAV_GENERATED <id> <bytes>`: (bytes−44)/48000 с (24 кГц моно 16 бит).
- Диспетчер: `gh workflow run` использует GraphQL и из облачной сессии Claude падает 403 → запускать REST: `gh api -X POST repos/osminoog09-star/Shorts/actions/workflows/<wf>.yml/dispatches -f ref=main -f 'inputs[job_path]=jobs/voice/<id>.json'`.
- Скачать artifact из облачной сессии Claude **нельзя** (blob storage закрыт прокси). Поэтому вся работа с голосом — внутри Actions: следующий workflow берёт его `gh run download <run_id>` (permissions `actions: read`), artifact живёт 1 день. Готовый MP4 с голосом — в private Drive `voice_out` (`scripts/voice_private_io.py upload`), не в Git и не в публичный artifact.

## Второй женский голос (AGENTS §3а)
- `jobs/voice_female/<id>.json` (`voice_id: female-qwen3-voicedesign-warm-v1`, до 12 реплик, `instruct_extra` — актёрская подсказка) → push в main запускает `.github/workflows/female-voice-design.yml` (Qwen3-TTS 1.7B **VoiceDesign**, описание тембра «тёплый бархатный, 30+» + seed 151 = кастинг round 3 вариант 3, ASR ≥0.85 до 3 попыток). Синтетический тембр по описанию, не клон человека. Run `42105028306`: 4/4, ASR 0.95–1.0.
