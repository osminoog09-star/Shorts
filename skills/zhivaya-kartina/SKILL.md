---
name: zhivaya-kartina
description: «Живая картина» (S11-D25) — длинный (20+ мин) рисованный нарратив про ИИ/технологии: SDXL-картины маслом + карта глубины + параллакс three.js + голос Дениса. Формат «N уровней» (POV «ты», метка в конце уровня). Триггеры: «живая картина», «как 8 уровней ИИ», «рисованный длинный ролик», «уровни».
---

# Живая картина · S11-D25 (утверждено Денисом 07.11.2026)

Эталон: **«Ты прошёл 8 уровней искусственного интеллекта»** — https://youtu.be/2suySU6uCGk (22:56).
Проект-образец: `longform/ai_levels/` (всё переиспользуемое лежит там). Все 80 промптов эталона: `PROMPTS_ai_levels.md`.
Пример кадров: `site/studio/i/recipes/zhivaya-kartina.jpg`.

## Что это

- **Стиль S11:** цифровая живопись маслом, кинематографичный свет (кьяроскуро), приглушённая палитра с тёплым янтарём, видимые мазки, дымка. Каждая фраза — свой кадр.
- **Глубина D25:** картина выдавливается по карте глубины (Depth-Anything) в рельеф, камера плавно едет сквозь него (dolly / pan / crane) — живой параллакс, а не зум по плоской картинке. Поверх — пыль/снег, мигающий курсор, карточки уровня и субтитры.
- **Формат «N уровней»** (вдохновлено разбором vVZK_o13Qk4, `reports/research/references/vVZK_o13Qk4/reference_audit.md`):
  - рассказ от второго лица: «ты» = герой (ИИ, профессия, вещь…);
  - 8 уровней × ~2:50, короткие фразы (~7 слов), ~300 слов на уровень → итого 21–24 мин;
  - открытие уровня: карточка «УРОВЕНЬ N · Имя · место, год» + связка «Прошлый отвечал за X. Этот отвечает за Y»;
  - внутри — реальная история с фактами, 1–2 цитаты крупно (`quote`);
  - закрытие: **«Метка уровня: …»** — одна фраза-шрам (`mark: true`);
  - сквозные мотивы (у ИИ: мигающий курсор, «Выйдите, пожалуйста, из комнаты»), финал закольцован на уровень 1;
  - предпоследний уровень — «Стоп. Тут честно» (что ещё не произошло).

## Мягкий параллакс (Денис 07.11: «искажение не надо сильно делать»)

- Выдавливание по глубине **0,24** (не 0,55), карта глубины в шейдере сглажена 5×5 — края людей/рам не рвутся и не тянутся.
- Боковые панорамы камеры вдвое меньше (x ±0,08), самый глубокий наезд — `depth .3`.
- Смена кадров — **настоящий наплыв** (уходящий кадр рисуется под входящим), без провала в чёрное. У сцены нет `scene.background` — он стирал уходящий кадр.
- Проверка после рендера: `ffmpeg -i film.mp4 -vf blackdetect=d=0.05:pix_th=0.06 -an -f null -` → чёрное только в задуманных местах (старт, паузы между главами, конец).
- Генератор любит ставить космические объекты на землю и рисует «парус» лодкой: для космоса в промпте `floating in black outer space`, в `neg` кадра — `landscape, ground, horizon…` (и `boat, sea, water` для паруса).

## Инструменты (всё локально на ПК, бесплатно)

| Шаг | Чем |
|---|---|
| Голос | Qwen3-TTS 1.7B, клон Дениса (`C:\M1lash\private\voice_ref`), ASR-проверка faster-whisper ≥0,80 |
| Кадры | SDXL base 1.0 fp16 + sdxl-vae-fp16-fix, 1344×768, 32 шага, DPM++ Karras, CFG 6 |
| Глубина | Depth-Anything-V2-Small → 16-bit PNG |
| Анимация | `longform/ai_levels/film.js` + `index.html` (three.js, шейдер рельефа) |
| Рендер | `longform/smart-strike/core/render/video.mjs` (headless Chromium → ffmpeg) |
| Музыка | легальная (эталон: Kevin MacLeod «Lightless Dawn», CC BY 4.0 → кредит в описание), ~8% под голосом |
| Финал | `scripts/pc/local_jobs.py finish` (горизонтальная концовка v7 + check.py + look.py), `scripts/qa/longform_duration_gate.py` |

## Промпт кадра

`<промпт кадра>, ` + STYLE, негатив общий:

- **STYLE:** `digital oil painting, cinematic concept art illustration, dramatic chiaroscuro lighting, muted desaturated palette with warm amber accents, visible painterly brushstrokes, atmospheric haze, highly detailed, film still composition`
- **NEGATIVE:** `photo, photorealistic, 3d render, cgi, plastic, cartoon, anime, text, letters, watermark, signature, logo, blurry, lowres, deformed hands, extra fingers, bad anatomy, disfigured face, cropped, frame, border`
- Промпт кадра: **кто/что + где + эпоха + свет + план** («seen from behind», «close-up», «wide establishing shot»). Людей лучше со спины/силуэтом — меньше кривых лиц.
- Эпоху писать предметами: 1966 → teletype, tape cabinets (не monitors). Спорные предметы SDXL рисует плохо (доска го → шашки/бильярд): описывать физически («pale wooden board with thin black grid lines, round flat stones»), смотреть контактный лист и перегенерировать с другим seed.

## Конвейер (команды из `longform/ai_levels`, после `env.ps1`)

1. Сценарий: `levels/l1.json … l8.json` — `card`, `shots[]` (id, seed, prompt, layers: snow/dust, cursor), `beats[]` (id, shot, text, `say` — как произносить латиницу, `alias` — цифрами для ASR, `quote`, `mark`).
2. `py -3.11 build.py voice l1 … l8` — голос (≈8 мин/уровень; повторы и нарезка на фразы автоматически, `FAILED` = править текст).
3. `py -3.11 build.py frames l1 … l8` — SDXL + глубина (≈3 мин/уровень). Смотреть контактный лист **глазами**, плохие удалить из `assets/` и `Работа/.../frames/` и перегенерировать.
4. `py -3.11 build.py timeline l1 … l8` → `timeline.json`; `py -3.11 build.py mix` → `mix.wav` (−15 LUFS).
5. Рендер из `longform/smart-strike`: `node core/render/video.mjs ../<проект> --fps 30 --workers 4 --size 1920x1080 --out <...>.mp4` (≈10 мин на 23 мин видео), mux с `mix.wav`.
6. `py -3.11 scripts/pc/local_jobs.py finish --body <mp4> --out C:\M1lash\Готово\<name>.mp4` (без `--vertical`!) + duration gate.
7. Обложка: самый сильный кадр + крупно «N УРОВНЕЙ …» (Arial Black, обводка). Описание: таймкоды уровней, кредит музыки, «Озвучка — мой голос. Иллюстрации созданы с помощью ИИ».
8. Показать Денису → после «ок» `local_jobs.py publish` (PRIVATE, без даты). Время выбирает Денис.

## Правила

- Голос только Денис; WAV/MP4/voice_ref не коммитить.
- Факты — только проверяемые; спорное смягчать («около», «десятки миллионов»).
- Новую тему согласовать с Денисом; стиль внутри формата повторно не спрашивать.
