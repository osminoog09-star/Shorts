# 03.11.2026 — исправление Авто-расписания

## Подтверждённые причины
1. bestSlots дважды считал taken+plan; время считалось в часовом поясе браузера.
2. data.json после refresh мог стереть локальный резерв; следующее нажатие предлагало тот же слот.
3. Не было общего атомарного резерва между вкладками.
4. Все youtube-direct jobs имели одну concurrency group: pending jobs разных видео отменялись.
5. Workflow получал только путь и читал изменяемый main. Предыдущий запуск мог применить более поздний выбор.
6. dispatch204 считался «Дата назначена», хотя YouTube ещё не подтвердил.
7. Карточки использовали только privacy=private из inventory и не показывали publish_at/receipt.

## Реальные владельческие даты
История sketch c36f3c78: последний выбор владельца 03.11 16:00 Tallinn. В Studio оставалось04.11 16:00, receipt04.11 14:00Z.
После фикса восстановлен ТОЛЬКО этот сохранённый выбор через штатный youtube-direct.yml schedule; без upload.
- run41607117254: PUT фактически применился (Studio03.11 16:00), но немедленный GET был устаревшим, job честно FAIL без ложной новой receipt.
- Исправлен bounded readback: максимум4 GET с1/2/4с между чтениями, без повтора PUT внутри функции.
- run41607737039 SUCCESS: receipt publish_at_utc=2026-11-03T14:00:00Z, schedule_confirmed_at=2026-11-03T09:02:41.029508+00:00. Реальный ролик9Bhnbw5bFeE.
НовостиoMhef8NQg1s:05.11 10:00 Tallinn /08:00Z, выбранная владельцем дата сохранена без нового API update.
Остальные5 приватных Shorts/пёс/kino003 не перезаливались и не переносились.

## Исправления
- scheduling.js: Tallinn/DST, dedupe, минимум4ч, запрет занятого слота.
- Один CAS-файл publishing/schedule_requests.json резервирует слот для всех вкладок. Перед выбором — свежие manifests GitHub, после клика — общий резерв, затем manifest и dispatch.
- Локальные резервы сохраняются при stale Pages refresh и reload. Отображаются стадии «назначается», ошибка и подтверждённая дата; slot остаётся занят до ясного результата.
- Workflow group теперь per-manifest, frozen expected_publish_at+request_id; stale date/request отклоняются ДО OAuth/записи.
- Backend проверяет общий reserve ledger, а успех записывает только после YouTube GET readback той же даты и private.
- Карточки показывают дату/время Tallinn, кино определяется также category_id1 из манифеста. Подтверждённые публичные видео не предлагаются на повторное назначение.
- Время можно исправить отдельной кнопкой в плане.
- Сетка production не менялась; новые случайные даты тестами не назначались.

## Проверки
22 Python uploader/regression tests PASS; Node scheduler PASS (Tallinn winter/summer, dedupe,4ч, одновременные вкладки, sequential Auto, immutable date, stale refresh); прежний auto-refresh smoke PASS.
Pages41606819037 SUCCESS с scheduling.js и новым тестом; браузер показал news05.11 10:00 и sketch pending03.11 16:00, кино-формат исправлен.
Контрольный живой server-to-YouTube flow41607737039 SUCCESS доказал расписание+readback+receipt.
В агентском браузере у сайта нет PAT владельца: не требовали его и не вводили. Саму кнопку Авто не отправляли на реальном видео ради теста; конкурентные UI-запросы проверены offline. Общий pipeline запущен через авторизованный GitHub UI.

Финальный Pages41608224453 SUCCESS,6m44s. Задержка была на checkout; браузер GitHub подтвердил Status Success, финальная очистка плана также выложена.
