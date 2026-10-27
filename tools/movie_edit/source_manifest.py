#!/usr/bin/env python3
"""Build a valid FFmpeg concat manifest from a list of video files."""
from pathlib import Path
import sys


def main():
    if len(sys.argv) < 3:
        raise SystemExit('Usage: source_manifest.py manifest.txt clip1.mp4 [clip2.mp4 ...]')
    manifest = Path(sys.argv[1])
    paths = [Path(p).resolve() for p in sys.argv[2:]]
    for path in paths:
        if not path.is_file():
            raise SystemExit(f'Missing clip: {path}')
        if "'" in str(path):
            raise SystemExit('Single quotes in file paths are unsupported')
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(''.join("file '{}'".format(p) + chr(10) for p in paths), encoding='utf-8')
    print(f'Wrote {len(paths)} clips to {manifest}')


if __name__ == '__main__':
    main()
