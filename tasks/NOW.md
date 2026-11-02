# NOW — что делается прямо сейчас (чекпоинт агентов)

Зачем: агент упёрся в лимит или сессия оборвалась — следующий запуск (тот же агент после сброса лимита или другой) продолжает **с этого шага**, а не с нуля. Решение Дениса 01.11.

Правила:
- Взял задачу дольше ~15 минут → запиши блок в свой раздел **до начала работы**.
- После **каждого** законченного шага: отметь `[x]`, обнови «Следующий шаг», `git commit` + `push` (коммит маленький: только этот файл).
- «Следующий шаг» пиши так, чтобы его выполнил агент **без контекста этого чата**: точная команда/файл/workflow, где лежат промежуточные результаты.
- Закончил — удали блок (итог — в HANDOFF.md). Пустой раздел = агент свободен.
- Чужой блок не трогать. Исключение: блок не обновлялся > 24 ч и его агент молчит — можно взять, написав «подхватил <кто> <дата>».
- Не класть сюда секреты, фильмы, длинные логи.

Шаблон блока:
```
### <короткое имя задачи> · начато <дд.мм чч:мм> · обновлено <дд.мм чч:мм>
Цель: <что должно получиться, 1 строка>
Шаги:
- [x] 1. …
- [ ] 2. …
Следующий шаг: <что именно сделать, команда/файл> **Drive intake:** 1) проверить появление папки по `publishing/drive_folder.json`, затем `gh workflow run drive-folder-intake.yml` и статус `publishing/drive_scan.json`; 2) отдельная обработка найденного файла в GitHub Actions: ASR RU + таймкоды + проверка сцены, только затем запуск `movie-short.yml` без публикации; 3) тест на реальном маленьком Drive-файле. Пока пустая папка — НЕ запрашивать старые 7 фильмов.
Где промежуточное: <пути, run ID, релизы>
Ждёт Дениса: <нет / что именно>
```

## Claude

## GPT/Codex
### 02.11 — ВСЕ НЕЗАКОНЧЕННЫЕ SHORTS, ПО ОДНОМУ · GPT
- [x] 003 V54 закрыта до PRIVATE review: FxIlxGWVCuw, run41507963691 SUCCESS; Studio private, HD complete, no claims currently. Итог вверху HANDOFF.md; не перезаливать и не назначать дату.
- [x] Полное дерево main3598 файлов инвентаризировано; реестр правил/Shorts: reports/research/2026-11-02_ALL_SHORTS_RULES_AND_BACKLOG.md. Согласованные существующие проекты; новые форматы не придумывать.
- [x]004 V48 пересобрана по реальным сменам планов; check.py0FAIL/1WARN, decodePASS, outro lag0ms; свежий look.py с --overwrite открыт. Код afc6183, отчёт a80f282; MP4 сохранён libfile_18b0162b199881918e93e16a5582fcff version2. Это PRIVATE_REVIEW, полная сверка речи/титров ещё не закрыта.
- [ ] Остаток004: восстановить artifact13094169003, прочитать текущий job/QA, исправить только читаемость тёмных/красных кадров, check.py + look.py финального MP4 и полный слуховой gate.
Следующий шаг:004V48 /workspace/scratch/004_v48/004_V48_OFFICIAL_PRIVATE.mp4 (Library libfile_18b0162b199881918e93e16a5582fcff v2), сверить титры со всей речью и ключевые швы; затем006.006V50 скачана /workspace/scratch/006_v50/kino_006_v50.mp4; source artifact13041863362, job jobs/motion/movie_review_006_v50_ru_wave_dialogue.json. НЕ перезапрашивать файлы. Не считать весь список готовым. Публичная003 уже ждёт решения о дате.

### 02.11 — фактически 6/6 кино-Shorts доставлены (PRIVATE, без публикации)
- [x] **001** kino_001_v53.mp4 **55.000с**, Actions 41401595596, artifact 13121673002, RU actor 77 words /44 ASS, check.py 0 FAIL, FFmpeg full decode PASS.
- [x] **002** kino_002_v51.mp4 **39.300с**, Actions 41402937982, artifact 13122169262, RU 34 words /18 ASS, check.py 0 FAIL, FFmpeg full decode PASS.
- [x] **003** kino_003_v52.mp4 **49.500с**, Actions 41404927108, artifact **13123895312**, 33 RU words/21 ASS, check.py **0 FAIL**, true peak outro **−1.2 dBTP**, sync lag 0.0ms, FFmpeg `-xerror` full decode PASS; contact sheet opened. V50/V51 failed strict TP; fixed in V52 only final AAC encode to 256k, approved outro PCM unchanged.
- [x] **004** kino_004_v47.mp4 **45.339с**, technical PASS but legibility in dark/red section still editorial concern.
- [x] **005** kino_005_v49_natural_open.mp4 **42.279с**, technical PASS.
- [x] **006** kino_006_v50.mp4 **37.600с**, technical PASS, **visual NO-GO**: long wave, third-party watermark in original source. Do not call RELEASE READY.
- [x] Actual physical six MP4 + corresponding QA packaged and ZIP CRC verified: `/mnt/data/M1lash_ALL_6_SHORTS_PRIVATE_20261102.zip` (124,535,928 bytes) **current conversation sandbox only**, not Git or YouTube. Links were provided.
- [ ] NEXT: targeted **004 readability** and **006 visual cuts/source watermark** editorial repair; independently listen to each line before approval. Only after that move to long Chigur graphics by code. Do not ask source files already obtained. Never publish/schedule without owner's «ок».



