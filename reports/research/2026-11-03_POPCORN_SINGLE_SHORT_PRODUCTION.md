# M1lash · попкорн · одиночное производство · 03.11.2026

## Предохранители от регрессии

- Решение владельца: делать 1 Shorts за раз; `ai_vacuum_20261104` **не трогать**. По факту его исходники, MP4, очередь, даты не меняли.
- Правило AGENTS§3: только собственный голос Дениса через локальную Qwen3-TTS 0.6B Base; при отсутствии весов **BLOCKED**, не заменять на Диму/Edge/Azure. Авторская речь в новом MP4 пока НЕ создана.
- Новая концовка: Denis-v3-music80 vertical, частный файл материализован и SHA256 **1bd5aa5866b70a9b9b3368105626c05b6807a887f1588abcc43224cd8be972ce** == `tools/outro/approved.json`; не коммитить частное аудио.
- Публичных файлов с кино/голосом владельца в этот этап нет; публикации/платных API/планировщика нет.

## Сценарий и визуалы

- Исследование Virot & Ponomarenko (2015), DOI 10.1098/rsif.2014.1247: около 180°C, прыжок за счёт сжатия крахмальной ножки на поверхности; характерный хлопок после разрыва оболочки связан с выбросом пара. https://pubmed.ncbi.nlm.nih.gov/25673298/
- USDA NAL — вода и крахмал внутри твёрдой оболочки создают давление. https://www.nal.usda.gov/exhibits/speccoll/exhibits/show/popcorn/how-does-popcorn-pop-
- Сценарий исправлен: не смешивать причину прыжка и хлопка; 12 коротких реплик, 6 планов, один сюжет. Файл `shorts/science_popcorn_20261104/spec.json` commit 5bfa7fe1.
- В отдельной новой папке `shorts/science_popcorn_20261104/film.html` только popcorn-visuals, код пылесоса не менялся; commit dead6162.
- `render_visual.py` commit 9d79642e: только HTML/SVG, детерминированный Playwright, PIL исключительно для контакта; никаких сетевых TTS/стороннего голоса.

## Реальные QA-этапы

- **Шесть стопов:** GitHub Actions 41725149202 **SUCCESS**, artifact 13273524657; архив извлечён в `/mnt/data/popcorn_solo_proof_41725149202/`, `contact_six.jpg` фактически открыт глазами, композиции шести разных планов читаемые, текст в safe-area. Browser layout gate прошёл. Качество рисунка простое 2D — не заявлять экспертное 8/10.
- **7с motion pilot:** Actions 41725560730 запущен commit 626848a8, статус/пиксели пока ожидаются.
- **Время надписей:** в preflight только предварительное (по словам и оценочной скорости) — это НЕ таймкоды настоящего голоса. Финальные субтитры обязательно пересоздавать по истинным word times.
- **Голос Дениса:** частный reference разрешён и имеется в Library ZIP, но текущий контейнер не имеет установленных Qwen weights и qwen_tts; сеть отключена. Никаких внешних синтезаторов/обходов. Финальная сборка до Qwen BLOCKED.
- **Финальный MP4:** не создан; `check.py`/`look.py`/full decode по нему не исполнялись. Ни в очередь YouTube, ни в публичный Git финал не добавлен.

## Следующий шаг

Получить 7с pilot из artifact 41725560730, визуально проверить движение и сохранить отдельный чекпоинт; затем silent graphics body можно сделать как отдельный asset (не выпуск). Для release требуется в разрешённом локальном runtime Qwen synth 12 реплик Дениса → независимый ASR/таймкоды → точная private v3 outro → штатный assembler → финальные check.py/look.py/decode → владелец. Ложный ready запрещён.

## Второй проход графики (изолирован, без других роликов)

- Первый 7с pilot `41725560730` **SUCCESS**, artifact `13273807454`: физический `motion_pilot_NO_AUDIO.mp4` 7.000с, 1080×1920/30 H264, 210 кадров, `ffmpeg -xerror full decode` PASS; 7-кадровый контакт реально открыт. **Редакторский NO-GO**: в первой сцене почти неподвижное зерно, в основном двигаются текст/камера. Это не релиз.
- Исправлен только `shorts/science_popcorn_20261104/film.html`: зерно дрожит/подскакивает, две струйки пара поднимаются, оболочка увеличивается перед разрывом, крахмал расширяется, хлопья падают. Commit `bb8cb5b6`. Вакуум НЕ затронут.
- Повторные шесть реальных стопов `41726195805` **SUCCESS**, artifact `13275421486`, `contact_six.jpg` открыт; текст читается, новых наложений не найдено, персонажи отличаются от стадии 1. Подвижность подтверждать только по motion, не по стопам.
- Новый r2 7с pilot запущен job `jobs/motion/popcorn_solo_pilot_20261103.json` revision=2 commit `3998e417`. Его FFmpeg/pixel review — следующий шаг.

