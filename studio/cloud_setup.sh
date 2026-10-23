#!/usr/bin/env bash
# Установка студии в облачной сессии Claude (Linux, сеть только через реестры пакетов и GitHub).
# После запуска путь к браузеру для рендера лежит в studio/.browser
set -e
cd "$(dirname "$0")"
echo "== npm"
npm install --silent --no-audit --no-fund
echo "== python"
python3 -m pip install --quiet --break-system-packages numpy pillow piper-tts playwright 2>/dev/null || python3 -m pip install --quiet numpy pillow piper-tts playwright
echo "== браузер для Remotion"
python3 -m playwright install chromium-headless-shell >/dev/null 2>&1 || true
B=$(find / -path /proc -prune -o -type f -name chrome-headless-shell -print 2>/dev/null | head -1)
echo "$B" > .browser
echo "browser: $B"
echo "== RHVoice"
if ! command -v RHVoice-test >/dev/null; then
  (apt-get update -q >/dev/null 2>&1 || true)
  apt-get install -y -q rhvoice rhvoice-russian rhvoice-english >/dev/null
fi
command -v ffmpeg >/dev/null || apt-get install -y -q ffmpeg >/dev/null
echo "== голоса Piper"
mkdir -p voices
for v in ru-irinia-medium en-us-ryan-high en-us-ryan-medium en-us-lessac-medium; do
  if [ ! -f "voices/$v.onnx" ]; then
    curl -sSL -o "voices/voice-$v.tar.gz" "https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-$v.tar.gz"
    tar xzf "voices/voice-$v.tar.gz" -C voices && rm "voices/voice-$v.tar.gz"
  fi
done
echo "== готово"
