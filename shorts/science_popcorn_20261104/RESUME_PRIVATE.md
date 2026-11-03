# Попкорн M1lash — точное продолжение после VOICE_BLOCKED
Дата: 04.11.2026. **Один Short, другие проекты не затрагивать.**

## Что уже реально есть

- `shorts/science_popcorn_20261104/spec.json`: научно сверенные 6 сцен, 12 реплик, approved voice = Denis/Qwen3.
- `film.html` + `render_visual.py`: изолированные авторские HTML/SVG кадры.
- `/Youtube/M1lash_Popcorn_SILENT_VISUAL_DRAFT_v2.mp4` в личной Library: 36.666667с, 1080×1920/30, 1100 кадров, SHA256 `9a64c97ca8efc0aa2853ff8c09b0bbffd8b4c8103877c4e17bfc2a68664efa10`; FFmpeg decode и контакт по всей длине выполнены. **Только графика, звук отсутствует, титры предварительные.**
- `/Youtube/M1lash_Popcorn_Private_Assembly_Pack_20261104.zip` в личной Library: частный образец Дениса, точно утверждённая v3-концовка, немой preview и `manifest.json`, SHA256 архива `0d6001aaf451c40a43a76e1194eb733415b7d4505f784743698f7b722792ddda`. Архив **НИКОГДА** не коммитить в Git.
- `synthesize_denis_private.py` и `build_private_master.py` созданы, 7 offline regression tests успешны (Actions run `41735884366`), **реальные 12 реплик ещё не генерировались**.

## Приватная сборка, когда локально появятся веса Qwen и faster-whisper

Нужны Python 3.12, CPU torch, `qwen-tts==0.1.1`, `faster-whisper`, `numpy`, `soundfile`, Chromium, Playwright, FFmpeg. Никаких платных TTS, внешней отправки голосового образца или Edge/Azure. Интернет только один раз для установки открытых библиотек/весов, если одобрены ресурсы; дальнейшая речь синтезируется **локально/offline**. Веса не входят в архив.

Сначала извлечь PRIVATE ZIP **ВНЕ** публичного checkout, например `/private/m1lash-popcorn/`. Не передавать пути `private/` и `denis_reference.wav` в GitHub Actions или в публичные отчёты.

Используя локально скачанный snapshot `Qwen/Qwen3-TTS-12Hz-0.6B-Base` и локальный `faster-whisper` CTranslate2:

```bash
export ORT_DISABLE_TELEMETRY=1 HF_HUB_DISABLE_TELEMETRY=1
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 DO_NOT_TRACK=1

python shorts/science_popcorn_20261104/synthesize_denis_private.py \
  --private-reference /private/m1lash-popcorn/private/denis_reference.wav \
  --local-model /private/model-cache/Qwen3-TTS-12Hz-0.6B-Base-snapshot \
  --whisper-model /private/model-cache/faster-whisper-small-snapshot \
  --private-output /private/m1lash-popcorn/generated-voice

python shorts/science_popcorn_20261104/build_private_master.py \
  --private-voice /private/m1lash-popcorn/generated-voice \
  --approved-outro /private/m1lash-popcorn/private/approved_denis_v3_vertical.mp4 \
  --private-output /private/m1lash-popcorn/private-final
```

Это примеры папок, не существующие на данном хосте. **Не запускать** пока фактические модельные веса/образец не доступны приватно. Скрипт синтеза строго проверяет модель/Whisper offline; каждая реплика сохраняется с SHA-256 и провенансом, повторный запуск проверяет сохранённые куски и не перезаписывает их без проверки.

## Обязательные выходные gates

- True word timestamps получены из настоящей озвучки, **все 12 lines = Denis**; различие с ожидаемой фразой по ASR проходит независимое сравнение, но ударения/окончания всё равно прослушать.
- **Полный перерендер** кадров с настоящей речью: предварительный silent MP4 не склеивать напрямую с новой дорожкой и не выдавать прежние captions за synced.
- Использовать только `tools/assemble_with_outro.py`, в котором одобренная v3 vertical концовка проверяется SHA256 `1bd5aa58…`.
- `skills/ext/ffmpeg-skill/scripts/check.py`, `look.py`, full decode `ffmpeg -xerror` **на конечном MP4**; осмотреть контакт и прослушать автора, не нормализовать концовку. После технического QA показать владельцу. На YouTube/публикацию — отдельно по AGENTS§6.
- Голос, референс, ZIP и конечный private MP4 **не помещать в публичный GitHub**. Чужие Shorts, особенно `ai_vacuum_20261104`, не трогать.

**Текущий статус:** VISUAL_COMPLETE / PRIVATE_VOICE_BLOCKED / NOT_READY / NO_YOUTUBE_UPLOAD.
Отчёт: `reports/research/2026-11-03_POPCORN_SINGLE_SHORT_PRODUCTION.md`. Живой чекпоинт: `tasks/NOW.md`.
