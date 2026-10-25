# Movie-edit шортсы (сцена из фильма/сериала + кинетический текст)

Эксперимент 25.10: «Скажи моё имя» (Во все тяжкие, 5×7).

1. Расшифровка речи: faster-whisper small (модель из npm `@skillninja/shortmovie-telop-model-p0..p3`, склеить model.bin), word_timestamps.
2. `edit.py` — куски исходника, шоты с центром лица, фразы со стилями и таймингом слов, удары/вспышки.
3. `base.py base.mp4` — вертикальный кадр 9:16, наезды, punch zoom, тряска, цветокор (cas+unsharp+eq).
4. `final.py base.mp4 v.mp4` — кинетический текст (`kinetic.py`: caps / ital / neon / bubble / wide / heis) и вспышки.
5. `audio.py audio.m4a` — диалог по монтажу + своя процедурная музыка (гул, сердцебиение, удары) + финал ведущего.
6. Финал: Remotion `edit-outro` (`studio/src/EditOutro.tsx`, данные `studio/src/edit_outro.json`) — ведущий за столом
   называет сериал, сезон и серию, лайк/подписка/спасибо. Рендер с прозрачностью (`--image-format=png`), наложить на
   размытый последний кадр, склеить.
