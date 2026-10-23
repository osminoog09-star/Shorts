#!/usr/bin/env bash
# Установка студии: Node-зависимости, голоса, Python-пакеты, RHVoice.
set -e
cd "$(dirname "$0")"
npm install
python3 -m pip install --quiet numpy pillow piper-tts || python3 -m pip install --quiet --break-system-packages numpy pillow piper-tts
# RHVoice (русские/английские голоса) — Linux (Debian/Ubuntu)
if command -v apt-get >/dev/null; then
  (sudo apt-get update -q && sudo apt-get install -y -q rhvoice rhvoice-russian rhvoice-english ffmpeg) || \
  (apt-get update -q && apt-get install -y -q rhvoice rhvoice-russian rhvoice-english ffmpeg)
fi
# Голоса Piper
mkdir -p voices
for v in ru-irinia-medium en-us-ryan-high en-us-ryan-medium en-us-lessac-medium; do
  if [ ! -f "voices/$v.onnx" ]; then
    curl -sSL -o "voices/voice-$v.tar.gz" "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-$v.tar.gz"
    tar xzf "voices/voice-$v.tar.gz" -C voices && rm "voices/voice-$v.tar.gz"
  fi
done
echo "Готово. Проверка: npm run list"
