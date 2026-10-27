#!/usr/bin/env python3
"""Offline preflight for M1lash movie-mystery Shorts metadata/voice/format.

Checks manifest declarations, NOT actual encoded image/audio or film rights.
Real listening, frames, licenses, and Content ID review remain mandatory.
Usage: python tools/movie_edit/validate_mystery.py release.json
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path


def normalized(text: str) -> str:
    """Fold case/ё/punctuation, making title in tags or hyphens detectable."""
    text = unicodedata.normalize("NFKC", str(text)).casefold().replace("ё", "е")
    return "".join(char for char in text if char.isalnum())


def public_strings(obj: object, name: str = "public"):
    if isinstance(obj, str):
        yield name, obj
    elif isinstance(obj, dict):
        for key, value in obj.items():
            yield from public_strings(value, f"{name}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from public_strings(value, f"{name}[{i}]")


def alias_present(alias: str, s: str) -> bool:
    a = normalized(alias)
    if not a:
        return False
    if len(a) >= 5:
        return a in normalized(s)
    # Short film titles, e.g. "Оно", must not match parts of other words.
    folded = unicodedata.normalize("NFKC", s).casefold().replace("ё", "е")
    word = re.escape(unicodedata.normalize("NFKC", alias).casefold().replace("ё", "е"))
    return re.search(r"(?<!\w)" + word + r"(?!\w)", folded) is not None


def check_manifest(data: dict) -> list[str]:
    errors = []
    internal = data.get("internal") or {}
    public = data.get("public") or {}
    outro = data.get("outro") or {}
    video = data.get("video") or {}
    publication = data.get("publication") or {}
    title = str(internal.get("film_title") or "").strip()
    aliases = list(internal.get("film_title_aliases") or [])
    if not title:
        errors.append("internal.film_title: missing private title")
    if not aliases:
        errors.append("internal.film_title_aliases: list Russian/original/translit names")
    aliases = [title] + [str(x) for x in aliases if x]
    if not isinstance(public, dict) or not public:
        errors.append("public: missing publish package")
    else:
        required = ["title", "description", "tags", "hashtags", "pinned_comment",
                    "thumbnail_text", "public_filename", "captions", "end_card_text"]
        for key in required:
            if key not in public:
                errors.append(f"public.{key}: required even if empty")
        for field, value in public_strings(public):
            for alias in aliases:
                if alias_present(alias, value):
                    errors.append(f"{field}: SPOILER, contains film title/alias ({alias})")
        filename = str(public.get("public_filename") or "")
        if not filename.lower().endswith(".mp4"):
            errors.append("public.public_filename: expected .mp4")

    cta_voice = str(outro.get("cta_voice_id") or "").strip()
    reveal_voice = str(outro.get("last_title_voice_id") or "").strip()
    if not cta_voice or not reveal_voice or cta_voice != reveal_voice:
        errors.append("outro: CTA and final title MUST have the exact same voice ID/provider")

    if outro.get("title_visible_on_screen") is not False:
        errors.append("outro.title_visible_on_screen: title must NEVER be shown")

    cta = normalized(outro.get("cta_text") or "")
    if not all(p in cta for p in ("подпиш", "спасибо", "лайк")):
        errors.append("outro.cta_text: include subscription, thank-you, like")
    speech = outro.get("spoken_lines") or []
    if not isinstance(speech, list) or len(speech) < 2:
        errors.append("outro.spoken_lines: CTA must precede final movie title")
    else:
        if not all(isinstance(x, str) for x in speech):
            errors.append("outro.spoken_lines: all entries must be text")
        else:
            last = normalized(speech[-1])
            if title and last != normalized(title):
                errors.append("outro.spoken_lines: very last spoken line must be ONLY the film title")
            if not any("подпиш" in normalized(x) and "лайк" in normalized(x) for x in speech[:-1]):
                errors.append("outro.spoken_lines: full CTA must come before the title")
            for line in speech[:-1]:
                if any(alias_present(alias, line) for alias in aliases):
                    errors.append("outro.spoken_lines: film title is spoken BEFORE final line")
                    break

    if video.get("width") != 1080 or video.get("height") != 1920 or video.get("full_bleed") is not True:
        errors.append("video: require full-screen 1080x1920 full_bleed=true")
    if video.get("dialogue_language") != "ru":
        errors.append("video.dialogue_language: movie-edit RU requires Russian dialogue")
    if video.get("music_ducking") is not True:
        errors.append("video.music_ducking: voice must remain intelligible")

    if publication.get("publish_ready") is True:
        if internal.get("film_rights_verified") is not True:
            errors.append("publication: film rights not verified")
        for field in ("music_license_verified", "visual_qa_done", "audio_qa_done"):
            if video.get(field) is not True:
                errors.append(f"publication: video.{field} must be true before release")
        if outro.get("lip_sync_verified") is not True:
            errors.append("publication: host mouth motion QA not done")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python tools/movie_edit/validate_mystery.py release.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("JSON root must be an object")
    except (OSError, ValueError) as ex:
        print(f"ERROR: cannot open manifest: {ex}", file=sys.stderr)
        return 2
    errors = check_manifest(data)
    if errors:
        print("FAIL: movie-mystery preflight")
        for x in errors:
            print(" -", x)
        return 1
    print("PASS: public text contains no configured title aliases; voice IDs and declared format agree.")
    if data.get("publication", {}).get("publish_ready") is not True:
        print("NOTE: DRAFT ONLY. Verify actual audio voice, frames, licenses/rights and QA separately.")
    else:
        print("NOTE: Manifest PASS alone does not certify an actual MP4 or legal rights.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
