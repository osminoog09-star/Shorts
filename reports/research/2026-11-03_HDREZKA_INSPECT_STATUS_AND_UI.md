# 03.11.2026 — HDRezka quality inspect: реальный статус и UI M1lash Studio

## Что было на экране
- Владелец на Android нажал «Проверить качество» для страницы фильма (1080p). Браузер показал только toast «Проверка запущена», а поле «Последнее действие» продолжало показывать «Проверка ещё не запускалась».
- Причина: GitHub workflow_dispatch возвращает 204 без результата; CI делает tests+Go build до самого inspect. Результат попадает в `publishing/hdrezka_status.json` только в конце; frontend не показывал промежуточное состояние.

## Проверено по реальным GitHub Actions
- Owner `inspect` 41548828784: tests SUCCESS, intake FAIL `source_unavailable`. Фактический статус `publishing/hdrezka_status.json`: `checked_at=2026-11-02T23:56:09Z`, `requested_quality=1080p`, `drive_uploaded=false`, сообщение «Плеер не открылся из GitHub Actions (возможно, блокировка запросов)».
- Повторный `inspect` 41548866880: tests SUCCESS, intake FAIL `source_unavailable`; шаг записи статуса тоже FAIL: `git pull --rebase` получил CONFLICT на `publishing/hdrezka_status.json` (из-за конкурентного обновления main), повторные git pull при unresolved conflicts не помогли. Вспомогательный pending run 41548841637 отменился при очередном workflow_dispatch.
- Это не проблема OAuth: `publishing/drive_auth_status.json connected=true`, ранее подтверждён реальный rclone lsf. **Фильм не загружен, качество 1080p не подтверждено.**

## Исправления (только инфраструктура, без видео)
- `site/studio/clips_ui.js`: после 204 dispatch сразу видимый статус «запрос отправлен», при рендере показывается живой active run вместо устаревшего not_started; ссылка на конкретную проверку.
- `site/studio/auto_refresh.js`: выбирается реально выполняемый run среди нескольких, учитывается время нового запуска и время результата; GitHub статус отображается до обновления JSON.
- `scripts/qa/test_studio_auto_refresh.cjs`: проверка active run и href точного запуска.
- `.github/workflows/hdrezka-intake.yml`: статус текущего задания сохраняется во временные файлы, каждый retry получает свежий origin/main, переносит только свои status-файлы и создаёт новый коммит, вместо `git pull --rebase` конфликтующего коммита.
- GitHub Pages 41549464524 SUCCESS, включая новый UI и QA; infrastructure CI 41549566628 SUCCESS (offline tests, safe OAuth/rclone diagnostic, pinned Go CLI compile). Это **не успех inspect/downloading**.

## Следующий технический гейт
Только когда доступен исходник, разрешённый на скачивание без DRM/CAPTCHA, повторно проверить `mode=inspect` и результат в `publishing/hdrezka_status.json`; при `source_unavailable` не обещать пользователю доступное качество или загрузку в Drive. Для полного end-to-end дополнительно нужен файл MP4 в папке Drive и подтверждение метаданных. Не загружать Shorts/ZIP в папку фильмов.
