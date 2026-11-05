# CLAUDE HANDOFF · 05.11.2026 · автономный голос Дениса + утверждённая концовка

**Читать первым после `git pull --ff-only`:** `tasks/NOW.md` → `AGENTS.md` §3–4, §8, §12 → `skills/m1lash-studio/SKILL.md` («Голос Дениса для Claude») → `skills/m1lash-studio/references/voice-runtime-preflight.md`. У владельца прямое решение: Claude должен работать **без ручной передачи медиа от GPT**. Всё программное и воспроизводимое хранится в этом GitHub; приватные бинарные reference/embedding и два outro существуют в owner-only Drive с `Drive file IDs + SHA256` в GitHub. **Никаких токенов, приватных референсов, embeddings и MP4 в PUBLIC git**, даже при реплике владельца «всё в Git» — это указатели + code/skills/CI, а не открытая публикация его голоса.

## Что уже передано в GitHub и работает

1. `tools/outro/approved.json` — ONLY Denis v7 voice10, `sha256` и Drive IDs для двух утверждённых версий. Private Google Drive: `M1lash/_studio/outro/` (folder `1_oGUuXdE3hTbDzx6IBRZxnjSbzyWGY5M`).
2. `scripts/fetch_outro.py`: на Actions по `GDRIVE_REFRESH_TOKEN` забирает **ОБА** v7 и проверяет SHA256 до atomic install в игнорируемые `media/outro/m1lash_outro_denis_v7_*.mp4`. При ошибке — `NO-GO`, не старый Дима. Подключён в `.github/workflows/movie-short.yml` и `drive-folder-intake.yml`. Проверка: реальный run `42090558386` **SUCCESS**, synthetic body → assemble 0 проблем → `check.py` 0 FAIL → `look.jpg` визуально проверен. Позднее run `42094845451` тоже SUCCESS. Это **тест склейки**, не кино-Short с русской ASR.
3. `tools/voice/approved.json`: voice_id `denis-qwen3tts-reference-v1`, model `Qwen/Qwen3-TTS-12Hz-1.7B-Base`, SHA256/Drive IDs **трёх** private ref files; в Git ни текста образца, ни WAV, ни embedding. `scripts/voice_private_io.py` — скачивание и загрузка результатов, hash gating; `scripts/denis_voice_tts.py` — local Qwen3 ICL+rate+faster-whisper ASR; `scripts/fetch_voice_clip.py` — принимает только SHA+Drive ID результата именно из `voice_out` с manifest/ASR; `jobs/voice/test_claude.json` — три утверждённые тестовые реплики; `.github/workflows/denis-voice-tts.yml` — голосовой workflow с `workflow_dispatch`, CPU и публичным cache весов.
4. Private Drive folder для входа: `M1lash/_studio/voice/` (`1dHg7yRbXkL6xooW2kb-FqV8FInKUUhC5`). Для результатов: `M1lash/_studio/voice_out/` (`1TqKuZOZoPczLHChe_lFv89OKkhuSLZyP`). Загружаются результаты `voice_out/<job_id>/`; artifacts хранятся 1 день. Не переносить их в публичный Git.

## Как Claude сам получает доступ к Google Drive

**Лучший путь — GitHub Actions**, не прямая передача личного OAuth токена в Claude. Из владельческого GitHub Secrets уже заданы `GDRIVE_REFRESH_TOKEN` плюс OAuth client pair (`YOUTUBE_OAUTH_CLIENT_ID` / `YOUTUBE_OAUTH_CLIENT_SECRET` или `YT_CLIENT_ID` / `YT_CLIENT_SECRET`). **Их значения никому не выписывать и не коммитить**. `scripts/fetch_outro.py`, `voice_private_io.py` и `fetch_voice_clip.py` самостоятельно обновляют access token через Google OAuth, читают private Drive file IDs и SHA; Claude управляет задачами только коммитами и `workflow_dispatch`. Drive owner folder никому публично не открывать. Владелец при необходимости может убедиться, что Secrets существуют: GitHub репозиторий → Settings → Secrets and variables → Actions → Repository secrets; наличие проверяется визуально, значения скрыты. Если Google отвечает 403/invalid_grant, прекратить без fallback; уведомить владельца, что требуется восстановить Drive/OAuth доступ, **не просить присылать токен в чат**. Данный Drive доступ **уже доказан** реальным CI outro run 42090558386; повторная авторизация для Claude при исправном токене не нужна.

