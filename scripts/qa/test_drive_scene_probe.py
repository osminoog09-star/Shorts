#!/usr/bin/env python3
import sys
import unittest
import tempfile
from io import BytesIO
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from drive_scene_probe import drive_id, hint_range


class ProbeTests(unittest.TestCase):
    def test_hint_hours_minutes(self):
        self.assertEqual(hint_range("~00:28–00:35"), (1680, 2100))
        self.assertEqual(hint_range("~02:05–02:22"), (7500, 8520))
        self.assertEqual(hint_range("~01:45–01:55"), (6300, 6900))

    def test_private_fetch_uses_drive_api_bearer_not_public_gdown(self):
        from drive_scene_probe import fetch_private_film
        class Reply:
            def __init__(self): self.headers={"Content-Length":str(1_000_001)}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def __init_buffer(self): return BytesIO(b"x"*1_000_001)
            def read(self, size): 
                if not hasattr(self, "_buffer"): self._buffer=self.__init_buffer()
                return self._buffer.read(size)
        from drive_oauth_config import FOLDER
        class MetadataReply:
            def __enter__(self):
                return BytesIO((
                    '{"id":"ABCDEFGHIJKLMN","parents":["'+FOLDER+
                    '"],"mimeType":"video/mp4","size":"1000001"}').encode())
            def __exit__(self, *args): return False
        with tempfile.TemporaryDirectory() as temp, patch(
            "drive_oauth_config.resolve_existing_client",
            return_value=({"_GDRIVE_ACCESS_TOKEN":"mock-access"}, "youtube")
        ), patch("drive_scene_probe.urlopen", side_effect=[MetadataReply(),Reply()]) as api:
            saved=fetch_private_film(
                "https://drive.google.com/file/d/ABCDEFGHIJKLMN/view",
                Path(temp)/"film.bin", {"GDRIVE_REFRESH_TOKEN":"mock-refresh"})
            self.assertEqual(saved,1_000_001)
            self.assertIn("Bearer mock-access", api.call_args.args[0].headers.values())
            self.assertIn("alt=media",api.call_args.args[0].full_url)

    def test_private_media_rejects_file_outside_owner_folder(self):
        from drive_scene_probe import fetch_private_film
        from drive_oauth_config import FOLDER
        class MetadataReply:
            def __enter__(self):
                return BytesIO(b'{"id":"ABCDEFGHIJKLMN","parents":["another-folder"],"mimeType":"video/mp4","size":"1000001"}')
            def __exit__(self, *args): return False
        with tempfile.TemporaryDirectory() as temp, patch(
            "drive_oauth_config.resolve_existing_client",
            return_value=({"_GDRIVE_ACCESS_TOKEN":"mock-access"}, "youtube")
        ), patch("drive_scene_probe.urlopen", return_value=MetadataReply()) as api:
            with self.assertRaisesRegex(RuntimeError, "разрешённой папки"):
                fetch_private_film(
                    "https://drive.google.com/file/d/ABCDEFGHIJKLMN/view",
                    Path(temp)/"film.bin", {"GDRIVE_REFRESH_TOKEN":"mock-refresh"})
            self.assertEqual(api.call_count, 1, "No media bytes may be requested outside M1lash owner folder")

    def test_drive_id_allowlist(self):
        self.assertEqual(drive_id("https://drive.google.com/uc?id=ABCDEFGHIJKLMN"), "ABCDEFGHIJKLMN")
        self.assertEqual(drive_id("https://drive.google.com/file/d/ABCDEFGHIJKLMN/view"), "ABCDEFGHIJKLMN")
        for bad in ["https://evil.test/uc?id=ABCDEFGHIJKLMN",
                    "https://drive.google.com/file/d/ABCDEFGHIJKLMN",
                    "http://drive.google.com/uc?id=ABCDEFGHIJKLMN"]:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                drive_id(bad)


if __name__ == "__main__":
    unittest.main()
