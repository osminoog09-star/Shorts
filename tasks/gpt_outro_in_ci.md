# GPT: концовка Дениса недоступна автоматике (аудит Claude 05.11)

Факт: `tools/assemble_with_outro.py` правильно требует `media/outro/m1lash_outro_denis_v7_*.mp4` (SHA в `tools/outro/approved.json`) и без неё даёт BLOCKED. Файлы лежат только в твоей Library. **Ни один workflow их не получает** → `movie-short.yml` и будущий конвейер «папка Drive → Short» в GitHub Actions не могут собрать готовый ролик. Последние запуски `movie-short.yml` (31.10) — failure.

Сделать:
1. Загрузить обе концовки v7 в приватное место Drive владельца (не в публичный Git, AGENTS §3–4), отдельно от папки фильмов (`M1lash/_studio/outro/`).
2. Общий шаг для workflows: скачать по `GDRIVE_REFRESH_TOKEN` в `media/outro/`, сверить SHA256 с `approved.json`, при несовпадении — стоп. Подключить в `movie-short.yml` и в конвейер папки Drive. `media/outro/m1lash_outro_denis_*` — в `.gitignore`.
3. Тест: `movie-short.yml` на коротком тестовом клипе → SUCCESS, `assemble_with_outro.py` без BLOCKED, check/look.
4. HANDOFF + урок.

## Исполнено GPT 05.11.2026 · VERIFIED CI smoke

- Исходные owner-approved **Denis v7 voice10** взяты из private ChatGPT Library по `library_file_id`, SHA256 ДО загрузки совпал с `tools/outro/approved.json`: vertical `2e514186940d130e6aea6aa5171b59ba7691d5cfe14fb329d65a8d12184a6b60`, horizontal `70b066b067cec45dbaaae91ef39ee79543ac9c396d0d1bd896885b1511867dae`. Отличающиеся файлы не принимались; Дима не использовался.
- В private Drive создано `M1lash/_studio/outro/`, folder `1_oGUuXdE3hTbDzx6IBRZxnjSbzyWGY5M`, file IDs `1DBSoGii58WlD4MwHK8myRwWZLo-OhHig` и `1sXYrDMWjIPDJjFNp6E_H27EK8pusjita` (metadata owner-only). Бинарников в публичном Git **нет**.
- `scripts/fetch_outro.py`: Google OAuth refresh, скачивание ровно двух pinned IDs, обе SHA в staging и только затем atomic install в `media/outro/`; отсутствие credential/403/hash mismatch → понятный nonzero NO-GO, никакого fallback. `scripts/qa/test_fetch_outro.py`: 6/6 PASS. `.gitignore` защищает `media/outro/m1lash_outro_denis_*`.
- Шаг подключён к `.github/workflows/movie-short.yml` и `.github/workflows/drive-folder-intake.yml`. Последний **реально** run `42089126542` SUCCESS; movie-short.py исправлен с legacy v3 на approved v7 SHA.
- `movie-short.yml` **реально** run `42090558386` SUCCESS: synthetic **3.2с** источник, `assemble_with_outro.py` 9.8с финальное тестовое видео с Denis v7 без BLOCKED, audio lag=0ms и check problems=0; `skills/ext/ffmpeg-skill/scripts/check.py` **12 проверок, 0 FAIL**, `look.py` создал 6 кадров; **контакт-лист визуально открыт** (цветовой тестовый источник + 4 кадра Denis outro), full decode PASS. CI artifact `13445011690` (не содержит private MP4/voice), срок 2 дня. Первый run 42089064375 failed из-за синтетической loudness на пороге −16.0 LUFS, исправили только mastering синтетического тела до −13.5, approved концовку не трогали.
- **Граница проверки:** verified CI outro fetch/assembly smoke — не утверждение полноценной сборки кино с ASR/title и не одобрение публикации. Movie-short build по `workflow_dispatch` остаётся отдельно owner-controlled, `upload=false` по умолчанию. YouTube не трогали.

HANDOFF.md и урок Studio обновлены; Claude может читать эти же пути. Реальный run SUCCESS подтверждён, задача `gpt_outro_in_ci.md` закрыта **для инфраструктуры концовок**.
