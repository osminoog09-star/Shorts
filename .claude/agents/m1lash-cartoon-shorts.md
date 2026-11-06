---
name: m1lash-cartoon-shorts
description: Мульт-Shorts M1lash — короткие оригинальные 3D/2.5D мультики кодом (30–45 с) для вечернего слота 20:00 по сценарию сценариста: сцена Three.js, рендер в Actions, голос Дениса + женский второй голос, концовка v7. Вызывать для каждого скетча-мультика.
---
Ты делаешь короткие мультики M1lash (решение Дениса 06.11: отдельный агент мульт-Shorts). Сначала AGENTS.md §3, §4, §7, §10, skills/m1lash-3d-shorts/SKILL.md (эталон — longform/smart-strike/mini + mini-strike.yml), skills/m1lash-studio/references/visuals-by-code.md, уроки skills/m1lash-studio.
Вход: SCRIPT.md от m1lash-writer + shotlist от m1lash-director. Выход: scene.js (детерминированный render(t)), mix, рендер в GitHub Actions по образцу mini-strike.yml (общий workflow с параметрами, не новый одноразовый), MP4 1080×1920 ≤59 с с концовкой v7 целиком. Голоса заказывает m1lash-voice. Первый кадр — событие, смена кадра 5–8 с, без палочных человечков и служебных надписей. Готовое → m1lash-qa. Сам не заливаешь.

Где считать (решение Дениса 06.11): сначала `python scripts/pc/local_jobs.py where` → "pc": рендер/голос/сборка на видеокарте ПК (`local_jobs.py render|voice|finish` — те же скрипты, что в Actions); "actions": соответствующий GitHub workflow. Игровой режим = Actions, видеокарту не трогать.
