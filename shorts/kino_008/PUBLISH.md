# kino_008 — кино-Shorts · PRIVATE YOUTUBE REVIEW / NO DATE (06.11.2026)

## Название
Они нажали кнопку — и даже ЗВУК исчез… 😨 #shorts

## Описание
Обратный отсчёт закончился. Но самая страшная часть началась потом.
Ты угадал фильм до последней секунды? Напиши, когда понял!

Song: Laeko - DONT WANNA KNOW!!!
Music provided by NoCopyrightSounds
Free Download/Stream: http://ncs.io/dontwannaknow
Watch: https://ncs.lnk.to/dontwannaknowAT/youtube

#shorts #кино #угадайфильм #фильмы #эпичнаясцена #сценаизфильма #m1lash

## Теги
кино, угадай фильм, эпичная сцена, обратный отсчёт, сильная сцена, кинозагадка, movie short, russian dub, shorts, m1lash

## Закреп
На какой секунде ты понял, что произойдёт? И узнал ли фильм до последней фразы? 👀

## Настройки
- **PRIVATE на YouTube без даты — только после настоящего full decode + official ffmpeg-skill check.py/look.py и визуальной/звуковой проверки.**
- `category_id="1"` (Фильмы и анимация), `made_for_kids=false`, `contains_synthetic_media=true`, `default_language=ru`.
- После появления `youtube_id` и PRIVATE GET добавить в `publishing/receipts/kino_008.json`, `publishing/queue/kino_008.json` (без `publish_at`), `publishing/queue.json` status=review. Тогда владелец назначает дату через M1lash Studio, НЕ агент.
- Не указывать фильм/год/франшизу публично: название только своим Qwen голосом Дениса в самом конце поверх последнего кадра нетронутого approved outro Denis v7; **без экранного титра** (исключение Batman на kino_008 НЕ распространяется).
- Фильм **внутри записи владельца**, не из пиратского torrent и не YouTube bot-check: `Screen_Recording_20261103_124519_Opera.mp4` 836471622 байт / `SHA256 a784b456047834339c4cc908d638f03d3b032917ca6b51aa948cf59312e656e1`. Исходник Google Drive, не коммитить.
- Исходный звук: русский в 4/5 samples по FFmpeg+faster-whisper; точные субтитры и нужный countdown/explosion ещё в QA. Рабочая сцена по первому приватному контакту ~15:30–18:40 **записи**, точнее пока не проверено.
- Голос: личный Qwen3-TTS 1.7B Base ICL, job `jobs/voice/kino_008_title.json`, no fallback; master-approved 6.6s voice10 outro SHA `2e514186940d130e6aea6aa5171b59ba7691d5cfe14fb329d65a8d12184a6b60`.
- Кино — правообладатель Universal Pictures; Content ID/монетизация и риск претензии не очищены. Владелец принял риск для кино-Shorts, но не для обхода DRM. Одинаковый исходник не заливать повторно при claim.

## Фактический результат 06.11.2026
- **YouTube PRIVATE video_id `G4IMzvrv1Zw`**: https://studio.youtube.com/video/G4IMzvrv1Zw/edit. YouTube API `videos.list` GET подтвердил `privacyStatus=private` и отсутствие `publishAt`, workflow run **42152379901 SUCCESS**. Дата назначения = **не установлена**, публикация = **не одобрена**.
- Финальный реальный MP4 1080×1920 / 30fps / **43.133333 с**, **27,228,692 байт**, SHA256 `7a00d601d62a578007ec7d98103cedcfd22e801c7c047d4fd225029abd19ed95`. Тело V2 32.766341с / verified RU recording, approved unmodified Denis v7 6.6с, финальный собственный voice Denis title ~3.405с. Голос Qwen V2 был проверен ASR 2/2 на GitHub Actions `42147263572`; отдельное субъективное прослушивание владельцем остаётся открытым.
- **QA финального MP4 подтверждён:** `tools/assemble_with_outro.py` + official `skills/ext/ffmpeg-skill/scripts/check.py --platform shorts --content` / `look.py --safe shorts --tiles 4x5` GitHub Actions `42151899972 SUCCESS`; 20 фактических кадров контакт-листа осмотрены GPT, 2 провала V1 исправлены. Финальный binary заново скачан из owner-private Drive и независимо проверен SHA256/full `ffmpeg -xerror` decode. Доказательства: `reports/research/2026-11-06_KINO_008_FINAL_V1_PRIVATE_QA.json`.
- Source MP4, owner voice WAV and approved outro остались в owner-private Drive; публичный GitHub хранит лишь метаданные. Не загружать повторно, не планировать без решения владельца. `publishing/queue/kino_008.json` и `publishing/receipts/kino_008.json` — единственные источники для сайта. **В M1lash Studio владелец сам назначает время**.
- Ограничения Content ID/права на кадры и саундтрек правообладателя остаются неизвестными до проверки владельцем в YouTube Studio. Получение `PRIVATE` не подтверждает отсутствия claim.
