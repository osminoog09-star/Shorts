#!/usr/bin/env bash
# Липсинк для 3D-ведущего: Rhubarb Lip Sync (MIT, офлайн, режим phonetic — работает с русским).
# ./tools/lipsync.sh <audio> <out.json>   → {"fps":30,"visemes":"XXBBCD..."} (буква на кадр: A–H, X)
set -e
IN="$1"; OUT="$2"; D="${RHUBARB_DIR:-/tmp/rhubarb}"
if [ ! -x "$D/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb" ]; then
  mkdir -p "$D"; curl -sL -o "$D/r.zip" https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.13.0/Rhubarb-Lip-Sync-1.13.0-Linux.zip
  (cd "$D" && unzip -q -o r.zip); chmod +x "$D/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb"
fi
ffmpeg -v error -y -i "$IN" -ac 1 -ar 16000 "$D/in.wav"
"$D/Rhubarb-Lip-Sync-1.13.0-Linux/rhubarb" -q -r phonetic -f json -o "$D/cues.json" "$D/in.wav"
python3 - "$D/cues.json" "$OUT" <<'PY'
import json,sys
c=json.load(open(sys.argv[1])); n=int(c['metadata']['duration']*30)+30; v=['X']*n
for m in c['mouthCues']:
    for f in range(int(m['start']*30), min(n, int(m['end']*30)+1)): v[f]=m['value']
json.dump({'fps':30,'visemes':''.join(v)},open(sys.argv[2],'w'))
PY
echo "ok $OUT"
