# Архив workflows (30.10.2026)

Одноразовые workflows конкретных выпусков и разовых установок. Решение Дениса 30.10: в `.github/workflows/` остаются только общие.
Отсюда GitHub их **не запускает**. Чтобы повторить — скопируй файл обратно в `.github/workflows/`, запусти, потом верни в архив.
Для нового выпуска не плодить `<выпуск>-xxx.yml`: использовать общие (`tts.yml`, `render-long.yml`, `join-long.yml`, `host-overlay.yml`, `movie-edit-source.yml`, `fetch.yml`, `music.yml`) с параметрами.

Здесь: Heron (6), Samsung (5), Interstellar (4 — пригодятся для пересборки «Интерстеллара»: источник, тайминги), Wolf (3), Brat 2, Movie mystery (3), Roman concrete (2), News 28.10/29.10/week44, Last Access preview, разовые установки ElevenLabs и huashu-motion.