### 02.11 — ФАКТИЧЕСКИ 6/6 PRIVATE MP4 В ОДНОМ ZIP · GPT
- [x] 001 V53 **55.000с**; 002 V51 **39.300с**; 003 V52 **49.500с**; 004 V47 **45.339с**; 005 V49 **42.279с**; 006 V50 **37.600с**. Все реальные файлы физически получены; `ffmpeg -xerror` 6/6 PASS, `check.py` 6/6 **0 FAIL**, контакт-листы финальных MP4 получены и открыты. 003 V52 artifact **13123895312**, TP −1.2 dBTP, outro audio lag 0 ms. Актёрская RU речь подтверждена в сборочных QA; это не полноценное прослушивание.
- [x] Общий PRIVATE архив: `/mnt/data/M1lash_6_SHORTS_PRIVATE_REVIEW_20261102.zip` **125535106 B, CRC PASS**, содержит 6 MP4 и QA. Источник реальных artifacts — **верх HANDOFF.md**. Никакой YouTube загрузки, дат или публичных действий.
- [ ] **Следующий шаг:** только конкретный художественный ремонт 003 (тёмные планы), 004 (красный контраст/читаемость), 006 (сторонний watermark/несколько серых планов), проверка слуха полной русской дорожки и прав. Владелец должен дать самостоятельное «ок» на релиз. Работать из уже добытых исходников, остальные три **не пересобирать** без доказанного брака; затем длинный Чигур/28 3D-окон.
Статус: COMPLETE технический PRIVATE REVIEW пакет 6/6, не RELEASE READY.

### 02.11 — 003 Whiplash строгий TP gate · GPT
- [x] Из ранее полученного RU source 003 (`13041278425`) смонтированы новые body с русским голосом/ASR, корректным началом и 3-секундным хуком. V50 run `41402501321`: 51.6с, 33 RU words/20 subtitles, **NO-GO +0.5 dBTP** при финальном AAC. V51 run `41403719341`: 49.5с, 33 RU words/21 subtitles, body/dialogue/outro sync исправны, TP **−0.8 dBTP**, ещё NO-GO (нужно ≤−1dBTP). В обоих случаях MP4 внутри runner создаётся, но статус не READY и обычный artifact не сохраняется после check.py fail.
- [x] Технический фикс codec-only: `tools/assemble_with_outro.py --audio-bitrate {192,256,320}k`, передано через `scripts/movie_short.py` и wrapper; **не меняет approved outro PCM/громкость**. Локально повторное AAC-кодирование отдельно approved outro: TP 192k **−1.6**, 256k **−2.0**, 320k **−1.9** (только диагностический тест, не финальный MP4).
- [ ] V52 run **41404927108**, job `jobs/motion/movie_review_003_v50_dialogue.json` (AAC 256k). После завершения скачать настоящий artifact, `ffmpeg -xerror`, `check.py` без FAIL, `look.py` глазами, full body/titres; если fails — не объявлять готовым и не трогать другие пять.
- [x] Пять независимо проверенных реальных MP4 в `/mnt/data/m1lash_final_20261102/`: 001 V53, 002 V51, 004 V47, 005 V49, 006 V50. 002 V51 run 41402937982 artifact 13122169262 check.py 0 FAIL и фреймы 0-38с открыты глазами. Финальный общий ZIP создать только при наличии шестого MP4.

### 02.11 — завершение Shorts: реальные MP4 (GPT текущий запуск)
- [x] На реальном 001 V53 `kino_001_v53.mp4` (artifact **13121673002**, run 41401595596) выполнены полный FFmpeg decode, независимый официальный `check.py` **0 FAIL / 1 WARN burned-in ASS**, `look.py` открыт, длительность **55.000с**, реальный файл скачан. 77 русских слов / 44 титра, хук первые 2с, approved rev4 outro + Dima; PRIVATE.
- [x] Из уже полученных artifacts физически доступны 004 V47 **45.339с**, 005 V49 **42.279с**, 006 V50 **37.600с**; на каждом снова `ffmpeg -xerror` и `check.py` 0 FAIL, файлы/контакты в текущем /mnt/data/m1lash_final_20261102 (только временно, не Git). 006 визуально слабая волна и источник с чужим watermark, не объявлять RELEASE READY.
- [x] 002 V50 из прежнего RU source **реально смонтирован 39.300с, 34 слов /18 captions, firm outro**, но CI **41402495108** честно остановил на единственном `check.py` loudness FAIL **−16.1 LUFS**. Тот же монтаж, body-only gain +0.6dB V51: job `jobs/motion/movie_review_002_v50_dialogue.json`, run **41402937982**.
- [x] **002 V51 физически получена**, run 41402937982 SUCCESS, artifact **13122169262**, `/mnt/data/m1lash_final_20261102/kino_002_v51.mp4` **39.300с**, 34 RU words/18 ASS, full FFmpeg decode PASS, official `check.py` 0 FAIL/1 WARN subtitles burn-in, `look.py` открытый контакт. PRIVATE, без YouTube.
- [x] 003 V47 кадровый аудит подтверждает обрыв «ШЕСТЬ И.» и тёмные пустые планы, выбраны реальные RU окна `114–141.5, 151–166`; V50 job `jobs/motion/movie_review_003_v50_dialogue.json` run **41402501321**, только private.
- [ ] **Следующее действие:** забрать MP4 из artifact run 41402501321 (003) и 41402937982 (002); оба проверить `ffmpeg -xerror`, официальный `check.py`, `look.py --tiles 3x2`, открытый контакт, кадры 0.6/12/25. Если NO-GO — точечный фикс, НЕ подмена старого V47.
- [ ] После шести реально имеющихся MP4 сделать единый private ZIP, добавить в HANDOFF итоги и QA, без загрузки/дат до владельческого «ок».
Не останавливать новую работу на анализе: финальный результат — именно видеофайлы, не отчёт.

