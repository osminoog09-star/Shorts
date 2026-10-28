#!/usr/bin/env python3
"""Offline regression: no unapproved voice or legacy outro in news renderer."""
from pathlib import Path
src=(Path(__file__).resolve().parents[1]/"render_news_20261028.py").read_text()
assert "VOICE NO-GO" in src
assert "verify_outro()" in src
assert "ru-RU-DmitryNeural" in src
assert "hashlib.sha256(OUTRO.read_bytes())" in src
assert 'python","-m","piper' not in src
assert "edge_failed" not in src
print("PASS: news voice policy")
