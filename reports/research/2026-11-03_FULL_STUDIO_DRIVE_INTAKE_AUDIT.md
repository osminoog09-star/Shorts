# M1lash Studio — полный технический аудит импорта фильма в Drive
**Дата:** 03.11.2026 (Europe/Tallinn). **Область:** сайт → GitHub API → Actions → исходник → MP4 QA → Google Drive; смежно безопасность и отображение прогресса.

## Итог
**Основная фактически воспроизведённая причина:** pinned `hdrezka-dl` при `--no-antibot-solver --info` завершается **exit 2 / `anti_bot_challenge`**, прежде чем получить качества. Плеер/потоки не доступны загрузчику из Actions. Это ограничение источника; без обхода защиты получить нужный файл автоматически с этого адреса не подтверждено. Сам Drive **не является причиной данного сбоя**.

## Реальные измерения и происхождение утверждений
| Участок | Измерение | Вывод |
|---|---|---|
| GitHub dispatch | Owner runs [41548828784](https://github.com/osminoog09-star/Shorts/actions/runs/41548828784), [41548866880](https://github.com/osminoog09-star/Shorts/actions/runs/41548866880) | оба `inspect` вернули `source_unavailable`; файл не скачан |
| Серверный source probe | [41550466981](https://github.com/osminoog09-star/Shorts/actions/runs/41550466981) | HTTP HEAD и GET страницы фильма = 200; `hdrezka-dl --no-antibot-solver --info` = exit 2 / `anti_bot_challenge`; качество отсутствует |
| Повторный probe | [41550688949](https://github.com/osminoog09-star/Shorts/actions/runs/41550688949) | HTTP HEAD/GET фильма и GET корня = 200, маркеры антибота в первых 12Кб не распознаны нашим обычным HTTP клиентом; CLI снова exit 2 / `anti_bot_challenge` |
| Код upstream | [cmd/hdrezka-dl/main.go](https://github.com/n0madic/go-hdrezka/blob/e54f622419178cc48b58347facc36d325ac6ac59/cmd/hdrezka-dl/main.go), [hdrezka.go](https://github.com/n0madic/go-hdrezka/blob/e54f622419178cc48b58347facc36d325ac6ac59/hdrezka.go), [utils.go](https://github.com/n0madic/go-hdrezka/blob/e54f622419178cc48b58347facc36d325ac6ac59/utils.go) | CLI сначала `Init()`: запрашивает **главную страницу /**, проверяет браузерную защиту, затем `GetVideo()`. Параметр `--no-antibot-solver` в нашем workflow запрещает решение challenge. HTTP 200 не означает, что HTML прошёл антибот и содержит плеер |
| Google Drive | [41548354350](https://github.com/osminoog09-star/Shorts/actions/runs/41548354350) | Google refresh, scope, права папки, реальный `rclone lsf` PASS; `publishing/drive_auth_status.json connected=true`. Тест **записи** фильма не выполнялся |
| Сохранение статуса | owner 41548866880 | второй run: `Record safe metadata status` FAIL по Git rebase conflict; статус `hdrezka_status.json` оставался старым |
| Live UI | `site/studio/{clips_ui,auto_refresh}.js` | раньше 204 из dispatch принимался за «запущено», но UI продолжал показывать `not_started`; исправлено в предшествующих коммитах |
| Security Drive | Google Drive metadata (прочитано 03.11) | папка `1ANvcXlUj0wBv1CG5U0bBQGdH-32OyaAi`: **`anyone=writer`**, любой с ссылкой может изменять содержимое. Исправление доступа требует решения владельца; без разрешения не меняли |

## Дополнительные неисправности и технические риски
1. **Точная ошибка источника скрывалась**: `run_process()` в `scripts/hdrezka_intake.py` игнорировал raw stdout/stderr и всегда отдавал общее `source_unavailable`. Теперь безопасный `classify_source_failure()` распознаёт challenge, HTTP-коды, DNS/TLS; сырые ссылки, HTML и токены не публикуются. Unit tests в `scripts/qa/test_hdrezka_intake.py`.
2. **Нет мгновенного результата dispatch**: GitHub REST workflow_dispatch отдаёт подтверждение приёма, а не проверки качества; CI перед `inspect` устанавливает Go 1.25 и компилирует downloader. UI теперь показывает GitHub run/очередь и ссылку, но не должен выдавать запрос за успешное скачивание.
3. **Конкурентные обновления статуса**: старый `git pull --rebase` внутри последнего шага workflow конфликтовал с чужими коммитами. Исправлено `308a31e2`: сохранять status во временный файл и накладывать его поверх свежего origin/main на каждой попытке.
4. **Повторные клики**: workflow concurrency для пользовательских задач держит лишь running+pending; при множественных нажатиях часть запросов будет cancelled. Это не причина anti-bot, но объясняет нестабильный прогресс. Не запускать несколько одинаковых проверок одновременно.
5. **1080p может требовать аккаунта**: документация CLI описывает ограничения 1080p/Ultra и premium; текущая попытка **не дошла** до проверки этого барьера. Нельзя обещать 1080p, когда есть только HTTP 200.
6. **Верификация файла ещё не проходила**: после `inspect` нужны `download` → существование файла → `ffprobe` (длительность >20 мин, размер и запрошенное разрешение) → `rclone` copy → подтверждение файла в Drive. Состояние сейчас `drive_uploaded=false`.
7. **Не смешивать два источника live-данных**: UI обновляет страницу через интервалы, но исходные YouTube счётчики обновляются отдельно Github Actions, не ежесекундно. Это не ошибка импорта видео, но влияет на ожидаемую «живость» сайта.

## Принятые узкие технические исправления
- `scripts/hdrezka_intake.py`: классификатор понятной ошибки без публикации private stdout. CI для юнит-тестов `hdrezka-intake.yml`.
- `publishing/hdrezka_status.json`: `source_antibot`, ссылки/токены/сырые HTML не сохраняются. Никакой фильм не объявлен загруженным.
- `site/studio/clips_ui.js` + `auto_refresh.js`: кнопка «Скачать в Drive» недоступна до `inspect status=ok` (и активного Google OAuth), чтобы не создавать гарантированно бесполезную задачу без качества.
- `.github/workflows/hdrezka-source-audit.yml`, `scripts/qa/diagnose_hdrezka_source.py`: отдельный **read-only** пробник HTTP status и CLI info; не запрашивает видео, не передаёт логины, не решает anti-bot, не печатает raw output.
- Правила `AGENTS.md` не изменялись, YouTube и существующие фильмы не тронуты.

## Чего пока НЕ доказано
- Конкретный провайдер/тип challenge (Cloudflare / DDoS-Guard / Anubis) **не определён**, только факт остановки на антибот-защите по ответу самого CLI.
- Нельзя считать HTTP 200 подтверждением доступности стрима, качества, русской дорожки или лицензии.
- Проверка реального `copyto` полнометражного MP4 через подключённый Drive ещё не выполнялась.
- Исправление статусов/классификатора — CI success ≠ end-to-end успешная загрузка.

## Следующий шаг
1. Проверить финальные результаты GitHub CI для последних изменений и опубликованный новый сайт.
2. Не пытаться обходить DRM, антибот или Premium: для полного теста использовать **доступный с разрешением на использование** полнометражный MP4 (только пользовательский/лицензированный источник) и проверить статус + Drive metadata; отдельный путь согласовать при необходимости.
3. Владелец должен перевести доступ Drive-папки из `anyone:writer` в Restricted (или другой минимальный доступ), иначе любой с ссылкой сможет удалять/подменять фильмы. Без разрешения владельца права не менять.

**Оценка:** исходный источник — BLOCKED; Google Drive — READ/LSF VERIFIED, WRITE NOT YET VERIFIED; Studio progress/status — fixed in code with CI; actual movie upload — NOT DONE.
