# GPT: концовка Дениса недоступна автоматике (аудит Claude 05.11)

Факт: `tools/assemble_with_outro.py` правильно требует `media/outro/m1lash_outro_denis_v7_*.mp4` (SHA в `tools/outro/approved.json`) и без неё даёт BLOCKED. Файлы лежат только в твоей Library. **Ни один workflow их не получает** → `movie-short.yml` и будущий конвейер «папка Drive → Short» в GitHub Actions не могут собрать готовый ролик. Последние запуски `movie-short.yml` (31.10) — failure.

Сделать:
1. Загрузить обе концовки v7 в приватное место Drive владельца (не в публичный Git, AGENTS §3–4), отдельно от папки фильмов (`M1lash/_studio/outro/`).
2. Общий шаг для workflows: скачать по `GDRIVE_REFRESH_TOKEN` в `media/outro/`, сверить SHA256 с `approved.json`, при несовпадении — стоп. Подключить в `movie-short.yml` и в конвейер папки Drive. `media/outro/m1lash_outro_denis_*` — в `.gitignore`.
3. Тест: `movie-short.yml` на коротком тестовом клипе → SUCCESS, `assemble_with_outro.py` без BLOCKED, check/look.
4. HANDOFF + урок.
