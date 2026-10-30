# «Я нанял ИИ, чтобы меньше работать» — тестовый Shorts (Claude, 30.10.2026)

Художественный скетч, не новость. **Не опубликован и не поставлен в очередь.**

- Готовый ролик: `videos/ai_bureaucracy_claude_ru.mp4` (1080×1920, 30 fps, ~57 с, H.264 + AAC).
- Тритмент, планы, кривая энергии: [treatment.md](treatment.md).
- Композиция huashu-motion (HTML + GSAP + Three.js): `film/index.html`, сцены — `film/assets/js/world.js`, персонажи — `film/assets/js/kit.js`.
- Ведущий: утверждённый `HostCard`/`Narrator2` из `shorts/laeko_host_demo` без изменений, собран в `film/assets/js/host.js` (`film/tools/host`).
- Голос: workflow `TTS`, задание `jobs/tts/ai_bureaucracy_claude.json` → `media/tts/ai_bureaucracy_claude/` (копия в `tts/`). Паспорт голосов каждого сегмента: `tts/manifest.json` (speaker, voice_id, engine, rate, source_file).
- Музыка и шумы: собственная процедурная партитура `om sound` (pizzicato), без сторонних треков. Laeko не используется — лицензия NCS для ИИ-видео не подтверждена.

## Повторная сборка

```sh
cd shorts/ai_bureaucracy/film
python3 tools/assemble_voice.py                                   # речь: сжатие пауз, раскладка, титры
RHUBARB_DIR=/tmp/rhubarb bash ../../../tools/lipsync.sh assets/voice/dima.wav assets/voice/dima_visemes.json
python3 tools/make_lipsync.py                                     # виземы ведущего + огибающая для ботов
(cd tools/host && npm install && npx esbuild host_entry.tsx --bundle --minify --format=iife \
   --define:process.env.NODE_ENV='"production"' --outfile=../../assets/js/host.js)
cd ../../.. && ./scripts/huashu-motion sound shorts/ai_bureaucracy/film && cd shorts/ai_bureaucracy/film   # музыка + эффекты
# картинка: либо целиком `om render` (на 2 ядрах без GPU не укладывается в 2 ч), либо возобновляемо кусками:
for a in $(seq 0 250 1709); do node tools/render_frames.mjs $a $((a+250>1709?1709:a+250)) out/frames; done
ffmpeg -framerate 30 -i out/frames/f%05d.jpg -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p \
  -vf scale=out_color_matrix=bt709:out_range=tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 out/picture.mp4
python3 tools/mix_final.py out/picture.mp4 ../../../videos/ai_bureaucracy_claude_ru.mp4
```

Нужны Node ≥ 22, ffmpeg, Chrome/Chromium (`OM_CHROME=...` если не в стандартном пути).

## Проверка экспорта (30.10.2026)

- `ffprobe`: 1080×1920, 30 fps, 1709 кадров, видео 56.97 с, аудио 56.97 с (AAC 48 кГц), полный decode без ошибок.
- Громкость: −14.0 LUFS integrated, пик −1.5 dBFS. Музыка/эффекты под речью на 10–17 дБ ниже голоса, в паузах поднимаются; после CTA — музыкальный хвост ~1.3 с, реплика не обрывается.
- `om check`: 0 ошибок (1 предупреждение «no-real-material» — неприменимо к вымышленному скетчу). `om qa`: нет однокадровых «вспышек», средний план 2.4 с; «склейки» 24.70–24.77 и 29.77–29.80 — это пружинное появление агента и быстрый кран камеры, не мерцание.
- Кадры просмотрены покадровыми листами по всем сценам; исправлены: камера внутри головы на плане телефона, пересвет переговорки, обрезанная доска, титры под увеличенным ведущим, обрезанный заголовок концовки, обрыв аудио на 54.1 с (несовпадение частот 192/48 кГц в сведении).
- Не проверено: прослушивание человеком в реальном времени (у агента нет звука) и просмотр на телефоне.
