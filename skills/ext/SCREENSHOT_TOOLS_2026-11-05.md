# Аудит 10 инструментов со скриншотов · 05.11.2026

Это **инвентаризация**, а не утверждение, что все десять программ запущены. Источники проверены по публичным репозиториям/документации и состоянию `osminoog09-star/Shorts`. Общий приоритет: `tasks/NOW.md` → `AGENTS.md` → `skills/m1lash-studio/SKILL.md`; никакие сторонние hooks, автопубликация или платные API этим документом не разрешены.

| На скрине | Проверенный источник | Что в M1lash | Реальный runtime |
|---|---|---|---|
| **Colibri** | https://github.com/JustVugg/colibri | `skills/ext/colibri/README.md` — pinned reference; это LLM runtime, **не генератор навыков** | Не установлен, веса не качали |
| **AutoHarness** | https://github.com/tigerless-labs/autoharness | `skills/ext/autoharness/SKILL.md` и `vendor/` (MIT), изучение learning pipeline | Автоhooks/Session capture **отключены**: сторонняя перезапись skills не разрешена |
| **Teardown** | https://github.com/lemomo-ai/lemo-opuscar | `skills/ext/lemo-opuscar/styles/teardown/STYLE.md`, стиль Exploded Teardown | Только стиль/кодовая документация |
| **Scrapling** | https://github.com/D4Vinci/Scrapling | `skills/ext/scrapling/SKILL.md`, `official/` и лицензия | Python fetchers/browser не установлены; запрет CAPTCHA/anti-bot bypass |
| **Opuscar** | https://github.com/lemomo-ai/lemo-opuscar | `skills/ext/lemo-opuscar/SKILL.md`; 66/66 STYLE.md, зарегистрировано в Studio | npm/Chromium/renders ещё не smoke-tested |
| **Glassy Dashboard V5** | на скрине только визуальный референс и текст CodeXr | Нет проверенного исходного репозитория/лицензии именно V5; не объявлять официальным skill | Не устанавливался; новый дизайн сайта отдельно согласуется |
| **Claude Watch /watch** | https://github.com/taoufik123-collab/claude-watch; MIT fork https://github.com/gAmUssA/watch-skill | `skills/ext/watch/SKILL.md` и `scripts/`; оба агента зарегистрированы | Код сохранён, текущий runtime smoke-test не подтверждён |
| **JavaRush AI Academy** | рекламный курс на скрине (16 уровней) | Не GitHub skill, не библиотека для M1lash | Не покупался/не подключался |
| **Graphify** | https://github.com/Graphify-Labs/graphify (v8; commit `59b5ab1151e031fb42e39cfc9a50bf96f2d57ae0`); Apache 2.0 | **Новое**: `skills/ext/graphify/SKILL.md` + `.claude/skills/graphify/SKILL.md` + `.agents/skills/graphify/SKILL.md`; маршрут в Studio | `graphifyy` **не установлен**, граф не создавался, hooks не активировали |
| **OpenClaw** | https://docs.openclaw.ai/install; https://github.com/openclaw/openclaw | Самостоятельная платформа агента, не отдельный skill; уже существующую M1lash Studio не заменяем | Не разворачивался; отдельная инфраструктура, доступы и безопасность потребуют решения владельца |

## Что проверено

1. По GitHub API прочитаны `AGENTS.md`, `skills/m1lash-studio/SKILL.md`, `tasks/NOW.md`; существующие `watch`, `Opuscar`, `Scrapling`, `AutoHarness`, `Colibri` и `teardown` реально открыты по файловым путям, не взяты только из слов постов Instagram.
2. Новый Graphify зарегистрирован в обеих агентских папках, в `skills/ext/` и Studio. Сохранена **запретительная конфигурация**: без `graphify install` с auto-hooks, без Cloud, без API и без изменения `AGENTS.md`.
3. Запуск Python runtime графа в текущем sandbox: `ModuleNotFoundError: No module named 'graphify'`; интернет для локального `git ls-remote` недоступен (`Could not resolve host: github.com`). Поэтому **CLI/AST/видео не тестировались** и статус `RUNTIME_NOT_INSTALLED`, а не PASS.
4. Работу над приостановленными `M1lash Мульт EP01` и `3D Coffee`, публикации, voice samples, YouTube schedule и workflow **не трогали**.

