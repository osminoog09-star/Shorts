---
name: m1lash-studio
description: Карта и пошаговый конвейер студии канала M1lash — от идеи и исходника до приватной заливки, расписания, аналитики, прогноза монетизации, сайта и виджета. Читать перед любой работой с роликом, публикацией, аналитикой или инфраструктурой студии.
---

# Студия M1lash — конвейер и инфраструктура

Правила канала — только `AGENTS.md` (главнее этого файла). Здесь — **как** всё устроено и в каком порядке делать.
Скил живой: каждый агент после работы дописывает сюда то, что узнал (раздел «Уроки»), с датой и автором.

## 1. Карта системы

| Что | Где | Когда работает |
|---|---|---|
| Аналитика (Analytics API, задержка 1–2 дня) | `youtube-analytics.yml` → `scripts/youtube_analytics.py` → `reports/youtube/latest.json`, `daily/`, `weekly/`, `monthly/`, `reports/videos.csv` | ежедневно 07:20 UTC |
| Прогноз монетизации | `scripts/ypp_progress.py` → `reports/youtube/ypp.json` | в том же запуске |
| Автоидеи (если GPT не написал) | `scripts/ideas_auto.py` + очередь экспериментов `reports/ideas/backlog.json` → `reports/ideas/latest.json` | в том же запуске |
| Пульс (живые счётчики Data API) | `youtube-pulse.yml` → `scripts/youtube_pulse.py` → ветка `pulse-data`, `pulse.json` (72 ч) | каждый час :07 |
| Сайт студии | `site/studio/index.html` + `scripts/build_studio_site.py` → `data.json`; деплой `motion-pages.yml` | после аналитики, пульса и пушей в site/reports |
| Android-виджет + уведомления | `android-widget/` → `android-widget.yml` → релиз `widget`, `m1lash-widget.apk`. Три варианта 2×2 / 4×2 / 4×4, раскладка по текущему размеру (`widget_s/m.xml`, все id во всех раскладках!). Уведомления: ждёт «ок», вышел ролик, всплеск, новые идеи, обновление | при пуше в android-widget/; новая версия = поднять `versionCode` → приложение само скачает и предложит установить (`UpdateActivity`). Подпись — секреты `WIDGET_KEYSTORE_*` |
| Заливка / расписание | `youtube-direct.yml` (`mode=upload` приватно без даты → `mode=schedule` после «заливаем») | вручную агентом |
| Плейлисты | `publishing/playlists.json` + `playlists.yml` | ежедневно |
| Озвучка | workflow `TTS` (edge-tts, Дима/Света) | по запросу |
| Исходники кино | `tools/movie_edit/source_jobs/*.json` → `movie-edit-source.yml`; `fetch.yml` для прямых ссылок | по запросу |

Сайт: `https://osminoog09-star.github.io/Shorts/studio/` (вкладки План · Что делать · Сводка · Ролики · Монетизация).

## 2. Конвейер ролика (по шагам)

1. **Идея** — из `reports/ideas/latest.json` (одобрена Денисом), из `reports/experiments.md` или **заявка зрителя** (см. §4).
2. **Стиль и глубина** — спросить Дениса 2–3 кода из `skills/vizavi-motion/references/style-library.md` (AGENTS §2).
3. **Исходник** (кино) — §3. Фильм/серию в репо, релизы, артефакты дольше 7 дней не кладём.
4. **Монтаж** — кино: `tools/movie_edit/` (`MYSTERY_SHORTS_TEMPLATE.md`, `validate_mystery.py`); анимация: `skills/m1lash-animation-production`.
5. **Голос** — Дима через `TTS`; финал: фирменная концовка без персонажа (AGENTS §4).
6. **Проверка** — AGENTS §12: полный decode ffmpeg, контрольные кадры, звук, длительность, метаданные.
7. **Паспорт** — строка в `publishing/queue.json` + `PUBLISH.md`, манифест `publishing/queue/<id>.json` без `publish_at`.
8. **Приватная заливка** — `youtube-direct.yml mode=upload`. Статус `review` → Денис видит на сайте («Ждёт твоего ок») и получает уведомление в виджете.
9. **«Заливаем»** от Дениса → вписать `publish_at` → `mode=schedule`.
10. **После выхода** — строка в `reports/videos.csv` (делает аналитика), эксперимент — в `reports/experiments.md`, итоги 48 ч / 7 д.

## 3. Где брать исходники (проверено 30.10.2026)

