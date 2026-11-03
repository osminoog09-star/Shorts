# 03.11.2026 — серверный прямой MP4 → Google Drive (резервный конвейер)

## Проблема источника
Требование: без телефона, без повторного Google OAuth, сохранить полноценный фильм для M1lash.
HDRezka на GitHub Actions выдаёт антибот-челлендж даже в обычном Chromium: [41558540041](https://github.com/osminoog09-star/Shorts/actions/runs/41558540041), `challenge_present=true`, `film_heading_present=false`, `download_control_present=false`. Встроенный CLI Anubis solver тоже не дал 720p/1080p (exit 3). Прямая ссылка на правообладательский MP4 «Оппенгеймера» не получена. Не обещать эту загрузку, не обходить CAPTCHA/DRM.

## Что реализовано
- `scripts/direct_movie_intake.py` и `.github/workflows/direct-movie-intake.yml`: самостоятельный серверный путь для прямых **доступных и разрешённых к использованию** публичных HTTPS MP4 с ограниченного набора хостов (Archive.org, download.blender.org, GitHub Releases). Не страницы плееров, не HLS/DRM. Проверка источника через Range первые 4096 байт, ftyp MP4, строгие URL/DNS/redirect validators. Не логировать raw URL, cookie, headers, media или секреты.
- В режиме `download`: потоково скачать оригинал во временную папку GitHub runner, лимит 6,5 ГБ; `ffprobe` проверяет MP4, длительность >=20 минут, требуемую высоту 1080p/720p и наличие хотя бы одной аудиодорожки. **Русский дубляж не подтверждается этим шагом**, `russian_dub_verified=false`; нужен последующий ASR и QA. Загрузка rclone `copyto` в приватную папку кинофайлов, затем повторно сверить размер объекта в Drive, удалить локальный temp; не писать видео в репо/не публиковать на YouTube.
- `site/studio/clips_ui.js`, `auto_refresh.js`, `build_studio_site.py`, Pages trigger: отдельный блок «Прямой MP4 → Google Drive (сервер)», кнопки inspect и upload по GitHub Actions и показ реального JSON-статуса. Отдельный `publishing/direct_movie_status.json`. Старую HDRezka кнопку не выдавать за успешную загрузку.

## Реальные проверки
1. [GitHub Actions 41560256794](https://github.com/osminoog09-star/Shorts/actions/runs/41560256794) — **SUCCESS**, 6/6 offline tests (whitelist/SSRF-style inputs/HTML reject/audio file/Drive metadata), а также **реальный HTTP** тест официально документированного public MP4 `https://archive.org/download/ArcherProductionsInc/DuckandC1951.mp4`: `direct_public_mp4_probe: reachable, valid MP4 file signature; max 4096 bytes read, NO upload`. Это проверка подключения и формата, **не** полный фильм 20+ минут.
2. [GitHub Pages 41559990034](https://github.com/osminoog09-star/Shorts/actions/runs/41559990034) — **SUCCESS**, deployed UI + node auto-refresh tests.
3. [GitHub Actions 41560398775](https://github.com/osminoog09-star/Shorts/actions/runs/41560398775) — **SUCCESS**, `drive_write_probe: create/read/exact-size/delete OK; movie folder unchanged`. Тестовый файл временно создавался **в корне Drive**, а не в папке фильмов, и удалён.
4. Отдельно прежняя [41552769772](https://github.com/osminoog09-star/Shorts/actions/runs/41552769772) — приватное чтение 1024 байт настоящего файла Drive OK; `drive-folder-intake.yml` читает 2 файла, но нужных новых фильмов 0.

## Чего **пока не доказано**
- Прямая загрузка фильма «Оппенгеймер» с HDRezka: BLOCKED (челлендж); доступного разрешённого MP4 не выявлено.
- End-to-end `download` **полного** фильма с прямой ссылки, сверка 20+ мин/1080p/аудио и rclone upload: не запущено, потому что такого исходника нет в распоряжении. Серверный тест 4КиБ и создание маленького файла в Drive не заменяют его.
- Права на использование любого пользовательского MP4 должны быть проверены до публикации. Владелец не одобрял публикацию, она не выполнялась.
- Права папки Drive всё ещё могут быть `anyone=writer` (по прежней проверке); OAuth доступен и без этой публичной настройки. Это отдельное решение владельца.

## Дальше
Не повторять HDRezka снова ради красивого CI; для указанного фильма нужна штатно доступная прямая незащищённая копия с соответствующим правом использования. Для неё путь сайт → GitHub Actions → MP4 QA → Drive уже подготовлен, но не считается end-to-end verified до результата настоящего MP4.

