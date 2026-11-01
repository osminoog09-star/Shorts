# GPT · 01.11 · «Чигур» V7 — визуальный preflight

GitHub Actions [#41314121375](https://github.com/osminoog09-star/Shorts/actions/runs/41314121375) SUCCESS, artifact 13086790544. Реально получены 6 стопов 960×540 из Three.js/Playwright (без PIL) и просмотрены глазами. Исходник `longform/chigur/graphics/three_stage_v7.js`, скрипт `shorts/chigur_v7_stills.py`.

**NO-GO: не встраивать в длинный.** Монета стоит неестественно, коридор слишком плоский, осциллограмма примитивна, сцена отказа повторяет монету, кейс low-poly, автомобиль — прямоугольник. Свет и глубина пока ниже эталона `tools/outro/`. Настоящий motion pilot до исправления 4–6 кадров не рендерить.

Локальная среда Chromium не даёт WebGL; рендер получен через стандартный workflow. Кадры: `/mnt/data/chigur_v7_stills/chigur_v7_scene_01..06.png`, контакт `contact.jpg`, полный ZIP `/mnt/data/chigur_v7_six_stopframes_QA.zip`.

Следующий шаг: V8 — исправить перспективу, физику монеты, форму автомобиля, глубину теней, микрореквизит; получить 6 новых PNG, сравнить с rev4; только затем 5–10с motion pilot. В REV19 все 28 старых окон ещё нетронуты.