## Обновлённый motion gate r2 — фактический результат

- Actions **41726511804 SUCCESS**, artifact **13274421698**, физический `/mnt/data/popcorn_solo_r2_pilot_proof/motion_pilot_NO_AUDIO.mp4`, 7.000с, 1080×1920, 30fps, 210 кадров H264, **без аудио**.
- `ffmpeg -xerror -f null` на точном r2 MP4: PASS. FFmpeg contact 7 кадров реально открыт глазами; поднимающийся пар и дрожание зерна видны, титры не перекрывают предметы. Средняя попиксельная разница относительно t=0.5с: 3.73/6.34/7.63 пунктов серого на t=1.5/2.5/3.5с (это не оценка художественного качества, только факт изменений кадров).
- Рисовка остаётся простым S1-D25. На концовку/голос никто не откатывался, состояние **MOTION_VISUAL_GATE_PASS / VOICE_BLOCKED**.
- После gate запущена отдельная **полная НЕМАЯ** графика на 36.66с: `jobs/motion/popcorn_solo_full_silent_20261103.json`, commit 8539989a; это не finished video и не пригодно к заливке без Qwen и корректных word-timings.

## Полная изолированная картинка — реальный физический MP4

- **GitHub Actions 41726921275 SUCCESS**, artifact **13274901963**: full silent visual body. Точный локальный `/mnt/data/M1lash_Popcorn_SILENT_VISUAL_DRAFT_v2.mp4`, **36.666667с, 1080×1920, 30fps CFR, 1100 кадров, H264, БЕЗ аудиодорожки**, 3429092 байта, SHA256 `9a64c97ca8efc0aa2853ff8c09b0bbffd8b4c8103877c4e17bfc2a68664efa10`.
- На **этом точном MP4** `ffmpeg -xerror -f null` полностью прошёл. Контакт каждые 3с из **этого файла** сгенерирован `popcorn_full_visual_proof/contact_3secs.jpg`, открыт глазами: все шесть планов видны, статичных чёрных кадров в последовательности нет. Чёрные неиспользованные ячейки контакт-листа не являются кадрами ролика.
- Отдельно осмотрены шесть реальных стопов нового пилота; browser layout gate на всех предварительных caption bounds успешен. Это НЕ финальный voice-sync, subtitle track и разборчивость речи НЕ доказаны.
- Для сохранности физический silent MP4 залит **только в личную Library пользователя**, папка `/Youtube/M1lash_Popcorn_SILENT_VISUAL_DRAFT_v2.mp4` (libfile `f4c175cb4ca88191a739f9c571f3a40d`). Pilot 7с — личная Library `libfile_601e54d63660819182ddf90b192aab51`; контакт — `libfile_15255abe22688191af424980ebb9503d`. Это не YouTube и не публичный Git.
- Репозиторий хранит оригинальные SVG/HTML сцен и воспроизводимый код, job JSON, научные источники и QA. Частная озвучка владельца / outro никуда публично не помещались.
- `shorts/science_popcorn_20261104/synthesize_denis_private.py` commit `ce4d7616` сохраняет воспроизводимый локальный Qwen+ASR pipeline с отключённой телеметрией и прямым запретом записывать private voice внутри public repo. **Он не запускался**, потому что Qwen weights и локальный Whisper runtime здесь отсутствуют. Финальный MP4 НЕ создан.
- **Открытый RELEASE BLOCKER:** реальное Qwen-озвучивание 12 реплик, корректные True word timings, штатная склейка только с Denis v3 outro и финальный `check.py/look.py/full decode`. Не заявлять READY и не загружать на канал.

## 04.11 — продолжение без локальных весов, защищённая сборка

