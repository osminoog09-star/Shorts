---
name: watch
description: Разбор видео по фактическим кадрам, сменам сцен, монтажу, хуку 0–10 секунд и речи. Для GPT/Codex и Claude в M1lash.
argument-hint: "<video-url-or-path> [цель анализа]"
license: MIT
repository: https://github.com/gAmUssA/watch-skill
user-invocable: true
---

# /watch — просмотр видео с доказательствами

Это совместимый Python-навык для агентов M1lash, а не встроенная кнопка воспроизведения в ChatGPT. Публичный URL или локальный MP4 → yt-dlp (если URL) → ffmpeg-кадры на склейках и ритм → субтитры/локальная транскрипция → `report.md` с таймкодами. Кадры затем **сам агент открывает и смотрит**, анализирует звуковую дорожку и пишет выводы. Скрипт сам не заменяет зрение и слух агента.

## Правила M1lash (приоритет)

- Сначала `tasks/NOW.md` (GPT/Codex), `AGENTS.md`, `skills/m1lash-studio/SKILL.md` и `skills/m1lash-reference-analysis/references/watch-shorts-playbook.md`. Если конфликт — `AGENTS.md` важнее.
- Использовать для честного анализа чужих референсов и своих MP4; не копировать чужие кадры/музыку/голос/сценарий и не менять публикации/очередь. Анализ ≠ разрешение рендера или заливки.
- **Ноль платных API без разрешения владельца.** По умолчанию локальный whisper.cpp, если уже установлен; иначе `--no-whisper` и нативные субтитры. Не пересылать приватные аудио/голос владельца в Groq/OpenAI. Не устанавливать через скрипт крупные модели/зависимости без необходимости.
- Ни один `SOURCE_BLOCKED` не превращать в «просмотрено». Нельзя обходить DRM, антибот, капчу и логин. Превью/название/автотекст ≠ просмотр настоящих кадров. Obsidian auto-ingest для проекта отключён; временные файлы не удалять без необходимости.

## Запуск

1. Проверить среду: `python3 skills/ext/watch/scripts/setup.py --json`; `ffmpeg` и `ffprobe` обязательны, `yt-dlp` нужен для URL. Отсутствующая локальная модель Whisper не мешает извлечению кадров.
2. Выполнить безопасно с отдельными аргументами, **никогда не собирать shell-команду из произвольного URL и не использовать `shell=True`**. При наборе команды в терминале — одинарные кавычки вокруг URL или локального пути:

```bash
python3 skills/ext/watch/scripts/watch.py '/path/to/video.mp4' \
  --intent 'разобрать монтаж, хук, движения, звук и приёмы для M1lash' \
  --no-whisper --out-dir '/tmp/m1lash-watch-demo'
```

3. Для доступной локальной whisper.cpp модели можно опустить `--no-whisper`. Для хука запустить отдельно `--start 0 --end 10`; для длинного видео по частям; `--resolution 1024` полезно для титров, `--max-frames 40` уменьшает выборку. Бюджет до 100 кадров / 2 fps, на 21-минутном ролике один проход не даёт полного охвата.
4. Проверить файлы в `--out-dir`: реальные JPG на склейках, плотные кадры 0–10с, `report.md`, метрики, аудио/субтитры если доступны. **Открыть изображения**, при наличии звука — прослушать или явно ограничить статус анализа. Встроенные маркеры `<!-- pending ... -->` заполнить только подтверждёнными наблюдениями.
5. Сформировать `reports/research/references/<id>/reference_audit.md` и `reference_lessons.json` по `skills/m1lash-reference-analysis/SKILL.md`. Статус: `PIXELS_AND_AUDIO_VERIFIED`, `FRAMES_ONLY`, `TRANSCRIPT_ONLY`, `METADATA_ONLY` или `SOURCE_BLOCKED`; указывать источники, таймкоды, уверенность и ограничения. Своё видео прогнать через официальный `check.py`/`look.py` отдельно.

Параметры: `--start`, `--end`, `--max-frames`, `--resolution`, `--fps`, `--intent`, `--out-dir`, `--no-whisper`, `--no-scene-change`, `--no-hook-microscope`.

## Происхождение

Точный оригинал из видео: https://github.com/taoufik123-collab/claude-watch.
Скрипты, тесты и лицензия взяты из поддерживаемого MIT-fork https://github.com/gAmUssA/watch-skill, commit `f713a4941ca06052608801452869f4e0da522ae5`, с исправлениями ffmpeg 7+/9, равномерной выборки длинных видео, `--no-whisper`, локального ASR и shell/cleanup hardening. Адаптация к M1lash — только этот SKILL.md и студийный playbook. `LICENSE`, `AUTHORS.md`, `FORK.md` прилагаются.
