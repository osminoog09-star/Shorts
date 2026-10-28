#!/usr/bin/env python3
"""Offline no-network gate for M1lash Dima/Sveta voice policy."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from voice_cast import DIMA, SVETA, validate_job

assert validate_job({"voice": DIMA, "lines": [
    {"id": "n1", "text": "Автор говорит.", "voice": DIMA},
    {"id": "f1", "text": "Отвечает Света.", "voice": SVETA},
]})[1][2] == SVETA

for bad in ("en-US-GuyNeural", "ru-RU-Dmitri-medium", "Liam", "espeak", None):
    try:
        validate_job({"voice": DIMA, "lines": [{"id": "bad", "text": "Привет", "voice": bad}]})
        raise AssertionError(f"accepted unauthorized {bad}")
    except ValueError:
        pass

try:
    validate_job({"voice": SVETA, "lines": [{"id": "intro", "text": "Привет"}]})
    raise AssertionError("Svetlana accepted as default author voice")
except ValueError:
    pass

# Existing production jobs should remain valid; no changes to historical audio files.
root = Path(__file__).resolve().parents[2]
checked = 0
for p in (root / "jobs" / "tts").glob("*.json"):
    validate_job(json.loads(p.read_text(encoding="utf-8")))
    checked += 1
assert checked > 0, "No job fixtures found"
print(f"PASS: Dima/Sveta policy and {checked} existing TTS jobs")
