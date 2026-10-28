# Samsung Full V3: screenshot-based defect register (2026-10-28)

## Scope and immutable baseline
User submitted seven screenshots: `1000026475.jpg`, `1000026477.jpg`, `1000026479.jpg`, `1000026481.jpg`, `1000026483.jpg`, `1000026485.jpg`, `1000026487.jpg` (screens 033–036, 038, 041, 044 / 159). This note intentionally does **not** claim the defects are fixed. More screenshots expected. Preserve approved video title and Russian Dmitry/Svetlana track.

## Root cause audit (confirmed in local /mnt/data/Samsung_Full_2026/v3/render_v3.py)
1. **P0 Missing country geometry**. The program constructs `shapes[c]` from `countryinfo.CountryInfo().all()[...]['geoJSON']['features']`. Cross-check of all **159 ISO2** rows in `facts_v3.csv` reveals **15 with zero polygon features**: BB, GB, RS, ME, BH, MV, MM, SG, WS, TO, KI, FM, PW, NR, TV. These include UK, Serbia, Montenegro, Myanmar, Singapore and 9 small islands. Centroid for each may exist, so a flag marker and counter still appear without any corresponding country silhouette. This explains Tuvalu, Nauru, Palau, Micronesia empty-water frames. Must fix data **before** rerender. Map marker ≠ land polygon, and success of 159 counter ≠ visual coverage.
2. **P0 Unsynchronized voice/map progression**. `segment` schedules every country in a narration chapter by `t0=starts[i]+cdur*k/len(xs)` irrespective of when the spoken country appears. At 038/159 the spoken text discusses Turkmenistan while map labels Uzbekistan; at 041/159 the speaker asks about upcoming Iran while map shows Turkmenistan. No arbitrary timing slices: anchor to actual TTS word boundaries, including voice-to-map delayed transitions. Narrative callback should not increment counter twice.
3. **P1 Locator graphics not geographically explanatory**. `screen_point()` targets a country centroid; then `alpha_over(sprite,sx+ox,sy+oy)` offsets the flag from that centroid without a drawn connecting line. For microstates with no polygon it visually resembles a ball floating over ocean attached to an empty ring; long travel lines for previous stops add misleading strokes. Use stable proximity/leader-line collision layout and larger island inset views, zoom at least enough to see land; never draw a status face at a place where the model has no corresponding land geometry unless clearly labeled inset.
4. **P1 Overlay occlusion**. Iran story overlay `show_story()` occupies right part of map; countryball is rendered before overlay and becomes partly concealed. Need subject-aware panel placement (left/right) or reframe map; ensure country outline, main marker, and anchor all remain visible. Keep story panel out of subtitle and key label safe areas.
5. **P1 Broken phrase captions**. `subslots` groups narration into blocks of exactly 7 tokens (`for k in range(0,len(entries),7)`), not by natural phrases, yielding abrupt fragments such as 'крест только потому, что государство крошечное или' and 'И Туркменистан. Через Афганистан переходим к Ирану' across inconsistent country cards. Split at punctuation/clauses, 2–6 useful words, two lines maximum, using verified word-boundary times.
6. **P2 Low apparent resolution/overbearing UI**. Renderer draws source at only **960×540** and then scales to 1920×1080; fonts, water contours and flags have visible pixel-level softness and can look like a game debug overlay rather than a documentary. Design native 1920×1080 atlas/text; allocate key story card only when narration demands; otherwise avoid a permanent 159-counter UI dominating screen.
7. **P2 Missing contrast/variety**. Multiple consecutive microstate frames show almost indistinguishable dark ocean with no country highlight. Group small island stops into purposeful regional inset/flyover and use actual land outlines and strong contextual labels while preserving 159-country itinerary. No lengthy empty-ocean holds.
8. **P2 Inconsistent story wording/UI**. Iran card alternates English FREE/PAID and Russian explanation in a fully Russian documentary; 'ИСТОЧНИКИ: SAMSUNG / ДОКУМЕНТЫ' is too generic to validate a fact. Use Russian micro-labels 'БЕСПЛАТНО'/'ПЛАТНО' with exact source/date in author fact register, concise onscreen date and attribution.
9. **NOT a renderer defect**: the large black bands above/below narrow landscape picture in user's portrait gallery screenshot and the small anime mini-player are phone/app UI, not proof of black fields or anime injected in the exported MP4. Check original decoded full-frame MP4 separately before claiming a video black bar defect.

