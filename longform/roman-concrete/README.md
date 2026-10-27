# Римский бетон, который сам себя чинит — длинное видео (Claude, сб 31.10)

Статус 27.10, 03:30: сцены s01–s14 + s04b написаны (scenes_a.js, scenes_b.js, lib.js), стоп-кадры проверены на временных таймингах.
Озвучка — jobs/tts/roman_concrete.json (Dmitry, ~8000 знаков ≈ 10,3 мин), часть сцен перегенерируется (сбои edge-tts).
Ведущий 16:9 — studio/src/HostLong.tsx (окно справа внизу; данные host_long.json — заполнить после озвучки).

Дальше: 1) дождаться всех media/tts/roman_concrete/*.mp3 (перезапуск workflow TTS при пропусках);
2) python3 make_timeline.py; 3) аудио: голос + музыка Kevin MacLeod (CC BY) + SFX → audio/roman_mix.m4a, audio/cues.json {duration};
4) render-long (project=roman-concrete, chunks=40, audio=audio/roman_mix.m4a) → join-long → Release;
5) host_long.json (окна: s02, начало s03/s06/s09/s11/s12/s13, s14; виземы через tools/lipsync.sh) → Remotion host-long по окнам → ffmpeg overlay;
6) обложка, PUBLISH.md (название, описание с источниками и атрибуцией музыки, теги). Публикует Денис сам (лимиты Metricool исчерпаны).
Источники: MIT News 06.01.2023 и 09.12.2025, ceramics.org (Jackson 2017), web.uvic.ca ROMACONS, MPA «Portland Cement 200 Years», Wikipedia (Плиний).
