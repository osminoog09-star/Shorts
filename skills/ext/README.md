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

## Из шортсов @mcdenil_ (30.10.2026)

| # | Что | Папки | Источник | Зачем нам |
|---|---|---|---|---|
| 08 | /watch | watch | taoufik123-collab/claude-watch | «смотрит» видео: кадр на каждую склейку, темп (склеек/мин), разбор хука 0–10 с, расшифровка. Для разбора чужих и своих Shorts. Нужны ffmpeg, yt-dlp; для Whisper — `GROQ_API_KEY` или `OPENAI_API_KEY` в `~/.config/watch/.env`, без ключа — `--no-whisper` (только субтитры YouTube). В облачной сессии YouTube не качается — только загруженные файлы |
| 09 | Humanizer | humanizer | blader/humanizer | убирает признаки «нейросетевого» текста: описания, сценарии, посты |
| 10 | Marketing Skills (6 из 52) | mkt-social, mkt-video, mkt-content-strategy, mkt-copywriting, mkt-marketing-ideas, mkt-marketing-psychology | coreyhaines31/marketingskills | заголовки, хуки, контент-план, психология удержания. Остальные 46 (SaaS/продажи) не ставили |

Правило: тексты для зрителя (названия, описания, сценарии) после написания прогонять через humanizer; разбор референса — через watch, выводы — в m1lash-reference-analysis.

### Дополнение 30.10: Marketing Skills — все 52
Решение Дениса 30.10: поставить весь пакет coreyhaines31/marketingskills, а не 6. Папки `mkt-*` (имя скила = `mkt-` + оригинальное). Внутри ссылки вида «see copywriting» означают `mkt-copywriting`. Пакет заточен под SaaS — для канала в первую очередь: mkt-social, mkt-video, mkt-content-strategy, mkt-copywriting, mkt-copy-editing, mkt-marketing-ideas, mkt-marketing-psychology, mkt-ab-testing, mkt-image, mkt-influencer-marketing, mkt-launch.

### Программы из тех же шортсов (ставятся на ПК, не скилы)
PersonaLive, OpenHands, MuMuAINovel — скрипты в `scripts/pc/`, строки в `LOCAL_PC_PLAN.md`. Remotion уже в `studio/` и `remotion-*`.
