"""No-network tests for one-time Drive authorization-code exchange."""
import importlib
import io
import json
import sys
import types
import unittest
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import MagicMock, patch

from scripts import drive_oauth_exchange as mod


class ExchangeTests(unittest.TestCase):
    def setUp(self):
        self.env = {
            "AUTH_NONCE": "9" * 32,
            "AUTH_KEY_ID": "github-secret-key-1",
            "AUTH_PUBLIC_KEY": "YQ==" * 16,  # intentionally dummy; overridden for success
            "AUTH_CLIENT_ID": "123-test.apps.googleusercontent.com",
            "GDRIVE_AUTH_CODE": "4/test-code-for-private-redirect",
            "YOUTUBE_OAUTH_CLIENT_ID": "123-test.apps.googleusercontent.com",
            "YOUTUBE_OAUTH_CLIENT_SECRET": "dummy-secret",
        }

    def test_invalid_nonce_never_exchanges(self):
        env = {**self.env, "AUTH_NONCE": "not-random"}
        with patch.object(mod, "urlopen") as go:
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.exchange_code(env)
        self.assertEqual(ctx.exception.code, "invalid_nonce")
        go.assert_not_called()

    def test_legacy_or_main_client_must_match_public_id(self):
        env = {**self.env, "AUTH_CLIENT_ID": "attacker.apps.googleusercontent.com"}
        with patch.object(mod, "urlopen") as go:
            with self.assertRaises(mod.DriveSetupError) as ctx:
                mod.exchange_code(env)
        self.assertEqual(ctx.exception.code, "oauth_client_changed")
        go.assert_not_called()

    def test_cannot_log_oauth_error_description_or_secret(self):
        env = {**self.env, "AUTH_CLIENT_ID": "mismatch.apps.googleusercontent.com"}
        with self.assertRaises(mod.DriveSetupError) as ctx:
            mod.exchange_code(env)
        self.assertNotIn("dummy-secret", str(ctx.exception))

    def test_one_time_exchange_outputs_only_sealed_token(self):
        fake_public = types.ModuleType("nacl.public")
        class PublicKey:
            def __init__(self, data): self.data=data
        class SealedBox:
            def __init__(self, key): pass
            def encrypt(self, secret): return b"sealed-" + secret[::-1]
        fake_public.PublicKey = PublicKey
        fake_public.SealedBox = SealedBox
        fake_nacl = types.ModuleType("nacl")
        fake_nacl.public = fake_public
        env = {**self.env, "AUTH_PUBLIC_KEY": "YQ=="}
        resp = MagicMock()
        resp.__enter__.return_value = io.BytesIO(json.dumps({
            "access_token": "hidden-access-token",
            "refresh_token": "private-new-refresh-value"
        }).encode())
        with patch.dict(sys.modules, {"nacl": fake_nacl, "nacl.public": fake_public}):
            with patch.object(mod, "urlopen", return_value=resp) as fetch:
                with patch.object(mod, "google_oauth_preflight") as preflight:
                    result=mod.exchange_code(env)
        self.assertEqual(result["status"],"ready")
        self.assertEqual(result["key_id"],env["AUTH_KEY_ID"])
        self.assertNotIn("private-new-refresh-value",json.dumps(result))
        self.assertNotIn("hidden-access-token",json.dumps(result))
        self.assertEqual(fetch.call_count,1)
        self.assertEqual(preflight.call_count,1)

    def test_exchange_failure_is_safely_classified(self):
        fake_public=types.ModuleType("nacl.public")
        fake_public.PublicKey=lambda x:x
        fake_public.SealedBox=lambda x:x
        fake_nacl=types.ModuleType("nacl")
        fake_nacl.public=fake_public
        env = {**self.env,"AUTH_PUBLIC_KEY":"YQ=="}
        err=HTTPError("https://oauth2.googleapis.com/token",400,"invalid",{},io.BytesIO(
            b'{"error":"invalid_grant","error_description":"PRIVATE CODE HERE"}'))
        with patch.dict(sys.modules,{"nacl":fake_nacl,"nacl.public":fake_public}):
            with patch.object(mod,"urlopen",side_effect=err):
                with self.assertRaises(mod.DriveSetupError) as ctx:
                    mod.exchange_code(env)
        self.assertEqual(ctx.exception.code,"auth_code_invalid")
        self.assertNotIn("PRIVATE CODE HERE",str(ctx.exception))


if __name__=="__main__":
    unittest.main()
