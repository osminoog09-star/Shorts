# QA — private promo V4 · «Атлас тёмных солнц»

**Фактический статус:** `DRAFT / TECH_BASICS_PASS / ART_NO_GO_FOR_PUBLICATION / VOICE_AND_APPROVED_OUTRO_PENDING`. **Это не готовая YouTube публикация и не 21+ минутный мультфильм.**

## Файлы и сохранение

- **Приватное хранилище:** Library `/Youtube/M1lash_DarkSuns_Promo_Private/ATLAS_TEMNYH_SOLNTS_PROMO_PRIVATE_PREVIEW_V4.mp4`, owner-only (`libfile_9aaaf608aec88191a5a7fd1e1aba672d`).
- Локальный файл из текущей сессии: `/mnt/data/dark_suns_promo_20261106/ATLAS_TEMNYH_SOLNTS_PROMO_PRIVATE_PREVIEW_V4.mp4`. Мгновенная ссылка для пользователя создаётся только в том сеансе, где путь реально существует.
- **Исходный код/stills/QA в private Library**: `/Youtube/M1lash_DarkSuns_Promo_Private/ATLAS_DARK_SUNS_SOURCE.zip` (`libfile_737ec67ea784819187317d0fb26a1bd4`). В ZIP `stage.html`, `render.py`, `audio.py`, contact sheets. Оригинальные WAV и приватный голос владельца не выгружаются в публичный Git.
- Реально декодированные кадры V4 в `/Youtube/M1lash_DarkSuns_Promo_Private/V4_FINAL_CONTACT.jpg` (`libfile_7e5e0daf96888191a682f73f123bb8d5`).

## Физически измерено

- Duration: 42.005s (видео 1260 кадров 42.000s); 1920×1080 / 30fps; H.264 / `yuv420p`, ограниченный диапазон ТВ, BT.709 transfer/primaries/matrix; AAC stereo 48kHz. Размер V3 17 MiB, V4 метаданные поправлены без повторной кодировки по цвету (размер по повторному readback не зафиксирован в этом файле).
- Финальный V4: `ffmpeg -v error -xerror -i ... -f null -` завершился с кодом 0 на всех потоках. На V2 `blackdetect >=0.12s`, `freezedetect >=2.5s`, `silencedetect >=1.2s` событий не выявили. Композиция V4 после перекодировки не менялась.
- Музыка: оригинальный procedural ambient из `audio.py`, без чужих мелодий и источников; на V2 после усиления +2dB интегральная громкость **−18.6 LUFS**, true peak **−1.7 dBFS**, LRA 7.9 LU; V4 наследует эту дорожку без перекодирования при финальном metadata remux.
- SHA256 V4: `8aacbf70029ee77710973dcbd2316d3e9f27c36cd01996569a0956139f56a76b`.
- Контакт-лист из **финального V4** физически открыт глазами, 12 разных временных точек: затвор, космическое угасание, живой транспорт над городом, зал обсерватории, Врата, героиня/компас, ковчег и титул. Пустых/сломанных сцен на этих точках нет.

## Почему не ставим READY

1. **Голос Дениса отсутствует.** AGENTS §3 требует narrator/главного героя только Denis Qwen. Чужой мужской TTS не заменять. Существующий CI `.github/workflows/denis-voice-tts.yml` успешно проверялся на других фразах, но в этом проекте отдельные утверждённые реплики не генерировались — при текущем локальном runtime Qwen/owner ref не доступны.
2. **Approved Denis v7 horizontal outro отсутствует** в локальной сборке. Не создавать фальшивую замену и не объявлять релизную версию.
3. **ART NO-GO**: видимые все 7 сцен — выразительный, но ещё упрощённый 2D cut-out/motion-comic. Недостаточно мелких деталей большого мира и натуральной анимации лица/руки, повторяются кольца затвора на нескольких планах. Нужно не путать сложный код и художественное качество. Сейчас это концептуальный видеопилот для решения владельца, не целевой S10-D25 ART 8/10.
4. **Официальные** `skills/ext/ffmpeg-skill/scripts/check.py` и `look.py` **НЕ запускались** в текущем контейнере (не установлен пакет скриптов из repo). Вместо этого на фактическом V4 выполнены ffprobe/full decode и самостоятельная FFmpeg-временная выборка 12 кадров, осмотр; не выдавать за эквивалент официальному check/look PASS. Перед приватной YouTube-заливкой надо получить инструменты из репозитория и запустить официальные команды на новой версии с голосом/outro.

## Важный технический урок

Первая сборка из screenshot-JPEG → x264 при `-pix_fmt yuv420p` дала V2 с **yuvj420p FULL** range в ffprobe. V3 перекодирован с `scale=in_range=pc:out_range=tv,format=yuv420p`, V4 дополнил SPS битстрим-флагами `h264_metadata=colour_primaries=1:transfer_characteristics=1:matrix_coefficients=1:video_full_range_flag=0`. Только после фактического probe V4 получено `yuv420p tv bt709/bt709/bt709`. Добавить явный range/BT709 gate в будущий конвейер кодовых сцен.