### 02.11 — 001 V52 loudness NO-GO → V53 code +0.4 dB body-only
- [x] V52 run `41400484209` stopped by strict `check.py` at −16.0 LUFS (one FAIL), no downloadable MP4 artifact. Hook working in temp run, QA still blocked.
- [x] Bounded `--body-gain-db` added to `scripts/movie_short.py` and passed through artifact wrapper; `jobs/motion/movie_review_001_v50_ru_dialogue.json` now **v53** uses +0.4 dB **body only**, exact official outro unmodified.
- [ ] **Immediately check run `41401595596` V53**, download actual MP4 only if artifact exists, verify 0 FAIL `check.py`, words, 0-3s hook, face/captions/safe area, rev4+Dima/outro lag. Previous real V51 is accessible PRIVATE but lacks hook.
- [ ] 006 V50 middle sea sequence and MR watermark visual NO-GO; 002 V41/003 V45 recover, 004 readability/sound; long Chigur only after shorts.
No YouTube/slot changes.

### 02.11 — фактический QA после восстановления исходников · GPT
Ссылки-истина: `reports/research/2026-11-02_GPT_REPO_FULL_TREE_AND_SHORTS_TRIAGE.md`, верх `HANDOFF.md`.
- [x] Инвентаризация всего дерева Git `main`, чтение актуальных правил и QA. Исправлен marker-rebase workflow (`f0a64a08`), фильмы и коммерческие аудио не пушились.
- [x] **001:** 181.448с RU source, 9/12 ASR windows PASS; V47 был молчаливой сценой. Рабочая приватная **V51** `artifact 13121112903`, 55.000с, 77 RU words/44 subtitles, official QA 0 FAIL. Первый 2с хук слабый — **V52** с опциональным on-screen hook (`ОН ПЫТАЕТСЯ ОТКУПИТЬСЯ`) в run **41400484209**; результат должен быть проверен реальным MP4, а не по статусу Actions.
- [x] **005:** реальный V49 MP4 из `13115195992`, 42.279с, 0 FAIL, SHA и полный decode проверены, PRIVATE REVIEW (требует независимого полного слуха).
- [x] **006:** из 349.25с source ASR 12/14 RU PASS; новый V50 из `13121445219`, 37.600с, 44 RU words/32 subtitles, 0 FAIL, декод PASS, **визуально NO-GO**: 21–28с серый кадр волны, в исходнике MR/Movie Rider watermark. **Не помечать READY**.
- [x] **002:** RU ASR `reports/research/2026-11-02_002_CARLA_SOURCE_RU_ASR.json` 9/11 PASS; `003` и `004` приватные старые MP4/исходники восстановлены для контрольного сравнения; ранее исправленная 003 V45 физически ещё отсутствует.
- [ ] 001 V52: скачать артефакт после run и **покадрово/аудио** проверить hook+ASS+outro, fallback V51 не заявлять финалом.
- [ ] 006: точечная видео-склейка на визуально содержательные планы (физический actor RU звук непрерывен), решить watermark/права; выполнить официальный assembler и полный QA.
- [ ] 002 V41 / 003 V45 — восстановить настоящие файлы или только доказательно исправлять дефекты, 004 проверить safe zone и русские титры.
- [ ] Независимый полный слух/юридический gate; только после шести Shorts — длинный Чигур (28 графических окон 3D). Никаких private YouTube upload, schedule, publish до gate.
Следующий шаг без вопросов: `41400484209` V52, затем кадры 006 21–28с и 002/003 V41/V45.

### 02.11 — полный Git tree audit и русская речь 001 Carson · GPT
Цель: закрыть реальные P0 кино-Shorts 001–006, не повторять уже исправленные V45, длинный Чигур только после Shorts.
Шаги:
- [x] Полная инвентаризация `main` Git tree (3561 blob на 519e975c, truncated=false) и ревизия AGENTS/HANDOFF/NOW, Claude и GPT аудитов; отчёт `reports/research/2026-11-02_GPT_REPO_FULL_TREE_AND_SHORTS_TRIAGE.md`.
- [x] Исходный RU artifact 001 `13034313090` проверен на окнах 126/138/150с; Actions run `41397822304` показал **0 речевых сегментов во всех 3 окнах**. Это причина отсутствия подписей в реконструкции 001 V47; нельзя выдавать тест как проверку всей дорожки.
- [x] Существующий job `jobs/mediaqa/001_carson_ru_speech_windows.json` переведён на 12 последовательных окон `0,15,...,165` для охвата всех ~181с; запущен GitHub Actions `41398179812` (только QA без YouTube).
- [ ] Прочитать `reports/research/2026-11-02_001_CARSON_FULL_SOURCE_RU_ASR.json` либо взять полный `fetch_workflow_job_logs` при NO_GO; найти русский диалог и его времена. Если по всем окнам 0 речи — исходник непригоден для диалогового Short, **не** делать подмену текстом Димы.
- [ ] Восстановить доступные прежние приватные мастера `001 V44, 002 V41, 003 V45, 006 V45` из реальных архивов/Actions, сравнить с регрессиями V47. 005 V49 уже подтверждена только PRIVATE (полный слух не закрыт); 004 V47 аналогично.
- [ ] Все шесть — полный контроль реального финального MP4: actor RU+Dima+финал на слух, `ffmpeg -xerror`, `check.py`, `look.py`, ASR соответствия, текст-safe, права; только потом PRIVATE review, длинный Чигур после.
Следующий шаг: GET `https://api.github.com/repos/osminoog09-star/Shorts/actions/runs/41398179812` и `reports/research/2026-11-02_001_CARSON_FULL_SOURCE_RU_ASR.json`; затем выбрать либо реальное речевое окно 001, либо честный NO-GO и искать старый V44. Не запрашивать у Дениса прежние 7 источников.
Где промежуточное: commit `ace9240e`, `fdca6591`; report `reports/research/2026-11-02_GPT_REPO_FULL_TREE_AND_SHORTS_TRIAGE.md`; Actions `41397822304` и `41398179812`.
Ждёт Дениса: нет; никакой публикации и даты.

