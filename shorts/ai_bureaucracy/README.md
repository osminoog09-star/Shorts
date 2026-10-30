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
