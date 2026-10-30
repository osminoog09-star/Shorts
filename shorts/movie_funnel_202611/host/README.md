# Концовки HostCorner, отдельно от киноисходников

Это прозрачные overlays, **не готовые Shorts**. В них нет кинодиалога и изображения фильма. Имена композиций: `FunnelEndingA` / `FunnelEndingB`, 1080×1920, 30 fps. Анимация ведущего скопирована из утверждённого `studio/src/HostCorner.tsx`; исходный общий компонент и его props не менялись. Здесь используются свои виземы.

TTS успешно сохранён в `media/tts/movie_funnel_202611/` (run 41116949032). Перед запуском скопировать два MP3 и JSON из этого каталога в соседний `audio/`; файлы JSON уже закреплены с word boundaries. Для A — `host_data.json`, для B — `host_data_b.json`. Последние слова названия не попадают в типографику.

Локально использован Remotion 4.0.539. Зависимости устанавливаются в `studio/`; для этого каталога можно создать локальную ссылку `node_modules` на `../../studio/node_modules` (в git она не входит). Для PNG/ProRes:

```sh
../../studio/node_modules/.bin/remotion still host/index.tsx FunnelEndingA host/qa.png --frame=140
../../studio/node_modules/.bin/remotion render host/index.tsx FunnelEndingA host/ending_a_alpha.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le
../../studio/node_modules/.bin/remotion render host/index.tsx FunnelEndingB host/ending_b_alpha.mov --codec=prores --prores-profile=4444 --pixel-format=yuva444p10le
```

Если контейнерная Node не поддерживает `os.networkInterfaces()`, локальный совместимый runner использует стандартный loopback вместо перечисления интерфейсов; это не настройка внешней сети или браузерного профиля. В среде с нормальной Node preload не нужен. При указанной ошибке можно запускать CLI через `node --require ./host/render_loopback.cjs ../../studio/node_modules/@remotion/cli/remotion-cli.js ...`.

Крупные промежуточные MOV не входят в git: их воспроизводят из кода. При использовании сохранённых VP9-alpha WebM декодировать через `-c:v libvpx-vp9` **перед** `-i`, чтобы ffmpeg сохранил alpha. Музыку и полный микс добавлять только на этапе киноэкспорта. Визуальный контроль PNG и decode не заменяют прослушивания или проверки всего фильма.
