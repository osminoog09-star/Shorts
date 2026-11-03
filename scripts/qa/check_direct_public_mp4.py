#!/usr/bin/env python3
"""Read 4 KiB from an officially documented public MP4; no download/upload.

This is a connectivity probe for the separate direct-MP4 fallback, NOT an
HDRezka test and NOT proof of a 20-minute source.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from direct_movie_intake import open_movie, require_mp4_header, IntakeError

PUBLIC_TEST_URL = "https://archive.org/download/ArcherProductionsInc/DuckandC1951.mp4"


def main() -> int:
    try:
        with open_movie(PUBLIC_TEST_URL, inspect_only=True) as response:
            chunk = response.read(4096)
            require_mp4_header(chunk)
        print("direct_public_mp4_probe: reachable, valid MP4 file signature; max 4096 bytes read, NO upload")
        return 0
    except IntakeError as error:
        print("direct_public_mp4_probe: blocked (" + error.code + ")")
    except Exception:
        print("direct_public_mp4_probe: failed (network or response error)")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