Для ручного доступа через GitHub CLI (Claude на локальной авторизованной машине) использовать `gh auth login` для GitHub и workflow. Сам доступ к Drive по `GDRIVE_REFRESH_TOKEN` есть только внутри Actions. **Не использовать OAuth из личной среды Claude без отдельного безопасного secret manager**, не выводить access token в логи.

## Запуск автономного голоса

1. Подготовить `jobs/voice/<job_id>.json`: `job_id, speaker:"denis", voice_id:"denis-qwen3tts-reference-v1", utterances:[{id,text,rate}]`; 1–8 фраз, 5–220 символов, rate 0.85–1.15. Ровно этот JSON (без private source) коммитить. Для контроля — `jobs/voice/test_claude.json` (три фразы).
2. Actions → **Denis Voice · Qwen3-TTS 1.7B Base ICL** → Run workflow → `job_path=jobs/voice/<job_id>.json`, либо `gh workflow run denis-voice-tts.yml --ref main -f job_path=jobs/voice/<job_id>.json`.
3. Проверить статус: `gh run list --workflow denis-voice-tts.yml --limit 5`, затем `gh run view RUN_ID --log-failed`. `SUCCESS` только после 3/3 ASR >=0.80 и private Drive upload. Artifact `denis-voice-<job_id>` → `gh run download RUN_ID -n denis-voice-<job_id>` (один день). Основная долговременная копия — Drive `voice_out/<job_id>/`, ссылка в `drive_receipt.json`/логе. **Публиковать ничего не нужно**.
4. В `manifest.json` требуются `speaker=denis`, `voice_id`, `engine=qwen3-tts-local`, `rate`, `source_file`, `sha256`, `asr_text`, `asr_similarity`, `owner_hearing=pending`. Пользователь слушает, только он оценивает тембр. ASR проверяет текст, не узнавание тембра.
5. Для фильма после получения Drive output WAV+SHA: `movie-short.yml` input `title_voice_drive_id` + `title_voice_sha256`, private `url` исходника, id/start/end/title/film и `upload=false`. Workflow проверяет voice_out manifest и загружает **Denis v7 outro** через общий fetch; сборка `tools/assemble_with_outro.py`; финальный `check.py` и `look.py`; без публикации. После готового MP4 нужен реальный owner review; только отдельное «ок» разрешает upload/schedule.

## Актуальный статус и неудачи: не выдавать за SUCCESS

- Real voice run `42092477812`: **FAIL** после того, как Qwen3-TTS 1.7B CPU сгенерировал все 3 WAV примерно за 30 минут: ошибка `BLOCKED: faster-whisper small model unavailable` в ASR. Логи без утечки reference. Не считать WAV из failed runner сохранёнными: artifact/Drive upload не сработали.
- **Исправление после этого run:** workflow добавил предварительный `snapshot_download('Systran/faster-whisper-small')`, передаёт `WHISPER_LOCAL_PATH` в генератор, а также установку `sox`. Следующий `test_claude` run должен повторить 3/3 синтез+ASR+private upload. Не считать фикс проверенным до нового реального `SUCCESS`.
- У Actions CPU без GPU ~10 минут/фразу плюс dependencies/cache; `timeout-minutes: 110`, возможны download/OOM/ASR ошибки, **без резервного голоса**. Не обещать «быстро».
- Movie outro P0 CI уже работает; не тратить время на повторное копирование v7 из личной Library, в Drive оба файла на месте и approved SHA. PAUSED мультпроекты, YouTube/queue не менять.

## Быстрый технический preflight для Claude

```bash
git pull --ff-only origin main
python -m unittest discover -s scripts/qa -p 'test_fetch_outro.py'
python -m unittest discover -s scripts/qa -p 'test_voice_private.py'
python -m unittest discover -s scripts/qa -p 'test_fetch_voice_clip.py'
python -m py_compile scripts/denis_voice_tts.py scripts/voice_private_io.py scripts/fetch_outro.py
gh workflow run denis-voice-tts.yml --ref main -f job_path=jobs/voice/test_claude.json
```

**Следующий шаг:** повторить реальный трёхфразовый voice CI, получить `SUCCESS` с ASR evidence, выдать владельцу приватную Drive ссылку на прослушивание; потом удалить временный `push` trigger voice-test и оставить `workflow_dispatch` (не менять owner review gate). Если учётные данные Drive откажут — STOP с точным HTTP-кодом, никакие токены не публиковать.