## При первом реальном запуске

- Graphify: на разрешённой машине с checkout `uv tool install graphifyy`, сверить `graphify --help`, начать с `GRAPHIFY_BACKEND=none GRAPHIFY_QUERY_LOG_DISABLE=1 graphify extract . --code-only`, записать действительную версию и результаты теста. Не включать автохуки в репозитории.
- Watch: `python3 skills/ext/watch/scripts/setup.py --json`, затем проба на легально доступном небольшом локальном MP4 с `--no-whisper`, кадры глазами и отчет.
- Opuscar: разрешённый staging runtime preflight и маленький test render, затем официальный ffmpeg-skill check/look; библиотека стилей сама по себе MP4 не создаёт.
- AutoHarness/OpenClaw: отдельное архитектурное решение, потому что захватывают сессии и/или получают расширенные права.

**Правило:** не путать «навык лежит в GitHub», «пакет установлен» и «возможность проверена в рабочем тесте».

## Claude · 05.11 вечер · вторая пачка скринов (Денис: «А плагины и тд»)
| Инструмент | Что это | Решение | Где |
|---|---|---|---|
| **Earshot** (Leonxlnx/earshot, MIT, `591fa3e`) | «Уши» для агента: словесное описание звука, `critique film.mp4`, банк SFX кодом, CPU | **ВНЕДРЁН**: навыки `earshot`, `earshot-real-sound`; шаг аудио-QA в `mini-strike.yml` (агент не слышит — теперь есть отчёт по звуку) | `skills/ext/earshot*` |
| **Claude Code Setup** (anthropics/claude-plugins-official, Apache-2.0) | официальный рекомендатор автоматизаций | **ВНЕДРЁН** навык `claude-automation-recommender` | `skills/ext/` |
| Из того же официального репо | `claude-md-improver`, `session-report`, `writing-hookify-rules`, `playground`; команды `/code-review`, `/revise-claude-md` | **ВНЕДРЕНЫ** (навыки + `.claude/commands/`) | `skills/ext/`, `.claude/commands/` |
| **Claude-mem** | память между сессиями (хуки + локальная БД) | уже в `LOCAL_PC_PLAN.md`; в облаке не нужен — у нас NOW.md/HANDOFF + память Claude | ПК |
| **Agent Reach** (Panniantong) | чтение Twitter/Reddit/YouTube/XHS через куки и обход API | **НЕ ВНЕДРЯЕМ**: противоречит AGENTS §2/§8 (не обходить антибот/капчу/логины); для поиска хватает WebSearch/Scrapling | — |
| **FreeLLMAPI** | прокси на бесплатные лимиты 34 LLM-провайдеров | **НЕ ВНЕДРЯЕМ**: риск нарушения условий провайдеров и утечки ключей; бюджет и так нулевой | — |
| **Strix** | автотест безопасности своих приложений | не для студии; можно для сайта студии на ПК позже | ПК, по запросу |
| **OpenClaw** | агент для ПК и мессенджеров | уже проверен GPT (PASS в песочнице), ставить на ПК | `LOCAL_PC_PLAN.md` |
| **Agency Agents** | набор ролей-промптов | не нужен: свои роли уже в навыках (director, animation, quality) | — |
| **n8n**, **Open WebUI** | серверы автоматизации/чата | нужен постоянный ПК/VPS; VPS платный → только на ПК | `LOCAL_PC_PLAN.md` |
| **Upscayl** | апскейл картинок/кадров, без облака | десктоп-приложение → ПК | `LOCAL_PC_PLAN.md` |
| Colibri, AutoHarness, Teardown, Scrapling, Opuscar, Graphify, Glassy Dashboard, JavaRush | первая пачка | разобраны GPT выше; Opuscar реально используется в `longform/smart-strike` | — |
