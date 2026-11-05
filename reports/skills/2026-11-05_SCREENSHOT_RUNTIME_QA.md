# M1lash — фактическая установка и проверка инструментов со скриншотов
Дата: 2026-11-05 (Europe/Tallinn). Владелец запросил установку и проверку **каждого** из 10 элементов. Приоритет: `AGENTS.md`, `tasks/NOW.md`, Studio Skill.

## Что реально запущено

Повторяемый GitHub Actions: `.github/workflows/skills-runtime-smoke.yml`; тесты `tools/skills_runtime_smoke.py`. Запуск в **одноразовых изолированных Ubuntu Linux GitHub-hosted runners** с пустыми моделями/каналами, без передачи личного образца голоса, секретов или доступа к YouTube. Флаг `permissions: contents: read` для установочных jobs, отдельный конечный `publish-summary` c `contents: write` только для сохранения результатов в `skill-smoke-results`. Никакой установки на телефон, домашний ПК или постоянно в ChatGPT **не было**. Внешние исходники/npm/PyPI скачиваются во время CI и исчезают после завершения runner.

Подтверждённый полный run: https://github.com/osminoog09-star/Shorts/actions/runs/41976454337, HEAD `19ac426ea5cdbb59d0f472f0e517168d49c48f91`. Вычитаны результаты ветки `skill-smoke-results` и **реальные логи каждого job**: 4/4 jobs SUCCESS и `publish-summary` SUCCESS.

| Screenshot | Install/test | Фактическое заключение и ограничения |
|---|---|---|
| **Colibri** | `git clone JustVugg/colibri` → `make -C c -j2 colibri` → ELF x86-64 + `--help` | **PASS**: компилятор создал CPU-движок, бинарник отвечает. **NO MODEL**: не скачаны многогигабайтные веса (от 22GB), генерацию ответов не тестировали. |
| **AutoHarness** | Уже сохранён `skills/ext/autoharness/vendor`, 30 исходных `.py` скомпилированы; тесты `skills_guard.scan`, `is_clean`, `skill_store.apply_delta` | **CORE PASS**: обнаружена инъекция, корректно применён и отклонён неоднозначный delta. **NO HOOKS**: самообучение на живой Claude сессии и MCP не включены/не тестированы из соображений безопасности и AGENTS. |
| **Scrapling** | Установка PyPI `scrapling 0.5.1`, `Selector` + CSS | **PASS**: реальное извлечение локального HTML текста и href. **NO INTERNET SCRAPE**: сайты с anti-bot/CAPTCHA, приватные данные и внешние домены не тестировались. |
| **Claude Watch /watch** | Из репо `skills/ext/watch/`, ffmpeg+ffprobe+yt-dlp; создан 4-сек. синтетический MP4 и запущен `watch.py --no-whisper` | **PASS**: 8 реальных JPG и `report.md`. **NO ASR/REMOTE VIDEO**: Whisper модель не скачивали, скачивание YouTube не тестировали; это не гарантия доступа к любому URL. |
| **Graphify** | PyPI `graphifyy 0.9.102`, `extract` на реальном `tiny.py` | **PASS**: 2 узла и 1 связь структурного AST-графа; локально, без внешней LLM/Cloud/MCP, без install-hooks. |
| **Lemo-Opuscar** | В репо 66 indexed STYLE.md (физически 67 STYLE.md с доп. шаблоном); отдельный upstream clone `lemomo-ai/lemo-opuscar` → `plugin/skills/lemo-opuscar/scripts/setup.sh deps` | **CORE PASS**: Node 22, npm dependencies, headless Chromium и Python 3.12 окружение. **BROWSER RENDER PASS**: реальный Playwright Chromium 153.0.8010.12 открыл Canvas/HTML, сохранил два физических различных PNG (1550 и 1551 байт), проверено побайтовое различие. Не путать с ART QA или рендером готового фильма/MP4. |
| **Teardown** | Проверен `skills/ext/lemo-opuscar/styles/teardown/STYLE.md` в наборе | **STYLE PASS**: это инструкция визуального приёма, не отдельное приложение/движок; отдельной установки нет. |
| **OpenClaw** | `npm install --ignore-scripts openclaw@latest` с изолированным префиксом, версия `2026.10.10` (`Node v24.22.2`), `openclaw --help` | **CLI PASS**: пакет установлен в runner, программа отвечает. **NO GATEWAY**: postinstall отключён, daemon/onboard, токены и каналы не настраивались; не считать рабочим личным агентом. |
| **Glassy Dashboard V5** | На скрине ролик/дизайн `code.xr`, официального конкретного source + licence нет | **NON_INSTALLABLE FROM EVIDENCE**: нельзя установить произвольный интерфейс как skill. Новый дизайн сайта требует согласования; не подменяли. |
| **JavaRush AI Academy** | На скрине рекламный курс/уроки | **NOT SOFTWARE**: не skill и не программа из GitHub; подписку/курс не покупали. |

## Установку CLI ≠ полноценное применение

Colibri без веса модели не умеет генерировать; AutoHarness без Claude hooks не захватывает сессии и не учится; OpenClaw без Gateway/каналов не работает как агент; Opuscar с браузером может рендерить, но художественное качество требует отдельного фактического MP4/ART QA; Scrapling на локальной странице не доказывает работы на защищённых сайтах. Это честные границы успешных тестов.

## Как повторить

В GitHub `osminoog09-star/Shorts` → Actions → **Third-party skill runtime smoke (isolated)** → `Run workflow`. В результате появляется ветка `skill-smoke-results`, `reports/skills/runtime_latest.json`; она хранит точный `run_id`, SHA, статусы каждого job. Выбрать run из JSON и просмотреть job logs. Скрипты не имеют доступа к приватным авторским материалам. Для постоянной установки в локальном Claude Code / ПК Дениса потребуется отдельная машина и учёт безопасности, без автоматической установки любых секретов или хуков.

## Реальные ошибки и решения

1. Ubuntu runner 26.04 без FFmpeg/ffprobe — добавлен `apt-get install ffmpeg`.
2. PyPI yt-dlp лежит в отдельной `venv/bin`, отсутствовал в PATH — добавлен в `$GITHUB_PATH`.
3. Официальный Opuscar setup живёт в `plugin/skills/lemo-opuscar/scripts/setup.sh`, а не в корне `scripts/setup.sh` — исправлен.
4. 67 физических `STYLE.md` вместо 66 из-за дополнительной папки-шаблона — проверка по **66 уникальным ссылкам в styles/README.md**, все пути обязаны существовать.
5. Скрины из соцсетей нельзя приравнивать к установочному пакету, публичная успешная компиляция к качеству кино, а зелёный CI к наличию постоянного агента.

**Без изменений:** `AGENTS.md`, паузы `M1lash Мульт EP01` и 3D Coffee, YouTube видео, очереди, графики публикаций, личные voice-файлы, бюджеты/платные API.
