"""No-network tests for scripts.hdrezka_intake: validators, quality and no false success."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

P = Path(__file__).resolve().parents[1] / "hdrezka_intake.py"
spec = importlib.util.spec_from_file_location("hdrezka_intake", P)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class IntakeTests(unittest.TestCase):
    def test_https_rezka_film(self):
        url = "https://rezka.ag/films/drama/54016-oppengeymer-2023-latest.html"
        self.assertEqual(mod.validate_source(url), url)

    def test_no_ssrf_userinfo_other_hosts_or_local_ports(self):
        for url in (
            "http://rezka.ag/films/drama/foo.html",
            "https://rezka.ag.evil.com/films/drama/foo.html",
            "https://evil.com/films/drama/foo.html",
            "https://user:pass@rezka.ag/films/drama/foo.html",
            "https://rezka.ag:8080/films/drama/foo.html",
            "https://rezka.ag/anything/foo.html",
            "https://rezka.ag/series/comedy/foo.html",
            "https://rezka.ag/cartoons/family/foo.html",
            "https://rezka.ag/anime/action/foo.html",
            "https://rezka.ag/animation/short/foo.html",
            "https://rezka.ag/films/drama/foo.html?url=https://127.0.0.1",
        ):
            with self.subTest(url=url), self.assertRaises(mod.IntakeError):
                mod.validate_source(url)

    def test_quality_parsing_premium_vs_normal(self):
        q = mod.parse_qualities("Film (2023)\nVoice A\n  1080p Ultra (premium): 3 GB\n  720p: 1.7 GB\nVoice B\n  1080p: 3 GB\n")
        self.assertEqual(q, {"1080p": "available", "720p": "available"})

    def test_premium_not_claimed_free(self):
        q = mod.parse_qualities("  1080p Ultra (premium)\n  720p: 1 GB")
        self.assertEqual(q["1080p"], "premium")

    def test_strict_quality_and_early_drive_failure(self):
        url = "https://rezka.ag/films/drama/54016-oppengeymer-2023-latest.html"
        with patch.object(mod, "inspect", return_value={"720p": "available"}):
            with self.assertRaises(mod.IntakeError) as ctx:
                mod.job(url, "1080p", "download", "", "somefolderid123456", "", Path("/tmp"))
            self.assertEqual(ctx.exception.code, "quality_unavailable")
        with patch.object(mod, "inspect", return_value={"1080p": "available"}):
            with self.assertRaises(mod.IntakeError) as ctx:
                mod.job(url, "1080p", "download", "", "somefolderid123456", "", Path("/tmp"))
            self.assertEqual(ctx.exception.code, "drive_not_connected")

    def test_short_or_fake_video_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            fp = Path(td) / "bad.mp4"
            fp.write_bytes(b"tiny")
            with self.assertRaises(mod.IntakeError) as ctx:
                mod.verify_video(fp, 1080)
            self.assertEqual(ctx.exception.code, "download_failed")

    def test_non_movie_files_never_go_to_drive(self):
        with tempfile.TemporaryDirectory() as td:
            for filename in ("site_archive.zip", "kino_short.mp4.txt", "README.md"):
                path = Path(td) / filename
                path.write_text("not a movie", encoding="utf-8")
                with self.subTest(filename=filename), self.assertRaises(mod.IntakeError) as ctx:
                    mod.upload_to_drive(path, "1ANvcXlUj0wBv1CG5U0bBQGdH-32OyaAi", "ignored")
                self.assertEqual(ctx.exception.code, "invalid_media_type")

    def test_safe_filename(self):
        out = mod.safe_output_name("https://rezka.ag/films/drama/54016-oppengeymer-2023-latest.html", "1080p")
        self.assertTrue(out.endswith(".mp4"))
        self.assertTrue(out.startswith("54016-oppengeymer-2023-latest_1080p_"))
        self.assertNotIn("/", out)


if __name__ == "__main__":
    unittest.main()
