# Внешние скиллы (из рилса «7 бесплатных плагинов для Claude Code», 27.10)

Подключены и для Claude (`.claude/skills/` → ссылки сюда), и для Codex/GPT (`.agents/skills/` → ссылки сюда).
Копии сняты 27.10.2026 с GitHub (--depth 1). Лицензии — в `_licenses/`. Обновлять: заново скопировать папку из репо-источника.

| # | Что | Папки | Источник | Зачем нам |
|---|---|---|---|---|
| 01 | HyperFrames (HeyGen) | hyperframes, hyperframes-cli, hyperframes-registry, media-use, remotion-to-hyperframes | heygen-com/hyperframes | видео из HTML-страниц: интро, титры, motion-графика для Shorts и длинных |
| 02 | Remotion | remotion-* (12) | remotion-dev/skills | наш studio/ (EditOutro, HostLong) — лучшие практики, субтитры, рендер |
| 03 | Эмиль Ковальски | emil-* | emilkowalski/skill | анимации: кривые, тайминги, пружины; ревью анимаций |
| 04 | taste-skill | taste-skill | Leonxlnx/taste-skill | убирает «одинаковый нейросетевой» дизайн |
| 05 | impeccable | impeccable | pbakaus/impeccable | аудит: отступы, шрифты, полировка |
| 06 | frontend-design (Anthropic, офиц.) | frontend-design | anthropics/skills | типографика, визуальное направление |
| 07 | UI UX Pro Max | ui-ux-pro-max | nextlevelbuilder/ui-ux-pro-max-skill | 192 палитры, 74 пары шрифтов (есть python-скрипт поиска) |

Бонусы (+2) из рилса раздаются только через Telegram-бота автора — не ставили.
HyperFrames CLI ставится отдельно (`npx hyperframes …`, см. hyperframes-cli/SKILL.md) — только когда понадобится.
Правило: для превью/обложек/титров/аутро сначала смотри frontend-design + taste-skill, для движения — emil-animate,
для Remotion-кода — remotion-best-practices. Стиль/глубину ролика всё равно спрашиваем у Дениса (AGENTS.md).
