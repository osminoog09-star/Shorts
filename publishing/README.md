# Прямая публикация YouTube — без Metricool

Статус: **внедряется, по умолчанию ничего не публикует**. Существующие ролики и расписание Metricool не изменяются. Автопилот создания RU/EN в `motion-studio` пока отдельно выключен.

## Как работает

Ролик уже готов и проверен человеком. Сначала создаётся манифест `publishing/queue/<slug>.json` (по примеру в `publishing/examples/`). Укажите существующий MP4 в `videos/` или **точные** GitHub Release tag + asset. Время `publish_at` — ISO-8601 **с числовым смещением Tallinn**, например `2026-11-04T19:00:00+02:00`. Скрипт проверяет летнее/зимнее время.

GitHub → Actions → **YouTube direct · review then schedule** → Run workflow:
1. `manifest` — относительный путь `publishing/queue/slug.json`.
2. `execute=false` (по умолчанию): только проверка без загрузки и без OAuth.
3. После проверки и сверки с календарём Metricool повторить с `execute=true`. Загрузка в YouTube произойдёт как **private** с `publishAt`; YouTube опубликует самостоятельно в выбранную дату. Скрипт проверит аккаунт YouTube и запретит публикацию не на тот канал.
4. Перед загрузкой GitHub коммитит запись `publishing/receipts/slug.json` со статусом `reserved`. При успехе статус `uploaded` и ссылка YouTube. При ошибке/неясном результате повторная загрузка **блокируется**, чтобы не создать дубль: проверить YouTube Studio и разбираться вручную.
5. Загруженные записи GitHub Actions (artifacts) хранятся 30 дней.

### Подключение OAuth один раз (секреты не показывать в чате и не коммитить)

1. В [Google Cloud Console](https://console.cloud.google.com/apis/library/youtube.googleapis.com) включить YouTube Data API v3 для своего проекта. В OAuth consent screen настроить приложение. Для надёжного refresh token желательно production, если применимо; в режиме Testing у external-приложений refresh token может истечь через семь дней.
2. Создать OAuth client типа **Desktop app** и скачать JSON **локально**, НЕ в открытый репозиторий.
3. На собственном ПК: `python -m pip install google-auth-oauthlib requests`, затем `python motion-studio/automation/oauth_setup.py --client /path/to/desktop-client.json --lang ru`. Войти в RU канал M1lash; программа покажет ID канала и refresh token. Повторить с `--lang en` только после создания и подключения второго канала.
4. В [GitHub → Settings → Secrets and variables → Actions](https://github.com/osminoog09-star/Shorts/settings/secrets/actions) добавить **repository secrets**:
   - `YOUTUBE_OAUTH_CLIENT_ID` и `YOUTUBE_OAUTH_CLIENT_SECRET` (можно использовать существующие `YT_CLIENT_ID` / `YT_CLIENT_SECRET` вместо них);
   - `YOUTUBE_REFRESH_TOKEN_RU` (для RU поддерживается прежний `YT_REFRESH_TOKEN`, если у него необходимые OAuth scopes);
   - `YOUTUBE_REFRESH_TOKEN_EN` отдельно, когда появится EN-канал.
5. ID русского канала уже внесён из подключённого Metricool. Для английского канала в `publishing/channels.json` заменить пустую строку `en` на его **проверенный** `UC...` ID. Секреты **никогда не хранить** в этом JSON.

### Проверки безопасности

- Выпуск начинается **только** с одобренного и готового MP4 и манифеста; публикация с рендера и генерация по трендам автоматически пока не связаны.
- Проверка даты и временной зоны, совпадения OAuth-канала, запрет повторов по receipt; по локальной очереди максимум **2 Shorts в день**, интервал **не меньше 6 часов**; посторонний Instagram не используется.
- Во время перехода скрипт **не видит очередь Metricool**: обязательно сверять текущие публикации и не планировать дубли. Также **не видит** вручную загруженные в YouTube Studio ролики — сверять перед execute.
- `contains_synthetic_media` отмечать по правилам YouTube; `made_for_kids` заполнять осознанно; проверять права на видео/аудио.
- Ничего не начинает публиковаться при добавлении этого кода. Для первой проверки рекомендуется отдельный небольшой оригинальный тестовый MP4, запланированный на свободный слот.
- Upload использует YouTube API resumable session. Квоты, доступные права, верификация/аудит Google OAuth и поведение публичного расписания зависят от проекта YouTube; настоящий тест возможен только после настройки OAuth.

## Локальная проверка

```bash
python3 -m pip install requests
python3 scripts/youtube_direct.py check --manifest publishing/queue/my-video.json
python3 -m unittest discover -s tests -p 'test_youtube_direct.py'
```

**ВНИМАНИЕ**: не менять `motion-studio/automation/config.json:enabled` на true ради этой публикации. Автопилот — отдельный эксперимент и с действующим календарём конфликтует.