- **YouTube с серверов GitHub не качается** (бот-проверка «Sign in to confirm you're not a bot»; оба запуска `movie-edit-source` 30.10 упали). Не обходить: никаких cookies, прокси, капч.
- Пиратские сайты/торренты не ищем и не используем.
- Рабочие пути: (а) **Денис присылает файл** (чат, Telegram, Google Drive) → прямая ссылка в `fetch.yml` или вложение агенту; (б) GPT-агент с браузером на ПК Дениса; (в) официальные/лицензированные клипы (Movieclips, каналы студий) — найти ссылку агентом, скачать Денису на телефон, прислать файл.
- В `source_jobs/*.json` всегда `purpose` и `rights_note`; риск Content ID принят Денисом (AGENTS §8).

## 4. Заявки зрителей (решение Дениса 30.10)

- Хорошая заявка из комментариев → ролик «По заявке @ник 💀»: ник в названии и в первом кадре (кинетический текст), в закрепе ответ автору заявки. Название фильма/сериала публично не пишем (AGENTS §8).
- «В оригинале» = оригинальная дорожка + русские субтитры (исключение к правилу «русский диалог» только для таких заявок).
- Эксперимент в `backlog.json`: метрика — комментарии и новые заявки.
- Ответ в комментариях YouTube публикует Денис (у нас нет права `force-ssl` на комментарии, и это публичное действие).

## 5. Аналитика: кто что делает

- **Автоматически (без агентов):** ежедневная аналитика, прогноз монетизации, автоидеи, ежечасный пульс, сайт, виджет.
- **GPT/Codex раз в день** (после 07:40 UTC): читает цифры, пишет свои 3–5 идей в `reports/ideas/latest.json` (`author: "gpt"`), ведёт `reports/experiments.md`, вс — недельный вывод, 1-го — месячный + `STRATEGY.md`. Промт — `tasks/gpt_daily_analytics.md`.
- **Claude** аналитику не ведёт, только читает выводы перед роликами.

## 6. Монетизация (YPP)

Пороги и даты — в docstring `scripts/ypp_progress.py`. Считаем по `engagedViews` (засчитанные). С 01.02.2027 полный порог для новых заявок 20 млн Shorts / 8000 ч. Официально — Studio → «Заработок».

## 7. Уроки (дописывать сверху: дата · автор · что узнали)

- 31.10 · GPT · OAuth `token_for('ru')` может работать для YouTube Data/Analytics, но не давать `youtube.force-ssl`. Тест `YouTube auth check` обязан дополнительно проверять `commentThreads.list` и считать `403 insufficientPermissions` за NO-GO; `status.comments=ok` в `pulse-data/pulse.json` подтверждать только по реальному запуску. Новый refresh token получать через интерактивный Google consent владельца и хранить **только** в GitHub Secrets, не в issue/чат/файл.
- 31.10 · GPT · Виджет: GitHub Actions `SUCCESS` при подписи debug и предупреждении о `WIDGET_KEYSTORE_B64` — ложный успех. Выпускной workflow обязан fail-closed без обоих постоянных секретов, проверять keystore и ключевой alias до сборки; никогда не перезаписывать release debug-сборкой. Нельзя генерировать постоянный ключ в недоверенном окружении без гарантированного безопасного сохранения в Actions Secrets.
- 31.10 · GPT · Кино-Shorts по зрительской заявке: найденный на YouTube официальный/лицензированный для владельца канала клип **не означает** право повторного использования M1lash и **не означает**, что доступен локальный MP4. Пока нет файловых байтов, нельзя выдумывать диалоги/таймкоды, заявлять QA PASS или делать private upload. Можно заранее подготовить отдельное утверждённое TTS-задание Димы, паспорт и queue статус `draft`; после получения легального исходника — полноценный монтаж/QA и `mode=upload` без `publish_at`.

- 31.10 · Claude · 3D-текст на сайте: Three.js r128 (TextGeometry в ядре) + свой typeface из Unbounded ExtraBold (`site/studio/i/font.json`, сделан opentype.js из @fontsource/unbounded). Вертексные цвета переводить `convertSRGBToLinear()`, иначе блёкло. Иконки/логотипы рендерятся тем же кодом через Playwright → PNG.
- 31.10 · Claude · Комментарии канала требуют scope `youtube.force-ssl` (иначе 403 insufficientPermissions) — `tasks/gpt_reauth_comments.md`.
- 31.10 · Claude · Мобильная вёрстка: у сетки оболочки `minmax(0,1fr)` и `min-width:0` у детей, иначе горизонтальный скролл-ряд распирает страницу.

- 31.10 · GPT · Качественный Shorts сначала синхронизировать по реальным MP3 Edge/Azure (`ru-RU-DmitryNeural` + `ru-RU-SvetlanaNeural`), затем строить кадры по таймлайну и обязательно делать полный decode/контактный лист реального MP4. В эпизоде `pretend_bot3_gpt` укорочены s02/s04: длительность 55,23 → 49,53 с. Не объявлять субъективное 8/10 без просмотра/прослушивания владельцем.
- 31.10 · GPT · Если Python-рендер в GitHub Actions временно синтезирует отсутствующие MP3, они остаются **untracked**; параллельный TTS-bot может записать такие файлы в main, и `git pull --rebase` остановится. Перед rebase выполнить безопасный `git restore -- media/tts/` и `git clean -fd -- media/tts/`, НЕ стирая пользовательские видео и рабочие файлы. Общий workflow `motion-render.yml` теперь имеет аудио-метаданные + full-ffmpeg-decode gate.

- 30.10 · Claude · `actions/checkout` берёт только main: чужую ветку тянуть `git fetch origin +ветка:refs/remotes/origin/ветка`, иначе `origin/ветка` не существует.
- 30.10 · Claude · Debug-подпись в CI каждый раз новая → обновление APK поверх не ставится. Только постоянный ключ из секретов. Секреты из облачной сессии Claude не записать (прокси) — делает GPT/Денис.
- 30.10 · Claude · RemoteViews: если раскладка без нужного id, а код в него пишет — виджет «не удалось загрузить». Держать все id во всех раскладках (лишние `gone`).
- 30.10 · Claude · Сайт: Three.js r128 с cdnjs (нет CapsuleGeometry), проверка — Playwright + swiftshader, three.min.js подставлять из npm.

- 30.10 · Claude · Засчитанные просмотры Shorts ≈ 50 % от всех. Последний день Analytics приходит нулями — отбрасывать.
- 30.10 · Claude · Analytics API почасово бессмысленен (задержка), почасово — только Data API счётчики.
- 30.10 · Claude · gh через прокси: GraphQL и логи джобов недоступны, REST repo-scoped работает.
