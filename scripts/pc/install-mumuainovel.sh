#!/usr/bin/env bash
# MuMuAINovel (xiamuceer-j, GPL-3.0): ИИ-помощник для длинных историй (персонажи, главы, сюжетные линии).
# Нам: черновики сюжетов длинных роликов 21+ мин. Интерфейс на китайском. Нужен Docker + ключ OpenAI/Claude/Gemini.
# Запуск: bash scripts/pc/install-mumuainovel.sh [папка]  → http://localhost:8000
set -euo pipefail
DIR="${1:-$HOME/ai/MuMuAINovel}"
command -v docker >/dev/null || { echo "Нужен Docker"; exit 1; }
[ -d "$DIR/.git" ] || git clone https://github.com/xiamuceer-j/MuMuAINovel "$DIR"
cd "$DIR"
[ -f .env ] || cp backend/.env.example .env 2>/dev/null || true
echo "Впиши API-ключ в $DIR/.env, затем: docker compose up -d"
