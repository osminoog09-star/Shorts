# Источники кино для M1lash — 31.10.2026

Собрал GPT по запросу владельца «Ищи тогда нужные»; репо `main`.
Действующие правила — AGENTS.md §8–9 и skills/m1lash-studio/SKILL.md §3.

**Статус:** проверены веб-страницы и точные сцены; локальные оригинальные MP4/MOV не получены. Лицензии на повторную публикацию M1lash не проверены. Не сообщать, что видео смонтировано, пока нет исходника, аудио и QA. YouTube с GitHub Actions упирается в bot-check — не обходить. Не использовать пиратские сайты.

## Приоритет A — Чигур: 2 Shorts (03.11, 05.11) + разбор 07.11

Фильм: No Country for Old Men (2007). Стиль S6-D25 утверждён.
1. Заправка / монетка: официальный видеофрагмент Miramax https://www.youtube.com/watch?v=opbi7d42s8E ; альтернативный лицензионно размещённый Binge Society https://www.youtube.com/watch?v=UHD-1Lts4_o ; текстовый ориентир и просмотр сцены https://clip.cafe/no-country-old-men-2007/sir-the-most-ever-lost-on-a-coin-toss/ (таймкод в полном фильме 00:23:46, 98 с).
2. Карсон Уэлс / Чигур в отеле: https://www.youtube.com/watch?v=nJxgv1IW02o (W&H, не правообладатель); отдельный контекст Уэлса с Моссом https://www.youtube.com/watch?v=jvtdUmUX-Ug. Наличие русской дорожки не подтверждено.
3. Карла Джин / отказ выбрать монету: https://clip.cafe/no-country-old-men-2007/you-dont-have-do-this-s7/ (01:50:01 в полном фильме, 63 с).
4. Отель, тишина, оружие: официальная подборка Miramax https://www.miramax.com/movie/no-country-for-old-men/ (Regal Motor Hotel / Cat and Mouse); индекс 4K моментов с точными секундами https://www.thepartwhere.com/t/no-country-for-old-men
5. Русский трейлер (именно **трейлер**, не полный фильм): https://kg-portal.ru/movies/nocountryforoldmen/trailers/3963/ — страница предлагает 1080p MOV 160,6 МБ и 720p MOV 110,3 МБ, серверную доступность по прямой ссылке подтвердить не удалось. Обнаруженный из редиректа предполагаемый URL 720p: https://media.kg-portal.ru/trailers/nocountryforoldmen/nocountryforoldmen_russiantrailer_1280.mov (не проверен GET).

## Приоритет B — новые кино-Shorts (2026-10-31-gpt-1/2/3)

- **Whiplash / Одержимость (2014):** первая репетиция, «Not quite my tempo» и бросок стула. Сцена видео https://www.youtube.com/watch?v=GBvBu5ErSSo ; индекс https://clip.cafe/whiplash-2014/not-quite-my-tempo/ (00:26:03 полного фильма, 46 с; следующие отдельные клипы: бросок стула); русский трейлер с вариантами загрузки 1080p/720p https://kg-portal.ru/movies/whiplash/trailers/18913/ . **Основной 46-секундный эпизод доступен для просмотра, но прямой MP4 не получен.**
- **Ex Machina / Из машины (2014):** точная сцена первого отключения и фразы Авы «не доверяй Натану»: лицензированный канал Movieclips https://www.youtube.com/watch?v=jGAsihLnYqM ; версия с разметкой: https://clip.cafe/ex-machina-2014/youre-wrong-s9/ (00:31:03, 31 с). Для развития интриги можно использовать вторую сцену https://clip.cafe/ex-machina-2014/why-did-you-tell-me-i-shouldnt-trust-nathan/ . Требуется русский звук или подходящее решение с субтитрами по правилам.
- **Nightcrawler / Стрингер (2014):** первый репортаж Лу: полицейский требует убрать камеру https://clip.cafe/nightcrawler-2014/hey-who-the-hell-are-you-freelance-what-are-you-doing-filming-for-tv-no-back-away-whats-happ/ (00:13:39, 35 с). Другой эпизод на ДТП https://clip.cafe/nightcrawler-2014/tv-news-s3/ (00:40:20, 21 с); **не путать** с первым выездом.
- **Заявка @ErnestoMarsel:** Breaking Bad S4E11 Crawl Space, финал со смехом Уолтера. Правообладатель https://www.sonypictures.com/tv/breakingbad ; дата/сценарный ориентир S4E11; конкретный чистый официальный MP4-сцены пока не найден. Заявка требует оригинальной английской дорожки и русских субтитров. Не брать кусок из видеоэссе конкурентов как исходник.

## Следующий технический шаг

У проекта есть `.github/workflows/movie-edit-source.yml` и `.github/workflows/fetch.yml`, но серверный YouTube не работает, а MOV-трейлер с указанного CDN в текущей среде не удалось скачать/проверить. Никаких прав не приобреталось и никакие видео не заливались. Если появится пригодная прямая видео-ссылка с подтверждённым разрешением использования — скачивать как временный артефакт (не коммитить фильм в git) через безопасный конвейер и проверить ffprobe, звук, декодирование и права.
