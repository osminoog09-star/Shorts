---
name: m1lash-razgon
description: "Экспериментальный Razgon 2D Studio в M1lash: preflight, пилот, голосовые и художественные ограничения."
---
# Razgon 2D → M1lash

Сначала читать `AGENTS.md`, `CODEX_NOTICE.md`, `skills/m1lash-director/SKILL.md`, `skills/m1lash-animation-production/SKILL.md`, `skills/m1lash-quality-improvement/SKILL.md`, `tools/razgon/README.md`.

Использовать Razgon только как альтернативный экспериментальный рендер. Источник — пользовательский архив с закреплённым SHA256; не коммитить архив в открытый GitHub без подтверждённой лицензии. Remotion и график публикаций не менять.

До длинного рендера: 3 ракурса модели, 6 выражений, читаемые кисти/пальцы, физическое действие с контактом, 3–5 кадров для визуального аудита и 15–30 сек пилота. Техническое PASS ≠ художественное PASS.

Главный голос Дима (`ru-RU-DmitryNeural`) и финальный CTA Димой; Света (`ru-RU-SvetlanaNeural`) только второстепенные роли. Проверить метаданные и фактическую речь. Полный длинный релиз ≥21:00 и должен пройти `scripts/qa/longform_duration_gate.py`. Нет E2E / прав на ассеты / качества — статус NO-GO, не публиковать.
