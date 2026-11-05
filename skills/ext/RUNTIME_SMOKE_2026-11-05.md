# M1lash · Runtime smoke 10 инструментов · 05.11.2026

**Итог:** проверка исполняемых компонентов проведена в изолированной удалённой Higgsfield Linux sandbox, а не на ПК владельца, не внутри ChatGPT и не в GitHub Actions. Изначальный список: `skills/ext/SCREENSHOT_TOOLS_2026-11-05.md`. Все операции без платных API, токенов M1lash/YouTube, логина, перехвата пользовательских сессий, автоматического изменения AGENTS.md, публикаций и запуска открытых серверов. Паузы `M1lash Мульт EP01`/3D Coffee не менялись. Данные ниже — фактически выполненные действия, а не план.

## Проверенная среда

- Временная sandbox: `/home/user/m1lash-tool-audit-20261105` (может быть удалена/истечь: **это не постоянная установка на пользовательском ПК**).
- Python 3.12.10, отдельный `.venv` через `uv`; Node 22.22.1 для Opuscar; отдельный Node 24.16.0 для OpenClaw, скачан из официального nodejs.org с SHA256-проверкой.
- `ffmpeg`, `ffprobe`, Node/npm, git, Playwright Chromium (software SwiftShader). **Ограничение:** GPU отсутствует.
- Клонированы источники по зафиксированным commit: Graphify `59b5ab1`, Scrapling `3a4bb5b`, Watch MIT fork `f713a49`, AutoHarness `ca4247b`, Colibri `0a5504a`, Lemo-Opuscar `bebbbe1`, OpenClaw `46943d5` (репозиторий; runtime отдельно из версии npm).
- Исполнение сторонних автоhooks из upstream запрещено; `Graphify install`, `openclaw onboard`, `autoharness` hooks и публикация не выполнялись.

## Фактический результат

| Инструмент со скрина | Установка/запуск | Проверенный тест | Итог и предел |
|---|---|---|---|
| **Graphify** | `graphifyy==0.9.102` в Python venv | `graphify extract sample-code --code-only --no-viz --no-cluster`; граф **5 узлов/7 связей**, JSON создан; `graphify query 'Camera render'` выдал реальные `EXTRACTED` связи | **PASS: локальный AST-граф+поиск.** Не тестировались платные/семантические backend и Cloud |
| **Scrapling** | `scrapling==0.5.1` + `scrapling[fetchers]`, `curl-cffi==0.17.0` | `Selector` выбирает русский текст из HTML; `Fetcher.get()` получил с локального `127.0.0.1` HTTP 200, верный заголовок | **PASS: парсинг и HTTP fetch**. Stealth/антибот обход и реальные чужие сайты не тестировались и не разрешаются |
| **Claude Watch /watch** | MIT fork source `f713a49`; `yt-dlp==2026.10.26` + ffmpeg доступны | Самостоятельно создан 12.000s H264/AAC тестовый MP4; `watch.py --no-whisper --max-frames 12` exit 0, **12 настоящих JPG** и `report.md` | **PASS: frames/video pipeline**. `setup.py --json`: `needs_local_whisper`; ASR не проверен, транскрипта нет |
| **AutoHarness** | Source импортирован в venv через отдельный `.pth` (не global); plugin v0.5.3 | `PYTHONPATH=src pytest -q tests/test_config.py tests/test_atomic.py` → **15 passed in 0.16s** | **PASS: выбранные unit-тесты**. Capture/hooks, самогенерация skills и модификация сессий **не активированы**, end-to-end не заявлен |
| **Colibri** | `uv pip install -e repos/colibri`, `colibri-engine==2.1.0`; upstream `c/coli` | `coli --version` → 2.1.0, `coli --help` → exit 0; `coli doctor` без модели ожидаемо сообщает «no model directory» | **PARTIAL: CLI установлен.** Не скачаны модельные веса, нет инференса; сам проект требует минимум ~22 ГБ только для наименьшей модели |
| **Lemo-Opuscar** | `npm ci --ignore-scripts` из источника; `three`, `playwright-core`, Chromium действительно запущены | Официальные `core/render/still.mjs` и `video.mjs` на отдельной оригинальной WebGL сцене: **6 JPG**, **3.000s H264 640×360 12fps 36 кадров**, full `ffmpeg -xerror` decode PASS, SHA256 `e7f27614f53fcb47fa0689b3746f49c6b38b01481ec39cfb1232a9675cbd2962` | **PASS: реальный upstream code renderer**, тестовая сцена не production M1lash. Есть software WebGL, 3D медленнее на CPU |
| **Teardown** | `styles/teardown/STYLE.md` + demo, HDRI из официального hash-verified pack (12.5MB), закреплённые CAD-данные и шрифты | Первая попытка 404 без отдельного HDRI — исправлено официальным `fetch.sh hdri`; `fetch_cad.sh` и `fetch_fonts.py` exit 0. После этого официальный `core/render/still.mjs` на demo **упирается в 30с `page.screenshot` timeout**, software GPU stalls | **PARTIAL/NO PASS для оригинального тяжёлого demo**. Облегчённый explode/3D принцип в собственном Opuscar-smoke проходит; полный Teardown-видео тест не выполнен |
| **OpenClaw** | `openclaw@2026.10.10` npm `--ignore-scripts --omit=optional` в отдельном каталоге; Node **24.16.0** | `openclaw --version`, `--help`, `status --json` → exit 0; чистые изолированные HOME/state; **0 агентов, 0 каналов** | **PASS: изолированный CLI/status**. Gateway, провайдеры, агентные задачи и мессенджеры не развёрнуты, сквозной сценарий не тестировался |
| **Glassy Dashboard V5** | На скрине только визуальная работа CodeXr; исходный код/точная лицензия отсутствуют | Нечего надёжно ставить как software package | **NOT INSTALLABLE FROM SCREENSHOT**. Не менять дизайн сайта по одному кадру |
| **JavaRush AI Academy** | Учебная реклама (16 уровней), не пакет и не CLI | Не выполнялись покупка/регистрация | **NOT A SKILL/INSTALLABLE TOOL** |

