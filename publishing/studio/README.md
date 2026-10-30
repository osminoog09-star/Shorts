# Страница «Студия M1lash»

Артефакт: https://claude.ai/artifact/Rq7ncwhpjnJHvRcrK4gktR (приватный, у Дениса).

1. Готовый ролик → запись в `publishing/queue.json` + `PUBLISH.md` рядом с исходниками (## Название / ## Описание / ## Теги / ## Закреп / ## Настройки).
2. `python3 publishing/studio/build.py` → `publishing/studio/dist/studio.html` (превью кадра встраивается через ffmpeg).
3. Claude публикует в тот же артефакт (Artifact, `url` выше). Codex страницу не публикует: он обновляет `queue.json` и пишет в `HANDOFF.md`, Claude пересобирает.
4. Пауза производства: `"paused": true` в `queue.json` (баннер на странице).
