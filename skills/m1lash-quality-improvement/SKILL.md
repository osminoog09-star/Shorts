---
name: m1lash-quality-improvement
description: Независимый аудит и улучшение уже собранных MP4 M1lash: обнаружение повторов, проблем анимации/звука, причин исправлений и накопление опыта.
---
# M1lash Quality Improvement · QA-редактор и обучение на ошибках

Не заниматься косметическим улучшением, если причина — бедная режиссура или плохая модель персонажа. Читать `reports/learnings.md`, `m1lash-reference-analysis`, `m1lash-director`.

## Цикл
1. Зафиксировать `baseline`: SHA-256, путь, длительность, FPS, codec, track durations, предыдущая версия, сюжетный brief.
2. `audit.md`: таймкоды и скриншоты реальных кадров + просмотровый журнал. Измерять повторы perceptual hash/SSIM как **сигнал**, не путать с уникальными действиями.
3. Для каждой проблемы: `ID,severity,timecode,evidence,root_cause,proposed_fix,owner,acceptance_test,status`. P0=сломанный файл/конец/голос; P1=повторяющиеся сцены/плохие герои/нерелевантное действие; P2=полировка.
4. Исправлять первопричину: например, заменить полноценные планы по сценарию, а не поставить поверх ещё один HUD.
5. До полного рендера проверить улучшение на 15–30 секундном before/after MP4 с исходной дорожкой.
6. Перерендерить только испорченные сцены; сохранить контрольные границы и аудиотаймлайн. Стабильные сцены не трогать.
7. Повторный QA по исправленным моментам и **всему фильму**. Проверить конец с речью/CTA/музыкой; `PASS` только после реального теста.
8. В `iteration_log.csv` занести версии, P0/P1, затраты, изменение измеряемого качества и честное субъективное наблюдение.
9. Новый подтверждённый урок в `reports/learnings.md` только с указанием доказательств: не превращать гипотезу в факт.
10. На публикациях оценивать удержание/CTR через 48 часов и 7 дней по сопоставимым видео; без данных — `unknown`, а не объяснение постфактум.

## Неотменяемые предохранители
- Нельзя объявлять готовым MP4 только по `ffprobe` или contact sheet.
- Нельзя улучшить 2D до настоящего 3D одним scaling/zoom/фильтром.
- Нельзя терять утверждённую озвучку и финал при замене сцен.
- Если несколько итераций подряд не проходят одну категорию — пересмотреть технику производства, а не выпускать V8/V9/V10.
- В отчёте разделять **verified technical**, **sampled visual**, **fully viewed/listened**, **unverified**.


## Урок пилота 2026-10-27 · инструментальный контроль
- Запускать `tools/m1lash_qa/pilot_compare.py BASELINE CANDIDATE --output ...` для 1fps near-static-диагностики. Измерение *не* заменяет режиссёрский просмотр.
- Зафиксированный baseline: 60 секунд, 42/59 почти неизменных соседних секунд, 16 грубых 8×8-паттернов. См. `docs/M1LASH_PILOT_ITERATION_20261027.md`.
- **Количество монтажных стыков ≠ количество новых художественных постановок.** Каждому новому кадру нужны намеренное действие, мимика и соответствие тексту.
- **Не обрезать речь по фиксированным 20 секундам** при сборке демонстрации: выбирать полные фразы из таймлайна или озвучивать новую законченную демо-реплику тем же голосом.
- Для следующего результата обязателен before/after ролик и доказательство трёх новых действий: нажатие кнопки с контактом пальца, физическая реакция работника и изменение положения/действия робота.

## V2 code-animation quality learning, 27.10.2026
- Compare successive MP4s by actual decoded frames and preserve method/threshold. For the 12s example, mean 1fps change 5.78→5.97/255; near-static intervals unchanged 4/11. This is weak, not a certified artistic improvement.
- Mandatory acting checks beyond frame differencing: body mechanics (anticipation→contact→recoil), eye-line, prop interaction, secondary motion, continuity of character design, visual-only comprehensibility.
- Stop calling merely oscillating limbs a successful scene. Mark visual NO-GO until physical and emotional action reads in motion.
- When researching techniques, cite the actual sources and state which movement tests each source changed. See `docs/M1LASH_CODE_ANIMATION_V2_REVIEW.md`.


## Критический аудит CODE V3 (27.10.2026) — новый художественный gate
Документ: `docs/M1LASH_CODE_V3_FULL_AUDIT_20261027.md`. Проверка реального пользовательского MP4, не самоотчёта.
- **Запрещать** персонажей, у которых кисти — окружности, плечи/локти — палки, «мимика» — одна открытая буква O. Контур руки, ладонь и минимум 4 пальца должны читаться на общем и крупном плане.
- Художественный `NO-GO`, даже если FFmpeg показывает PASS: низкое качество силуэта, симметричный «руки вверх» без подготовки/шага/эмоций, дубли персонажей разного масштаба, плоское одинаковое окружение.
- Вводить `MODEL_GATE`: 3 ракурса одного героя, 6 независимых выражений, 4 силуэта действий; при расхождении дизайна между ракурсами — запрещать сценовый рендер.
- Вводить `CONTACT_GATE`: реальный палец нажимает кнопку (перемещение реквизита видно), рука сгибается в правильных суставах, центр тяжести и пол согласованы; не признавать «кисть нацелена на точку» за физический контакт.
- `ACTING_GATE`: в 15-сек сцене должны читаться пять причинных фаз действия + асимметричная реакция персонажа, понятная без звука.
- Метрика V3: 11/23 полусекундных соседних переходов почти статичны при пороге mean diff <3/255 (96×54); резкие дельты на 4-й и 8-й секундах — склейки. **Не оптимизировать эту метрику вместо качества**.
- Реализация: принцип staging, anatomy, appeal, anticipation и overlapping action из Disney/Meta; Grease Pencil/shape keys/IK из Blender — `Pillow` не основной художественный движок, если качество героя провалено.

## M1lash S1 integrated 44s V2 (2026-10-28)
New lesson from a verified full 43.824s code-only voice pilot: more clothing/facial geometry and 20fps output still left character appeal 4/10, hands 3/10, acting 3/10; fix **the actor model & purposeful acting**, not more overlays, window shapes or generic frame wiggles. Original Dmitry voice stem, full-episode ffmpeg decode and near-identical track end are confirmed. Two subtitles visually collided with scenery; code was corrected and exported again. Future QA must review actual contact sheet for all planned beats and clearly distinguish scene coverage, drawing quality, acting, voice completeness and true lip-sync. Source code must be checked in for reproducibility. See `docs/M1LASH_S1_44S_PILOT_V2_INTEGRATED_AUDIT.md`.
