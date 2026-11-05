---
name: m1lash-3d-shorts
description: 3D-мульт кодом для Shorts M1lash (Three.js + Playwright покадрово): сценарий → голос Дениса + женский VoiceDesign → сцена → микс → концовка v7 → QA, всё в GitHub Actions. Использовать для коротких оригинальных 3D-мультиков.
---
# 3D-мульт кодом · Shorts (Claude, 05.11.2026)

Эталонный проект: `longform/smart-strike/mini/` («Забастовка умного дома»), workflow `.github/workflows/mini-strike.yml`.
Перед стартом: `AGENTS.md` (§2 grill-me, §3 голос, §4 концовка, §6 публикация, §12 QA), `skills/m1lash-studio/SKILL.md`, `skills/m1lash-director`, `skills/m1lash-animation-production` (гейты MODEL/CONTACT/ACTING), `python3 tools/studio_learning.py preflight`.

## 0. Решения владельца (grill-me, до кода)
Тема, формат (Shorts 30–45 с / горизонт), 3D или 2D, кто говорит женским голосом, кто герой (мультяшный Денис — только по его фото), мат. Без «да» не начинать. Только оригинальные герои: никаких известных персонажей/«в стиле <франшиза>», даже если так написано в чужом гайде.

## 1. Голос первым — от него тайминг
- Денис: `jobs/voice/<id>.json` (≤8 реплик) → `denis-voice-tts.yml` (REST dispatch, см. `skills/denis-voice-ci`).
- Женский: `jobs/voice_female/<id>.json` → `female-voice-design.yml` (push).
- Длительности из логов → `mini/voices/dur.json`; реплики ставить в `LINES` сцены по ним. Артефакты живут 1 день — рендер запускать в тот же день.

## 2. Сцена (`scene.js`)
- `window.DUR`, `window.render(t)` детерминированно (без `Date.now`/`Math.random`, только `hash()`), `window.READY` после `document.fonts.load`. Three.js 0.170 из `vendor/` через importmap.
- Порядок в `render(t)`: свет/настроение → **поза героя** → `hero.updateMatrixWorld(true)` → реквизит, который летит к герою (контакт берёт координаты головы/руки ЭТОГО кадра) → **камера в конце** (шоты — функции `cam(t) → [pos, target, fov]`, могут кадрировать героя по `headPos()`).
- Экраны техники — CanvasTexture с LED-лицом; перерисовка только при смене ключа. Таблички — двусторонние.
- Крупный план вертикали: fov 34, дистанция ≥1.7 м от головы, цель на 0.2 м ниже глаз. Ближе — голова «лезет» в кадр.
- Субтитры DOM в безопасной зоне (top 1250px из 1920, справа отступ 150px), ≥0.8 с на плашку; бейдж говорящего.
- Проверка стопов локально: `node core/render/still.mjs mini <t…> --size 1080x1920 --out <scratch>` (~2 с/кадр SwiftShader).

## 3. Звук (`mix.py`, только в Actions)
Голоса по `LINES` (выравнивание речи), процедурные SFX на каждое видимое событие, музыка CC BY из `media/music` с RMS музыки = 0.08 от речи (≤0.10 по §4), lips.json (RMS по 1/30 с) для рта. Атрибуция трека — в описание.

## 4. Сборка и QA (Actions, `mini-strike.yml`)
`runs-on: ubuntu-24.04` (на 26.04 Playwright не ставит браузер). Рендер `core/render/video.mjs --fps 30 --workers 4`, mux, `scripts/fetch_outro.py` (SHA), `tools/assemble_with_outro.py --max-seconds 59`, `ffmpeg -xerror`, `check.py --platform youtube-shorts`, `look.py`, лист 2 к/с и кадры → ветка `qa/<id>` (без звука). MP4 → private Drive для владельца. YouTube — только `upload=true` после его «ок».

## 5. Гейты перед показом владельцу
MODEL (3 ракурса, 6 эмоций, кисти с пальцами), CONTACT (палец на рычаге/ручке в кадре контакта), ACTING (подготовка → действие → реакция → завершение), каждая реплика меняет кадр, нет пустого кадра >2 с, звук каждого события. Статус DRAFT, пока владелец не посмотрел.

## Уроки
- 05.11 · Claude · Голова героя «шлемом»: полусфера-причёска ложилась на брови. Линию роста поднимать поворотом шапки (rotation.x ≈ −0.8) и проверять крупным стопом.
- 05.11 · Claude · Скачать artifact в облачную сессию нельзя → всё, что трогает приватный голос, делать в одном workflow.
