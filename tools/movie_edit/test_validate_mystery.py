#!/usr/bin/env python3
"""Self-contained regression tests: no secret title in public fields or visible cards."""
import copy
import json
import unittest
from pathlib import Path

from validate_mystery import check_manifest


ROOT = Path(__file__).parent
EXAMPLE = json.loads((ROOT / "mystery_release.example.json").read_text(encoding="utf-8"))


class MysteryValidationTests(unittest.TestCase):
    def fresh(self):
        return copy.deepcopy(EXAMPLE)

    def assert_bad(self, obj, needle):
        problems = check_manifest(obj)
        self.assertTrue(any(needle in x for x in problems), problems)

    def test_template_draft_passes(self):
        self.assertEqual(check_manifest(self.fresh()), [])

    def test_public_title_spoiler_is_rejected(self):
        obj = self.fresh()
        obj["public"]["title"] += " Тайный фильм"
        self.assert_bad(obj, "public.title")

    def test_english_alias_hidden_in_hashtag_is_rejected(self):
        obj = self.fresh()
        obj["public"]["hashtags"].append("#SecretMovie")
        self.assert_bad(obj, "public.hashtags")

    def test_burnt_caption_spoiler_is_rejected(self):
        obj = self.fresh()
        obj["public"]["captions"].append("ТАЙНЫЙ ФИЛЬМ")
        self.assert_bad(obj, "public.captions")

    def test_public_filename_spoiler_is_rejected(self):
        obj = self.fresh()
        obj["public"]["public_filename"] = "secret_movie_short.mp4"
        self.assert_bad(obj, "public.public_filename")

    def test_pinned_comment_spoiler_is_rejected(self):
        obj = self.fresh()
        obj["public"]["pinned_comment"] += " secret movie"
        self.assert_bad(obj, "public.pinned_comment")

    def test_voice_provider_mismatch_is_rejected(self):
        obj = self.fresh()
        obj["outro"]["last_title_voice_id"] = "piper:ru_RU-dmitri"
        self.assert_bad(obj, "same voice ID")

    def test_film_name_must_be_last_and_standalone(self):
        obj = self.fresh()
        obj["outro"]["spoken_lines"].append("Благодарю за просмотр!")
        self.assert_bad(obj, "last spoken line")

    def test_film_name_must_not_appear_earlier(self):
        obj = self.fresh()
        obj["outro"]["spoken_lines"].insert(0, "Тайный фильм")
        self.assert_bad(obj, "BEFORE final line")

    def test_visible_title_is_rejected(self):
        obj = self.fresh()
        obj["outro"]["title_visible_on_screen"] = True
        self.assert_bad(obj, "NEVER be shown")

    def test_horizontal_window_is_rejected(self):
        obj = self.fresh()
        obj["video"]["full_bleed"] = False
        self.assert_bad(obj, "full_bleed")

    def test_unverified_release_cannot_mark_ready(self):
        obj = self.fresh()
        obj["publication"]["publish_ready"] = True
        self.assert_bad(obj, "film rights not verified")


if __name__ == "__main__":
    unittest.main()
