#!/usr/bin/env python3
"""M1lash voice-cast release gate. Current owner decision: 2026-10-28.

Dima (ru-RU-DmitryNeural) is the author/main narrator in ALL new videos,
including host CTA and mystery-film reveal. Sveta (ru-RU-SvetlanaNeural)
is a secondary character voice. Never silently substitute Liam/Piper/eSpeak.
"""
from __future__ import annotations

DIMA = "ru-RU-DmitryNeural"
SVETA = "ru-RU-SvetlanaNeural"
APPROVED = {DIMA: "dima", SVETA: "sveta"}


def validate_job(job: dict) -> list[tuple[str, str, str, str, str]]:
    """Return (line-id, text, voice-id, rate, pitch) after strict validation."""
    if job.get("voice") != DIMA:
        raise ValueError(f"NO-GO: main narrator must be Dima ({DIMA}); got {job.get('voice')!r}")
    lines = job.get("lines")
    if not isinstance(lines, list) or not lines:
        raise ValueError("NO-GO: empty or malformed TTS lines")
    result = []
    seen = set()
    for line in lines:
        ident = line.get("id")
        text = line.get("text")
        voice = line.get("voice", DIMA)
        rate = line.get("rate", job.get("rate", "+0%"))
        pitch = line.get("pitch", job.get("pitch", "+0Hz"))
        if not isinstance(ident, str) or not ident or "/" in ident or "\\" in ident or ident in seen:
            raise ValueError(f"NO-GO: invalid/duplicate line id: {ident!r}")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"NO-GO: empty speech at {ident}")
        if voice not in APPROVED:
            raise ValueError(f"NO-GO: unauthorized voice at {ident}: {voice!r}")
        if not isinstance(rate, str) or not isinstance(pitch, str):
            raise ValueError(f"NO-GO: invalid rate/pitch at {ident}")
        seen.add(ident)
        result.append((ident, text, voice, rate, pitch))
    return result
