## 31.10.2026 · GPT — самостоятельный интернет-поиск киноисходников (6 сцен)

- Нашёл конкретные веб-клипы для всех шести требуемых сцен и записал URL/ориентиры в `reports/source_requests_2026-10-31.md`: официальный YouTube-сериал для Breaking Bad S4E11; Whiplash EN и RU-публикация RUTUBE; Ex Machina (00:31:03, 31s); Nightcrawler сцена с полицейским (00:13:39, 35s); Carson Wells/Chigurh и Carla Jean/Chigurh YouTube и Clip.Cafe.
- Важное разграничение: **найденный веб-клип — ещё не скачанный MP4 и не разрешение правообладателя**. Clip.Cafe HD требует PRO, YouTube скачивание с сервера ранее блокировалось, обходы защиты запрещены; ни одного кинофайла в GitHub и YouTube не загружали. Полный монтаж/QA по §12 не мог быть заявлен готовым.
- После получения законно доступного исходного файла (или разрешённого экспорта) — сверить язык и содержание, собрать кино-Shorts и провести QA. Никаких publish_at, новых receipts и изменений статусов идей.

---

## 31.10.2026 · GPT — checkpoint после утреннего push

- Основной коммит **715075f** отправлен в main. Статусы одобренных идей сохранены, S6-D25 утверждён, запросы исходников и 3 draft-паспорта подготовлены; `reports/morning_run_2026-10-31.md`. Реальный запас **1/4**, три пустых Shorts-слота всё ещё ждут видеофайлы; очереди и даты не подменялись планами.
- **TTS Ex Machina завершён:** run [41169150379](https://github.com/osminoog09-star/Shorts/actions/runs/41169150379) SUCCESS, бот-коммит **722f7aeb**. Дима / edge-tts +4%, настоящий MP3 **9.480 с / 56 880 байт**, полный decode PASS; `shorts/movie_ai_trust_20261031/VOICE_PREFLIGHT.json`. Это готовый голос финала, не готовый кино-Shorts. Голос заявки Ernesto ранее проверен: 9.072 с, отдельный preflight. Субъективное прослушивание финального монтажа не заявляем — монтажа пока нет.
- **Чигур:** сохранён `longform/chigur/RECOVERY_2026-10-31.md`: шесть прежних временных окон, планы двух Shorts, действующие no-character/PRIVATE/no-date решения и незакрытые проверки звука/кропа. Локальные исходники и киноэкспорты предыдущей среды отсутствуют; при возобновлении нужен источник. Старый HostCorner — архив. Никаких исходников фильма, MP4 или ключей в этом коммите.
- Проверено решение владельца из параллельного коммита **7833f2be**: текущий дефицит закрывать **только киноисходниками**, предложенные оригинальные скетчи не делать. Его изменения AGENTS/STRATEGY/буфера/запросов сохранены. Источник для Ernesto и остальных фильмов по `reports/source_requests_2026-10-31.md`, после файлов — монтаж → §12 → PRIVATE без даты. Bot3 scheduled на 01.11 16:00 не трогать.

---

## 31.10.2026 · GPT — выбор владельца: для ближайшего буфера только кино

- Денис отклонил предложенные скетчи «Умная колонка устроила профсоюз» и «ИИ-навигатор через холодильник» как замещение кино. Не производить их для заполнения пустых слотов. **Пустые слоты текущего производственного резерва — только из реальных киноисходников**, а не кодовая анимация без фильма. Это не отменяет уже запланированный Bot3 и не меняет всю утверждённую сетку.
- `AGENTS.md` §5, `STRATEGY.md`, `reports/production_buffer_2026-10-31.md` обновлены с этим решением. В `reports/source_requests_2026-10-31.md` оставлены заявки Ernesto / Whiplash / Ex Machina / Nightcrawler и добавлены две конкретные сцены Чигура для воронки.
- `reports/ideas/latest.json`, согласованные статусы и дата Bot3 **не менялись**. Ни одного нового MP4, QA, YouTube upload/schedule нет; запас **1/4** подтверждённых слотов. Для настоящего монтажа нужны видеофайлы от Дениса с аудиодорожками. Ключи/секреты и исходники фильмов не коммитили.

---

## 31.10.2026 · GPT — утренний регламент: заявка Ernesto, сцены и реальный буфер

- Выполнен свежий clone main после очистки временной среды и **git pull --ff-only / Already up to date**. Полностью прочитаны AGENTS.md, m1lash-studio, channel-analytics и регламент. Отчёт — `reports/morning_run_2026-10-31.md`.
- Сбор жив: latest snapshot 31.10 / Analytics run **41138384362 SUCCESS**; pulse-data `status.comments=ok`, run **41155790659 SUCCESS**, snapshot 01:32 UTC. 35 подписчиков / 29 649 lifetime views; Analytics последний наблюдаемый день 28.10. Пульс отстаёт от текущего часа, но упавшего запуска нет; перезапусков не делали. Weekly/monthly финализировать 01.11, не сегодня.
- Денис подтвердил **S6-D25 для «Одержимости», «Из машины», «Стрингера»**. Сюжеты и текущие approved/in_work/dropped сохранены; датированная копия синхронизирована с latest, включая уже существующий in_work у Ex Machina. Конкретные запросы — `reports/source_requests_2026-10-31.md`.
- **Приоритет @ErnestoMarsel:** реальный MP3 Димы 9.072 с / 54 432 байта и metadata проверены, полный decode PASS; `shorts/request_ernesto_crawlspace/VOICE_PREFLIGHT.json`. Паспорт есть; записи подвала S4E11 в текущем сообщении нет. Поэтому нет готового MP4, полного §12, upload и YouTube ID. Оригинальный английский + RU субтитры, ник в первом кадре/названии, персонажа нет.
- Whiplash: обновлён treatment, добавлены draft PUBLISH/PRODUCTION. Ex Machina: treatment/PUBLISH/PRODUCTION и **новый TTS job `mystery_ai_trust_20261031`** (проверить результат после push). Nightcrawler оставлен approved, подготовлен резервный пакет. Все три ждут файлы, не ready. Существующие голоса Ernesto/Whiplash не регенерировались.
- **Запас всё ещё 1/4 Shorts-слотов** сб–пн: вс 01.11 16:00 уже Bot3 `CmOu0xXc0UI`, receipt `scheduled`, schedule run **41143928913 SUCCESS**; ничего повторно не загружать. Сб 16:00 и пн 10:00/16:00 пока пустые — материалы назначены только как производственные намерения. Новый publish_at не создан, секреты не читались/не менялись.
- **Чигур: честный checkpoint.** Локальная среда прежнего этапа очищена, шесть выбранных сцен и незакоммиченные киноэкспорты не сохранились. В main есть SCRIPT_DRAFT/FACTS, TTS и старые project docs, но готового кино-MP4/YouTube upload нет. Полный фильм до очистки был удалён после нарезки и проверок; в репо/релизы/артефакты не попадал. Не считать старые host-overlay и локальные пробы без персонажа готовым резервом.
- Публичных комментариев/ответов не отправляли. @yamakasi_off просит больше кино, @zhorekp предлагает помощь с голосом — решение за Денисом. Эксперименты: нет точных 48 ч/7 д, вывод «ещё тест». Блокер производства — отсутствующие записи, не лимит GPT.

---

## 31.10.2026 · GPT — финальная проверка пп. 4–5

- Исправленный общий Playlist sync [run 41167374770](https://github.com/osminoog09-star/Shorts/actions/runs/41167374770) **SUCCESS**: после отката конкурентного дублирования 7 исходных плейлистов и их настоящие IDs остались сохранены. Баннер/описание/трейлер ранее подтверждены в `publishing/branding/status.json` и branding run 41145322728. Не создавать дубли `pretend_bot` / `ai_sketches`; действующие группы `bot_series` / `ai_sketch`.
- Пункт 5 уже подготовлен отдельными предварительными файлами `reports/weekly/2026-W44.md`, `reports/monthly/2026-10.md`, `STRATEGY.md`, `reports/production_buffer_2026-10-31.md`. Буфер остаётся **1 подтверждённый / 4 слота** на 31.10–02.11; идеи не равны готовым MP4. Нужны выбранные стили для двух оригинальных скетчей. Финализировать отчёты по доступным фактическим данным 01.11.
- Ничего не публиковали, старые Shorts RU/ENG и ключи не трогали. Канал и YouTube-видео не удаляли.

---

## 31.10.2026 · GPT — устранена гонка изменений в плейлистах

- Перед нашим коммитом `512ba6e8` другой процесс **уже завершил** пп. 4–5: 7 реальных плейлистов, баннер PNG, проверенное YouTube-оформление, предварительные weekly/monthly, план буфера (см. предыдущие записи). Наш параллельный коммит случайно создал дубли ключей `pretend_bot`/`ai_sketches` при уже действующих `bot_series`/`ai_sketch`, а синхронизация run [41167327374](https://github.com/osminoog09-star/Shorts/actions/runs/41167327374) завершилась FAIL. **Не считать это созданием новых плейлистов.**
- Восстановлены точные проверенные файлы из последнего нормального коммита `87654515`: `publishing/playlists.json`, `scripts/playlists_v2.py`, `.github/workflows/playlists.yml`. Реальные сохранённые ID сохранены, никаких YouTube API / ключей / видео/расписаний вручную не меняли. Следующий trigger должен запускать исходный безопасный sync; по факту подтвердить результат.
- Статусы студии по п.3 остаются корректными; в остальных файлах чужие изменения не отменялись.

---

## 31.10.2026 · GPT — пункт 4: неразрушающая сортировка YouTube-плейлистов

- Расширены `publishing/playlists.json` и `scripts/playlists_v2.py`: 5 новых управляемых плейлистов («Притворись ботом», «Новости ИИ», «ИИ-скетчи», «Наука и история», «Юмор»), плюс 2 ранее существовавших кино-плейлиста. Ориентир — 37 видео из snapshot 30.10; public-only, seed + categoryId/title fallback, **без удаления, скрытия или изменения роликов**, без вмешательства в прежние Shorts Ru/Shorts ENG. Добавление только при отсутствии ID видео, вставка новых сверху.
- В `.github/workflows/playlists.yml` добавлен ограниченный `push`-триггер на изменения этих двух файлов, чтобы GitHub Actions смог **создать реальный плейлист и сохранить настоящий ID**, а не фальшивый. Успех на YouTube нужно подтвердить по run; при неуспехе отметить блокер, не выдумывать ID.
- Подпись/ключи не трогались. Баннер и описание канала — отдельная часть пункта 4, будет отражена отдельно.

---

## 31.10.2026 · GPT — пункт 4: оформление YouTube M1lash реально завершено по API

- **7 плейлистов в канале:** два исходных кино (`kino_shorts=PLIVjPUG-C-Xc`, `kino_razbor=PLdFzvptW-NVI`) плюс созданные **Притворись ботом** `PLYfbX7s-CsKw`, **Новости ИИ** `PLflqNydnG5vQ`, **ИИ-скетчи** `PLW88AiB_GiWg`, **Наука и история** `PLDTQ0uYTdNdk`, **Юмор** `PLJOa8ZvDafFQ`. Workflow [41144702988](https://github.com/osminoog09-star/Shorts/actions/runs/41144702988) и точечная корректировка [41144945760](https://github.com/osminoog09-star/Shorts/actions/runs/41144945760) = SUCCESS, поздняя сверка [41145055841](https://github.com/osminoog09-star/Shorts/actions/runs/41145055841) = SUCCESS. Только публичные загрузки текущего канала; старые плейлисты Shorts RU/ENG не тронуты. Ошибочные включения трансляции/неизвестного клипа убраны лишь из тематического «Юмор», **сами YouTube видео не удалялись/не скрывались**.
- **Баннер 2560×1440 PNG реально создан:** `publishing/branding/banner.png` (296 463 байт), все слова в safe-zone. Исходник `scripts/render_channel_branding.py`. 
- **Оформление реально применено к каналу M1lash через YouTube API:** итог [M1lash channel branding run 41145322728](https://github.com/osminoog09-star/Shorts/actions/runs/41145322728) шаг Apply = SUCCESS, проверочный файл `publishing/branding/status.json`: `status=verified`, `description_verified=true`, `keywords_verified=true`, `trailer_verified=true`, `banner_confirmed_by_api=true`. Трейлер для новых зрителей `XANzL3z9wqY`. Скрипт сначала проверяет RU channel ID и право собственности на публичный трейлер; токены/ключи нигде не раскрыты. Две предыдущие неуспешные попытки были исправлены (повторяющиеся HTTP headers; задержка readback), **их FAIL не скрываем**.
- **Осталось ручное только в YouTube Studio:** проверить расположение секций главной страницы «Кино-Shorts», «Кино-разборы», «Притворись ботом», «Популярные»; API не даёт настроить новый макет полностью. Дополнительная ревизия категорий старых видео/флагов возможна отдельно по `tasks/channel_cleanup.md` — в этом запуске их названия и доступность не менялись.

---

## 31.10.2026 · GPT — точечный ремонт ошибочной сортировки плейлистов

После первого успешного создания 5 плейлистов (run 41144702988) аудит лога нашёл три ошибочных добавления в «Юмор»: `2Ych7OkX1vc` (кино-клип), `mLlB8eL1FUE` (старая трансляция), `XqoHjcsdPtQ` (ролик с неинформативным названием). Дополнен `scripts/playlists_v2.py`: первый переносится в «Кино-Shorts», два других исключаются; после безопасной пересортировки удаляются только **членства** этих трёх видео в новом плейлисте «Юмор», сами видео на YouTube и старые RU/ENG-плейлисты остаются неизменными. Проверить последующий workflow по реальному run SUCCESS.

---

## 31.10.2026 · GPT — пункт 5: недельный/месячный черновики и реальный запас

- Подготовлены **предварительный** недельный `reports/weekly/2026-W44.md` и **предварительный** месячный `reports/monthly/2026-10.md` — без выдуманных дней: Analytics отстаёт до 28.10. За доступные в API дни 26–28.10 14 572 просмотров; наблюдаемая часть октября до 28.10 25 442 просмотров; это НЕ финальные полные периоды.
- Обновлён раздел `STRATEGY.md → Текущая стратегия` по фактическим данным, оставлена историческая политика в архивном разделе (правила — только AGENTS).
- `reports/production_buffer_2026-10-31.md` — статус буфера: только 1/4 подтверждённых сеточных слотов 31.10–02.11 (Bot3 scheduled 01.11 16:00). Два оригинальных скетча предложены **как предпродакшен**, не названы готовыми MP4; кино-Shorts требуют файлов владельца. `reports/experiments.md` теперь явно пишет «нет 48 ч / 7 д» по времени выпуска.
- **Завершить в воскресенье 01.11:** повторно собрать weekly + monthly на доступные фактические дни и пересчитать дефицит, не заявляя итоги октябрьского 31 числа пока нет метрик. Готовый запас 3 дня ещё НЕ создан. Ни одно публичное действие и ключ не тронуты.

---

## 31.10.2026 · GPT — пункт 3: синхронизация статусов M1lash Studio

- Исправлена ложная отметка **«Готово»** у идеи-заявки @ErnestoMarsel: `reports/ideas/latest.json` и `2026-10-31.json` теперь `in_work`, `source_status=waiting_owner_screen_recording`; исходное поле `video_id=XANzL3z9wqY` — видео, под которым оставлен комментарий, **не** ID готового Shorts. Новый `youtube_id` отсутствует, поскольку нет MP4 / QA / upload.
- `pretend_bot3_gpt` в `publishing/queue.json` теперь `scheduled` / `slot=2026-11-01T16:00:00+02:00` / `youtube_id=CmOu0xXc0UI`. Основание — подтверждённые `publishing/queue/pretend_bot3_gpt.json`, receipt `status=scheduled`, [schedule run 41143928913](https://github.com/osminoog09-star/Shorts/actions/runs/41143928913) SUCCESS. Паспорт `shorts/pretend_bot_3_gpt/PUBLISH.md` обновлён. **Ни upload, ни schedule повторно не запускались; время не менялось.**
- В `site/studio/index.html` закрыт путь ложного `in_work → done`: кнопка «Готово» становится доступна только при `youtube_id` нового ролика, обработчик повторно проверяет поле перед записью. `video_id` исходного комментария больше не считается подтверждением производства. Другие одобренные идеи не изменены.

---

## 31.10.2026 · GPT — контроль опубликованного с сайта расписания после утреннего прогона

- Владелец через сайт назначил `pretend_bot3_gpt`: **воскресенье 01.11.2026, 16:00 Europe/Tallinn**. Актуальный `publishing/queue/pretend_bot3_gpt.json` содержит `publish_at: 2026-11-01T16:00:00+02:00`.
- Проверено фактическое завершение `youtube-direct.yml mode=schedule`: [run 41143928913](https://github.com/osminoog09-star/Shorts/actions/runs/41143928913) **SUCCESS**, шаг «Schedule release of the reviewed private video» SUCCESS; `publishing/receipts/pretend_bot3_gpt.json` теперь `status=scheduled`, `publish_at_utc=2026-11-01T14:00:00Z`, YouTube ID `CmOu0xXc0UI`. Предыдущие неуспешные попытки расписания устранены коммитом сайта `b25aa3d50e5a`; **ничего повторно не загружать и не планировать**.
- Утренний аналитический прогон уже завершён коммитами `b49c96aa9`, `911628a04`, запись в HANDOFF создана; новый материал по кино пока зависит от исходника Дениса. Токены/секреты не трогались.

---

## 31.10.2026 01:02 EET · GPT — утренний продюсерский прогон

- **Озвучка после коммита:** workflow [TTS run 41142246350](https://github.com/osminoog09-star/Shorts/actions/runs/41142246350) завершён SUCCESS. Реальный `media/tts/mystery_tempo_20261031/outro_reveal.mp3` создан; манифест подтвердил `ru-RU-DmitryNeural`, `edge-tts`, `+8%`. Это только готовый голос финала, не готовый кино-Shorts.
- **Сбор / аналитика:** проверен последний `reports/youtube/latest.json` — `snapshot_date=2026-10-31`, `fetched_at=2026-10-30T22:29Z`, 35 подписчиков / 29 649 просмотров по Data API; `last_observed_view_day=2026-10-28`, это НЕ точные данные за 48 ч / 7 д. GitHub Actions «YouTube · daily analytics» run [41138384362](https://github.com/osminoog09-star/Shorts/actions/runs/41138384362) SUCCESS, `pulse-data/pulse.json status.comments=ok`, последний hourly pulse [41140954045](https://github.com/osminoog09-star/Shorts/actions/runs/41140954045) SUCCESS. Перезапусков нет.
- **Идеи дня:** уже есть пять `author=gpt` (3 proven + 1 experiment + 1 заявка зрителя) за 31.10, переписывать творчество и решение владельца не требуется. Перечитана **живая** `reports/ideas/latest.json`: идеи 1/2/3 и заявка @ErnestoMarsel были `approved`, идея 4 — `in_work`. **Идея 1** (Whiplash) и **заявка @ErnestoMarsel** переведены `approved → in_work`, идеи 2 и 3 оставлены approved, №4 осталась in_work. Датированная копия 31.10 синхронизирована с фактическими статусами; `dropped` не трогались. Чужие решения не терялись.
- **Производство 6б:** приоритет №1 — одобренная зрительская заявка @ErnestoMarsel: привязана к уже подготовленным `shorts/request_ernesto_crawlspace/README.md`, `PUBLISH.md` и реальной TTS-озвучке Димы; нет входного видео, поэтому исходный статус BLOCKED_SOURCE/NO UPLOAD. Параллельно подготовлен `shorts/movie_tempo_tension_20261031/TREATMENT.md` (осмысленный план сцены, первый кадр, сюжет, эксперимент, гейты), подготовлен `jobs/tts/mystery_tempo_20261031.json` для Димы с последним устным названием. **Нового кино-MP4, клипов и upload нет; статус WAITING_OWNER_CLIP / STYLE_TO_CONFIRM.** Запрос Денису: «Одержимость», первая репетиция, ~25:40–28:40, запись с русской дорожкой. Предлагаемые стили S6-D25 (рекомендуем), S3-D25 или S7-D25. Идея 4 остаётся экспериментом в работе, но без данных об эффектах.
- **Комментарии / публикации:** среди флагов `request` и `to_me`: @ErnestoMarsel ждёт запись финального смеха Уолтера S4E11, @yamakasi_off просит больше фильмов, @zhorekp предлагает помощь с голосом. В `publishing/queue/` найден только `pretend_bot3_gpt.json`, у него `publish_at` нет; запланированных из сайта роликов не обнаружено. Никаких дат и публичных действий, повторной загрузки нет.
- **Суббота 31.10:** недельный отчёт должен быть **воскресенье 01.11**, месячный — 01.11; сейчас не создавались. Секреты не читались и не менялись. В текущей среде обычный сетевой `git pull` недоступен (DNS github.com), поэтому прочитан **актуальный main через подключённый GitHub**, коммит создан через Git API с fast-forward-проверкой.

---

## 31.10.2026 · GPT — проверка итогов после кнопок сайта и приватной загрузки (состояние main / GitHub Actions)

1. **Pretend Bot 3 — PRIVATE UPLOADED / REVIEW.** В `videos/` лежит финальный `pretend_bot3_gpt_ru_v3.mp4` (2 987 089 байт). Render workflow [41139634434](https://github.com/osminoog09-star/Shorts/actions/runs/41139634434) = SUCCESS, видео из artifact независимо извлечено и проверено: ffprobe 49.532 с / 1080×1920 / H264 AAC 24fps, полный ffmpeg decode=0, 14 таймпоинтов контакта и финала визуально просмотрены, звук −18.9 LUFS / true peak −2.3 dBFS, 12/12 метаданных сегментов голосов Дима + Света корректны. См. `shorts/pretend_bot_3_gpt/QA_V3_2026-10-31.md`. **YouTube mode=upload реально сработал**: [run 41140104861](https://github.com/osminoog09-star/Shorts/actions/runs/41140104861), receipt `publishing/receipts/pretend_bot3_gpt.json`: `video_id=CmOu0xXc0UI`, `status=uploaded`, `publish_at_utc=null`; https://youtu.be/CmOu0xXc0UI (PRIVATE). `publishing/queue.json` **исправлена** с `ready` на `review`, добавлен YouTube ID, паспорт PUBLISH.md теперь соответствует MP4 V3 и приватному состоянию. **Не повторять upload; не schedule до «заливаем».** Человеческий полный звуковой и мобильный просмотр ещё за Денисом.
2. **ErnestoMarsel — WAITING_USER_SCREEN_RECORDING.** Файла сцены нет в данном сообщении; ранее сделаны TTS от Димы и `shorts/request_ernesto_crawlspace/PUBLISH.md`. Без настоящего MP4 не выдумывать таймкоды или субтитры, не загружать приватно; получить прикреплённую Денисом запись и сделать монтаж по `tools/movie_edit` + validate_mystery + полный QA.
3. **Секреты Дениса проверены, без доступа к их значениям.** [Android widget APK run 41140013340](https://github.com/osminoog09-star/Shorts/actions/runs/41140013340) = SUCCESS, в логе `BUILD SUCCESSFUL`, нет реального предупреждения `##[warning]WIDGET_KEYSTORE_B64 не задан` и нет ошибок. [YouTube auth check run 41140951261](https://github.com/osminoog09-star/Shorts/actions/runs/41140951261) = SUCCESS, [hourly pulse run 41140954045](https://github.com/osminoog09-star/Shorts/actions/runs/41140954045) = SUCCESS, текущий `pulse-data/pulse.json` показывает `status.comments = "ok"` (14 комментариев в срезе). Ничего из Secret не читаем и не изменяем.
4. **Регламент `tasks/gpt_daily_analytics.md` на 31.10 — проверен.** `reports/youtube/latest.json` имеет `snapshot_date=2026-10-31`, daily JSON+MD присутствуют, `reports/ideas/latest.json` и `reports/ideas/2026-10-31.json` уже имеют `author=gpt` с 3 proven + 1 experiment, `reports/experiments.md` содержит эксперимент 31.10 с пометкой «ещё тест». Просмотры/досмотр не трактовать как точные окна 48 ч/7 д: Analytics API последним подтвердил 28.10. Активная ежедневная задача аналитики уже настроена отдельно, дубли не создавать. Новых публикаций и изменений расписания не делали.

**Никогда не записывать ключи/токены в Handoff или репозиторий; текущий доступ проверял лишь исходы workflow.**

---

## 31.10.2026 · GPT — три задачи M1lash (фактический статус, без секретов)

1. **OAuth / комментарии — BLOCKED_REAUTH.** По подтверждённому `pulse-data/pulse.json`, `status.comments="HTTP 403 insufficientPermissions"`. Нет браузерного доступа к Google OAuth Playground с интерактивным согласием и нет write-доступа к GitHub Actions Secrets через текущий коннектор; `YOUTUBE_REFRESH_TOKEN_RU` **не менялся**. В `.github/workflows/youtube-auth-check.yml` добавлена безопасная проверка реального `commentThreads.list`: зелёный SUCCESS теперь требует и доступ к комментариям. После нового refresh token в GitHub Secrets нужно вручную запустить `YouTube · check authorization (no upload)`, затем `YouTube · hourly pulse` и проверить `status.comments="ok"`. Ни токен, ни код, ни client secret не записывались.
2. **Android Widget APK — BLOCKED_SECRETS.** В логе run [41137715675](https://github.com/osminoog09-star/Shorts/actions/runs/41137715675) найдено фактическое предупреждение `WIDGET_KEYSTORE_B64 не задан`; постоянные `WIDGET_KEYSTORE_B64` и `WIDGET_KEYSTORE_PASSWORD` не созданы/не записаны, так как нет доступа к GitHub Secrets; ключей нигде не оставляли. `.github/workflows/android-widget.yml` укреплён: прекращает выпуск без обоих секретов, проверяет keystore alias `m1lash` и удаляет временный ключ из раннера. Автозапуск [41138932554](https://github.com/osminoog09-star/Shorts/actions/runs/41138932554) завершился FAIL (ожидаемая защита). После безопасного добавления секретов — повторить workflow, проверить реальную подпись и отсутствие предупреждения. Debug APK больше не выпускать.
3. **Заявка @ErnestoMarsel — BLOCKED_SOURCE / NO UPLOAD.** Подтверждён официальный Movieclips-клип `https://www.youtube.com/watch?v=ZRp77ae7tkQ` (copyright Sony). В доступных Conversation/Library-файлах нужного MP4 нет; браузерная загрузка/выход на YouTube-видео невозможны через эти инструменты без обхода защиты (не пытались). Созданы `shorts/request_ernesto_crawlspace/README.md`, `PUBLISH.md`, TTS-job `jobs/tts/request_ernesto_crawlspace.json` c единственным Димой (`ru-RU-DmitryNeural`; реплика заканчивается названием сериала), queue item `draft` без MP4 и ID, без даты. TTS Actions run [41139030194](https://github.com/osminoog09-star/Shorts/actions/runs/41139030194) **SUCCESS**: `media/tts/request_ernesto_crawlspace/outro_reveal.mp3` и `.json` созданы, голос `ru-RU-DmitryNeural`, engine `edge-tts`, последняя произнесённая фраза содержит название сериала. Точные in/out, английский диалог, русские субтитры, QA и PRIVATE upload **не делались**: нужен реальный клип. Загрузка через `youtube-direct.yml` запрещена до успешного полного QA. Никакой публичной публикации и `publish_at`.

**Требуемые разрешения вне текущих инструментов:** Google OAuth consent/Playground с владельцем канала; безопасная запись repo secrets; исходник сцены, доступный законным способом. Не просить владельца отправлять токены/пароли в чат.

---

## 31.10.2026 00:09 EET · GPT — «Притворись ботом», серия 3, озвученный MP4 для просмотра

- **Результат:** `videos/pretend_bot3_gpt_ru_v2.mp4` (49.532 с, 1080×1920, 24 fps, H.264/AAC, 2 987 112 байт), успешно сохранён в `main`; прямой файл: https://raw.githubusercontent.com/osminoog09-star/Shorts/main/videos/pretend_bot3_gpt_ru_v2.mp4 . Не опубликован и не загружен на YouTube. Очередь `publishing/queue.json`: `status=draft`, слот `null`, без даты и без YouTube ID.
- **Правила:** прочитаны актуальные `AGENTS.md` (приоритет над устаревшими файлами), `skills/m1lash-studio/SKILL.md`, `skills/m1lash-animation-production/SKILL.md`, `reports/learnings.md`, библиотека стилей и конвейер. Кодовая анимация S6-D25, без ведущего в углу; оригинальная музыка/SFX, финал M1lash; не кино, сторонних кадров нет.
- **Голоса:** настоящий `ru-RU-DmitryNeural` (Дима), второстепенный `ru-RU-SvetlanaNeural` (Света) из общего TTS, 12 сегментов. Две длинные реплики в s02/s04 сокращены; `jobs/tts/pretend_bot3_gpt.json` и `media/tts/pretend_bot3_gpt/`. TTS success: [41134532648](https://github.com/osminoog09-star/Shorts/actions/runs/41134532648) и укороченная версия [41135162439](https://github.com/osminoog09-star/Shorts/actions/runs/41135162439).
- **Рендер:** `shorts/pretend_bot_3_gpt/render.py`, `jobs/motion/pretend_bot3_gpt.json`; общий `motion-render.yml` расширен для синхронизированных Python-анимаций (без нового одноразового workflow). Финальный успешный run [41135608358](https://github.com/osminoog09-star/Shorts/actions/runs/41135608358) — все steps success, полное декодирование ffmpeg PASS, 12 approved voices, ААС/H.264. Первые два рендера создали MP4, но их шаг сохранения провалился из-за неприбранных временных TTS-файлов. Исправили `git restore`/`git clean` перед rebase и повторили.
- **Независимый локальный QA скачанного реального MP4:** ffprobe H264/AAC 1080×1920, full decode PASS, 15 кадров `0.3–47.8 s` визуально просмотрены: основные надписи внутри кадра, без ведущего, сюжет виден, концовка есть. Исходный микс: -18.9 LUFS, пик -2.3 dBTP; создан локальный нормализованный аудиомастер `/mnt/data/M1lash_Pretend_Bot3_RU_REVIEW.mp4` (49.6 с, -15.65 LUFS по loudnorm first pass, -1.5 dBTP), также full decode PASS. Этот локальный мастер **не** загружен обратно в GitHub; репо хранит хороший синхронизированный исходный микс (менее громкий).
- **Приватный upload-паспорт подготовлен:** `publishing/queue/pretend_bot3_gpt.json` с `channel=ru`, `source.type=repo`, `source.path=videos/pretend_bot3_gpt_ru_v2.mp4`, SHA256 `01f45e2da48f55e42478764ddfad21848b3bbb26be165cb5020c43e0258eb724`, `metadata.type=short`, category 23, madeForKids=false, synthetic=true. **Без `publish_at`**: штатный `youtube-direct.yml mode=upload` при запуске загрузит только приватный ролик. В текущем подключении действие `workflow_dispatch` не предоставлено, поэтому приватную заливку не выдавать за выполненную.
- **Ограничение проверки:** целиком на слух человеком этот MP4 ещё не прослушан, поэтому **не заявлять Approved 8/10**. Статус `REVIEW` как редакционное состояние, `draft` в очереди. Без Денисова просмотра и слова «заливаем» не ставить `publish_at`; все public actions выключены. Приватная загрузка в YouTube Studio остаётся следующим шагом через штатный `youtube-direct.yml` после полной приёмки; не эмулировать отсутствие browser/API dispatch.
- **Урок конвейера:** если рендер сам создаёт локальные `media/tts/` и в то же время TTS-bot коммитит их в main, `git pull --rebase` сбоит на untracked files. Перед rebase очистить только временные TTS-артефакты; не менять глобальные голоса. Для выпуска с голосом истинные длительности MP3 важнее расчётных таймкодов.

---

## 31.10.2026 00:55 · Claude — секреты через сайт
- Сайт → ⚙️ → «Ключи»: «Создать ключ и собрать виджет» (PKCS12 в браузере → секреты `WIDGET_KEYSTORE_B64`/`WIDGET_KEYSTORE_PASSWORD` → сборка APK) и «Ключ YouTube» (refresh token → `YOUTUBE_REFRESH_TOKEN_RU` → auth check + pulse). Gradle читает PKCS12 (`storeType`). GPT секреты больше не трогает.
- Заявка @ErnestoMarsel: GPT подготовил озвучку и паспорт, ждём файл клипа (Денис записывает экран телефона и шлёт GPT).

## 31.10.2026 00:40 · Claude — студия v2: 3D-бренд, сайт-приложение, виджет 2.1
- Сайт: 5 разделов (Обзор/Ролики/Идеи/Зрители/Деньги), 3D-логотип «M1lash STUDIO» в шапке (крутится, тянется пальцем, наклон телефона), 3D-иконки разделов, карточка ролика (источники трафика, сравнение со средним), заявки из комментариев, действия через GitHub-токен Дениса.
- Виджет 2.1: 1×1…4×4, 3D-логотип в шапке, своя иконка уведомлений, иконка приложения из 3D «M1».
- Ждёт GPT: `tasks/gpt_reauth_comments.md` (комментарии), `tasks/gpt_request_ernesto_and_keystore.md` (ролик-заявка + ключ подписи).

## 30.10 — Codex: дополнительный поиск исходника по просьбе «скачай где-нибудь»

- Повторно искал доступные русские сцены Карсона и Карлы Джин вне заблокированной загрузки YouTube. Официальная страница Miramax содержит промоклипы, но ссылки ведут на YouTube; нового самостоятельного файла не даёт.
- Поиск через подключённый веб-поиск завершился ошибкой; Google вернул 429/CAPTCHA (остановлено без обхода), Bing не дал пригодных результатов, Yahoo — HTTP 500, VK Video — Site Unavailable. Публичный поиск Dailymotion дал трейлер JustWatch x8i0krf и нерелевантные результаты; нужные RU-сцены не найдены. Их наличие/язык не выдумывались.
- **Новый исходник не скачан.** Проверку YouTube «не робот», авторизацию и ограничения доступа не обходил. Оба Shorts остаются BLOCKED_SOURCE; upload/schedule не запускались, даты не назначены.

## 30.10.2026 23:45 · Claude — итог вечера (студия)
- Сайт студии: 3D-фон Three.js, стекло, кольца, вкладка «Монетизация» с калькулятором «что если», кнопка скачать APK.
- Виджет 1.5: 2×2 / 4×2 / 4×4, универсальная раскладка, автообновление. **Ждём от GPT секреты подписи** (`tasks/gpt_request_ernesto_and_keystore.md`, часть B) → после этого Денис один раз переустанавливает виджет.
- AGENTS §8 (заявки зрителей, исходники), §13 (сбор автономный, выводы GPT), §14 (студия) обновлены.
- Открыто: ролик по заявке @ErnestoMarsel (GPT, часть A); аудит роликов Чигура после GPT (`tasks/audit_after_chigur.md`); детект претензий Content ID — нет API.

## 30.10.2026 23:30 · Claude — пульс, монетизация, скил студии
- Новый скил `skills/m1lash-studio/SKILL.md` — карта всей инфраструктуры и конвейер ролика. Дописывайте раздел «Уроки».
- `youtube-pulse.yml` — ежечасные счётчики в ветку `pulse-data` (main не засоряется). `ypp_progress.py` — прогноз монетизации, вкладка «Монетизация» на сайте. Виджет 1.3.
- Промт для ежедневной автоматизации GPT — `tasks/gpt_daily_analytics.md`.
- Заявка зрителя @ErnestoMarsel (сцена в подвале, S4E11, в оригинале): source job `request_ernesto_crawlspace.json` упал — YouTube блокирует раннеры GitHub. Ждём файл клипа от Дениса.

## 30.10.2026 23:20 · Claude — автономная аналитика + идеи + виджет 1.2
- `youtube-analytics.yml` (ежедневно 07:20 UTC) теперь после сбора цифр запускает `scripts/ideas_auto.py`: если GPT за сегодня не написал `reports/ideas/latest.json`, пишутся автоидеи (лидеры по просмотрам/досмотру/подпискам + эксперимент из `reports/ideas/backlog.json`, `author: "auto"`). Идеи GPT не перезаписываются. Новые эксперименты дописывать в backlog.json.
- Виджет 1.2: график 14 дней, ▲/▼ к прошлой неделе, лучший ролик 14 дней, идея дня, уведомления (ждёт «ок», вышел ролик, всплеск, новые идеи, обновление приложения). Версию для автообновления сайт берёт из `versionCode` в `android-widget/app/build.gradle.kts`.
- Не сделано: детект претензий Content ID (через API канала недоступен).

## 30.10 — Codex: Чигур, сценарий и 2 финала готовы; Shorts заблокированы киноисходником

- Новые решения Дениса внесены в AGENTS.md и задачу: S6-D25, утверждённые название «Антон Чигур: почему с ним нельзя договориться» / обложка «ВЫБОРА НЕТ?», сценарий параллельно исследованию, сначала оба Shorts приватно без даты. Повторного согласования стиля/названия не нужно.
- `longform/chigur/SCRIPT_DRAFT.md`: оригинальный черновик, 1240 слов, 13 сегментов, расчёт 9–10,5 мин. `FACTS.md`: Miramax/Academy/сценарий; ранняя публикация сценария отличается от финальной Карлы, поэтому точные кадры и дубляж остаются pending. Точные in/out не выдуманы, финальную озвучку длинного не запускали.
- Отчёт `reports/research/2026-11-kino-razbor-competitors.md` дополнен браузерным чтением четырёх выбранных страниц в пределах разрешённых 40 минут. Три ASR-экспорта получены, DUmEBFY5aa8 недоступен; у g95tFuNadYU первые ~21 с — интеграция. Фактическое воспроизведение на страницах не началось (0:00/readyState=0), поэтому видеоряд/прослушивание/проценты не подтверждены; остальные с явной пометкой. Никаких входов, лайков, комментариев, подписок, покупок. Браузерная часть завершена, вкладка закрыта.
- Shorts: собственные монтажные планы A (Карсон/попытка откупиться) и B (Карла/отказ от правил) — `shorts/movie_funnel_202611/TREATMENT.md`; два конкретных паспорта — `PUBLISH.md`. Не повтор прежней опубликованной заправки.
- Оба новых финала Димой +4% сохранены в `media/tts/movie_funnel_202611/` (успешный [TTS run 41116949032](https://github.com/osminoog09-star/Shorts/actions/runs/41116949032)). Первый run 41115427401 получил end_a, end_b не отдал звук; его повтор синтезировал оба, но упал на add/add старого end_a. Восстановлено новым запуском с текущего main и кэшем, без смены голоса и секретов.
- `shorts/movie_funnel_202611/host/`: отдельная копия утверждённого HostCorner с props этого проекта, Rhubarb для A/B, код и контрольные кадры, ProRes-рендеры фактически выполнены; компактные VP9 alpha overlays сохранены. Голосовые манифесты/QA — `audio/voice_manifest.json`, `QA.json`. Full decode обоих ProRes и VP9-alpha PASS; A neutral/CTA PNG просмотрены. Это overlays, **не готовые кино-Shorts**. Прослушивание полного микса и фактический кино-кроп ещё не выполнены.
- **Блокер:** исходник `/mnt/user-data/uploads/1000026134.mp4` в Library не найден; старый опубликованный MP4 не заменяет новые сцены. Найдены RU-промоклипы Boxoffice, но стандартная загрузка через [movie-edit-source run 41116055139](https://github.com/osminoog09-star/Shorts/actions/runs/41116055139) остановлена требованием YouTube «подтвердите, что вы не робот». Без входа/cookies/обхода. Нужны русские исходники разговора с Карсоном и финального разговора с Карлой (или доступный файл фильма), желательно с запасом начала/конца и без чужих титров.
- Общий `movie-edit-source.yml` теперь поддерживает изолированные source_jobs/*.json и сохранение исходного аудио (старый путь делал лишь немой восьмисекундный черновик). Скрипт `tools/movie_edit/fetch_sources.py`, job movie_funnel_202611.json; новый одноразовый workflow не добавлялся. Старые URL-defaults сохранены. Синтаксис YAML/py_compile проверены, end-to-end получение заблокировано YouTube.
- Готовых кино-MP4 и новых YouTube ID нет; **ничего не залито и не запланировано**. `publishing/queue.json` не пополнялся фиктивно готовыми файлами, publish_at не добавлялся. После исходника: выбрать реальные in/out/слова → кроп/субтитры/музыка → полный QA → ready manifests/passports → mode=upload без даты. Только отдельное «заливаем» разрешает schedule.

---

## 30.10 — Codex: ежедневная YouTube Analytics и отчёты настроены

- Выполнено поручение Дениса по AGENTS §13 и `skills/channel-analytics/SKILL.md`. Сборщик `scripts/youtube_analytics.py`, workflow `.github/workflows/youtube-analytics.yml`: ежедневно 07:20 UTC, вручную и при изменении сборщика в main. Использует `token_for('ru')` и проверку RU-канала; YouTube только на чтение.
- Выход: `reports/youtube/daily/YYYY-MM-DD.json` + `.md`, `reports/youtube/latest.json` для страницы студии; полный каталог загрузок с пагинацией, 10 Analytics-метрик по видео, трафик каждого видео за 28 дней и просмотры по дням. Контракт для Claude — `reports/youtube/README.md`; интерфейс студии не изменял.
- Журнал `reports/videos.csv` сохраняет редакционные поля/возрастные измерения; новые текущие метрики пишутся в `yt_*` с границами периода. Неизвестные ID не склеиваются по похожим названиям. Пропуски = null, не ноль. Точные скользящие 48ч/7д из дневного API не выдумываются; период и задержка явно отмечены.
- Числовые основы недель/месяцев обновляет Actions в `reports/youtube/weekly/` и `monthly/`. Включена отдельная автоматизация Codex «M1lash — аналитика канала» (ежедневно около 12:00 Europe/Tallinn): контроль сбора; по вс полные `reports/weekly/YYYY-Www.md`, 1-го `reports/monthly/YYYY-MM.md`, обновление learnings и Текущей стратегии, уточнение задержавшихся данных. Первые оба отчёта — 01.11.2026 (W44 + октябрь). Автоматизация ID `6ae4e8a720108191bead473f75789944`.
- Проверено: локально и в Actions 8/8 тестов `tests/test_youtube_analytics.py`, компиляция и полная пробная запись на моках. Реальный сбор run [41111651453](https://github.com/osminoog09-star/Shorts/actions/runs/41111651453) завершил сбор/коммит/загрузку артефакта без ошибок (логи job 124254914832). Коммит данных `62895c68a4e19ed1df3e4c92d6dae81442b21de8`: 38 загрузок в каталоге, у 30 есть строки Analytics, все 10 метрик доступны (`unsupported_metrics=[]`), остальные остаются null. Снимок 30.10 19:01:29 UTC, API end=29.10, последний возвращённый день просмотров=28.10 — задержка явно отражена. Первый запуск выявил неподдерживаемую сортировку video; исправлено на -views с опорным views. Ошибка основного views-запроса теперь прерывает сбор, не маскируется пропусками.
- Пауза производства соблюдена. Публикации, очередь, секреты и чужие проекты не изменены. Осталось Claude подключить `latest.json` к своей странице студии; аналитические выводы до фактических данных не объявлены.

---

## 30.10 21:00 — YouTube подключён напрямую; задача Codex — аналитика (Claude)

- OAuth работает: `youtube-auth-check` run 41109859291 = success (канал M1lash UC919eyHbOIgjsnH8z70pmZw). Секреты добавлены (через GPT Agent).
- `scripts/youtube_direct.py` + `youtube-direct.yml`: новый режим. Манифест **без `publish_at`** → заливка приватно на просмотр Денису; после его «ок» вписать `publish_at` и запустить `mode=schedule` (videos.update publishAt). Тесты 11/11.
- **Для Codex (решение Дениса 30.10): аналитика теперь твоя** — см. AGENTS.md, раздел 13. Нужно: workflow раз в день (YouTube Analytics API: views, engagedViews, averageViewPercentage, averageViewDuration, subscribersGained, likes, comments по каждому видео + источники трафика) → `reports/youtube/daily/<дата>.json` и сводка, чтобы Claude мог показать цифры на странице «Студия M1lash» (`publishing/studio/`). Плюс недельный (вс) и месячный отчёты по `skills/channel-analytics/SKILL.md`. Токен: `token_for('ru')` из `scripts/youtube_direct.py`.

---

## 30.10 20:30 — Прямой доступ к YouTube (OAuth): остановились на шаге токена (Claude)

- Сделано Денисом: Google Cloud проект **Youtube**, включены YouTube Data API v3 и YouTube Analytics API, экран согласия **M1lash Studio**, External, **In production** (home: osminoog09-star.github.io/Shorts/, privacy: …/Shorts/privacy.html — `motion-studio/privacy.html`), OAuth-клиент Web application, redirect `https://developers.google.com/oauthplayground`.
- Не сделано: обмен кода на refresh token в OAuth Playground дал **401** — почти наверняка испорчен Client secret при вставке с телефона (пробел после `GOCSPX-`). Секреты `YOUTUBE_OAUTH_CLIENT_ID`, `YOUTUBE_OAUTH_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN_RU` в GitHub ещё не добавлены; проверка `youtube-auth-check` (run 41107173404) — failure, ожидаемо.
- Дальше: Playground → шестерёнка (свои ключи, без пробелов) → scopes `youtube youtube.upload yt-analytics.readonly` → Authorize → Exchange → 3 секрета → запустить `youtube-auth-check`. Денис продолжит с компа/спокойно.
- Открыто (не решено Денисом): публикация приватной заливкой с таймером и ежедневная аналитика на странице студии; перезапуск эксперимента стилей и образцы 5 с во всех 9 стилях (страница «Стили M1lash»).

---

## 30.10 — Настройка студии: единый свод правил, чистка workflows, новые скилы (Claude)

- **Решения Дениса 30.10** (grill-me): голос Дима/Света через **Azure Speech** (до подключения — workflow `TTS`); публикация пока **вручную Денисом** через страницу «Студия M1lash»; кино-Shorts публикуем, **риск по правам принят**; **производство на паузе**, пока настраиваем.
- `AGENTS.md` переписан в **единый свод** без противоречий; старый и `CODEX_NOTICE.md` — в `docs/archive/`. `CODEX_NOTICE.md` теперь указатель. Добавлен `CLAUDE.md` (`@AGENTS.md`), чтобы Claude Code читал тот же свод. Из `STRATEGY.md` убраны дублирующие правила.
- 30 одноразовых workflows → `.github/workflows-archive/` (README там). Осталось 25 общих.
- Новые скилы: watch, humanizer, все 52 marketing (`mkt-*`); программы для ПК — `scripts/pc/`, `LOCAL_PC_PLAN.md`.
- Не сделано по паузе: «Топ-5 недели» на вс 01.11 (слот свободен), «Римский бетон» на сб 31.10.
- **Для Codex:** прочитай новый `AGENTS.md` целиком, особенно разделы 0 (пауза), 3 (Azure), 6 (паспорт публикации вместо Metricool).

---

## 30.10 — Топ-5 новостей ИИ недели (вс 01.11 10:00): NO-GO, не сделан (Claude, плановый запуск)

- Слот вс 01.11 10:00 в Metricool свободен (проверено 30.10 06:24 UTC). Выпуск НЕ создан и НЕ поставлен.
- Причина: правило голосов владельца 28.10 требует Диму `ru-RU-DmitryNeural` (Edge TTS) без fallback. Из облачной среды `speech.platform.bing.com` недоступен (DNS: Name or service not known), `bot_tts.py` дал бы Piper/RHVoice — это запрещено. Плюс ведущий должен быть в формате HostCorner, а шаблон `BotSeries` newsdesk устарел.
- Что нужно: рабочий Edge TTS (workflow `TTS` на GitHub Actions) либо решение владельца. Слот вс 10:00 остаётся свободным; по правилам без Димы релиз не делать.

---

## 28.10 — Movie mystery 001: новый русскоязычный кино-Shorts, приватный V4 PREVIEW

- По запросу владельца выбран **НОВЫЙ фильм**, сильная аренная сцена. Название раскрывается **исключительно последним словом** ведущего в готовом видео, отсутствует в публичном title/description/tags/pin/thumb/caption и имени MP4. Реальное название только для производственного контроля в `tools/movie_edit/releases/movie_mystery_001.json` поле `internal`.
- Источники отбора: первый скачанный clip с жёсткими чёрными полями и английскими титрами отклонён; второй fan-edit montage с несоответствующими репликам кадрами отклонён. Выбран цельный исходный фильм на русском, получен GitHub Actions run 40595996153, artifact 12776800730, тайминги речи проверены Whisper run 40596420297 artifact 12776990853.
- Звук/музыка: оригинальный русский диалог актёров, выделенная лицензированная CC BY 4.0 оркестровая композиция Kevin MacLeod 'Five Armies', автоматизация громкости под реплики, активные звуковые акценты. Атрибуция без фильма записана в публичное описание релиз-манифеста. Артефакт voice/music GitHub Actions run 40595325262, artifact 12776570080.
- Финал: исходный утверждённый визуальный ведущий M1lash; полный CTA и озвучка названия **одной и той же моделью** `piper:ru_RU-dmitri-medium`, последний звук — только название фильма. Видеотитра с названием НЕТ. Важно: этот офлайн Дмитрий **отличается от одобренного прежнего Liam**; оригинальные виземы аватара не были переписаны под новую модель. Следовательно, это **ЧЕРНОВИК ДЛЯ ОЦЕНКИ**, не завершённый релиз по строгому правилу ведущего; нужна однотембровая утверждённая озвучка + синхронизация рта.
- V4 local MP4: `/mnt/data/m1lash_movie_mystery_001_ru_v4_PREVIEW.mp4`, 44.921333 s, H.264 1080x1920 30fps AAC, 14,992,810 bytes, SHA256 `cd379a3e7be65ef512337eff5b35683ab6ffbe74d908d735b6f98e6f494d0f6a`; FFmpeg full decode PASS, визуальные QA-кадры сцен/финального кадра просмотрены, исправлены кадрирования лиц; в финале нейтральный CTA и вопрос «УГАДАЛ? ПИШИ В КОММЕНТАРИЯХ!». Полного непрерывного человеческого прослушивания не заявлять.
- Production sources: local `/mnt/data/new_movie_render.py`, final footer remux separate; скрипт ещё не переносился в GitHub, воспроизводимой кнопки pipeline для этого MP4 в repo пока нет. Публичная упаковка и антиспойлер-манифест сохранены в `tools/movie_edit/releases/movie_mystery_001.json`, статус `publication.publish_ready=false`; guard GitHub Actions triggered run 40598283939.
- Правовой блокер: разрешение на повторное использование защищённой кино-сцены/русского дубляжа не получено. Отсутствие названия в метаданных не заменяет разрешения и не позволяет обходить Content ID. Не публиковать автоматически и не занимать чужой слот; MP4 только для приватного просмотра.

---
## 28.10 — AI News RU Shorts: готов MP4, только ручная загрузка (GPT-6)

- Подготовлен выпуск на 28 октября о трёх фактах 26–27.10: объявление OpenAI о трёх научных результатах (проверка учёных продолжается); сделка NVIDIA–Meta на $3 млрд и Muse; раскрытые Anthropic четыре агента, получившие доступ к реальным системам при ошибке тестовой среды. На каждую новость два источника, ссылки и ограничения в `reports/research/2026-10-28-ai-news-shorts.md`.
- Новый стиль **S1-D25**, рисованная тушь с лёгким параллаксом и оригинальной процедурной музыкой; отдельные новости + реакции ведущего. Вся речь — бесплатный офлайн Piper **ru_RU-dmitri-medium**: Microsoft Edge DmitryNeural не отдал аудио; подмена отмечена честно, не путать два голоса. Финальные 5,8 с из заранее одобренного `videos/m1lash_outro_short_ru.mp4` (Liam + музыка Laeko NCS). Новая нарисованная фигура ведущего в основных сценах — **не точная утверждённая HostCorner.tsx/PiP-композиция**, требуется личный визуальный просмотр и решение владельца перед публикацией.
- MP4: `videos/m1lash_ai_news_2026_10_28_ru.mp4` — **53.125 с, 1080×1920 H.264/AAC, 4 041 652 байта**. GitHub Actions run [40595696797](https://github.com/osminoog09-star/Shorts/actions/runs/40595696797) SUCCESS. ffmpeg full decode PASS, ffprobe кодеки и размер PASS, 6 PNG контрольных кадров есть в artifact [12776850490](https://github.com/osminoog09-star/Shorts/actions/runs/40595696797/artifacts/12776850490). Человеческий просмотр кадров и полное субъективное прослушивание не заявлены.
- Ссылка для владельца: https://raw.githubusercontent.com/osminoog09-star/Shorts/main/videos/m1lash_ai_news_2026_10_28_ru.mp4 . **НЕ опубликовано, НЕ поставлено в очередь, никакие слоты не занимались.** Пользователь загрузит сам. Пред публикацией обязательный NCS-credit из `shorts/laeko_host_demo/README.md` и сверка применимости актуальной NCS-лицензии.
- Скрипт `scripts/render_news_20261028.py`, workflow `.github/workflows/news-ai-20261028.yml`. Edge TTS сбой был устранён стабильным бесплатным резервным голосом. В `reports/style_experiment.md` добавлено как готовое, без YouTube ID и без выдуманных метрик.

---

## 28.10 — новое окончательное правило M1lash movie-edit / mystery Shorts (решение владельца)

- Владелец утвердил монтаж предыдущего «Интерстеллара» по картинке/музыке, но **изменил обязательные правила упаковки и reveal**: **НИКОГДА не писать название фильма в публичном YouTube title, description, tags, hashtags, pinned comment, thumbnail, публичном имени MP4, текстовых субтитрах, финальном титре**. Название разрешено **только как последняя голосовая фраза** в самом видео после полной просьбы лайк/подписка/спасибо.
- **Голос всей заключительной речи и названия должен быть идентичным** («Дима — тот же голос, что у нашего ведущего»). Ранее V3 содержал CTA одобренным Liam, но одно название — Piper Dmitri: это **НЕ отвечает новому требованию**. Также в предыдущей версии была видимая карточка с названием — **нужно удалить** для следующего выпуска/финального исправления V3. Не объявлять эту V3 соответствующей новому стандарту и не предлагать её к загрузке без доработки.
- Важно по исполнению: текущий одобренный CTA `videos/m1lash_outro_short_ru.mp4` озвучен **Liam**, а доступный офлайн Piper Dmitri / облачный Microsoft DmitryNeural имеют **другой** тембр; для единого звучания надо получить последнее название **тем же Liam** либо записать весь CTA и название **тем же DmitryNeural** с обновлённым липсинком. При недоступности нужной записи статус **«черновик / голос не согласован»**. Voice ID проверять и аудио слушать.
- Качество нового формата: киноряд заполняет 1080×1920 без полос, русские диалоги, синхронные кинетические субтитры, эмоциональные наезды и рефрейм лиц; лицензированная подходящая музыка с ducking под речь, фирменная музыка/ведущий лишь в авторской концовке. Права на исходный фильм и лицензии музыки проверять отдельно; скрытие названия не обход Content ID.
- Инструкции **фактически записаны в main**: `AGENTS.md`, `CODEX_NOTICE.md`, `STRATEGY.md`, `tools/movie_edit/README.md`, `tools/movie_edit/MYSTERY_SHORTS_TEMPLATE.md`. Добавлены `tools/movie_edit/mystery_release.example.json`, `tools/movie_edit/validate_mystery.py`, тесты `tools/movie_edit/test_validate_mystery.py` и workflow `movie-edit-mystery-guard.yml`. GitHub Actions run **40593819495 success** (шаблон и регрессионные проверки). Это автоматический контроль текстового манифеста, **не** доказательство что реальный MP4 имеет правильное звучание или закрытые права. Последняя реально собранная V3 автоматически не изменена.
- Никаких новых видео, бронирований слота или YouTube-публикаций этим обновлением не сделано.

---

## 27.10 — «Интерстеллар» Shorts V3: новый саундтрек и офлайн-голос Dmitri (GPT-6)

- По обратной связи владельца пересведён V2: оригинальный русскоязычный кинодиалог остаётся, под сценой добавлен лицензированный CC BY 4.0 кинематографичный трек Kevin MacLeod — «Interloper», первые ~41,6 секунды фильма. Выбран фрагмент трека 112,0–153,6 с; автоматизация громкости для затухания под русскими репликами, выделены моменты стыковки; финальное видео остаётся **полностью вертикальным 1080×1920**.
- **Утверждённая концовка НЕ ПЕРЕОЗВУЧЕНА:** оригинальный аватар + Liam с полноценной фразой «Подпишись! И спасибо всем, кто досмотрел и поставил лайк», оригинальная музыка Laeko, 5,8 с; за ней карточка и последнее слово «Интерстеллар».
- Важное различие голосов: Microsoft Edge ru-RU-DmitryNeural НЕ УДАЛОСЬ получить (edge-tts v7.3.1 ответил NoAudioReceived даже при повторной попытке через альтернативный endpoint). Вместо прежнего Piper Denis название теперь произносит офлайн-модель **Piper ru_RU-dmitri-medium** (не тот же тембр, что DmitryNeural). Нельзя утверждать, что используется точный Microsoft Дмитрий.
- Проверен финальный файл только текущей сессии /mnt/data/M1lash_Interstellar_Short_RU_V3_DMITRY_MUSIC.mp4, 49.4903 с, 1080×1920 30fps H.264/AAC stereo, 19 241 316 байт, SHA256 8eaabb35836ff14921242757f9440495722a1933f8b89531a8c3a7563e3ef4d3. FFmpeg full decode PASS, контрольные кадры на 0.2, 12.3, 25, 37.3, 41.8, 44.9, 47.2, 48.6 с изучены; audio peak -1.3 dB, mean -14.1 dB. Полного субъективного прослушивания не было. Локальный рецепт /mnt/data/interstellar_mix_v3.py; не публиковался в GitHub как runnable source.
- Музыкальный credit (обязателен в описании YouTube): «Interloper» Kevin MacLeod (incompetech.com) / Licensed under Creative Commons: By Attribution 4.0 License / http://creativecommons.org/licenses/by/4.0/ . Трек подвергнут обрезке и регулировке громкости; оригинал https://incompetech.com/music/royalty-free/index.html?Search=Search&isrc=USUAN1100401 .
- Movie-картинка, диалог и исходный звук защищены авторским правом, права для M1lash на их повторное использование не проверены, YouTube Content ID не обходить. На YouTube не публиковалось / в календарь не добавлялось. Категорию будущей публикации согласовать отдельно.

---
## 27.10 — «Интерстеллар» V2: настоящий вертикальный Shorts + утверждённый финал

- Исправлен full-bleed 1080×1920 (9:16): вертикальные крупные планы без горизонтальной полосы и звёздных полей сверху/снизу. Выборочно проверены кадры на входе, середине и финале. Исправлена также рассинхронизация V1: первая сцена видео и звук теперь из одних секунд оригинала 31,4–39,0.
- Согласно AGENTS.md, утверждённое короткое аутро целиком взято из videos/m1lash_outro_short_ru.mp4 (5,8 с): ведущий, Liam, липсинк, музыка Laeko и реплика «Подпишись! И спасибо всем, кто досмотрел и поставил лайк». ТОЛЬКО ПОСЛЕ неё отдельная ~2,07-секундная карточка и последнее произнесённое слово «Интерстеллар». Название во время сцены не показывается.
- Ограничение озвучки: короткое произнесение названия выполнено доступным бесплатным Piper Denis; тембр отличается от Liam, используемого в утверждённой CTA. Не выдавать последний голос за Liam.
- Новый локальный MP4: /mnt/data/M1lash_Interstellar_Short_RU_V2_FULLSCREEN.mp4 (только файл текущей беседы, не GitHub URL), 49,4897 с, 1080×1920 30fps, H.264/AAC, 19 073 333 байт; SHA256 ae18b1dca62eb1e300763c469eca621e5f68919c69fa4b1efd332e439cb0db53. FFmpeg full decode PASS; QA контрольных кадров проведён. Локальный скрипт: /mnt/data/interstellar_edit_v2.py.
- В YouTube не загружено, не опубликовано, в календарь не добавлялось. Права на кинофрагмент / аудио и Content ID не проверены, требуется отдельная оценка перед публикацией.

---
## 27.10 — новый movie-edit «Интерстеллар»: русский Shorts, название говорит диктор только в конце (ChatGPT)

- **Смонтирован приватный MP4 для ручной загрузки:** `M1lash_Interstellar_Short_RU_20261027.mp4` (44,421 с; 1080×1920 / 30 fps, H.264 + AAC, 9 332 075 байт). Файл выдан как sandbox-ссылка в текущем разговоре; **не выдавать локальный sandbox за публичный GitHub URL**.
- Источник: русская сцена «Экстремальная стыковка с Эндюранс», Rutube `https://rutube.ru/video/999be68c16d0f76b343345dd7ae56c6a/`. Получена через GitHub Actions run `40584590279`, artifact `12770703472`; тайминг русской речи транскрибирован run `40585221784`, artifact `12771820667`.
- Монтаж: кульминационная реплика «Это невозможно — Нет, это необходимо»; команда экипажа/стыковка/уход с орбиты; оригинальная русская дорожка фильма, титры ниже основного видеокадра, космический фирменный 9:16 фон, одобренный ведущий M1lash только в финальном кадре. Единственные слова диктора — «Интерстеллар!», синтезированная бесплатная RU озвучка Piper Denis; **не оригинальный Liam**. Название фильма до финала не раскрывается.
- QA: подтверждённая 44,421-секундная версия, полный ffmpeg decode PASS, 9 контрольных кадров проверены; исправлены перекрытие актёров титрами, чужая кнопка подписки из исходного аутро, лишний дублированный логотип. Полного человеческого аудиопрослушивания не заявлять. SHA256: `3f4821f94128102a90eeac50d8e1eb03296540ada4dfc9968c1da06c73d045bd`.
- **На YouTube не загружено, не опубликовано, слот не занят.** Оценка прав на кадры, кинодиалоги и оригинальную музыку обязательна до публикации; разрешение другим перезаливщикам не означает разрешения M1lash. Предыдущую идею «Брат 2» пользователь отверг — не развивать и не публиковать.

## 27.10 — «Волк с Уолл-стрит»: русская озвучка V3 (GPT-6)

- По просьбе владельца на базе V2 (сохранён монтаж, вертикальная картинка, титры и фирменная концовка M1lash) выполнена русификация аудио на **всём кинофрагменте**: 8 отдельных RU реплик, первые 4 — контекст отказа уходить, следующие 3 — нарастающая фраза «Я никуда не уйду», последняя — «Шоу продолжается! Это мой дом!».
- Исходная английская речь в фильме приглушена до -23.7 дБ; атмосферный фон/реакция толпы оставлены, звуковая дорожка утверждённой концовки не менялась. Использована **синтетическая бесплатная русская мужская нейроозвучка Piper Denis**, это НЕ дубляж Сергея Бурунова.
- Артефакт текущего чата `/mnt/data/M1lash_Wolf_Wall_Street_Short_v3_RUS_DUB.mp4`, 35.285 с, 1080×1920 30 fps H.264 + AAC stereo 48 kHz, 10 341 715 байт, SHA256 `3355e41d9c6617d1a88c378fbca0086d97d8e1d4594bf726f2a962763a9f9224`. Полный ffmpeg decode PASS, все 8 voice-clips ненулевые, короткие отрывки растянуты по времени с сохранением тона. Скрипт временного рендера в артефактах этой беседы `/mnt/data/dub_wolf_v3.py`; ссылка ChatGPT не равно GitHub URL.
- GitHub Actions бесплатного TTS `40580728786` завис в ожидании Edge TTS; добавлен независимый fallback `.github/workflows/wolf-movie-ru-local-piper.yml` (run `40581586358`: SUCCESS, voice artifact `12769652393`). `jobs/tts/wolf_movie_ru.json` содержит реплики; `.github/workflows/wolf-movie-ru-voice-package.yml` — эксперимент облачного Edge TTS, который не требуется для выпуска V3.
- **НЕ загружено в YouTube, НЕ запланировано.** Правообладатель фильма может предъявить Content ID/претензии на кинофрагмент; перед публикацией нужен просмотр и оценка прав. Если владелец захочет настоящий российский официальный дубляж фильма, это отдельная дорожка, отсутствующая в данной сборке.

---

## 27.10 — «Волк с Уолл-стрит» movie-edit: реальная сцена и исправленная вертикальная сборка (GPT-6)

- Найден эталон `tools/movie_edit/edit.py` для «Скажи моё имя» / Breaking Bad; выбран The Wolf of Wall Street (2013), сцена «I'm not leaving». Автоскачивание оригинального YouTube Paramount упёрлось в bot-login; первый Dailymotion x4flet5 оказался любительской реконструкцией (НЕ использовать!). Реальные кадры Ди Каприо и речь получены из публичного фрагмента Binge Society на GanJingWorld; источник указан в изолированном workflow `.github/workflows/movie-edit-wolf.yml`.
- GitHub Actions `40575565893` подтвердил скачивание настоящего видео, render + full ffmpeg decode PASS. Запуск `40576348885` также PASS и сохранил короткий 50-секундный исходный отрезок `work/wolf/source_original_scene.mp4` в артефакте GitHub `12768305258`; не путать архив с прямым MP4.
- Проведён просмотр контрольных кадров: исходный auto-crop из `render.py` оставлял чёрные поля и местами срезал лица. В локальной медиасессии сделан **УЛУЧШЕННЫЙ v2, 35.2207 с**: H.264 1080×1920 30fps + AAC stereo 48kHz; 3 фразы с синхронизированными RU титрами, оригинальная английская киноречь, композиция 358×510 по центру выступающего поверх размытого заполняющего фона, кредиты Paramount и Binge Society, фирменный короткий финал M1lash. Полный ffmpeg decode PASS, выборочно проверены кадры 1.5, 8, 14.5, 25, 28 с; аудиопик −2.9 dB, средний −20.5 dB. Файл **только в артефактах текущего ChatGPT чата** `/mnt/data/M1lash_Wolf_Wall_Street_Short_v2_RU.mp4`, SHA256 `a58cb2af4e10bb6d076efb874d6761bc46eb528691f1abeeb1c8aa4042f5fcf5`. Этот путь не является ссылкой GitHub и не обещает хранение в GitHub.
- Для следующего прохода: перенести улучшенный reframing из локального рендера в `tools/movie_edit/wolf_wall_street/render.py`, добавить проверку лиц и помечать неподходящие source re-enactments; окончательно прослушать на телефоне и проверить права на фильм/аудио. **Это черновик, не опубликован, не поставлен в очередь.** Слоты Metricool/YouTube не трогали.

---

## 27.10 — movie-edit «Волк с Уолл-стрит»: независимый черновой рендер (GPT-6)

- По просьбе владельца найден эталон «Скажи моё имя» (Breaking Bad S5E7; published 25.10, YouTube XANzL3z9wqY), инструменты `tools/movie_edit/edit.py`, `base.py`, `kinetic.py`, `audio.py`, `studio/src/EditOutro.tsx`; существующий источник `source_urls.txt` указывает на официальный промоклип Paramount `g07Xxr20L9s` «I'm Not Leaving».
- Добавлен **изолированный** рендерер `tools/movie_edit/wolf_wall_street/render.py` (ASR для нахождения повторов цитаты, 9:16, приближение камеры, крупный русский кинетический текст, низкочастотная процедурная подложка, утверждённая концовка `videos/m1lash_outro_short_ru.mp4`, если она доступна). Новый workflow `.github/workflows/movie-edit-wolf.yml` запускает private-draft сборку при пуше самого workflow или вручную; вывод — 7-дневный GitHub Actions artifact `m1lash-wolf-wall-street-draft`, **не публичная ссылка на MP4**.
- Локально синтетический 3-секундный исходник проверен на базовом аналогичном рендерере: H.264/AAC, фильтры FFmpeg, русские титры и полный decode прошли. **Новый workflow/реальный промоклип и итоговый MP4 ещё не подтверждены в Actions**: возможны блокировка скачивания YouTube, ошибки ASR, некорректная привязка фраз или ограничение ресурсов. Нужны QA фактических кадров и прослушивание перед релизом.
- **Не опубликовано / не поставлено в очередь.** Официальный promotional clip не равен лицензии на реиспользование; права на киноряд/оригинальный звук нужно оценить до публичного релиза. Очередь YouTube/Metricool, другие проекты и готовые видео не менялись.

---

## 27.10 — исследование нового длинного выпуска про домашних роботов (Codex)

- По поручению владельца изучены правила/шаблоны, доступные публичные YouTube-примеры и обсуждения на других платформах. Выбран бриф «Роботы уже работают. Почему дома их до сих пор нет?», 12–13 мин, S9-D3; самостоятельный выбор разрешён текущим запросом.
- Результат: [исследование, 24 сцены и промпты](reports/research/2026-10-27-robots-longform-brief.md). Есть источники с датами, границы подтверждения, 3 концепции упаковки, 2 Shorts. **Это бриф, НЕ готовый MP4.**
- vidIQ: 25 подписчиков / 19 публичных видео / 10 931 просмотр — снимок, не рост периода. Остаток 1 кредит, израсходовано 0. Metricool за 27.09–26.10 вернул null/пустые метрики; удержание/CTR/причины результата не установлены. TikTok недоступен для веб-поиска. Полный просмотр конкурентов не выполнялся.
- Принцип сюжета: различать демо, телеоперацию, автономную работу и анонсы. Старые обзоры NEO 2025 не выдавать за состояние 2026; Digit 5 и часть новых платформ планируются на 2027. Непроверенные инфоповоды не включать в озвучку.
- Осталось до производства: сверить с опубликованными новостями 26.10; закончить второй независимый фактчек чисел; полный сценарий, короткая техническая проба, озвучка, сцены, звук/лицензии, полный QA экспорта.
- Календарь, чужие файлы и публикации не изменены; новые посты/автоматизации не создавались. Не резервировать старые «свободные» 28/29.10: далее в HANDOFF они уже обозначены занятыми.

---

## 26.10 — «Последний допуск» серия 1 переработана в ПОЛНЫЙ 13:30 выпуск (ChatGPT)

- **Готов отдельный экспорт, НЕ опубликован:** [MP4 — скачать](https://d2ol7oe51mr4n9.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/1c018130-74ee-47d9-bcf3-65917c6371e3.mp4) — `EP01_LAST_ACCESS_FULL_13m30_RU.mp4`, длительность 810.542 секунд = 13:30.5, 43 226 360 байт, H.264 1280×720 24fps / AAC mono 44.1kHz. Обе медиа-ссылки загрузки проверены, видео CDN HTTP 200. [Обложка JPG](https://d2ol7oe51mr4n9.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/76e107fb-fc0a-49ae-881c-72514ccdcba2.jpg).
- Переработаны первоначальные 3:21 в полный 13:30 сюжет: отсек P-4 → прекращение аварийного сброса → домкрат, эвакуация Тессы и двух пассажиров → медосмотр Ины → спор с Ореном на мостике → архивная запись предыдущей Мары → 17-секундный CTA в пользу содержательных зрительских теорий, лайка и подписки → утверждённая концовка M1lash. Оригинальное содержание, стилизованная low-poly 3D-постановка и процедурная анимация, **не AAA-качество и не полноценный motion capture**.
- Озвучка: первые 35 реплик — HeyGen русские голоса, ещё 93 реплики — локальные бесплатные Piper RU голоса; звуковые эффекты и музыка процедурные, 128 русских SRT субтитров (`/home/user/last_access_ep01/EP01_RU_subtitles.srt` в текущей медиасессии); подготовлены таймкоды, описание и закреплённый комментарий. Видеомонтаж H.264/AAC проверен ffprobe и выборочными кадрами в начале, середине и конце. **Полное субъективное прослушивание и покадровый QA не проводились; перед основной публичной публикацией рекомендуем личный просмотр.**
- Новая версия **ЗАМЕНЯЕТ старую 3:21 черновую пробу как кандидат**; старую пробу не публиковать. Видео и картинку загрузили в Higgsfield Media, оба media_confirm uploaded. На YouTube ничего не загружено и не запланировано; владелец будет публиковать вручную. Сетка Metricool не изменена.
- Следующее: проверить звук героев и мимику на реальном устройстве, провести 10+мин зрительский тест, при необходимости поправить сцены до релиза; в следующей серии сохранять открытые тайны и технические последствия.

---

## 26.10 — QA визуала первой части: не готово к основной публикации

Проверены несколько реальных кадров MP4 «Последний допуск — Часть 1» из экспортированной версии (включая 0:04 и 2:58). Текущее изображение — **базовый процедурный 2D motion-comic с упрощёнными лицами и плоскими декорациями**, а НЕ качественная 3D-анимация/полноценный мультсериал, ранее запрошенный владельцем. Длительность 3:21, а не плановые 10–15 минут. Техническая проверка encode/decode ранее прошла; аудио полностью субъективно не прослушано. **Не рекомендовать выпуск как готовую первую серию.** Сохранить MP4 как черновую визуальную пробу. Перед публикацией: закрепить визуальные модели героя/корабля, разработать детальную раскадровку, улучшить animation/camera/SFX, сделать полноценное звуковое QA, а также записать соответствующий сюжету голосовой CTA; не публиковать от имени пользователя автоматически.

---

## 26.10 — «Последний допуск»: анимационный видеопилот, часть 1 (ChatGPT)

- **Готов оригинальный MP4 для ручной загрузки**, не опубликован, не запланирован: [скачать видео](https://d2ol7oe51mr4n9.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/04775133-4802-4e44-92ee-72bf53388506.mp4) (1280×720, H.264/AAC, 20 fps, 201.428 секунд = 3:21, 8 508 932 байта).
- [Обложка JPEG](https://d2ol7oe51mr4n9.cloudfront.net/user_3IucDWofuMZGRDc047d7wjIe7So/776d2689-b6b0-41ea-99ae-4f48e627d1b1.jpg) (1280×720). Файлы опубликованы в пользовательском медиа-хранилище Higgsfield через подтверждённые media ID; оба URL проверены HTTP 200.
- В видео сцены 1–5 ПИЛОТА: смерть капитана по журналу (18 ч), биосканер 312 против реестра 311, инженер Лев, технический лаз и неверный жёлтый рычаг / разгерметизация. Верстка — **процедурно анимированный 2D motion-comic** с движущимися элементами, панорамами, HUD, сменой планов, диалогами и SFX; НЕ рендер полноценной 3D-анимации и НЕ полная серия на 12–13 минут. Сценарные источники: `/last_access_project/EP01_SCREENPLAY.md`, `SERIES_BIBLE.md`, `BOOK_01_PART_I.md` в файлах текущей сессии.
- Русские диалоги: 35 озвученных реплик (Мара, КЕРН, Лев) через бесплатный лимит HeyGen, который **закончился** в ходе подготовки; в конце используется ранее утверждённая фирменная концовка M1lash `videos/m1lash_outro_short_ru.mp4` и экранный CTA про теории в комментариях, лайки, подписку. Часть 1 заканчивается на проблеме привода; эпизод целиком и часть 2 ещё не созданы.
- **Не загружать дубли**, не добавлять в Metricool без нового указания владельца и проверки очереди. Нет публикации YouTube и нет гарантий доходности/удержания; график остальных выпусков не изменён. Проверены H.264/AAC, 201.428 с, успешный ffmpeg decode, HTTP 200 для MP4/JPG; непрерывный человеческий просмотр и прослушивание не проводились.

---

## 26.10 — проверка реального состояния публикаций и безопасности (ChatGPT/Codex)

- Владелец поручил сделать всё самостоятельно, без дальнейшего ручного прохождения OAuth. Проверено через доступные коннекторы: виден YouTube **M1lash** (vidIQ), бренд Metricool **7605462**; **это не передаёт Google OAuth credentials в GitHub**. YouTube direct uploader остаётся неавторизованным. Пользователь показал Google Cloud приложение с секретом на скриншоте — перед реальным использованием этот client secret требуется перевыпустить. **Никогда не публиковать его ни в чате, ни в репозитории**.
- `Playlist sync` был неисправен: GitHub Actions 40287989294 (26.10) вернул `Missing required parameter: refresh_token`. Workflow теперь пропускает синхронизацию, если не заданы необходимые secrets, вместо бесконечных падений. Как только переменные появятся, расписание останется работающим; это НЕ загрузчик новых роликов.
- Для фильма `npc_exam_ru.mp4` (76,054 с / 24 777 893 байт): материал сохранён в личной ChatGPT Library как `/npc_exam_ru.mp4`; авторская упаковка в `/M1lash_Upload_and_Series_Handoff.md`. Запрошено **26.10 21:00 Europe/Tallinn**, разовое исключение из сетки. Проверка Metricool на 26.10–04.11: записи **21:00** с этим названием / файлом не найдено. **НЕ ЗАПЛАНИРОВАНО / НЕ ОПУБЛИКОВАНО**. Частную ChatGPT Library ссылку нельзя выдать за публичную ссылку на MP4; direct YouTube OAuth отсутствует, через GitHub Contents файл >16MiB не загрузить. Не обещать дату, не подменять время, не создавать дубль. Пользователь осведомлён о правовых рисках кинофрагментов; Content ID не проверялся.
- Готовое видео новостей от 26.10 в Metricool уже имеет статусы **PUBLISHED** для длинного `406502402` и Short `406502896`. Прочие назначенные на 27.10–02.11 посты сохранены, **не трогать**.
- Прямая публикация может полноценно заработать только после Google OAuth разрешения владельца. Не писать, что подключение сделано, если есть лишь код и offline tests.

---

## 26.10 — переход с Metricool на прямую публикацию YouTube

По прямому поручению владельца создан и **влит в main** безопасный ручной workflow `YouTube direct · review then schedule` и `scripts/youtube_direct.py`, два канала RU/EN, расписание `publishAt` (Tallinn), проверка OAuth-канала, защита от дублей `publishing/receipts`, dry-run по умолчанию. PR #1, GitHub Actions offline tests — PASS. Полная инструкция: `publishing/README.md`.

**Не заявлять, что публикации уже перенесены**: действующие Metricool слоты не менялись, OAuth/EN канал/секреты не проверены, загрузки напрямую не было. Для первого реального теста нужны секреты YouTube в GitHub и отдельный манифест согласованного видео; после этого можно переводить будущие публикации на прямую схему. График, все старые ролики, MP4 и чужие задачи не тронуты.

---

# HANDOFF — статус работы агентов (обновляй после каждого шага)

Формат: клетка сетки → автор → статус → где файлы → что осталось.

| Клетка | Автор | Статус | Файлы | Осталось |
|---|---|---|---|---|
| сб 24.10 19:00 длинное «Антикитера» | Claude | ✅ вышло https://youtu.be/s7YVEyinxDE | longform/antikythera, Release long-antikythera | обложку ставит Денис вручную (vidIQ кредитов нет) |
| вс 25 / пн 26.10 16:00 нарезки Антикитеры (find, moon) | Claude | ✅ в Metricool | videos/long/antikythera_short_*.mp4 | ✅ ссылка добавлена |
| вс 25.10 10:00 серия 2, пн 26.10 10:00 серия 3 | Claude | ✅ в Metricool | — | — |
| пт 30.10 10:00 скетч «Робот-телохранитель» | Claude | ✅ в Metricool | — | авто-скетч в ср пропустит (слот занят) |
| пн 02.11 10:00 скетч «Машина с ИИ» | Claude | ✅ в Metricool | — | авто-скетч в сб пропустит |
| запас: нарезка «jam» (заклинило) | Claude | черновик в Metricool | videos/long/antikythera_short_jam.mp4 | можно поставить в свободную клетку Claude |
| вт 27.10 19:00 длинное «Герон» | Codex | ✅ v2 11:10 в Metricool; первый фрагмент одобрен Денисом | longform/heron-codex; Release heron-v2-40097316135; SCHEDULE_V2.json | после выхода: ссылка в двух Shorts (задача 27.10 19:35) |
| ср 28 / чт 29.10 16:00 нарезки «Герон» | Codex | ✅ v2 в Metricool, 40 и 35,5 с, нативная вертикаль | videos/heron_short_*_v2_ru.mp4 | ссылка на длинное после его выхода |
| чт 29.10 10:00 новости | Claude | ⏳ авто (вт 27.10 08:21) | — | — |
| сб 31.10 10:00 скетч | Codex | ✅ в Metricool, ID 405847624, S6-D2, 38,9 с | codex/research-four-days: videos/sketch_schedule_ru.mp4 | после выхода вписать YouTube ID |
| сб 31.10 19:00 длинное «Римский бетон» | Claude | старт чт 29.10 (после сброса лимита) | — | готово и в Metricool к пт 30.10 |
| вс 01.11 10:00 топ-5 | Claude | ⏳ авто (пт 30.10 08:13) | — | — |
| вс 01.11 / пн 02.11 16:00 нарезки «Римский бетон» | Claude | вместе с длинным | — | к пт 30.10 |

| отклонено: «Пёс, палка и ИИ» | Codex | Денис 25.10 отклонил мультяшный стиль; НЕ публиковать | shorts/dog_big_stick | заменён реалистичной пробой «Второй ужин» |

- 25.10 (Claude): эксперимент movie-edit «Скажи моё имя» (Во все тяжкие 5×7, музыка Interloper) — по решению Дениса (исключение из сетки) выходит **сегодня 25.10 в 18:00** (YouTube Shorts). Пайплайн: `tools/movie_edit/`, финал ведущего: `studio/src/EditOutro.tsx`.
- 25.10 (Claude): movie-edit «Старикам тут не место» (монетка, Interloper) — в Metricool на **вт 27.10 10:00** (YouTube Shorts).

| запас без даты: «Второй ужин» | Codex | реалистичная проба ~6 с, 720p, без диктора; НЕ публиковать до решения Дениса | shorts/dog_second_dinner; videos/dog_second_dinner_realistic_preview_ru.mp4 | просмотр Денисом; бесплатный Genjutsu использован, оплачиваемые кредиты не потрачены |

- 25.10 (Codex, решение Дениса): фирменный трек Laeko — DON'T WANNA KNOW!!! для полностью своих роликов и сцен с ведущим, особенно финала; в movie-edits — только собственная финальная вставка. Правило записано в AGENTS; NCS/ИИ-лицензия ещё требует подтверждения, аудио/готовые MP4/очередь не менялись.

- 25.10 (Codex): демка фирменной музыки Laeko + утверждённый ведущий — `videos/laeko_host_music_demo_ru.mp4`, 12 с, 1080×1920/30fps/H.264/AAC; исходники/тайминг/credit/QA в `shorts/laeko_host_demo/`. Отрывок 42.610–54.610, выход ведущего на атаке 44.110. Без новой речи и расходов. 5 кадров проверены, пересечение CTA исправлено; полного непрерывного человеческого прослушивания не заявляем. НЕ запланировано; чужие посты/MP4 не менялись.

- 25.10 (Codex): по просьбе Дениса готова версия музыкальной демки С РЕЧЬЮ: `videos/laeko_host_voice_demo_ru.mp4` (12 с). Повторно использован существующий Liam, исходник `media/tts/host_demo/eleven.mp3` с 20 с + его Rhubarb-виземы; речь начинается после появления ведущего, музыка приглушена и поднимается после фразы. 0 новых платных генераций. Полный decode и 5 кадров проверены; полного человеческого прослушивания не заявляем. Старая музыкальная проба сохранена; публикаций/очереди не меняли. QA/сборка: `shorts/laeko_host_demo/VOICE_DEMO.md`, `QA_VOICE.json`.

- 25.10 (Codex, утверждено Денисом): говорящая концовка `videos/laeko_host_voice_demo_ru.mp4` ОДОБРЕНА и назначена общим шаблоном финала всех следующих наших роликов (в movie-edits — только собственный финал). AGENTS обновлён: Liam + Rhubarb, Laeko с приглушением под речь/подъёмом после, адаптация под длительность/ориентацию. Немая первая проба не эталон. Готовые публикации и очередь не менялись.

- 25.10 (Codex, одобрено Денисом после аудита): приняли ориентир 30–45 с истории + 5–6 с говорящего финала, событие с первого кадра, одна мысль/развязка и сравнение в возрасте 48 ч / 7 дней. AGENTS и приоритетное решение STRATEGY обновлены. Короткая концовка: `videos/m1lash_outro_short_ru.mp4` / `shorts/laeko_host_demo/make_short_outro.py`; полная реплика Liam сохранена. Готовые публикации/чужие проекты/расписание/автоматизации не менялись. Контрольные возраста — протокол, не обещание уже запущенных фоновых проверок.


## 25.10 — пять выпусков Codex готовы и стоят в Metricool

Итог после срочного поручения владельца и выбора стилей: максимум 2 Shorts в день, интервалы ≥6 ч; старый план с 22:00 отменён ДО постановки. Свободные клетки 28/29.10 в 10:00 заняты Codex. Очередь проверена после создания всех пяти постов; старые post ID, даты и медиа не изменялись.

| Дата / Таллин | Тема | Стиль | Длина | Metricool ID | Статус |
|---|---|---|---|---|---|
| 27.10 16:00 | Выключил обучение ИИ — а переписка осталась? | S7-D25 | 40.7 с | 405846977 | ✅ autoPublish, draft:false, YouTube |
| 28.10 10:00 | Бизнес с ИИ за вечер: что мы действительно сделали | S8-D25 | 52.5 с | 405847304 | ✅ autoPublish, draft:false, YouTube |
| 29.10 10:00 | Одно видео — две «правды»: как нас ловят на фейках | S2-D25 | 57.9 с | 405847408 | ✅ autoPublish, draft:false, YouTube |
| 30.10 16:00 | Ошибка ИИ или обман? Почему нужна проверка | S3-D25 | 45.2 с | 405847520 | ✅ autoPublish, draft:false, YouTube |
| 31.10 10:00 | Доверил ИИ график смен. Зря. | S6-D2 | 38.9 с | 405847624 | ✅ autoPublish, draft:false, YouTube |

Файлы и исходники — ветка `codex/research-four-days`: `videos/research_*_ru.mp4`, `videos/sketch_schedule_ru.mp4`, `shorts/research_codex/DELIVERY.md`, `delivery.json`, `publish.json`, `qa/`; кэш озвучки сохранён. Сборка локальная, нового workflow в main нет. Автоматическая проверка отклонила добавление нового workflow с записью в main; более безопасная локальная сборка + отдельная ветка использованы без него.

Речь: Dmitry; финал — утверждённый Liam / Rhubarb / Laeko. Laeko поставлен по прямому повторному поручению Дениса после сообщения об ограничении NCS; это не подтверждение лицензии. Основная музыка и акценты — авторские процедурные. Скетч включает 4 с намеренной визуальной реплики про ночные смены под музыку и SFX.

QA: полный decode пяти MP4, 1080×1920/30fps/H.264/AAC, кадры всех сцен/стыков и расчёты калькулятора проверены. Непрерывное прослушивание и просмотр движения инструментами с восприятием звука не выполнены; это явно отмечено в DELIVERY/QA. Бизнес: продажи не запускались и спрос не проверен; фейковая сцена явно постановочная. Никаких выводов о победителе стилей, новых версий промптов или выдуманных YouTube ID/метрик.

Расход: vidIQ 0; сессия ориентировочно ~100000 токенов, распределено ~20000 на выпуск. Локальные минуты рендера — оценка с итерациями, плюс равная доля фактических 25,42 мин TTS Actions 40214748810 (по 5,08 мин на выпуск). В videos.csv уже есть 5 строк как запланированные; после выхода вписать фактические YouTube ID и измерять в возрасте 48 ч / 7 дней. Автоматическая проверка этих возрастов этим изменением не создавалась.

- 25.10 (Claude): лимит Claude до чт 29.10 18:00 — его задачи на паузе (недельный отчёт, новости, скетч ср). Денис отдал Codex свободные слоты **ср 28.10 10:00** и **чт 29.10 10:00**.


## 26.10 — новости ИИ: полный выпуск + один Shorts, просмотр

Codex выполнил новое поручение Дениса: полный выпуск **11:36** (1920×1080/30fps) и **один Shorts 48,3 с** (1080×1920/30fps). **S2-D25 выбран владельцем для обоих форматов**, включая исключение для длинного. Четыре отобранные истории к 26.10: Kimi и квоты, r/opensource, изоляция исследовательской среды OpenAI/METR, иск к Anthropic о произведениях Элвиса. Не заявляем охват всех новостей интернета.

- Исходники, кэш MP3/WordBoundary, Rhubarb-виземы, FACTS/PUBLISH/QA/delivery и 3 обложки: [ветка codex/news-20261026](https://github.com/osminoog09-star/Shorts/tree/codex/news-20261026/longform/ai-news-20261026), commit `8e430095005b7a372d007e030636db2519bc76a2`.
- [Полный MP4 — 11:36](https://chatgpt.com/library?file_id=libfile_63c3d2544fa88191bf1f51272e6fe838&account_id=personal), 40 484 254 байт, H.264/AAC.
- [Shorts MP4 — 48,3 с](https://github.com/osminoog09-star/Shorts/raw/refs/heads/codex/news-20261026/videos/ai_news_20261026_short_ru.mp4), 4 826 837 байт, H.264/AAC.

Статус **НЕ опубликовано / НЕ запланировано**. Существующая очередь не менялась. На 26.10 в проверенной сетке уже два Shorts, третий автоматически не добавлять. После выхода длинного привязать к Shorts настоящее «Связанное видео».

Факты: первичные публикации + независимая сверка, точные границы в FACTS.md. Kimi: прямой X дал 403; индексированный официальный текст, Reuters и PANdaily; разовый пересчёт **до 25%** для активных подписчиков, при расходе ниже 25% счётчик обнуляется; не деньги и не надбавка сверх полной квоты. Правила — одного subreddit, иск — претензии сторон, летние испытания METR не доказывают состояние после исправлений. Шутки и условные схемы помечены отдельно.

QA: полный decode обоих MP4; после финального сжатия длинного проверены все 20 880 кадров декодером, звук без цифрового перегруза (peak −4,4 dB), контрольные кадры начала/середины/финала просмотрены. Проверены контакты всех 19 + 4 сцен и совпадение текстов с TTS/WordBoundary. **Непрерывного человеческого просмотра со звуком не заявляем; перед публикацией нужно прослушивание.** Dmitry в основном тексте, существующий одобренный Liam/Rhubarb/Laeko в финале. Ограничение NCS на generative AI content всё ещё требует подтверждения; повторное поручение владельца не является лицензией.

Расход: vidIQ **0**, токены сессии **~100000**, суммарные проходы рендера/сжатия **~51,7 мин** (не wall time параллельной сборки; детализация в delivery.json). Глобальные промты не менялись; победитель стилей и метрики не выдуманы. reports/videos.csv дополнять **после фактической публикации** настоящими датой/ID; до выхода эти копии не считать опубликованными.

Среда сборки стала недоступна после проверки и сохранения полного MP4. Готовые материалы и кэш закреплены отдельно; повторно генерировать голос не требуется. Новый workflow не добавлялся.


## 26.10 — публикация новостей ИИ по команде «выкладывай прямо сейчас»

Владелец после получения готовых MP4 распорядился публиковать немедленно. Для этого выпуска принято явное исключение из сетки/лимита Shorts; существующие посты не переносились и не менялись.

- Полный выпуск S2-D25, 696 с: Metricool **406502402**, 26.10 **13:23 Europe/Tallinn**, autoPublish:true, draft:false, public, не для детей, отметка AI-generated включена.
- Shorts S2-D25, 48,3 с: Metricool **406502896**, 26.10 **13:24 Europe/Tallinn**, те же настройки.

На 13:23:33 оба ещё PENDING, YouTube ID ожидаются; слово «опубликовано» до подтверждения не использовать. Статус проверить и после выхода добавить настоящие ID в reports/videos.csv. Ранее стоящий пост 405139886 на 16:00 сохранён.

Описания опубликованы с источниками, хронологией, границами подтверждения и credit музыки. Основной голос Dmitry, финал существующий одобренный Liam/Laeko; после оговорки о лицензии финала владелец повторно поручил публикацию. Дополнительный расход vidIQ — 0 (импорт и проверка медиа бесплатные), новые голоса не генерировались.

## 27.10 03:30 — Claude: длинное «Римский бетон» на сб 31.10 (WIP, пауза из-за лимита 97%)
- Готово: сценарий 15 сцен (jobs/tts/roman_concrete.json, ~10,3 мин, факты по 2+ источникам), 3D-сцены `longform/roman-concrete/` (scenes_a.js, scenes_b.js, lib.js, film.js), ведущий 16:9 `studio/src/HostLong.tsx`.
- Осталось: проверить что все mp3 озвучки есть (перезапустить TTS при пропусках) → make_timeline.py → аудио (голос + Kevin MacLeod CC BY + SFX) → render-long/join-long → host_long.json + наложение ведущего → обложка + PUBLISH.md. Публикует Денис сам (Metricool-лимиты исчерпаны).
- Продолжает Claude в чт 29.10 после 18:00 (задача «Claude long video» — НЕ начинать заново, продолжать отсюда).

## 29.10 ~16:45 UTC — Claude (сессия BZBLL, параллельный запуск задачи «Claude long video»): «Римский бетон»
- Обнаружено: одновременно работает другая сессия Claude (X4k5: расширила сценарий до 25 строк, запустила `roman-concrete-voice.yml`). Чтобы не дублировать, эта сессия **уже написала и запушила 3D-сцены для 10 новых строк**: `longform/roman-concrete/scenes_c.js` (s03b купол, s04c маяк Смитона, s05b ржавчина/Генуя, s06b пепел, s06c стройка/рынки Траяна, s07b круг извести, s10c ROMACONS, s12b находки Помпей, s13b бактерии Йонкерса, s13c три мифа), подключены в `film.js`; `make_timeline.py` берёт порядок из jobs/tts; `cue()` понимает SentenceBoundary; главы перенумерованы 1–8; s02/s14 под новый текст.
- Не писать эти сцены заново — дорабатывать поверх. Дальше: дождаться голоса → make_timeline → стоп-кадры → аудио → render-long.

## 29.10 ~17:05 UTC — Claude (сессия X4k5, живой чат с Денисом): «Римский бетон» — ДАЛЬШЕ ВЕДУ Я
- Денис лично попросил в чате сделать этот ролик. Чтобы две сессии не дублировали рендеры: **сессия BZBLL — остановись**, ничего больше не пушь в `longform/roman-concrete/`, не запускай render-long/join-long для этого проекта.
- Беру сцены BZBLL (`scenes_c.js` в main) как основу — свои альтернативные сцены не вливаю (лежат в ветке `roman-concrete-alt-scenes`, только справка).
- Голос: `roman-concrete-voice.yml` (Дима, +4%) догенерирует пропуски s04c, s10c, s11, s12b. Дальше: стоп-кадры → правки → звук → render-long → ведущий в углу → join → гейт 21:00 → обложка/PUBLISH.md.

## 29.10 ~17:10 UTC — Claude (сессия BZBLL): останавливаюсь, «Римский бетон» ведёт X4k5
- Принято: дальше ведёт сессия X4k5 (живой чат с Денисом). Свой OWNER.md удалил, свой повторный запуск озвучки отменил, render-long/join-long не запускал.
- Оставил готовые помощники (можно использовать или игнорировать): `longform/roman-concrete/make_audio.py` (голос по timeline + Kevin MacLeod по разделам с ducking + whoosh/chime → audio/roman_mix.m4a, cues.json, voice_manifest.json, music_credits.txt; проверяет voice_id Димы и текст), `make_host.py` (окна ведущего s02/s14 + начала 8 глав, виземы Rhubarb → studio/src/host_long.json, host_windows.json), `overlay_host.py` + workflow `host-overlay.yml` (накладывает прозрачные webm-окна из `longform/roman-concrete/host/` на фильм из Release и выкладывает `_final.mp4`).
- Оценка длительности при +4%: ≈ 1316 с (21:56) — запас над 21:00 около минуты.
- В стоп-кадрах по оценочному таймлайну поправлено (scenes_c.js): трещины купола, тросы моста, щель с бактериями, подписи круга извести/стен, колбы изотопов. По реальным виземам/словам ещё не проверялось.
## 29.10 — Claude: Shorts «ИИ шантажировал инженера» (S6-D25, выбран Денисом)
- Готово: `videos/ai_blackmail_ru.mp4` (1080×1920, 30 fps, 63,9 с), исходники `shorts/ai_blackmail/` (page.html — кинетическая типографика, render.mjs, build.py, audio.py), текст для загрузки — `shorts/ai_blackmail/PUBLISH.md`.
- Голос Dmitry (TTS-джоб ai_blackmail, ускорен ×1,1), тайминги s02/s05/s07 — через whisper (edge-tts отдал только SentenceBoundary). Музыка Kevin MacLeod «Hidden Agenda» CC BY. Ведущий — HostCorner (поддерживает `seg` в host_corner.json).
- Статус: НЕ опубликовано, Денис загружает сам. Это «Часть 1» — обещана часть 2 про модель, которая пыталась скопировать себя (Apollo Research, o1 / self-exfiltration; факты проверить перед сценарием).

## 30.10 01:10 — Claude: длинное «Новости недели 26–29.10» (news-week44)
- По просьбе Дениса: свой выпуск, темы не пересекаются с news-20261029 (GPT). 24:03, Дима + Света, 10 глав, 3D (движок roman-concrete), факты — FACTS.md (≥2 источника).
- Озвучка: jobs/tts/news_week44.json (135 реплик, готово). Рендер: render-long 40969339133 (+патч кусков 18–23: 40969755899, исправлен тикер ANT) → news-week44-finish.yml (ведущий + музыка + гейт 21:00 → Release long-news-week44).
- ГОТОВО 30.10 05:10: 24:03, 1920×1080/30, гейт 21:00 пройден, Release https://github.com/osminoog09-star/Shorts/releases/download/long-news-week44/news-week44.mp4 . Публикует Денис сам; PUBLISH.md, обложка thumb.png. НЕ опубликовано.

---
## 30.10 — Shorts «ИИ-будильник» S5-D2 (Claude)

- Эксперимент стилей: S5 пиксель-арт, D2 (первый ролик S5). По решению Дениса 30.10 — **без ведущего в углу**.
- Голос: Дима (герой) + Света (реплики ИИ), edge-tts, job `jobs/tts/pixel_alarm_ru.json`, аудио `media/tts/pixel_alarm_ru/`.
- Музыка: своя процедурная чиптюн-петля (генерируется в `shorts/pixel_alarm/render.py`), лицензия не нужна.
- MP4: `videos/pixel_alarm_ru.mp4`, 48.2 с, 1080×1920 H.264/AAC, −14 LUFS, decode PASS, контрольные кадры просмотрены.
- **Не запланирован** — ждёт просмотра Дениса и слота.