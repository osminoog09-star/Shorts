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

## Из рилсов про скилы для монтажа (01.11.2026)

| # | Что | Папки | Источник | Зачем нам |
|---|---|---|---|---|
| 11 | FFmpeg Skill | ffmpeg-skill | kajisho5/ffmpeg-skill (MIT, коммит 1ce2c18) | 42 офлайн-инструмента ffmpeg: `check.py` (формат под Shorts/YouTube), `look.py` (контакт-лист), `cropdetect.py`, `join.py`, `caption.py`, `loudness.py`. Плюс `references/gotchas.md` — грабли concat/DTS/субтитров. Обязательная проверка — `skills/m1lash-studio` §2а |

Скопированы только `SKILL.md`, `scripts/`, `references/`, `templates/`, `mcp/` (2 МБ из 47; доки, сайт, демо и тесты не нужны). Скрипты без сети (только stdlib + ffmpeg 6.1+), проверено 01.11. Запуск — `python3 …/scripts/<tool>.py` **без** `-I`.
Не ставили: ghost-editor (под говорящую голову, ведущего мы убрали), claude-shorts (дублирует `movie-short`; взята только идея рубрики выбора сцены → m1lash-studio §2б), OpenMontage (AGPL, тяжёлый — в `LOCAL_PC_PLAN.md`), Open Higgsfield (интерфейс к платным API).

## Подборка «10 трендовых GitHub-репозиториев для Claude» (11.11.2026)

Код прочитан до установки (клон в карантин, ничего не запускали). Поставлены только текстовые скилы, без хуков и без `npm/pip install`.

| # | Что | Папки | Источник | Зачем нам |
|---|---|---|---|---|
| 12 | Diagram Design | diagram-design | cathrynlavery/diagram-design (MIT, коммит f2496ac) | 45 типов схем и графиков (воронка, таймлайн, Sankey, сравнения, дерево) как HTML+SVG: инфографика для объясняющих Shorts через HyperFrames, схемы для сайта студии и отчётов. Сети нет, кроме ссылки на Google Fonts. PNG-экспорт — `scripts/export_png.py` через уже стоящий playwright. При первом запуске спросит про стиль: брать токены бренда M1lash из `site/studio/` |
| 13 | Ponytail | ponytail, ponytail-review | DietrichGebert/ponytail (MIT, коммит 96608e0) | «Ленивый сеньор»: минимальная правка без лишних абстракций, ревью кода. Для скриптов конвейера и сайта студии. Взяты только 2 SKILL.md; хуки (автоактивация, статус-строка, трекер токенов) **не ставили** |
| 09 | Humanizer — обновлён 3.1.0 → 4.0.0 | humanizer | blader/humanizer | только `SKILL.md`, местных правок в старой версии не было |

Уже стояли (из той же подборки): humanizer (09), impeccable (05), ui-ux-pro-max (07), scrapling (только справка, runtime не ставили). У impeccable на GitHub версия новее — обновлять отдельно, со сверкой.
Не ставили:
- **REA** (morluto/rea) — реверс-инжиниринг приложений и бинарников: MCP-сервер на Node, репо 155 МБ, Ghidra/binwalk/jadx. Каналу не нужен.
- **Hallmark** (Nutlope/hallmark) — дублирует taste-skill, impeccable, frontend-design, ui-ux-pro-max; генерация картинок только через платный Together AI (`TOGETHER_API_KEY`), есть установщик хуков.
- **«Onyx» = senlindesign/taste-skill** — подпись и ссылка на картинке не совпадают. По ссылке — скил разбора дизайна сайта по URL (460 звёзд, **без лицензии**, конфликт имени с нашим taste-skill). Настоящий Onyx (onyx-dot-app/onyx) — платформа чата с базами знаний на Docker, не скил.
- **Last 30 Days** (mvanhorn/last30days-skill) — дублирует Agent Reach (Reddit/X/YouTube уже читаем). Мастер настройки сам ставит CLI и просит читать куки браузера; TikTok/Instagram — только с платным ScrapeCreators.