### 02.11 — точечное восстановление Short 005, без повторного круга
- [x] Проверил /mnt/data и поиск в личной библиотеке: прежний итоговый ZIP V45 и MP4 **не найдены**. Все RU source artifacts доступны; ничего повторно у владельца не запрашивать.
- [x] Проверка точной сцены 005: source `m1lash_short_source_13052196021.zip`, `originals/nightcrawler_no_thieves_ru_test.mp4`. В движении кадр t14–19 относится к работодателю (сдвиг X), t24–29.5 к Лу справа, t29.5+ к работодателю. Контакт 4 исходных и отдельные 9 итоговых preflight-кадров открыты глазами.
- [x] Исправлен код `scripts/movie_short.py`: measured ASS width ≤790px, шрифт/длина группы под экран, `--editorial-profile nightcrawler` и ручные точки actor-focus вместо авто выбора чужого лица.
- [x] **CI blocker найден и устранён**: в `motion-render.yml` неэкранированный YAML `QA: private...` в concurrency group блокировал все jobs (0 jobs); `movie-media-qa.yml` имел случайно продублированные 25+ строк YAML. Теперь оба реально запустились.
- [x] Самостоятельный точечный BODY-only preflight `/mnt/data/005_patch_preflight/005_corrected_body_PRIVATE_NO_OUTRO.mp4`, 32.033333 с 1080×1920/30, сохранён оригинальный RU звук, full FFmpeg decode PASS. **Это не финальный Short и не замена фирменной концовки**.
- [x] Actions `41382193226` export approved rev4 + Dima PRIVATE artifact 13113069102 (success); Actions `41382544964` exported **real 005 V48 MP4**, artifact **13114505366**; full video/audio decode PASS, QA 0 FAIL, 50 blocks RU ASR, 40.979с. **10 реальных кадров** 0.4–33с визуально просмотрены, t23.6 лицо в кадре, т14/t31 работодатель в кадре, X-overflow отсутствует. **НО 0.4с обрубленный ASR текст «РЕБЕННАЯ РАБОЧАЯ»: художественный NO-GO.** 
- [x] **02.11 следующий шаг выполнен в исходнике, без нового фильма:** проверено, что V48 начинает титр «РЕБЕННАЯ РАБОЧАЯ» на t0.4с, потому что `segments[0]` резал оригинал с **17.0с посреди произносимого слова**. На исходном RU аудио обнаружен более тихий участок около 15.7с перед началом активной реплики (RMS); созданы 4-секундное проверочное видео и контакт 5 кадров из того же RU source: `/mnt/data/005_new_start_preflight.mp4`, `/mnt/data/005_new_start_contact.jpg` — открыт глазами, оба глаза/лицо не обрезаны.
- [x] В `scripts/movie_short.py` ночной ручной центр по X теперь сдвигается по фактической длине сегментов, сохраняя план работодателя; обновлён `jobs/motion/movie_review_005_v48_patch1.json` source windows **15.7–41 / 50–58**, edition `v49_natural_open`, только приватный QA; commit `54948dbb`.
- [x] **V49 получен и независимо проверен:** GitHub run **41384470736**, artifact **13115195992**, физический `/mnt/data/m1lash_005_v49_review/kino_005_v49_natural_open.mp4`, SHA256 `e83f583fa5e8ca8d7530fbbcb0853b5ff0f167747dfe28314102dd6b52db974b`, 42.279с (тело 33.333 + утверждённая концовка 6.6 + Дима title 1.996), ASR 92 RU слова/52 титра. **ОБРЫВОК СЛОВА ИСЧЕЗ**: t0.4 «НО ПОНЯЛ», t0.8 «ЧТО СОВРЕМЕННАЯ», t1.6 «РАБОЧАЯ КУЛЬТУРА». Full ffmpeg decode 0 ошибок; официальный check.py 0 FAIL/1 WARN и look.py повторены локально, просмотрены 21 стоп +12 на промежутке 17.5–23c. Лица/титры не обрезаны; t19.5–20.5 кино-проход по потолку ~1с — художественная слабость, но не сломанный кроп. Отчёт `reports/research/2026-11-02_SHORT005_TARGETED_RECOVERY_PRIVATE_QA.md`, приватный QA ZIP в `/mnt/data/M1lash_005_V49_PRIVATE_REVIEW_WITH_QA.zip` CRC PASS. **Публикация не разрешена**, полный человеческий слуховой контроль пока отсутствует.
- [ ] **Следующий шаг:** 001 Carson — `/mnt/data/shorts_sources/001_chigur_carson_ru.mp4` 181.45с ранее скачанный RU source, V47 отложить (0 ASR, 0 subs); найти прежде одобренный V44, либо на существующем source аудио 128–160с проверить, есть ли действительно нужная русская речь; только затем минимальный смысловой ремонт. 002/003/004/006 — старые результаты/проблемы в аудите. 005 V49 можно отдавать только PRIVATE review на «ок», не публиковать.
- [ ] Потом 001/002/003/004/006 только по конкретным исправлениям из `reports/research/2026-11-01_GPT_SIX_SHORTS_DEEP_FRAME_AUDIT.md`; длинный Чигур на паузе, YouTube upload/даты запрещены до владельческого ok.

