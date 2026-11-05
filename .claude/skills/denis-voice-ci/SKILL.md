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
