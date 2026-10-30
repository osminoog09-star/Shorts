# Задача GPT/Codex (30.10.2026): Shorts по заявке подписчика + ключ подписи виджета

Сначала прочитай AGENTS.md и skills/m1lash-studio/SKILL.md (раздел 4 «Заявки зрителей»).

## A. Ролик для @ErnestoMarsel
Заявка (комментарий под «Скажи моё имя 💀»): «Сделай момент со смехом Уолтера в подвале в конце 11 серии 4 сезона. Желательно в оригинале».
Решения Дениса 30.10 (все «да»):
1. Звук — оригинальная английская дорожка + русские кинетические субтитры (исключение только для заявок).
2. Название сериала нигде публично не писать (AGENTS §8). Название ролика: «По заявке @ErnestoMarsel 💀 #shorts»; в первом кадре текст «По заявке @ErnestoMarsel». В конце — голос Димы (TTS) с CTA, последние слова — название сериала (по правилу кино-Shorts).
3. Исходник — лицензированный клип Movieclips «Breaking Bad — Where Is the Money? (S4E11)»: https://www.youtube.com/watch?v=ZRp77ae7tkQ (© Sony). С раннеров GitHub YouTube не качается (бот-проверка) — скачай через свой браузер/ПК, обходить защиту нельзя. Нужен финал сцены: Уолт в подвале, смех. Исходник в репо/релизы не класть.
4. Формат: 1080×1920 на весь кадр, лица не обрезать, 30–45 с + финал 2–3 с, первый кадр — событие. Стиль S6-D25. Проверка AGENTS §12 + tools/movie_edit/validate_mystery.py.
5. Залить ПРИВАТНО без даты: youtube-direct.yml mode=upload, манифест publishing/queue/request_ernesto.json, строка в publishing/queue.json (status: review), PUBLISH.md. Закреп-текст для Дениса: «@ErnestoMarsel, сделали по твоей заявке! Какую сцену следующей?». Дату НЕ ставить — ждём «заливаем» от Дениса.
6. Запиши результат в HANDOFF.md и урок в skills/m1lash-studio/SKILL.md §7.

## B. Постоянный ключ подписи Android-виджета (5 минут)
Без него каждая сборка APK подписана новым ключом и обновление не ставится поверх.
```
keytool -genkeypair -keystore m1w.jks -alias m1lash -keyalg RSA -keysize 2048 -validity 20000 -dname "CN=M1lash Widget" -storepass "<придумай пароль>" -keypass "<тот же пароль>"
base64 -w0 m1w.jks | gh secret set WIDGET_KEYSTORE_B64 -R osminoog09-star/Shorts
printf %s "<пароль>" | gh secret set WIDGET_KEYSTORE_PASSWORD -R osminoog09-star/Shorts
rm m1w.jks
```
Потом Actions → «Android widget APK» → Run workflow. В логе не должно быть предупреждения «WIDGET_KEYSTORE_B64 не задан». Ключ и пароль никуда не писать (ни в репо, ни в чат).
