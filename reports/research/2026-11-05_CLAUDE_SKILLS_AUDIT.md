# Аудит навыков в Git · Claude · 05.11.2026 (по просьбе Дениса «все навыки должны быть в гите»)

## Итог
115 навыков (`skills/` + `skills/ext/`), все подключены **ссылками** в `.claude/skills` и `.agents/skills`; `python3 scripts/sync_skills.py --check` → 0 проблем.

## Что было не так и что сделано
| # | Проблема | Исправление |
|---|---|---|
| 1 | `denis-voice-ci` лежал копией только в `.claude/skills/` — не было в `skills/`, у Codex (`.agents`) вообще не было | Перенесён в `skills/denis-voice-ci/`, подключён ссылкой обоим агентам |
| 2 | `sync_skills.py --check` не видел копий/лишних папок в агентских каталогах (поэтому п.1 проходил проверку) | Добавлен поиск «копий» — теперь такой случай = проблема |
| 3 | `tools/studio_learning.py preflight` падал (обязательный шаг AGENTS §2): журнал содержит статус `in_progress`, review `not_needed_for_CI_smoke` и доказательства-ссылки на Actions runs | Валидатор принимает эти значения и ссылки на run/URL вместо файла |
| 4 | `m1lash-animation-production`: «Голос: **Дима**» — противоречит AGENTS §3 (с 04.11 только голос Дениса) | Строка заменена на актуальное правило (Денис + женский VoiceDesign) |
| 5 | `m1lash-director` ссылался на архивный `CODEX_NOTICE.md` | Ссылка убрана |
| 6 | Не было навыка для 3D-мульта кодом и женского второго голоса | Новый `skills/m1lash-3d-shorts`; в `denis-voice-ci` — проверенные факты (REST-диспатч, длительности, artifacts) и раздел про женский голос |
| 7 | Не было безопасного способа отдать владельцу MP4 с его голосом | `scripts/drive_private_upload.py` → приватная папка Drive `voice_out/<папка>` |

## Проверка запуска (облачная сессия Claude, 05.11)
| Навык / инструмент | Результат |
|---|---|
| ffmpeg-skill (`check.py`, `look.py`, `probe.py`) | PASS |
| lemo-opuscar (`core/render/still.mjs`, `video.mjs`) | PASS — реальные кадры мини-мульта |
| hyperframes CLI (`npx hyperframes --version`) | PASS |
| huashu-motion (submodule) | PASS (v0.3.1) |
| watch (`watch.py --help`) | PASS |
| graphify, scrapling, yt-dlp | были не установлены → `pip install graphifyy scrapling yt-dlp` → PASS (только в этой сессии) |
| faster-whisper | PASS |
| Remotion `studio/` | файлы на месте (рендер не запускался) |
| denis-voice-tts.yml (Actions) | PASS run 42105048407, ASR 4/4 |
| female-voice-design.yml (Actions, новый) | PASS run 42105028306, ASR 4/4 ≥0.95 |
| elevenlabs-* | не используем: платный API (AGENTS §2 нулевой бюджет) — только справка |
| mkt-*, emil-*, impeccable, humanizer и др. | текстовые навыки, исполнять нечего |

## Ограничения (честно)
- Облачная сессия Claude не может скачивать Actions artifacts и Drive: всё с приватным голосом идёт внутри Actions.
- GitHub `ubuntu-latest` = 26.04: Playwright 1.56 там не ставит браузер → для рендера `ubuntu-24.04`.
- Установка pip-пакетов в этой сессии не постоянная; на ПК Дениса — по `LOCAL_PC_PLAN.md`.

## Запуск новых навыков (Claude, 06.11 ночь)
| Навык | Результат | Заметка |
|---|---|---|
| anim-graph | PASS — 4 с 1080×1920, 20 с рендер | русские подписи работают |
| anim-minimalistic-graphics | PASS | |
| anim-map-route | PASS | интерфейс карты на английском («9 min», «Arrived») |
| anim-breakdown | PASS | модель всегда телефон, меняются только подписи |
| anim-stick-figure | PASS — 35.7 с, озвучка+выравнивание слов+музыка+SFX+картинка | для наших роликов голос подавать файлом Дениса (`make.sh <папка> <wav>`), Kokoro только тест |
| anim-zach-d-films | не запускался отдельно | тот же движок, что stick-figure |
| earshot | CLI ставится и запускается | в `mini-strike.yml` |
| watch (`reference-watch.yml`) | YouTube из Actions: «Sign in to confirm you're not a bot» → SOURCE_BLOCKED | референсы — файлом от Дениса или на ПК |
| awa-video-reel, gstack | submodules, не запускались | нужны модели/браузер, скачивание блокирует облачная сеть → ПК или Actions |

Настройка в облаке: браузер Playwright не скачивается (прокси) → `anim-kit/node_modules/playwright*` ссылками на установленный, `HYPERFRAMES_BROWSER_PATH=<chromium>`; модели Kokoro/Parakeet с GitHub releases качаются (969 МБ, в `.gitignore`).
