"""No-network unit tests for direct, rights-cleared MP4 intake."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

P = Path(__file__).resolve().parents[1] / "direct_movie_intake.py"
spec = importlib.util.spec_from_file_location("direct_movie_intake", P)
import sys
sys.path.insert(0, str(P.parent))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ProbeResult:
    headers = {"Content-Length": "1048576"}
    def __init__(self, video=True):
        self.data = b"\\x00\\x00\\x00\\x18ftypisom" + b"X" * 4096 if video else b"<html>challenge</html>"
    def read(self, n):
        return self.data[:n]
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False


class DirectMovieTests(unittest.TestCase):
    def test_whitelist_and_unsafe_urls(self):
        accepted = [
            "https://archive.org/download/ArcherProductionsInc/DuckandC1951.mp4",
            "https://ia601606.us.archive.org/9/items/test/movie.mp4",
            "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_320x180.mp4",
            "https://github.com/example/repo/releases/download/v1/movie.mp4",
        ]
        for url in accepted:
            with self.subTest(url=url):
                self.assertEqual(mod.safe_source(url), url)
        refused = [
            "http://archive.org/download/x.mp4",
            "https://fakearchive.org/download/x.mp4",
            "https://archive.org.evil.example/x.mp4",
            "https://evil.test/private.mp4",
            "https://user:password@archive.org/download/x.mp4",
            "https://archive.org:8443/download/x.mp4",
            "https://archive.org/download/x.mp4?token=secret",
            "https://archive.org/download/x.m3u8",
            "https://archive.org/download/xx.html",
            "https://rezka.ag/films/drama/x.html",
            "https://127.0.0.1/private.mp4",
            "https://localhost/private.mp4",
        ]
        for url in refused:
            with self.subTest(url=url), self.assertRaises(mod.IntakeError):
                mod.safe_source(url)

    def test_fake_response_rejected(self):
        with self.assertRaises(mod.IntakeError) as error:
            mod.require_mp4_header(b"<html>fake anti-bot page</html>")
        self.assertEqual(error.exception.code, "not_mp4")

    def test_inspection_only_checks_header_never_claims_quality(self):
        url = "https://archive.org/download/ArcherProductionsInc/DuckandC1951.mp4"
        with patch.object(mod, "open_movie", return_value=ProbeResult()):
            result = mod.job(url, "inspect", "1080p", "", "", Path("/tmp"))
        self.assertTrue(result["reachable"])
        self.assertNotIn("height", result)
        self.assertNotIn("drive_uploaded", result)

    def test_remote_file_verification_requires_exact_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "movie.mp4"
            video.write_bytes(b"valid-content")
            fake = SimpleNamespace(returncode=0, stdout=json.dumps([
                {"Name":"movie.mp4","Size":12}
            ]))
            with patch.object(mod.subprocess, "run", return_value=fake):
                mod.confirm_drive_file(video, "/fake.conf")
            bad = SimpleNamespace(returncode=0, stdout=json.dumps([
                {"Name":"movie.mp4","Size":13}
            ]))
            with patch.object(mod.subprocess, "run", return_value=bad):
                with self.assertRaises(mod.IntakeError) as error:
                    mod.confirm_drive_file(video, "/fake.conf")
            self.assertEqual(error.exception.code, "drive_verify_failed")

    def test_download_requires_existing_oauth(self):
        url = "https://archive.org/download/ArcherProductionsInc/DuckandC1951.mp4"
        with tempfile.TemporaryDirectory() as tmp, self.assertRaises(mod.IntakeError) as error:
            mod.job(url, "download", "1080p", "", "/nonexistent/m1lash-rclone.conf", Path(tmp))
        self.assertEqual(error.exception.code, "drive_not_connected")


if __name__ == "__main__":
    unittest.main()
