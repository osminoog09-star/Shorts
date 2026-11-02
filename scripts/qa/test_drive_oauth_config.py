"""Offline regression tests for Google Drive OAuth configuration; never use real secrets."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

modpath = Path(__file__).resolve().parents[1] / "drive_oauth_config.py"
spec = importlib.util.spec_from_file_location("drive_oauth_config", modpath)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class DriveConfigTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "GDRIVE_REFRESH_TOKEN": "1//dummy-test-refresh-value",
            "YOUTUBE_OAUTH_CLIENT_ID": "12345-abcdefgh.apps.googleusercontent.com",
            "YOUTUBE_OAUTH_CLIENT_SECRET": "GOCSPX-FAKE-only-for-tests",
        }

    def test_builds_drive_token_without_using_shared_rclone_client(self):
        s = mod.make_config(self.env)
        self.assertIn("[m1lash]", s)
        self.assertIn("scope = drive", s)
        self.assertIn("root_folder_id = " + mod.FOLDER, s)
        self.assertIn('"refresh_token":"1//dummy-test-refresh-value"', s)
        self.assertNotIn("access_token_value", s)

    def test_legacy_config_supported(self):
        s = mod.make_config({"GDRIVE_RCLONE_CONFIG": "[m1lash]\ntype = drive\ntoken = {}\n"})
        self.assertIn("type = drive", s)

    def test_missing_refresh_rejected(self):
        with self.assertRaises(mod.DriveSetupError) as ctx:
            mod.make_config({
                "YOUTUBE_OAUTH_CLIENT_ID": self.env["YOUTUBE_OAUTH_CLIENT_ID"],
                "YOUTUBE_OAUTH_CLIENT_SECRET": self.env["YOUTUBE_OAUTH_CLIENT_SECRET"]
            })
        self.assertEqual(ctx.exception.code, "missing_credentials")

    def test_newline_injection_rejected(self):
        for key in self.env:
            with self.subTest(key=key):
                env = dict(self.env)
                env[key] += "\n[malicious]"
                with self.assertRaises(mod.DriveSetupError):
                    mod.make_config(env)

    def test_private_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "rclone.conf"
            mod.save_config(self.env, config)
            self.assertEqual(config.stat().st_mode & 0o777, 0o600)

    def test_check_does_not_claim_success_on_rclone_failure(self):
        with patch.object(mod.subprocess, "run") as run:
            run.return_value.returncode = 1
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.check_access(Path("/tmp/config"))
            self.assertEqual(ctx.exception.code, "oauth_or_folder_denied")


if __name__ == "__main__":
    unittest.main()
