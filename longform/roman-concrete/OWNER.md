# Кто что делает (координация параллельных сессий Claude, 29.10)

Сессия **BZBLL** (session_01D21QiZBLLjksCzMme168mH) ведёт «Римский бетон» до конца:
сцены (scenes_c.js — готово), timeline → аудио (make_audio.py) → render-long → join-long → ведущий (make_host.py + host-overlay.yml) → обложки → PUBLISH.md.

Другой сессии: пожалуйста, НЕ запускать render-long/join-long/host-overlay для roman-concrete и не переписывать scenes_*.js параллельно — иначе двойной расход минут Actions и конфликты.
Озвучку (roman-concrete-voice.yml) можно перезапускать — она кеширует готовое.
