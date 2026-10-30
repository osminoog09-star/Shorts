#!/usr/bin/env bash
# OpenHands Agent Canvas (MIT): self-hosted центр управления агентами (OpenHands, Claude Code, Codex…).
# Вариант с Docker-песочницей (агент видит только PROJECTS_PATH). Windows — см. README.windows.md в репо OpenHands.
# Запуск: bash scripts/pc/install-openhands.sh [папка проектов]  → http://127.0.0.1:8000
set -euo pipefail
command -v docker >/dev/null || { echo "Нужен Docker Desktop / Docker Engine"; exit 1; }
export PROJECTS_PATH="${1:-$HOME/projects}"
mkdir -p "$PROJECTS_PATH" "$HOME/.openhands"
docker run -it --rm -p 127.0.0.1:8000:8000 -e AGENT_CANVAS_ALLOW_LAN_SESSION_KEY=true \
  -v "$HOME/.openhands:/home/openhands/.openhands" -v "${PROJECTS_PATH}:/projects" \
  ghcr.io/openhands/agent-canvas:1.34.0
