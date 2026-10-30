#!/usr/bin/env bash
# PersonaLive (GVCLab, Apache-2.0): живая анимация портрета, ~12 ГБ VRAM. Только для ПК Дениса (NVIDIA 12 ГБ).
# Запуск: bash scripts/pc/install-personalive.sh [папка]   (по умолчанию ~/ai/PersonaLive)
set -euo pipefail
DIR="${1:-$HOME/ai/PersonaLive}"
command -v nvidia-smi >/dev/null || { echo "Нет nvidia-smi — нужна видеокарта NVIDIA с драйвером"; exit 1; }
command -v conda >/dev/null || { echo "Нужна conda (Miniconda): https://docs.conda.io/en/latest/miniconda.html"; exit 1; }
[ -d "$DIR/.git" ] || git clone https://github.com/GVCLab/PersonaLive "$DIR"
cd "$DIR"
conda env list | grep -q '^personalive ' || conda create -y -n personalive python=3.10
conda run -n personalive pip install -r requirements_base.txt
echo "Дальше: скачать веса по README (раздел Download weights), затем inference_offline.py или web_start.sh (Node 18+)."
