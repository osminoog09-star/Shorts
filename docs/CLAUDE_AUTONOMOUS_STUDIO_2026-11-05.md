# Передача M1lash Studio → Claude · 05.11.2026

**Цель:** Claude самостоятельно получает из GitHub рабочие инструкции, запускает озвучку Дениса, скачивает утверждённую концовку v7, собирает видео и выполняет QA. Повторно просить GPT переносить файлы/голос не требуется. `AGENTS.md` важнее этого документа, решения о публикации остаются у владельца. Старые паузы `PAUSED_BY_OWNER` не снимать.

## Начать именно с этого

```bash
git pull --ff-only origin main
sed -n '1,160p' AGENTS.md
sed -n '1,140p' tasks/NOW.md
cat skills/m1lash-studio/references/voice-runtime-preflight.md
cat tools/outro/approved.json
cat tools/voice/approved.json
```

Все актуальные навыки, скрипты, журнал ошибок, workflows и текущие задачи живут в `osminoog09-star/Shorts` (ветка `main`). Специально для Claude есть `.claude/skills/`; для Codex/GPT `.agents/skills/`. Упомянутые в `AGENTS.md` правила важнее сторонних skill. Инвентаризация дополнительных внешних навыков: `skills/ext/SCREENSHOT_TOOLS_2026-11-05.md` и результаты их реальных частичных smoke: `skills/ext/RUNTIME_SMOKE_2026-11-05.md`.

## Приватные файлы — НЕ в публичном Git

Денис **не должен** потерять контроль над голосом, embedding или авторскими аудиофайлами. Для кода через Git нужны только **SHA256 и приватные Drive file IDs**, а реальные WAV/текст образца, параметры, private outputs и два approved MP4 остаются в принадлежащем владельцу закрытом Google Drive. Нельзя класть в публичные Git history, LFS, релизы, issues, артефакты со свободным доступом, логи или PR.

**Drive (проверены приватная загрузка и metadata владельца):**

| Назначение | Папка | ID |
|---|---|---|
| Корень студии | `M1lash` | `1leE1IaWgApfD1nN-oa7xWHlV9XwVnX-R` |
| Вертикальная и горизонтальная утверждённые концовки | `M1lash/_studio/outro/` | `1_oGUuXdE3hTbDzx6IBRZxnjSbzyWGY5M` |
| Образец личного голоса, ref_text и параметры Qwen3-TTS | `M1lash/_studio/voice/` | `1dHg7yRbXkL6xooW2kb-FqV8FInKUUhC5` |
| Результаты синтеза (по отдельным job ID) | `M1lash/_studio/voice_out/` | `1TqKuZOZoPczLHChe_lFv89OKkhuSLZyP` |
| Записи фильмов (ДРУГАЯ папка) | `M1lash — фильмы для будущих Shorts` | `1ANvcXlUj0wBv1CG5U0bBQGdH-32OyaAi` |

Проверенные ID/хеши концовок: `tools/outro/approved.json`, образцов: `tools/voice/approved.json`. **Не копировать** хеши вручную в код, всегда читать соответствующий manifest. Изменившийся SHA означает NO-GO без fallback.

### Как Claude получает доступ к Google Drive в GitHub Actions

Существующий механизм — приватный OAuth владельца, **не публичный share-link**. На странице GitHub `osminoog09-star/Shorts → Settings → Secrets and variables → Actions → Repository secrets` нужны:

- `GDRIVE_REFRESH_TOKEN` — refresh token именно того Google-аккаунта, которому принадлежат приватные файлы, со scope `https://www.googleapis.com/auth/drive` или подходящим `drive.file`, выданный **тем же** OAuth Client.
- `YOUTUBE_OAUTH_CLIENT_ID` и `YOUTUBE_OAUTH_CLIENT_SECRET` — принадлежащая этому refresh token пара Client ID/Secret; существующая альтернатива в скриптах — `YT_CLIENT_ID` + `YT_CLIENT_SECRET`. Секреты не дублировать без нужды.

OAuth-проверка происходит **в GitHub Actions раннере** через `https://oauth2.googleapis.com/token`; в логах не выводить refresh/access token, Client secret, HTTP body Google. GitHub connection у Claude должен иметь разрешение на чтение/запись файлов репо и запуск workflows. Секреты Claude **не читает и не получает в чат**: workflow получает их из `secrets.*`. Если Drive возвращает 401/403, проверить совпадение аккаунта, OAuth Client, scope и права на ID private files; не обходить закрытый доступ открытием «доступ всем по ссылке».

Проверка доступа (на доверенном runner с разрешёнными секретами):

```bash
python scripts/fetch_outro.py
python scripts/fetch_outro.py --verify-only
python scripts/voice_private_io.py fetch --dest "$RUNNER_TEMP/m1lash-private-ref"
python scripts/voice_private_io.py verify --dest "$RUNNER_TEMP/m1lash-private-ref"
```

Первая пара создаёт `media/outro/m1lash_outro_denis_v7_vertical.mp4` и `...horizontal.mp4` (gitignore). Вторая — только во временном приватном каталоге runner, с SHA256 трёх private assets. **Никакого старого Димы.** Блокировка = прекращение работы, а не автоматическая смена голоса.

### Проверенная концовка CI — задача tasks/gpt_outro_in_ci.md

**GitHub Actions `movie-short.yml` push-only smoke run 42090558386 SUCCESS**, job 127467140997, проверил реальный fetch обоих MP4 + SHA256, синтетическую 3.2с сцену и `tools/assemble_with_outro.py`. `check.py` 12/12, 0 FAIL, `look.py` реальные 6 кадров просмотрены, full FFmpeg decode PASS. Не было upload на YouTube. Этот тест **не доказывает полный кино-Shorts/ASR**. `drive-folder-intake.yml` тоже включает fetch gate. У workflow `movie-short.yml` обычный запуск требует отдельное проверенное Denis title voice и SHA; `upload=false` по умолчанию.