## Установка, тестовая среда и воспроизведение

Установлено в **одно изолированное окружение**, не в главную ветку и не на компьютер пользователя:

```bash
# Executed in isolated remote Linux:
ROOT=/home/user/m1lash-tool-audit-20261105
uv venv --python python3 "$ROOT/.venv"
uv pip install --python "$ROOT/.venv/bin/python" scrapling graphifyy pytest yt-dlp
uv pip install --python "$ROOT/.venv/bin/python" 'scrapling[fetchers]'
uv pip install --python "$ROOT/.venv/bin/python" -e "$ROOT/repos/colibri"
# AutoHarness — Python path в test-venv, НЕ hooks/плагины:
# $ROOT/.venv/lib/python3.12/site-packages/m1lash-autoharness-source.pth → $ROOT/repos/autoharness/src
(cd "$ROOT/repos/opuscar" && npm ci --ignore-scripts --no-audit --no-fund)
# OpenClaw: official sha256-verified Node24 in $ROOT/node24/bin;
# npm install --no-save --ignore-scripts --omit=optional openclaw@2026.10.10
```

`/watch` запускается скриптом `$ROOT/repos/watch/scripts/watch.py`; компоненты Lemo — через официальные Node render modules. AutoHarness source импортируется, но agent hooks отключены. `teardown` требует 3D GPU или настройки software WebGL/дополнительное упрощение, нельзя выдавать тайм-аут за рендер PASS.

## Что не означает эта проверка

- Не установлено **глобально в ChatGPT**, на телефоне или компьютере владельца.
- В публичный GitHub помещаются только навыки, документация и результаты; **не** 22 ГБ модель Colibri, install-среда, sample MP4 с private voice или OAuth-секреты.
- Watch **не** умеет гарантированно открывать YouTube с антибот-защитой; легальный MP4/доступный источник необходим.
- OpenClaw/AutoHarness не получили прав на сообщения, GitHub-действия или автоизменение навыков.
- Теcты на небольшой тестовой сцене/локальном HTML не доказывают качество продакшен-ролика или успешную работу на сайте пользователя.

**Следующий технический шаг, если появится постоянная согласованная машина:** развернуть этот venv/npm по закреплённым версиям, прогнать Watch на настоящем разрешённом MP4, провести Colibri inference лишь при наличии локальной модели и ресурсов, дать Teardown аппаратный WebGL и отдельно согласовать любое включение OpenClaw gateway/AutoHarness hooks. На M1lash не менять действующие форматы, план, паузы и правила публикации.
