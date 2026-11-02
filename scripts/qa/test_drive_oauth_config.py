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
            self.assertIn('"access_token":"mock-token"', mod.make_config(self.env))
            self.assertIn('"refresh_token":"1//dummy-test-refresh-value"', mod.make_config(self.env))

    def test_google_drive_disabled_api_classified_without_leaking_details(self):
        from urllib.error import HTTPError
        from unittest.mock import MagicMock
        from io import BytesIO
        import json
        def reply(obj):
            ctx = MagicMock()
            ctx.__enter__.return_value = BytesIO(json.dumps(obj).encode())
            return ctx
        reason = json.dumps({"error":{"errors":[
            {"reason":"accessNotConfigured","message":"PRIVATE ERROR DETAILS"}]}}).encode()
        problem = HTTPError("hidden",403,"bad",{},BytesIO(reason))
        with patch.object(mod, "urlopen", side_effect=[
            reply({"access_token":"mock-access"}),
            reply({"scope":"https://www.googleapis.com/auth/drive"}),
            problem]):
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.google_oauth_preflight(self.env)
        self.assertEqual(ctx.exception.code, "drive_api_disabled")
        self.assertNotIn("PRIVATE ERROR DETAILS",str(ctx.exception))

    def test_google_drive_other_403_does_not_claim_disabled_api(self):
        from urllib.error import HTTPError
        from unittest.mock import MagicMock
        from io import BytesIO
        import json
        def reply(obj):
            ctx=MagicMock()
            ctx.__enter__.return_value=BytesIO(json.dumps(obj).encode())
            return ctx
        problem=HTTPError("hidden",403,"bad",{},BytesIO(json.dumps({
            "error":{"errors":[{"reason":"rateLimitExceeded"}]}
        }).encode()))
        with patch.object(mod,"urlopen",side_effect=[
            reply({"access_token":"mock-access"}),
            reply({"scope":"https://www.googleapis.com/auth/drive"}),
            problem]):
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.google_oauth_preflight(self.env)
        self.assertEqual(ctx.exception.code,"drive_api_denied")

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

    def test_existing_legacy_oauth_client_used_when_main_client_denied(self):
        env = {**self.env, "YT_CLIENT_ID": "legacy.apps.googleusercontent.com",
               "YT_CLIENT_SECRET": "legacy-secret"}
        def check(candidate):
            if candidate["YOUTUBE_OAUTH_CLIENT_ID"].startswith("12345"):
                raise mod.DriveSetupError("oauth_client_denied", "Denied")
        with patch.object(mod, "google_oauth_preflight", side_effect=check) as preflight:
            resolved, label = mod.resolve_existing_client(env)
        self.assertEqual(label, "legacy")
        self.assertEqual(resolved["YOUTUBE_OAUTH_CLIENT_ID"],env["YT_CLIENT_ID"])
        self.assertEqual(resolved["GDRIVE_REFRESH_TOKEN"],env["GDRIVE_REFRESH_TOKEN"])
        self.assertEqual(preflight.call_count,2)

    def test_existing_oauth_client_unchanged_on_success(self):
        with patch.object(mod,"google_oauth_preflight",return_value=None) as preflight:
            resolved, label = mod.resolve_existing_client(self.env)
        self.assertEqual(label,"youtube")
        self.assertEqual(resolved["YOUTUBE_OAUTH_CLIENT_ID"],self.env["YOUTUBE_OAUTH_CLIENT_ID"])
        preflight.assert_called_once()

    def test_both_existing_clients_denied_safely(self):
        env = {**self.env, "YT_CLIENT_ID":"legacy.apps.googleusercontent.com",
               "YT_CLIENT_SECRET":"legacy-secret"}
        with patch.object(mod,"google_oauth_preflight",
                          side_effect=mod.DriveSetupError("oauth_client_denied","no access")):
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.resolve_existing_client(env)
        self.assertEqual(ctx.exception.code,"all_oauth_clients_denied")
        self.assertNotIn("legacy-secret",str(ctx.exception))

    def test_check_does_not_claim_success_on_rclone_failure(self):
        with patch.object(mod.subprocess, "run") as run:
            run.return_value.returncode = 1
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.check_access(Path("/tmp/config"))
            self.assertEqual(ctx.exception.code, "oauth_or_folder_denied")


if __name__ == "__main__":
    unittest.main()