### Qwen3-TTS для Claude

Workflow: `.github/workflows/denis-voice-tts.yml` (`workflow_dispatch`); скрипты `scripts/voice_private_io.py`, `scripts/denis_voice_tts.py`; тест `jobs/voice/test_claude.json` (3 фразы). Публичная модель `Qwen/Qwen3-TTS-12Hz-1.7B-Base` (ICL, CPU, bfloat16, eager) без платных API. `faster-whisper small` проверяет **реальный распознанный текст**, не тембр; тембр слушает владелец. Sample/reference/embedding никогда не входят в cache публичных моделей. WAV + `manifest.json` + SHA + ASR и Drive receipts в приватной папке `voice_out/<job_id>/`; Actions artifact retention **1 сутки** и требует GitHub-доступ.

Создать новый `jobs/voice/<id>.json`: `job_id` совпадает с именем файла, `speaker=denis`, `voice_id=denis-qwen3tts-reference-v1`, `utterances=[{id,text,rate}]` с 1–8 фразами (5–220 символов, `0.85≤rate≤1.15`). Commit, затем:

```bash
gh workflow run denis-voice-tts.yml -f job_path=jobs/voice/test_claude.json
gh run list --workflow denis-voice-tts.yml --limit 5
gh run view <run_id> --log-failed
```

**Важный честный статус 05.11:** run `42092477812` FAILURE на шаге ASR, *после* реального синтеза 3/3 WAV (примерно по 10 минут каждая). Секреты и 1.7B Qwen работали; причина: Whisper small пытался загрузить веса после тяжёлого синтеза, модель недоступна и workflow fail-closed без публикации. Исправления: `scripts/denis_voice_tts.py` commit `eabe582` загружает заранее подготовленный локальный CTranslate2 snapshot; `.github/workflows/denis-voice-tts.yml` commit `9d24c99` перед Qwen скачивает публичный `Systran/faster-whisper-small` и проверяет `model.bin`. Повторный полный **ASR PASS и прослушивание** не подтверждены, пока новый run не завершится успешно. Не называть их успешными без логов.

GitHub-hosted CPU может синтезировать **медленно**: в реальном тесте 3 фразы заняли около 31 минуты. `timeout-minutes: 110` — верхний предел workflow, не обещанный срок. Модель Qwen и ASR публичные и кэшируются через `actions/cache`, приватные образцы не кэшировать. Если workflow завершился ошибкой — смотреть конкретную секцию, применять `voice-runtime-preflight.md`, записывать в NOW; **никаких fallback на Диму/edge-tts и никаких платных API**.

### Подключение результата к ролику

1. Попросить workflow синтезировать текст и вручную/скриптом выбрать прошедший ASR WAV из `voice_out/<job_id>/`. Проверить SHA в `manifest.json` и удостовериться, что `speaker=denis` и `owner_hearing=pending`.
2. Сначала `python scripts/fetch_outro.py` и SHA; затем `python tools/assemble_with_outro.py body.mp4 -o private_review.mp4 --title <approved-voice.wav>` для кино-Shorts (или `--horizontal` для длинного). Официальные `check.py` / `look.py` запускать **на окончательном MP4**, глазами проверить контакты и отсутствие чёрных вспышек, пустых голосовых хвостов, титров до разрешённого времени.
3. В `movie-short.yml` указан input `title_voice_drive_id` + `title_voice_sha256`: это **отдельный owner-private файл**, не URL для публичного чтения. Для test кино-Shorts `upload=false`, публикация только после решения владельца; `AGENTS.md` §6 главнее.

### Обязательный порядок и взаимодействие агентов

- Read `tasks/NOW.md` → `AGENTS.md` → Studio skill → relevant project skill/queue/HANDOFF. Уже сделанное не перезаписывать. После каждого завершённого шага — маленький commit, обновить NOW и HANDOFF. В GitHub commit можно передать фактические версии, точные пути и ссылки на runs; **не вставлять private голосовые данные**.
- Claude может сам запускать `workflow_dispatch` после разрешения GitHub Actions (нет необходимости ждать GPT). Не использовать tools, требующие покупки, и не активировать PAUSED мультпроекты.
- Никакие действия внутри этого файла не разрешают YouTube upload, публичную публикацию, заполнение `publish_at` или изменение утверждённой 6.6-секундной концовки.

## Следующий обязательный технический шаг

1. Проверить в GitHub Actions run после фикса `Systran/faster-whisper-small`, получить 3/3 `asr_similarity≥0.80`. Реальная оценка тембра только по прослушиванию владельца.
2. Удостовериться в 3 WAV, `manifest.json`, owner-private Drive `voice_out/test_claude` receipt и artifact retention 1 день.
3. После успешного теста убрать временный push-триггер из voice workflow (оставить **только workflow_dispatch**), затем обновить `skills/m1lash-studio/SKILL.md` раздел «Голос Дениса для Claude», `reports/learning/journal.json` и HANDOFF с реальными IDs/QA.
4. Для текущего kino_007 в NOW остаётся отдельный видео-QA и утверждение владельца. Не смешивать воспроизведение голоса с разрешением публиковать.

**Вывод:** код, модель, конфигурация, fetch/outro, handoff и правила передаются Claude **через GitHub**; приватный голос остаётся в owner-private Drive, доступен Claude только через Actions с существующими секретами. Это разделяет автономность и безопасность.
