# 01.11.2026 — шесть текущих кино-Shorts: восстановление и добивка

**Приоритет от владельца: сначала все шесть Shorts, НЕ длинный Chigur. Ничего не публиковать и не ставить даты без «ок».**

## Факт 004
- Rebuild workflow `.github/workflows/movie-short-004-rebuild.yml`, Actions **41333893324**, artifact **13094169003**.
- Настоящий mp4 **004_V47_REBUILT_PRIVATE.mp4**, **45.339s**, 1080×1920/30fps, H264/AAC. Извлечён в QA контейнер `/mnt/data/m1lash_6shorts_final/`.
- `tools/assemble_with_outro.py` approved vertical outro и новый `ru-RU-DmitryNeural`: lag **0.3ms**, full decode **PASS**, body loudness -14.7 LUFS / -3.9 dBTP. `check.py` **0 FAIL**, WARN лишь «external subtitle stream absent» (burn-in). `look.py --safe shorts` просмотрен глазами (красная Ava сцена, шрифты выше нижней UI зоны), итог фото `004_V47_final_look.jpg`.
- Финальный independent Whisper small: актёры `ru .964/.942` на 10/22с; Дима финальная фраза `ru .996`, слово «машин» распознано. Дима outro/title один голос по метаданным. Аудио полностью лично не прослушано; правовой статус фильма открыт. Статус **PRIVATE review**, не YouTube.
- Это **новая 004 V47**, а не прежний 44.100s V46: новая скорость и длительность TTS title 3.456s, итог 45.339s. Не подменять V46 как битово идентичный.

## Восстановлены 5 остальных настоящих русских исходников (никаких новых запросов владельцу)
- 001: Chigur driver, Actions artifact **13070052528**, `originals/chigur_actual_driver_2007_ru.mp4`, 140.02s.
- 002: Chigur Carla, artifact **13069849250**, `originals/chigur_carla_final_ru_real.mp4`, 220.02s.
- 003: Whiplash, artifact **13041278425**, `originals/whiplash_russian_rehearsal_scene.mp4`, 311.542s. Старый кандидат artifact 12776800730 реально оказался **Gladiator**, не использовать!
- 005: Nightcrawler, artifact **13052196021**, `originals/nightcrawler_no_thieves_ru_test.mp4`, 58.15s.
- 006: Interstellar waves, artifact **13041863362**, `originals/miller_waves_landing_ru_candidate.mp4`, 349.25s. Старая сцена 239s — иная, целевые action/wave ближе к 223–266s.
- Архивы действительно скачаны, ffprobe/контактные листы исходников созданы и открыты глазами. Во всех этих 5 исходниках ещё нужен реальный QA нового монтажного MP4.

## Новый параллельный workflow для финалов
- `.github/workflows/movie-short-five-rebuild.yml`, триггер `jobs/shorts-rebuild/remaining_5_ru.json`, инициирован commit `f6592830`.
- 5 jobs: 001 [71–108], 002 [163–207], 003 [124–166], 005 [17–58], 006 [223–266]. Использует восстановленные RU Actions исходники, `scripts/movie_short.py` и официальный `tools/assemble_with_outro.py`, делает ASR timed subtitles, crop, финал Дима, ffmpeg skill check/look, отдаёт review MP4 в Actions artifact. **Не загружает на YouTube.**
- Для каждого job запишется `reports/research/short_XXX_V47_RUN.json` с run_id и status. При статусе success получить артефакт `movie-short-XXX-RU-V47-review-RUN`, распаковать, запустить/сверить full-decode и check.py, открыть финальный контакт глазами; только потом считать его кандидатом PRIVATE review.
- Эти пять **новые V47 редакторские сборки**, НЕ идентичные прежним V45, потому что старые 214MB ZIP с master MP4 существовали только в прошлой временной сессии и здесь недоступны. Запрещено лгать о «сохранённом том же монтаже».
- Дополнительная CI `.github/workflows/shorts-approved-assets.yml` экспортирует 6 ровных Дима-title и утверждённый outro для локального реконструирования, run ID пишется в `reports/research/shorts_approved_assets_run.json`; при успешном экспорте можно использовать для точной локальной доводки.