### 01.11 · ФАКТИЧЕСКИЙ ГЛУБОКИЙ АУДИТ 6 SHORTS (приказ владельца)
- [x] Шесть V47 MP4 реально распакованы из Actions artifacts; **6/6 новый full FFmpeg decode PASS** на обоих потоках, формат 1080×1920 30fps H264/AAC.
- [x] На каждой истории извлечено по одному кадру каждые 2с (15/16/17/17/16/22 кадров), просмотрено глазами; также проверено 24 кадра всех шести утверждённых концовок и 18 full-HD спорных кадров.
- [x] В `reports/research/2026-11-01_GPT_SIX_SHORTS_DEEP_FRAME_AUDIT.md` точно зафиксированы риски: 001 ASR=0/нет титров; 002 титр слева за кадром t12; 003 хук с обрывка «ШЕСТЬ И.», повтор Флетчера; 004 тёмный красный кадр и мелкие титры, RU фильм/Dima ASR PASS; 005 гигантская надпись за оба края t0.4 и лицо обрезано t23.6; 006 мало титров и horizontal letterbox t40. Ни один V47 в публикацию не допускать.
- [x] QA ZIP `/mnt/data/M1lash_6_SHORTS_REAL_AUDIT_V47_20261101.zip` (только материалы проверки, без MP4) сформирован и CRC PASS. Все кадры/отчёты сохранены в текущем контейнере.
- [ ] **Следующий шаг** (НЕ очередной V48): восстановить действительно прежние `001 V44/002 V41/003 V45/005 V45/006 V45` из приватных оригинальных ZIP/файлов, сравнить с проблемными V47; устранить только подтверждённые оставшиеся дефекты и сделать полный QA+слух. Никакой публикации до владельческого «ок». Важно: старые MP4 в данной среде не подтверждены, НЕ врать, что они готовы/проверены заново.

### 01.11 · УБРАТЬ ПОВТОРНЫЕ СБОРКИ ПО УКАЗАНИЮ ВЛАДЕЛЬЦА
- [x] Денис подтвердил: монтаж текущих 6 кино-Shorts **уже делался**, заново без оснований не перемонтировать.
- [x] V47 artifacts run 41336716775 физически скачаны; **6/6 MP4 full ffmpeg decode PASS**, официальные `check.py` 0 FAIL. Но контентный аудит `reports/research/2026-11-01_GPT_V47_REBUILD_REGRESSION_AUDIT.md` нашёл регрессии: **001 0 слов/нет титров (NO-GO), 003 снова повтор Флетчера, 005 лицо срезано, 006 затянутая слабая сцена, 002 одна и та же женщина почти весь фильм**.
- [ ] **Следующий шаг без повторной сборки:** сохранить прежние проверенные 001 V44 / 002 V41 / 003 V45 / 005 V45 / 006 V45 как **предпочтительные**, 004 V47 проходит техническую и RU ASR; найти/восстановить именно эти уже проверенные mp4 (не заменять новой V47), вручную свести один PRIVATE review packet. Старые исходники/фильмы повторно не просить. 001 V47 в готовые не включать. Только после полного слухового QA и ручного просмотра — дать Денису на «ок». Не запускать новый CGI/Chigur/материалы Drive до окончания Shorts.