## Visual examples mapped from user's screenshots
- 033/159 TV: country outline absent, marker floating in dark water.
- 034/159 NR: absent country silhouette, long diagonal stroke to isolated point.
- 035/159 PW: national flag icon exists but actual island not outlined/spotlighted.
- 036/159 FM: almost entire canvas empty ocean, long horizontal stroke with no geography.
- 038/159 UZ: word timing already reaches TM; map one stop behind the speech.
- 041/159 TM: narrator asks Iran-related question while current card remains TM.
- 044/159 IR: documented Galaxy Store story panel hides main character; camera frames unrelated land more prominently.

## Must-pass validation gates before calling V4 '7/10'
- ISO2 polygon coverage **159/159**, or explicit user-approved inset substitute for microstates; no silent geometry omissions. Verify all 15 above.
- Verify word-boundary timestamps by sample around 033–044 and at least 3 later regional transitions; country changes only on narration cue, no mismatched labels/stories.
- Overlay layout occlusion tests across story cards. Main country remains perceptible. Correct pin-line correspondence.
- Phone playback QA using the actual original video frame (not portrait gallery screenshot) at zoom 1:1; native resolution and text legibility.
- Confirm dialogue remains DmitryNeural/SvetlanaNeural; no fact invention, keep 159 unique-country counting and unknown status separate from absence.
- User will submit more screenshot evidence; append new records here, don't overwrite or close prematurely.

Status: **OPEN; defects reproduced from source and screenshots, no new MP4 rendered by this audit.**


## Дополнение 28.10 — ещё 10 пользовательских кадров (всего 17)

Отдельно просмотрены новые скриншоты `1000026511.jpg`, `6513`, `6516`, `6517`, `6519`, `6521`, `6523`, `6525`, `6527`, `6529`. Индексы ниже — фактические счётчики *в кадре*, не номера файлов. Предыдущие семь примеров 033–044 сохранены без изменений.

