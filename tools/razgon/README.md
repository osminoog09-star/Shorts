# Razgon 2D Studio → M1lash: экспериментальный адаптер

Данный каталог добавляет QA для пользовательского ZIP Razgon; он **не заменяет** Remotion. Бинарный ZIP не коммитится в публичный репозиторий: в пользовательском архиве отсутствует явная лицензия на распространение.

## Локальная проверка и установка

```bash
python tools/razgon/preflight.py --archive /path/to/razgon-2d-studio-m1lash-patched.zip --install-parent /tmp/m1lash-work
cd /tmp/m1lash-work/razgon-2d-studio
npm install
npx playwright install chromium
python tools/doctor.py
node render.mjs --project examples/reaction-time --sheet --scale 0.3
```

Исходный архив проходит `tools/verify_kit.py` (30/30). В patched ZIP исправлены `render.mjs` и `audio/mix.py`, поэтому старые внутренние контрольные суммы этих двух файлов не совпадают; SHA256 исправленного ZIP закреплён в `preflight.py`.

## M1lash — обязательные ограничения

- Дима `ru-RU-DmitryNeural` — ведущий и CTA; Света `ru-RU-SvetlanaNeural` — второй голос. Никакого подменного голоса. Проверка метаданных: `python tools/razgon/preflight.py --voice-manifest voice_manifest.json`; она не заменяет слуховую проверку.
- Новые полноценные длинные выпуски от **21:00**; релизный технический gate: `python scripts/qa/longform_duration_gate.py FINAL.mp4`.
- Сначала модель, режиссура, 15–30 сек пилот и визуальная экспертиза; лишь затем длинный рендер. Stick figures сами по себе не соответствуют утверждённому качеству персонажей.
- Не трогать расписание Metricool, YouTube Direct и чужие публикации. Интеграция не выполняет upload/publish.
- Для релиза обязательны полный декод MP4, аудиосинхрон, реальные кадры и проверка авторских прав.

## Аудит 2026-10-28

**PASS:** ZIP целый, 30/30 файлов исходника, JS/Python syntax, создание тестового проекта, генерация звука. Обнаружена потеря конца голоса при `-shortest`; patched mixer теперь отвергает рассинхрон более 0.25 с. Patched renderer ограничивает локальный HTTP-сервер и проверяет код выхода ffmpeg.

**NOT VERIFIED:** Chromium end-to-end, итоговая художественная экспертиза, лицензия, реальный TTS Димы и Светы. Движок не считается production-ready.

Unit tests: `python -m unittest discover -s tests -p test_razgon_preflight.py -v`.
