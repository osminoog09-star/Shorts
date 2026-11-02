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

    def test_google_oauth_invalid_grant_is_classified_without_leaking_body(self):
        from urllib.error import HTTPError
        import io
        body = b'{"error":"invalid_grant","error_description":"private-no-log"}'
        with patch.object(mod, "urlopen", side_effect=HTTPError("hidden",400,"bad",None,io.BytesIO(body))):
            with self.assertRaises(mod.DriveSetupError) as exc:
                mod.google_oauth_preflight(self.env)
        self.assertEqual(exc.exception.code, "refresh_token_rejected")
        self.assertNotIn("private-no-log",str(exc.exception))

    def test_google_oauth_detects_missing_drive_scope(self):
        from unittest.mock import MagicMock
        from io import BytesIO
        def reply(data):
            ctx=MagicMock()
            ctx.__enter__.return_value=BytesIO(__import__("json").dumps(data).encode())
            return ctx
        with patch.object(mod, "urlopen", side_effect=[
            reply({"access_token":"mock-token"}),reply({"scope":"https://www.googleapis.com/auth/youtube"})]):
            with self.assertRaises(mod.DriveSetupError) as exc:
                mod.google_oauth_preflight(self.env)
        self.assertEqual(exc.exception.code,"drive_scope_missing")

    def test_google_oauth_accepts_drive_folder_with_write_access(self):
        from unittest.mock import MagicMock
        from io import BytesIO
        import json
        def reply(data):
            ctx=MagicMock()
            ctx.__enter__.return_value=BytesIO(json.dumps(data).encode())
            return ctx
        with patch.object(mod, "urlopen", side_effect=[
            reply({"access_token":"mock-token"}),
            reply({"scope":"https://www.googleapis.com/auth/drive"}),
            reply({"id":mod.FOLDER,"mimeType":"application/vnd.google-apps.folder",
                   "capabilities":{"canAddChildren":True}})
        ]):
            self.assertIsNone(mod.google_oauth_preflight(self.env))

    def test_google_oauth_folder_readonly_rejected(self):
        from unittest.mock import MagicMock
        from io import BytesIO
        import json
        def reply(data):
            ctx=MagicMock()
            ctx.__enter__.return_value=BytesIO(json.dumps(data).encode())
            return ctx
        with patch.object(mod, "urlopen", side_effect=[
            reply({"access_token":"mock-token"}),
            reply({"scope":"https://www.googleapis.com/auth/drive"}),
            reply({"id":mod.FOLDER,"mimeType":"application/vnd.google-apps.folder",
                   "capabilities":{"canAddChildren":False}})
        ]):
            with self.assertRaises(mod.DriveSetupError) as exc:
                mod.google_oauth_preflight(self.env)
        self.assertEqual(exc.exception.code, "drive_folder_read_only")

    def test_check_does_not_claim_success_on_rclone_failure(self):
        with patch.object(mod.subprocess, "run") as run:
            run.return_value.returncode = 1
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.check_access(Path("/tmp/config"))
            self.assertEqual(ctx.exception.code, "oauth_or_folder_denied")


if __name__ == "__main__":
    unittest.main()
