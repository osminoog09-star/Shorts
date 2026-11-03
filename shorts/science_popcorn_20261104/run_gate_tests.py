#!/usr/bin/env python3
"""Run ONLY popcorn preflight gates in existing whitelisted motion job. No media."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
test = ROOT / "tests/test_popcorn_private_gates.py"
if not test.is_file():
    raise RuntimeError("Popcorn tests not checked out")
subprocess.run([sys.executable, str(test)], cwd=ROOT, check=True)
print("POPCORN_OFFLINE_UNIT_GATES_PASS: no voice/media/YouTube actions")
