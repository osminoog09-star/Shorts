# Другие исходные женские голоса — четыре новые частные пары

Владелец отверг все3DSPвариантаSerena; исходнаяSerena «ещё куда бы ни шло» остаётся ориентиром, но не утверждённой постоянной соведущей. Авторизован новый поиск других исходных тембров сразрешённымиспользованием. Перед текущей работой прочитаны NOW/AGENTS/Studio. Создан и затем завершён отдельный checkpointNOW.

Сделаны физические4новыхMP3 на одном тексте вопроса и одном мужскомWAVответе из прежнего кастинга:1KokoroSveta,2KokoroMasha,3QwenVoiceDesignWarm,4QwenVoiceDesignClear. Никакогоpitchshift/эквалайзеракSerena. Не подменять этиголоса прежнейMicrosoftСветланой илиперенастроеннойSerena.

Источники/разрешения:
- zaakirio/kokoro-ru, snapshotd649c57b239b18c4c384378127cbf01dba039bc1. ГотовыеfemalevoicepacksSveta/Masha; автор описываетconsentedstudioactorsизDialogs/OpenRAIL. Дополнительно физически прочитана LICENSE.mdофициальногоdatasetslangswap/dialogs-ru-emotional-conversations: в§1разрешено коммерческоеиспользование производных/outputs, вконцевойсноскеавторуказываетписьменноеинформированноесогласие актёров. Есть use restrictions иобязанностьпередаватьлицензию. ПолныйтекствключёнвчастныйZIP иID3commentобоихKokoroMP3. Собственной независимойпроверкидоговоровсдикторами не было; не выдаватьоткрытоелицензионноезаявление за юридическуюгарантию.
- Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign, snapshot5ecdb67327fd37bb2e042aab12ff7391903235d3,официальныйlicenseApache2.0. Дваголосасгенерированы зановопотекстовымописаниям, languageRussian. «Тёплаянизкая» и«яснаяразговорная» —requestedattributes, несубъективно подтверждённыекачества. Не клонировалисьслучайныеженскиезаписиизинтернета. ApacheLICENSEофициальногоQwenрепозиториясохранёнвпроекте; отдельногоHF/LICENSEзагрузитьнеудалось, licensemetadataApacheподтверждена первичнойкарточкой.

Синтез:
- Kokoro: официальныйfp32ONNX326MB,stylepacks;G2Pофициальныйru_g2p._from_marked, customacute-awareespeak-data. Во всёмвопросе вручнуюпровереныударения, поэтомуиспользован explicitstressпутьбезRUAccentзагрузки. espeakтолькофонемизирует, аудиовывод — нейросетьKokoro, не eSpeakTTS.
- Qwen:CPU/BF16/4threads,двеуникальныеинструкции,seed151/213,temperature.7. Модельныевеса вscratchcache, неттратыAPI;ORT/HFтелеметрии выключеныдоимпорта. Собственныйголос/образецДенисавнешнимсервисамнеотправлялся.

Проверки четырёхфактическихженскихреплик independentWhisperSmall:4/4textsimilarity1.0,всеRussian. Речьнеускорялась/высотанеизменялась послеTTS;trimтолькокрайнейтишины, уровеньприведён кизмеренномуDenis−17.16LUFS. Музыкинет,серединастереообщая,пауза0.32с.
Пары:1−17.52LUFS/−5.22dBTP;2−17.57/−5.23;3−17.14/−5.11;4−17.30/−5.27. Разница≤0.43LU;4/4полныхffmpeg-xerrordecodeбезошибок. ПроверенныймужскойPCMвкаждомWAVmaxdiff0.0(вlossyMP3идентичностьPCMнеобещать). ASR/LUFSнеоцениваютприятность,акцент,естественностьилисочетаниеголосов;личноепрослушиваниеитембровыйвыборвладельцаpending.

ЧастныеMP3иZIPсохранены,IDsвtasks/cohost_voice_casting.md. ВпубличномGitтолькокод/отчёты/метаданные,никакихMP3/WAV/embeddings/modelweights. tools/voice_casting/round3/*.py PRIVATE_WORKDIR;projectZIPсодержиттотжекод,raw/trim/normalized/pairedаудио,манифесты/QA/лицензии,нонемодельныевеса. Подготовкапростая,потребуетзависимостиonnxruntime/phonemizer/misaki/espeakng-loader/numpy/soundfileиQwenTTSдляVoiceDesign,ffmpeg/WhispersmallдляQA.

Постоянныйженскийголос/форматещёнеутверждён. Послеего выборадляVoiceDesignзакрепитьчастныйсинтетическийreferenceиvoiceID;непроектироватьзаново каждуюреплику — иначеуйдётпостоянствотембра. Shorts/outro/основнойавторостаютсяголосомДениса. НетYouTubeupload/date.

Первичныеисточники:
https://huggingface.co/zaakirio/kokoro-ru
https://huggingface.co/datasets/langswap/dialogs-ru-emotional-conversations/blob/main/LICENSE.md
https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign
https://github.com/QwenLM/Qwen3-TTS