### Текущий контроль кино-Shorts — ошибки и точные повторные действия
- 001/002/003/005/006: первый run `41334672815` упал из-за незаметных `\` перед GH expressions, дававших URL артефакта `%5C...`→401. Исправлено в `.github/workflows/movie-short-five-rebuild.yml` (commits `9b9291a`, `341d533`); 001 обязательно Carson, не водитель.
- Второй run `41335816190` скачал все RU исходники и дошёл до Whisper, но **все пять** отключил `dead_windows`: 001 16.5–19.5с; 002 3–6,7.5–10.5,36–39с; 003 22.5–30с; 005 24–33с; 006 31.5–42с. Не заявлять как готовые.
- Кадры 001/002/005/003/006 исследованы; для 001/002/003/005 записаны точные монтажные окна `scripts/qa/cut_russian_story_segments_v47.py`. Для 006 FFmpeg сцены корабля 254–265с показывают важное движение, не вырезать: добавлен `scripts/qa/movie_action_gate.py` и **опциональная** проверка реальных кадров + SFX в `scripts/movie_short.py`, только для 006 (нижняя граница motion median18, LUFS >-45, 3–12с).
- Третий run `41336716775` на коммите `dd2c933` запускает пять матричных сборок с этими исправлениями. **Следующий шаг:** через `tools.mcp__GitHub__fetch({url:'https://api.github.com/repos/osminoog09-star/Shorts/actions/runs/41336716775'})` прочитать status, `fetch_workflow_run_jobs`/logs для отказов, `fetch_workflow_run_artifacts` при success, `download_workflow_artifact`, проверить реальный MP4 через `check.py`, `look.py`, визуальный контакт и звук. Один консолидированный private ZIP, без YouTube публикации.
### Шесть Shorts, фактический результат 01.11
- 004: run 41333893324, artifact 13094169003; V47 45.339s настоящий MP4; check.py 0 FAIL, look.py глазами, outro lag 0.3ms, русский ASR актёров p=.964/.942 и Димы p=.996. Файл находится в /mnt/data/m1lash_6shorts_final/, ссылка уже дана пользователю. Не публиковали.
- 001/002/003/005/006: запущен параллельный GitHub workflow movie-short-five-rebuild.yml, V47 пока НЕ готовые мастера. Для каждого искать reports/research/short_ID_V47_RUN.json, скачать artifact и открыть контакт; до этого статус PENDING.
- В main также есть альтернативные job specs jobs/motion/movie_review_ID_v47.json от другого агента. Не загружать дубли: предпочесть сюжет 001 Carson, 002 Carla, 003 Whiplash, 005 Nightcrawler, 006 Interstellar и финальный QA.
- Неправильный кандидат 003 source artifact 12776800730 = Gladiator, отбраковали. Правильный Whiplash = 13041278425.
Следующий шаг: взять реальные artifact всех пяти, проверить MP4/звук/check/look, только после этого PRIVATE review. Никаких фильмов у Дениса повторно не просить.
### Приоритет по прямому приказу Дениса: довести 6 Shorts до финала · 01.11 19:50 Tallinn
Цель: закрыть 001–006 с реальным MP4, русским звуком и независимыми check/look, затем PRIVATE review без даты; длинный «Чигур» строго ПОСЛЕ.
Шаги:
- [x] Получена команда «Доделай щортсы сначала до конца». Длинный «Чигур»/V14 поставлен на паузу без публикации.
- [x] Проверен прошлый статус: 003/005/006 V45 и 004 V46 уже реально монтировали и проходили check/look, НО временные мастер-файлы прежней сессии не смонтированы в этот контейнер. `git ls-remote` заблокирован DNS; GitHub connector доступен.
- [ ] Повторно восстановить доступные точные исходники и медиа через GitHub Actions artifact, найти approved outro, получить воспроизводимый финал и QA; отсутствие старых master MP4 не скрывать.
- [ ] Проверить авторский Дима voice и русскую актёрскую речь на 001–006, особенно финальное название 006.
- [ ] Собрать и выдать реальные финальные MP4/ссылки, сверить check.py/look.py и отправить на PRIVATE review только после gate, без даты.
Следующий шаг: из старых Actions artifacts восстановить 004 из 13070096727 (уже локально присутствует ZIP), получить approved outro `media/outro/m1lash_outro_v1_vertical.mp4` и новое Дима title через Actions. Затем остальные исходники/аудио по `reports/source_requests_2026-10-31.md` и `HANDOFF.md`. Использовать `tools/assemble_with_outro.py`, `skills/ext/ffmpeg-skill/scripts/check.py` и `look.py` только на реальном финальном MP4. Не подменять старые V45 фальшивой READY отметкой.
Где промежуточное: `scripts/qa/rebuild_004_clean_ru_safe_v46.py`, `reports/research/2026-11-01_GPT_004_V46_SAFEZONE_AND_CHIGUR_V9.md`, Actions media artifacts.
Ждёт Дениса: только финальное «ок» после реального PRIVATE просмотра.


### Доработка семи кино-роликов после актуализации студии · 01.11
Цель: 6 Shorts и «Чигур» до реально проверенных PRIVATE masters, без публикации.
Шаги:
- [x] Перечитать актуальные AGENTS.md, весь m1lash-studio/SKILL.md/«Уроки», visuals-by-code.md, NOW, ежедневный регламент, план исправлений, аудит Claude, issues GPT; 7 строк «Понял» внесены в HANDOFF.
- [x] Штатный `tools/assemble_with_outro.py --help` и п.2а: **6 новых настоящих MP4 V41–V44**, финал собран исключительно этой командой, без ручного concat/AAC. Полный decode, внутренний аудио-тайминг и совпадение концовки — все 6 PASS.
- [x] На **каждом из шести выбранных MP4** штатный `check.py --platform shorts` — **0 FAIL**, единственный WARN «нет внешней дорожки титров» (они вшиты); `look.py --tiles 3x2 --safe shorts` — 6 PNG, просмотрены глазами. Все 6 в приватном QA ZIP, без заливки.
- [x] Пакетный дефект стартовых пиков 001/004/006 устранён **только обработкой тела** (мягкий 150мс fade и выборочный gain), утверждённая концовка сохранена по стандартной функции. Добавлены 4 безопасные CLI-опции в `tools/assemble_with_outro.py`, NumPy ускорение с fallback.
- [x] Этап 3 (п. 3 после проверки Claude 15:20): реально перемонтированы 003/005/006 в V45, без повторного удаления уже вырезанного: 003 контрплан 2.0 с из 21.0–23.0с исходника БЕЗ неверного вшитого титра и при сохранении актёрского аудио, 005 -0.733 с тихой паузы, 006 -1.900 с моря. Финалы через только assemble_with_outro.py. Штатные check.py 3/3 (0 FAIL, subtitle stream WARN), look.py 3/3 визуально просмотрены. Длительности ВСЕХ шести MP4 и QA в reports/research/2026-11-01_V45_CLAUDE_AUDIT_MOVIE_EDITS_003_005_006.md. Независимый слух/ASR 006 и 004 safe-zone остаются отдельными открытыми пунктами.
- [x] Этап 5a: точным `look.py --safe shorts` подтверждено, что 004 при 26с имеет субтитр на нижней 18%-й UI полосе. Самостоятельно восстановлен **чистый RU source** `/mnt/data/m1lash_exmachina_safe_source/originals/machina_ava_ru_blackout_ok_candidate.mp4` из Actions artifact 13070096727, точно найдено соответствие аудио исходника/body по FFT; план исправления в `reports/research/2026-11-01_004_SAFEZONE_ORIGINAL_SOURCE_RECHECK.md`. До пересборки 004 NO-GO.
- [x] Этап 4 preflight V7: 6 новых 16:9 Three.js стопов реально отрендерены Actions #41314121375 (artifact 13086790544), открыты глазами и **NO-GO** — не тянут качество rev4. Отчёт `reports/research/2026-11-01_CHIGUR_V7_SIX_STOPFRAMES_VISUAL_REJECTION.md`.
- [x] **V8: шесть PNG реально получены** в Actions #41318411623 (success; artifact 13088501329) и открыты глазами. Художественный **NO-GO**: слишком грубая геометрия, плавающая осциллограмма, слабая композиция; координаты осциллограммы в коде поправлены, новый рендер ещё не проведён. Детали `reports/research/2026-11-01_CHIGUR_V8_VISUAL_AUDIT.md`.
- [x] **Short 004 V46**: реально новый 44.100с MP4 из чистого RU исходника (без старой вшитой нижней плашки), аудио фильма сохранено; ASS подняты выше UI-safe. Фирменный outro собран строго `tools/assemble_with_outro.py`; полный decode PASS, встроенный QA 0 проблем, lag 0мс, официальный `check.py` 0 FAIL, финальный `look.py --safe shorts` **открыт глазами**. Отчёт `reports/research/2026-11-01_GPT_004_V46_SAFEZONE_AND_CHIGUR_V9.md`. Независимый ASR/слух пока NOT VERIFIED.
- [x] **Chigur V9**: CI Actions 41320278050 / artifact 13088732380, шесть настоящих 3D PNG отрендерены и визуально проверены; осциллограмма стала локальной деталью прибора, но художественный **NO-GO**, 28 старых окон пока нетронуты.
- [x] Прочитаны новые задания Claude: `tasks/gpt_week_45_plan.md`, `tasks/gpt_site_clip_requests.md`, `tasks/gpt_site_queue_ux.md`; в `publishing/clip_requests.json` **уже есть 10** RU кино-сцен, повторно не создавать.
- [x] Сайт «Клипы» — первая функциональная часть: вкладка с числом ожидаемых сцен, карточки 10 заявок, безопасное сохранение HTTPS-ссылки и пользовательской заявки через GitHub токен в браузере. `site/studio/clips_ui.js`, `scripts/build_studio_site.py`; **автоимпорт/рендер и тест мобильного UX остаются открытыми**.
- [x] Drive intake этап 1: одна папка для НОВЫХ сцен без ссылок, безопасный gdown metadata scanner, fuzzy RU/EN+год, статусы, button+cron 2ч, тесты CI; работоспособность запуска подтверждена `publishing/drive_scan.json` с scanned_at=2026-11-01T15:55:45Z. Реальная папка пока НЕ настроена.
- [x] Drive intake этап 2a: добавлен консервативный `scripts/drive_scene_probe.py` + `drive-scene-probe.yml` (каждые 6 часов, сразу отключается при пустой папке), RU язык 3 пробами, полный ASR фильма, 3 НЕПРОВЕРЕННЫХ кандидата времени, статус в `publishing/scene_candidates.json`, без YouTube/исходников в Git. Тесты HH:MM и URL, подключён статус на сайт. На настоящем фильме НЕ проверено.
- [x] 01.11: Денис сообщил, что открыл доступ к Drive-папке; `publishing/drive_folder.json` переведён в `scan_enabled=true`, commit `2919a683`, запускает workflow по push. Метаданные Google Drive **в момент проверки всё ещё `shared=false`, только owner**; не утверждать, что публичный доступ проверен.
- [ ] Drive intake этап 2b: получить свежий результат `drive-folder-intake.yml` и убедиться в публичной доступности папки; проверить E2E маленьким файлом, потом RU ASR+визуальный/слуховой QA сцены → `movie-short.yml` приватно; cache/виджет. `reports/research/2026-11-01_DRIVE_FOLDER_INTAKE.md`.
- [ ] Сайт «В работе»/перенос даты с подтверждением занятых слотов и автоматический Drive→temp fetch→movie-short, см. новые задания Claude.
- [x] 01.11 V10: 6 новых Three.js кадров из CI run 41326149031 / artifact 13091745319 **реально скачаны и визуально просмотрены**. Полный экран кадры сделаны, но художественный NO-GO: неправильно стоящие бумажные реквизиты в 01/04, сквозная осциллограмма в 03, слабая композиция/свет. Нельзя вклеивать в 28 окон.
- [x] 01.11 004: восстановлен старый RU mp4 из Actions artifact 13070096727 **без запроса фильма**. В новом generic `movie-media-qa.yml` Whisper подтвердил RU в двух речевых окнах 68/84с, вероятности 0.916/0.918, окно 33с без речи. Report `reports/research/2026-11-01_004_SOURCE_RU_ASR.json`. Это подтверждает source, не финальную озвучку Димы.
- [x] 01.11 V11: 6 фактических PNG из Actions `41326594117`, artifact `13091586449`, контакт-лист открыт глазами. Горизонтальная бумага, видимый сигнал, машина с лобовым стеклом улучшены, но общий художественный **NO-GO** (плоские помещения, модели/композиции недостаточны). Не вклеивать.
- [x] 01.11 V12: реальный Actions run `41327034271`, artifact `13091328887`, **все 6 PNG 960×540 скачаны и просмотрены глазами**. Утверждённый S6-D25 text/lens на 3D: читается, предметы не закрывает. Но сцены коридора/авто и отсутствие человеческой реакции всё ещё художественный NO-GO для полной сборки 28 окон. Отчёт `reports/research/2026-11-01_CHIGUR_V10_V11_PHYSICAL_STILLS_QA.md`.
- [x] 01.11 V12 motion: CI **41327391256**, artifact **13092590059**, настоящие 6.000с H264/AAC 1920×1080 **30fps**, полный ffmpeg `-xerror` decode PASS, 6 кадров 0.5–5.5с собраны и **просмотрены глазами**, motion RGB mean diff 1.69–2.45. Но **художественный NO-GO**: почти статичная камера/волна. Отчёт `reports/research/2026-11-01_CHIGUR_V12_MOTION_PILOT_QA.md`.
- [x] 01.11 V13: Actions **41327670440**, artifact **13092121882**, 6 PNG просмотрены глазами; NO-GO: фигура-манекен, рука отказа не попала в кадр. `reports/research/2026-11-01_CHIGUR_V13_V14_ART_DIRECTION.md`.
- [ ] 01.11 V14: `longform/chigur/graphics/three_stage_v14_atmosphere.js` заменил манекен тенью двери, переместил руку в кадр и сменил камеру; `jobs/motion/chigur_v14_six_stills.json` отправлен в CI. Проверить `reports/research/chigur_v14_run.json`, скачать 6 PNG, открыть глазами; только после этого решать следующий pilot/full graphics.
- [ ] Этап 4: 28 устаревших PIL-графических окон длинного REV19 заменить постановкой HyperFrames/HTML+Three.js+Playwright. До full render сначала **4–6 достойных стопов**, сравнить с rev4 outro и настоящий 5–10с pilot; V5 старый прототип NO-GO.
- [ ] Этап 5: полный звук, исходные кинодоказательства, финальные check.py/look.py длинного 1920×1080, финальный HANDOFF/урок, передать на личное «ок»; ничего не публиковать.
Следующий шаг: **V14 Chigur 6 stills → visual QA**: проверить `reports/research/chigur_v14_run.json`, скачать 6 PNG и визуально проверить отсутствие манекена/наличие руки отказа; 28 окон пока NO-GO. 004 source RU ASR PASS по двум речевым окнам, НО финальный Дима/слух/права не закрыты. **Справка по уже существующим видео:** `/mnt/data/m1lash_work_20261101/004_V46_OFFICIAL_PRIVATE.mp4` 44.100с из русского чистого киноисходника, новый safe-zone текст; штатный assembler `outro_lag_ms=0.0`, `check.py` 0 FAIL, финальный `look.py --safe shorts` и полный decode PASS, глаза просмотрены, результат в `reports/research/2026-11-01_GPT_004_V46_SAFEZONE_AND_CHIGUR_V9.md`. ASR RU/права — НЕ проверены, статус PRIVATE. **Chigur**: 6 V9 стопов отрендерены Actions #41320278050, но художественный NO-GO — не вклеивать; качественно менять композицию/модели, а не выдавать CI зелёный за 8/10, затем 6 PNG → 5-10с пилот → 28 окон. **Claude задачи**: 10 сцен уже в `publishing/clip_requests.json`; создана вкладка `site/studio/clips_ui.js` (поля ссылок и сохранение в GitHub), Pages CI #41321472413 SUCCESS (включая node --check и сборку data.json), провести ещё мобильный визуальный тест; дальше `tasks/gpt_site_clip_requests.md` этап download/fetch (не готов), `tasks/gpt_site_queue_ux.md` «В работе»/перенос даты. Никаких загрузок на YouTube.
Где промежуточное: `/mnt/data/m1lash_edit_v45/M1lash_6_SHORTS_V45_STORY_EDITS_PRIVATE_QA_20261101.zip` (214211685B, SHA256 0dbd4ddcff7fc32ea6e67ed7262aa194ff46ee1d10261660d5427e100c7ecb72); исходный предыдущий `/mnt/data/M1lash_6_MOVIE_SHORTS_OFFICIAL_ASSEMBLER_V41_V44_PRIVATE_QA_20261101.zip` (218163056B, SHA256 `5ccedaa93cffc298a55dc6bd543d7e185e8910a887ab2b692be5bed5cc67c01e`); `/mnt/data/m1lash_2a_rebuild/` (6 MP4 + check + contacts + QA); отчёт `reports/research/2026-11-01_V41_V44_OFFICIAL_ASSEMBLER_6SHORTS_QA.md`; исходники body `/mnt/data/movie_shorts_remastered_v22_private/`; long `/mnt/data/M1lash_Chigur_REV19_1080p_PRIVATE_REVIEW.mp4`.
Ждёт Дениса: ничего; согласование публикации исключительно за ним.
