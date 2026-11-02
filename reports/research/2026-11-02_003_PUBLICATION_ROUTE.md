# Штатная публикация №003: сверка инструкций Клода

Проверены AGENTS§6, CLAUDE.md (перенаправляет к AGENTS), publishing/README.md, publishing/studio/README.md, youtube-direct.yml, youtube_direct.py, build_studio_site.py и site/studio/index.html из Git.

- AGENTS актуальнее старого publishing/README: приватная заливка БЕЗ publish_at, расписание отдельно.
- MP4 32.7МБ по AGENTS должен быть в videos/. Манифест принимает repo MP4 или release asset; произвольный URL/artifact он не принимает.
- youtube-direct.yml: validate → resolve source → OAuth/channel preflight → persist reservation → upload → receipt. Никакой новой настройки OAuth не нужно.
- Сайт показывает review по receipts со status=uploaded без publish_at_utc. Кнопка «Заливаем» меняет publish_at и запускает mode=schedule; загрузки локального MP4 на сайте нет.
- fetch.yml умеет скачать файл по URL в репозиторий; использовать его для обхода отклонённой передачи нельзя.
- Владелец подтвердил звук V54: «Все ок». Это owner QA, не прослушивание агентом.
- Автопроверка отклонила upload MP4 в GitHub Release: разрешение на передачу файла публичному репозиторию сочла недостаточным. Файл НЕ передан. Создан только пустой Draft untagged-be816b2467ff47dc2e37; не опубликован.
- Нельзя назвать ролик залитым, пока нет подтверждённого YouTube ID/receipt. Ни upload, ни schedule ещё не запускались.
