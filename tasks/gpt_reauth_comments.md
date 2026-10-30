# Задача GPT (31.10.2026): дать ключу YouTube право читать комментарии

Почему: `youtube-pulse.yml` получает от commentThreads.list `HTTP 403 insufficientPermissions` — в refresh-токене нет нужного scope. Без него на сайте пустая вкладка «Зрители» (заявки, обращения, топ-комменты).

1. Google Cloud → проект «Youtube» → OAuth consent screen → Data access → Add scopes: `https://www.googleapis.com/auth/youtube.force-ssl` (оставить уже добавленные).
2. OAuth Playground (⚙️ → Use your own OAuth credentials → client ID/secret приложения M1lash Studio). Отметить ВСЕ scope сразу:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube.force-ssl`
   - `https://www.googleapis.com/auth/youtube.readonly`
   - `https://www.googleapis.com/auth/yt-analytics.readonly`
   Authorize → войти аккаунтом канала M1lash → Exchange authorization code for tokens.
3. Новый refresh token → секрет `YOUTUBE_REFRESH_TOKEN_RU` в osminoog09-star/Shorts (заменить). Токен никуда больше не писать.
4. Проверка: Actions → «YouTube auth check» (должен быть SUCCESS), затем «YouTube · hourly pulse» → Run. В ветке `pulse-data` в `pulse.json` поле `status.comments` должно стать `"ok"`.
5. Запись в HANDOFF.md.