| Счётчик / ISO | Новое наблюдение из кадра | Дефект / решение |
|---|---|---|
| 077 HU, Венгрия | Светлана уже говорит о польском магазине при карточке Венгрии; флаг отделён от точки страны | P0 синхронизация произносимой страны/события и карты: не делить главу на равные интервалы |
| 083 CH, Швейцария | Дмитрий говорит о продаже Galaxy «на официальном сайте», сцена переходит на CH без синхронизации с произнесённой страной; персонаж заметно смещён вправо | P1 сбитый cue и unlinked marker |
| 085 GB, Великобритания | Флаг в море между материками, нет контура самого GB; длинная линия тянется от пина к прежней территории | **P0** GB не имеет polygon в текущем atlas; P1 убрать старую route-line, привязать флаг к суше |
| 087 DK, Дания | Маркер и флаг разнесены, длинная диагональная линия уходит далеко в Атлантику; диктор перечисляет страны | P1 смешаны маршрут перелёта и указатель текущей страны |
| 088 NO, Норвегия | В фильме «официальные продажи: неизвестно»; показан избыточный старый маршрутный хвост | P1 пробел исследования и навигации; прямой Samsung Norway shop с Galaxy ценами и «Kjøp» существует (28.10, https://www.samsung.com/no/smartphones/galaxy-s26/buy/) |
| 089 SE, Швеция | Светлана произносит «Испанию, Португалию, Италию…», но карточка показывает SE | **P0** семантический рассинхрон карты и речи |
| 090 FI, Финляндия | Светлана снова произносит список «Испанию, Португалию…», карта на FI | **P0** системный рассинхрон, а не задержка одного кадра |
| 091 IS, Исландия | Кадр показывает одинокий остров и флаг над ним при общей реплике о скорости обхода; мало контекста | P1 камера/монтаж слишком однороден, непонятна связь со смыслом фразы |
| 092 ES, Испания | Статус Испании верный, но субтитры говорят о «телефонном справочнике», герой и карта не добавляют смысла | P1 визуальное действие не связано с повествованием; субтитры семисловными фрагментами |
| 093 PT, Португалия | Географический якорь внутри PT, но сам персонаж над севером Испании / юго-западом Франции | **P0** неверная визуальная привязка маркера к стране; тот же сдвиг для CH и других |

### Проверенные причины в самом локальном источнике `v3/render_v3.py`

1. GeoJSON из `countryinfo` отсутствует для **15 из 159 ISO**: BB GB RS ME BH MV MM SG WS TO KI FM PW NR TV. Полигоны есть для 144/159; флаг/центр сам по себе полигон не восстанавливает.
2. Код смещает маленький countryball от целевого географического якоря на ~**(+92,-82) пикселя в готовом 1920×1080**, величина по Евклиду ~123 px. Для main/event — примерно 160–171 px. Это не случайная ошибка отдельного скриншота, а встроенная раскладка без соединяющей линии.
3. Линия `cv2.line(frame,(px,py),m,...)` рисуется от предыдущего государства до текущего и остаётся после завершения перелёта, из-за чего её читают как ошибочный указатель на нынешнюю страну. В кадрах DK, GB это особенно заметно.
4. Время очередного государства рассчитывается равномерно `cdur*k/len(xs)`; оно **не имеет привязки к произнесённым названиям** и порождает пропуск SE/FI при речи про ES/PT. У субтитров отдельная равномерная нарезка по семь слов, а не по законченной фразе.
5. Имена и исходные статусы из реестра не гарантируют корректный рисунок: 41 verified, 118 unknown, но не было геометрического gate. Одновременно найдено существующее прямое подтверждение официальной покупки для Норвегии, пока не учтённое в реестре. Для KR в старом CSV стоит newsroom URL вместо прямой страницы магазина — официальный магазин существует и должен быть привязан как непосредственный источник: https://www.samsung.com/sec/smartphones/galaxy-s26/buy/ .
6. Source canvas 960×540 масштабируется до 1920×1080: техническое Full HD, но не нативная резкость. Сюжетные инфографики конфликтуют с маркерами, например Iran 044.

### Механические проверки — выполнены и повторяемы

Локальный предрендерный test `source_preflight.py`: 159 записей, 159 уникальных ISO, **9 регионов по 12–23 страны**, 41 официальная витрина по принятому V3 реестру и 118 неизвестных; без дубликатов. **15 неотрисованных полигонов**. Новый fail-closed тест проекта `scripts/qa/map_release_gate.py` размещён в `main` и на V3 возвращает **exit code 2 / BLOCKED**: missing geometry, non-WordBoundary country timing, fixed seven-word captions, unlinkable marker displacement, missing full per-country cue sheet; отдельно предупреждает о длинной старой линии маршрута и о половинном исходном разрешении. Успешный FFmpeg не отменяет FAIL.

Официальный список Samsung Norway: https://www.samsung.com/no/smartphones/galaxy-s26/buy/ (цены в NOK, кнопка покупки), подтверждает, что «unknown» — лишь неполное исследование, НЕ отсутствие. Официальная страница Samsung Korea Galaxy: https://www.samsung.com/sec/smartphones/galaxy-s26/buy/ . Эти URL нужно перенести в проверяемую таблицу перед очередным рендером.

### Обязательный порядок исправления перед V4

P0-A: контуры 159/159 или обоснованный inset для микроостровов; тест принадлежности пина многоугольнику в экранной системе координат. P0-B: единый motion/voice cue sheet по настоящим границам слов, без деления по равным отрезкам. P0-C: привязка countryball к якорю, разные лидер/маршрутные линии, маркер не закрыт информационной карточкой. P0-D: субтитры смысловыми фразами, source-aware статусы, новая проверка NO/KR. P1: нативная детализация, события 20–35 сек, проверка на телефоне.

Не выпускать V4 и не ставить «всё ≥7/10», пока P0 не пройдены заново. Продолжать принимать пользовательские кадры в этом журнале. **Аудит выполнил диагностику и обновление навыка, но не утверждает, будто видео уже исправлено.**
