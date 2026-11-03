# Новости ИИ за 2 ноября 2026 — фактический review master

[MP4, 40.433 с](https://raw.githubusercontent.com/osminoog09-star/Shorts/62a8b36137515ca6587b078dc449c4146154e26f/videos/m1lash_ai_news_20261103_ru.mp4)

Файл: videos/m1lash_ai_news_20261103_ru.mp4, **9 613 071 байт**.
SHA256: `7fdb95b889966ff614f768b335c03252e0c664dd0123f11c2ee3cc99fa61148a`.
Не загружен в YouTube, дата не назначена. Полное человеческое прослушивание и непрерывный просмотр не заявляются.

## Реальные проверки

- 1080×1920, 30 fps CFR, H264/BT.709, AAC stereo 48 kHz.
- check.py конечного файла: **0 FAIL / 1 WARN** — нет отдельной дорожки субтитров, они вшиты.
- Полный ffmpeg decode повторён после восстановления из артефакта; ошибок нет.
- Весь файл: −15.3 LUFS, −1.9 dBTP. Тело: −15.1 LUFS; утверждённая концовка: −15.9 LUFS.
- История 33.833 с + approved rev4 6.600 с. Штатный assembler: problems=[], сдвиг концовки **0.3 мс**, difference −31.9 dB.
- 27 групп титров, минимальная длительность **0.817 с**. Реальный браузер проверил все 27 прямоугольников: **0 пересечений с источниками**, шрифт не ниже 64 px.
- Конечный look.py и все шесть кадров с реальной озвучкой открыты глазами **по immutable commit62a8b36137515ca6587b078dc449c4146154e26f**. Последняя цифра и подпись не перекрыты.
- Полный ASR сохранён. Small-модель потеряла отрицание в одной фразе; отдельная непредвзятая medium-проба без initial_prompt распознала «а не обещают идеального помощника». Оба результата сохранены, не скрыты.
- Отдельная проба конца распознала весь CTA до «поставил лайк». ASR не заменяет человеческий слух.

## Производство и источники

Обновлён прежний S1-D25 черновик, сохранив бумажный стиль. События от02.11: LifeVal, Grid Protectors, S-1/A Anthropic. Фактчек/даты/два источника на факт — shorts/ai_news_20261103/sources.json. Старые события26–28.10 не выданы за свежие. В случае Grid новое событие — анонс программы02.11, базовое соглашение Georgia Power от22.07 обозначено отдельно.

Графика — честная 2.5D HTML/SVG/CSS с paused GSAP clock по HyperFrames-подходу; checkmark адаптирован из registry marker-checklist-card. Не заявляется прохождение npx hyperframes check. PIL использован только для контактов.
Шесть реальных голосовых файлов: Дима ru-RU-DmitryNeural / Edge, без Piper/Azure fallback. Кэш media/tts/news_20261103. Собственные тихие процедурные plucks; музыка Laeko уже в штатном финале, credit в PUBLISH.md.

## Выполненные этапы

- Stills41563843584: 6 исправленных кадров открыты.
- Pilot41564587503: целая реплика n03, реальные тайминги/ASR/look.
- Full41566378199: промежуточный40.433с master; обнаружены18 слишком коротких титров.
- Caption repair41567900438: только область850×254, прежняя графика сохранена; файл собрался и прошёл QA, но git pull отказался из-за неучтённого изменённого MP4.
- Recovery41568667754 SUCCESS: восстановлен **тот же** MP4 из artifact13199498632, ZIP CRC проверен. Рендер/синтез не повторялись. Исправлен save_remote_evidence: при явно разрешённом save_review_mp4 master коммитится вместе с QA.
- Audio probe41569292785 SUCCESS: отдельные caveat/CTA, без заданной модели правильной фразы.

Артефакты:
- reports/research/2026-11-03_NEWS_FULL_{QA.json,check.json,assembly.json,layout_gate.json,caption_repair.json,artifact_recovery.json,final_asr.json}
- reports/research/2026-11-03_NEWS_TARGETED_AUDIO_PROBE.json
- reports/research/qa/news_20261103_full_final_look.jpg
- reports/research/qa/news_20261103_full_stills_contact.jpg

Платные генерации не запускались. Статус — review master/draft до слухового QA и решения владельца; не RELEASE_READY.
