---
name: graphify
description: Локальная карта связей кода и документации M1lash с помощью Graphify. Использовать для сложных вопросов об архитектуре и трассировки зависимостей, не вместо обязательного чтения AGENTS.md/NOW.md.
license: Apache-2.0
repository: https://github.com/Graphify-Labs/graphify
---

# Graphify — навык архитектурного анализа M1lash

Официальный upstream: `Graphify-Labs/graphify`, ветка `v8`, просмотренный commit `59b5ab1151e031fb42e39cfc9a50bf96f2d57ae0`. Официальный PyPI-пакет **`graphifyy` (две y)**, команда `graphify`. Это проектная инструкция для Claude Code/Codex, **не установленный Python runtime** и не подключение Graphify Cloud/MCP. Перед запуском проверить версию пакета/документацию и изменения.

## Приоритет и безопасность

1. Сначала `tasks/NOW.md` (GPT/Codex), корневой `AGENTS.md`, `skills/m1lash-studio/SKILL.md`; Graphify не меняет утверждённые решения, существующие hooks, настроенные workflow, планы роликов и полномочия публикации.
2. Не запускать автоматический `graphify install` в корне репозитория: он может добавлять always-on hooks и править `AGENTS.md`. Этот навык уже зарегистрирован вручную; команды установки hooks/агентов из upstream **не исполнять**.
3. Без Graphify Cloud, телеметрии, MCP, ключей API, внешних LLM и отправки приватных файлов. Не сканировать `.env`, secrets, приватные голоса/MP4 и соседние каталоги. Начинать только с локального **`--code-only`**, `GRAPHIFY_BACKEND=none`. Не запускать `--watch`, `--mcp`, `--neo4j-push` и `--falkordb-push` по умолчанию.
4. Для одного точного файла/строки использовать обычный GitHub search/read. Строить граф только для большого кода или сложных зависимостей и при наличии локального checkout. Существующий `graphify-out/graph.json` лучше переиспользовать, но сначала проверить источник и дату.

## Активация на отдельной машине с checkout Shorts

Требуются Python ≥3.10, интернет для установки и `uv` или `pipx`. Ставить **изолированно**, не в глобальный Python и не запускать setup стороннего кода без просмотра:

```bash
uv tool install graphifyy
graphify --help
# Из корня локального checkout, без интеграции hooks:
GRAPHIFY_BACKEND=none GRAPHIFY_QUERY_LOG_DISABLE=1 graphify extract . --code-only
# Для графа по содержимому:
graphify query "Как связаны сборка ролика и проверка качества?"
graphify path "module-a" "module-b"
graphify explain "module-a"
```

CLI может меняться в новых версиях; сверить точные команды по `graphify --help`, не выдавать пример за выполненный smoke-test. Артефакты `graphify-out/graph.json`, `graph.html`, `GRAPH_REPORT.md` по умолчанию локальные, ничего из них автоматически не коммитить, не публиковать и не отправлять в Cloud.

## Отчётность

Завершать анализ проверяемыми файлами/путями и явным разделением фактов `EXTRACTED` от `INFERRED`; при отсутствии `graphify` писать `RUNTIME_NOT_INSTALLED` и продолжать штатными GitHub-инструментами. При настоящей установке зафиксировать используемую версию, код выхода CLI и smoke QA в `HANDOFF.md`.

## Источники

- https://github.com/Graphify-Labs/graphify
- https://github.com/Graphify-Labs/graphify/blob/v8/README.md
- upstream `graphify/skill-agents.md` — текстовый справочник, **не исполнять автоматически**. Лицензия Apache-2.0.
