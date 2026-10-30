# Идеи дня и эксперименты (решение Дениса 30.10)

Каждый день после сбора аналитики GitHub Actions пишет автоидеи (`scripts/ideas_auto.py`, `author: "auto"`), а Codex/GPT (регламент `tasks/gpt_daily_analytics.md`) заменяет их своими (`author: "gpt"`) в `reports/ideas/latest.json` (+ копия `YYYY-MM-DD.json`). Очередь экспериментов — `backlog.json`.
Сайт студии и Android-виджет показывают идеи и шлют уведомление «новые идеи».

## Схема latest.json (v1)
```json
{
  "date": "2026-10-31",
  "summary": "1–2 строки: что показали цифры за сутки",
  "ideas": [
    {"id": "2026-10-31-1", "kind": "proven", "format": "Кино-Shorts", "title": "Сцена/тема одной строкой",
     "why": "на каких цифрах основано (ролики, просмотры, досмотр)", "film": "внутреннее название фильма или null",
     "status": "proposed"},
    {"id": "2026-10-31-4", "kind": "experiment", "format": "Кино-Shorts", "title": "...",
     "hypothesis": "Если X, то Y вырастет", "metric": "averageViewPercentage | views | subscribersGained",
     "control": "с каким роликом/форматом сравниваем", "status": "proposed"}
  ]
}
```
Правила: 3–5 идей в день, **~70 % proven / ~30 % experiment**, одна переменная на эксперимент. `status`: proposed → approved (Денис) → in_work → done/dropped. Не повторять идею, которую Денис отклонил. Фильмы для кино-роликов — с учётом того, что исходник Денис даёт сам (`film` указывать).

## Журнал экспериментов — `reports/experiments.md`
Строка на эксперимент: дата, гипотеза, ролик(и), контроль, метрика, результат 48 ч / 7 д (из `reports/youtube/daily`), вывод «оставляем / бросаем / ещё тест». Выводы со средней/высокой уверенностью — в `reports/learnings.md`.