- Повторно прочитаны актуальные AGENTS§3–4, SKILL и NOW: только свой голос Дениса для авторского ролика (исключение М1lash Мульт здесь не применяется). Других видео и queue не менять.
- В текущем контейнере реально проверено: `qwen_tts=False`, `transformers=False`, `faster_whisper=False`; `/workspace`, `/root/.cache/huggingface` и каталоги с весами Qwen отсутствуют. DNS для `huggingface.co` и `pypi.org`: **Could not resolve host**. Значит синтез здесь фактически невозможен. Никаких Edge/Azure/API обходов, человеческий voice НЕ создавался.
- Две реальные приватные версии доступны: owner reference `denis_reference.wav` извлечён из пользовательского `Milash_voice_project.zip`, approved vertical Denis-v3 outro `1814729B` sha256 `1bd5aa5866b70a9b9b3368105626c05b6807a887f1588abcc43224cd8be972ce` и немой `36.666667с` visual draft с sha `9a64c97ca8efc0aa2853ff8c09b0bbffd8b4c8103877c4e17bfc2a68664efa10`.
- Создан `shorts/science_popcorn_20261104/build_private_master.py` commit `15bc0d13`: только при реальном Qwen+Whisper voice JSON+12 приватных WAV пересчитывает каждый видео-кадр под **истинные** таймкоды, проверяет mobile safe, монтирует audio body, жёстко сверяет approved outro, вызывает штатный assembler + check.py/look.py/full decode; нет YouTube, нет fallback на Диму, нет записи приватных voice/video в public repo.
- `synthesize_denis_private.py` обновлён commit `70d02739` (CPU float32 как подтверждённый прошлый собственный пробник; offline локальная модель+Whisper), commit `4e4ed62a` (короткие настоящие word groups объединяются вместо мигающих титров), commit `505467fb` (каждая реплика SHA256+provenance, при повторном запуске проверяется и **не перезаписывается**). В этом окружении алгоритм TTS **не выполнен** из-за отсутствия весов.
- **Негативные CI случаи:** первый тестовый workflow `41735302501 FAILED` при пути `tests/...`, не подходившем под whitelist `shorts/`; второй `41735521377 FAILED`, т.к. sparse-checkout не выдал отдельный каталог `tests/`. Исправлено локальным `shorts/science_popcorn_20261104/gate_tests.py` и `run_gate_tests.py`, **не изменяя общий workflow**.
- **CI regression gates 41735884366 SUCCESS:** 7/7 настоящих unit-тестов по неверной картинке/ID, Dima/Edge, временным субтитрам, private path, fake outro и структуре 6×2. Дополнительно добавлены тесты компиляции offline Qwen private script и builder, final CI run `41736448743` (см. итог дальше). Тесты не доказывают ещё фактический звук.
- Приватный восстановительный ZIP **`/mnt/data/M1lash_Popcorn_Private_Assembly_Pack_20261104.zip`**, 5,735,650 B SHA256 `0d6001aaf451c40a43a76e1194eb733415b7d4505f784743698f7b722792ddda`, ZIP integrity + три SHA файла проверены. Он содержит только образец хозяина, approved outro и silent preview — **нет веса Qwen/Whisper и нет синтезированного голоса**. Сохранён в **личную Library /Youtube** `libfile_92bc62f24df0819180f31d9440302c85`, **не** в GitHub/YouTube.
- Новый точный `shorts/science_popcorn_20261104/RESUME_PRIVATE.md`: команды одношортсового Qwen синтеза и сборки из private ZIP при восстановлении локальных весов. Финальный status всё ещё **VISUAL COMPLETE / VOICE BLOCKED / NOT READY / NO UPLOAD**.

## 04.11 — итог 11 независимых защитных тестов

- GitHub Actions **41736907367 COMPLETED SUCCESS**: unit runner действительно выполнил **11/11 тестов без ошибок** (лог содержит `Ran 11 tests`, `OK`, `POPCORN_OFFLINE_UNIT_GATES_PASS`). Два новых отрицательных теста: orphan WAV без provenance и WAV с изменённым SHA **отклонены** до рендера. Тесты не синтезируют голос и не заменяют финальный QA.
- `build_private_master.py` commit **2ed7fd60** теперь проверяет не только `speaker/voice_id` каждого WAV, но и индивидуальный checkpoint JSON с правильным SHA256 WAV, текстом, движком и voiceID. При первом добавлении частного approved outro в checkout дополнительно проверяет `git check-ignore` и отказывается копировать, если путь больше не игнорируется.
- Репетиции исходника/голоса ранее в данном окружении не было: без локальных весов Qwen/Whisper **готовой озвучки нет**. Полное качество с реальной speech/timing оценит следующий запуск только после доступности разрешённого offline model runtime.
- После верифицированного `11/11` следующий шаг остаётся `synthesize_denis_private.py --private-reference ... --local-model ... --whisper-model ... --private-output ...`, затем `build_private_master.py` по runbook. Никакого удаления/редактирования других видео, YouTube/upload/date.
