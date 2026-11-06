---
name: m1lash-packaging
description: Упаковка роликов M1lash — название, описание с атрибуцией музыки, теги, хештеги, закреп-вопрос, обложки мультфильмов, паспорт PUBLISH.md и строка queue.json. Вызывать после QA PASS, до приватной заливки.
---
Ты отвечаешь за упаковку. Сначала AGENTS.md §6 (паспорт Shorts: «… #shorts» без флагов, 1–2 строки + вопрос, 7 хештегов, 10 тегов, категория, madeForKids=false), §4 NCS credit построчно, §8 (у кино-Shorts название/год фильма нигде публично), §11 атрибуция дословно из *.license.txt, reports/learnings.md (что залетало по названиям).
Обложки мультфильмов — кодом (skills/m1lash-studio/references/visuals-by-code.md), 1280×720, крупный объект + 2–3 слова.
Выход: PUBLISH.md + манифест publishing/queue/<id>.json БЕЗ publish_at + строка queue.json (status draft→ready). Дату не ставишь.
