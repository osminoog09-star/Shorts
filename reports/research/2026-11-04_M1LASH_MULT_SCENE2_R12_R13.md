# M1lash Мульт EP01 · сцена 2 · реальный QA 04.11.2026

**Six stills r12:** run 41797715066 SUCCESS, artifact 13305988936. Физически скачаны/открыты шесть JPG t7.5–12.4, контакт /mnt/data/M1lash_mult_r12_scene2_6frames.jpg. Реальное последовательное появление 09:00 ПЛАНЁРКА → 09:05 ПОДГОТОВКА → 09:10 ИТОГИ, текст виден в кадре, не пиктограммы.

**Actual scene2 MP4 r12:** Actions 41798234674 SUCCESS, artifact 13306850877, H264 1080×1920/30fps, 180 кадров, **6.000с/1,546,554 B**, SHA256 `5cad63f60395b4811b7adaaf6d5102cc157722cc9d437e53b4753ce4345e9465`. Фактически скачан, ffmpeg -xerror full decode PASS. 12 JPEG через 0.5с получены именно из MP4; открытый контакт `/mnt/data/M1lash_mult_r12_scene2_12realMP4frames.jpg`. **ART NO-GO:** после появления третьей карточки t10.5–12.5 герой слишком статичен.

**r13 narrow fix:** commit 05834fc — руки опускаются, голова/корпус устало наклоняются после третьей карточки. Run 41798828543 SUCCESS, artifact 13306054126; реально открыты 6 scene2 frames t7.5–12.4, на t12.4 заметна реакция. **Это stills, не подтверждённый motion ART PASS.** Настоящий r13 6с пилот запущен job `jobs/motion/m1lash_mult_ep01_pilot_r13_scene2.json` commit 5472f9d; проверять 12 MP4 кадров и full decode.

**Scene 3:** коммит b413c64 добавил движение монеты к АКСу и 3D receipt `100 €`→`ОПЫТ +100`; шесть screenshots salary_13_4..18_2 добавлены commit fe5a882. Job r14 scene3 commit 5426055 запущен; **пиксели ещё не оценены**.

Никакого финального 39с MP4, голоса Дениса, второго женского TTS, approved outro или YouTube upload. Следующий шаг: ART motion сцен 2 и 3 → сцены 4–6 → приватная озвучка/ASR → official check.py/look.py/full decode/слух → согласование владельца. Ошибки не скрывать за зелёным CI.
