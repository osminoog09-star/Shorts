#!/usr/bin/env python3
"""Regression tests: public Drive inventory never fabricates a verified scene."""
import sys
import unittest
import json
from io import BytesIO
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import drive_folder_intake as intake


class DriveIntakeTests(unittest.TestCase):
    def test_private_drive_list_uses_oauth_without_public_sharing(self):
        from drive_oauth_config import FOLDER
        class Reply:
            def __init__(self, value): self.value=value
            def __enter__(self): return BytesIO(json.dumps(self.value).encode())
            def __exit__(self, *args): return False
        env = {"GDRIVE_REFRESH_TOKEN":"fake-secret"}
        with patch("drive_oauth_config.resolve_existing_client", return_value=(
            {"_GDRIVE_ACCESS_TOKEN":"mock-access-token"}, "youtube"
        )), patch.object(intake, "urlopen", return_value=Reply({
            "files":[{"id":"abcdefghijklmnop", "name":"Whiplash.2014.mp4",
                       "mimeType":"video/mp4"}]
        })) as requested:
            found=intake.list_folder_authenticated(
                "https://drive.google.com/drive/folders/" + FOLDER, env)
        self.assertEqual(found, [{
            "path":"Whiplash.2014.mp4",
            "url":"https://drive.google.com/file/d/abcdefghijklmnop/view"
        }])
        self.assertIn("Bearer mock-access-token", requested.call_args.args[0].headers.values())
        self.assertNotIn("fake-secret", json.dumps(found))

    def test_private_drive_requires_secret_and_owner_folder(self):
        from drive_oauth_config import FOLDER
        with self.assertRaisesRegex(RuntimeError,"GDRIVE_REFRESH_TOKEN"):
            intake.list_folder_authenticated(
                "https://drive.google.com/drive/folders/" + FOLDER, {})
        with self.assertRaisesRegex(RuntimeError,"не совпадает"):
            intake.list_folder_authenticated(
                "https://drive.google.com/drive/folders/ABCDEFGHIJKLMNOP", {
                    "GDRIVE_REFRESH_TOKEN":"secret"
                })

    def test_folder_allowlist(self):
        url = "https://drive.google.com/drive/folders/ABCDEFGHIJKLMN?usp=sharing"
        self.assertEqual(intake.folder_url(url), "https://drive.google.com/drive/folders/ABCDEFGHIJKLMN")
        for bad in [
            "http://drive.google.com/drive/folders/ABCDEFGHIJKLMN",
            "https://drive.google.com.evil.test/drive/folders/ABCDEFGHIJKLMN",
            "https://drive.google.com/file/d/ABCDEFGHIJKLMN/view",
            "https://evil.test/drive/folders/ABCDEFGHIJKLMN",
        ]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                intake.folder_url(bad)

    def test_bilingual_title(self):
        self.assertGreaterEqual(intake.score("Старикам тут не место (2007)", "No.Country.For.Old.Men.2007.RU.mkv"), 90)
        self.assertGreaterEqual(intake.score("Одержимость (2014)", "whiplash_2014_rus.mp4"), 90)
        self.assertGreaterEqual(intake.score("Бэтмен (2022)", "The.Batman.2022.mkv"), 90)
        self.assertLess(intake.score("Меню (2022)", "trailer_the_menu_2022.mp4"), 85)

    def test_no_false_scene_claim(self):
        req = [{"id": "a", "film": "Одержимость (2014)", "status": "нужен"}]
        files = [{"path": "Whiplash.2014.mp4", "url": "https://drive.google.com/uc?id=abc"}]
        result = intake.summarize(files, req)
        self.assertEqual(result["matched_film_count"], 1)
        self.assertEqual(result["items"][0]["status"], "фильм найден")
        self.assertIsNone(result["items"][0]["scene_start"])

    def test_privately_inspected_recordings_are_not_fake_full_movies(self):
        files=[
            {"path":"Screen_Recording_20261102_101336_Opera.mp4","url":"https://drive.google.com/file/d/batclipa/view"},
            {"path":"Screen_Recording_20261102_103133_Opera.mp4","url":"https://drive.google.com/file/d/batclipb/view"},
            {"path":"Screen_Recording_20261103_124519_Opera.mp4","url":"https://drive.google.com/file/d/oppclip/view"},
        ]
        req=[
            {"id":"w45-batman-riddler","film":"Бэтмен (2022)"},
            {"id":"w45-oppenheimer-trinity","film":"Оппенгеймер (2023)"},
            {"id":"w45-menu-burger","film":"Меню (2022)"},
        ]
        registry={"items":[
            {"filename":files[0]["path"],"film":req[0]["film"],"source_kind":"excerpt","priority":1},
            {"filename":files[1]["path"],"film":req[0]["film"],"source_kind":"excerpt","priority":2},
            {"filename":files[2]["path"],"film":req[1]["film"],"source_kind":"excerpt","priority":1},
        ]}
        got=intake.summarize(files,req,registry)
        self.assertEqual(got["file_count"],3)
        self.assertEqual(got["matched_film_count"],0)
        self.assertEqual(got["matched_excerpt_film_count"],2)
        self.assertEqual(got["missing"],["Меню (2022)"])
        self.assertEqual(got["items"][0]["status"],"отрывок найден")
        self.assertEqual(got["items"][0]["filename"],files[0]["path"])
        self.assertEqual(len(got["items"][0]["candidates"]),2)
        self.assertEqual(got["items"][1]["status"],"отрывок найден")
        self.assertEqual(got["items"][2]["status"],"нет фильма в папке")
        self.assertTrue(all(x["scene_start"] is None for x in got["items"]))

    def test_titled_full_movie_preferred_over_generic_excerpt(self):
        files=[{"path":"The.Batman.2022.mp4","url":"https://drive.google.com/file/d/full/view"},
               {"path":"Screen_Recording_20261102_101336_Opera.mp4","url":"https://drive.google.com/file/d/clip/view"}]
        req=[{"id":"w45-batman-riddler","film":"Бэтмен (2022)"}]
        registry={"items":[{"filename":files[1]["path"],"film":req[0]["film"],"source_kind":"excerpt"}]}
        got=intake.summarize(files,req,registry)
        self.assertEqual(got["items"][0]["status"],"фильм найден")
        self.assertEqual(got["items"][0]["filename"],files[0]["path"])
        self.assertEqual(got["matched_excerpt_film_count"],0)

    def test_ambiguous_requires_confirmation(self):
        req = [{"id": "a", "film": "Одержимость (2014)", "status": "нужен"}]
        files = [
            {"path": "Whiplash.2014.mkv", "url": "https://drive.google.com/uc?id=111"},
            {"path": "Whiplash.2014.mp4", "url": "https://drive.google.com/uc?id=222"},
        ]
        result = intake.summarize(files, req)
        self.assertEqual(result["items"][0]["status"], "нужно подтвердить фильм")
        req[0]["match_confirmed_filename"] = "Whiplash.2014.mkv"
        result = intake.summarize(files, req)
        self.assertEqual(result["items"][0]["status"], "фильм найден")


if __name__ == "__main__":
    unittest.main()
