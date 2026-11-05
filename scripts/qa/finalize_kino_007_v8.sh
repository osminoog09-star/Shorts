#!/usr/bin/env bash
# Kino_007 V8: non-destructive tail trim + private QA, NO UPLOAD.
# Usage: bash scripts/qa/finalize_kino_007_v8.sh /path/V8.mp4 [/path/V8_review.mp4]
set -euo pipefail
[[ $# -ge 1 && -f "$1" ]] || { echo "Usage: $0 V8.mp4 [OUT.mp4]"; exit 2; }
src="$(readlink -f "$1")"
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
dst="${2:-$(dirname "$src")/kino_007_v8_trimmed_PRIVATE_REVIEW.mp4}"
[[ "$dst" != "$src" ]] || { echo "Refusing overwrite"; exit 2; }
qa="${dst%.*}_qa"
mkdir -p "$qa"
duration="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$src")"
python3 - "$duration" <<'PY'
import sys
v=float(sys.argv[1])
if not 45 <= v <= 49:
    raise SystemExit(f"NO-GO: expected V8 ~46.567s; got {v:.3f}s")
PY
# Spoken title from prior V8 ASR ends ~43.121. Keep ~0.43s margin.
# Use stream copy, so the approved Denis voice/outro is not re-mixed.
ffmpeg -hide_banner -loglevel error -nostdin -y -i "$src" -t 43.55 \
  -map 0:v:0 -map 0:a:0 -c copy -movflags +faststart "$dst"
ffmpeg -hide_banner -loglevel error -xerror -i "$dst" -f null - \
  >"$qa/full_decode.log" 2>&1
ffprobe -v error -show_format -show_streams -of json "$dst" >"$qa/ffprobe.json"
ffmpeg -hide_banner -nostats -i "$dst" \
  -vf "blackdetect=d=0.06:pix_th=0.10,freezedetect=n=-50dB:d=0.55" \
  -an -f null - 2>"$qa/visual_events.log"
ffmpeg -hide_banner -nostats -i "$dst" \
  -af "silencedetect=noise=-35dB:d=0.4" -vn -f null - \
  2>"$qa/silence_events.log"
ffmpeg -hide_banner -nostats -i "$dst" \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" \
  -vn -f null - 2>"$qa/loudness_measure_only.log"
for t in 33.90 34.05 40.50 40.65 43.45; do
  ffmpeg -hide_banner -loglevel error -y -ss "$t" -i "$dst" \
    -frames:v 1 "$qa/frame_$t.jpg"
done
if [[ -f "$repo/skills/ext/ffmpeg-skill/scripts/check.py" ]]; then
  python3 "$repo/skills/ext/ffmpeg-skill/scripts/check.py" "$dst" \
    --platform shorts 2>&1 | tee "$qa/official_check.log"
else
  echo "NO-GO: official check.py missing" | tee "$qa/official_check.log"
fi
if [[ -f "$repo/skills/ext/ffmpeg-skill/scripts/look.py" ]]; then
  python3 "$repo/skills/ext/ffmpeg-skill/scripts/look.py" "$dst" \
    --tiles 3x2 --safe shorts -o "$qa/official_look.jpg" \
    2>&1 | tee "$qa/official_look.log"
else
  echo "NO-GO: official look.py missing" | tee "$qa/official_look.log"
fi
sha256sum "$dst" | tee "$qa/sha256.txt"
echo "PRIVATE REVIEW ONLY: inspect frame captures, listen for full title, inspect all QA logs."
echo "Not FINAL until official QA + manual visual/audio review + owner OK."
echo "$dst"
